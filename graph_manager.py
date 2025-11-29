import json
import networkx as nx
from typing import List, Dict, Any, Set
from models import Node, Edge, GraphResponse

class GraphManager:
    def __init__(self, json_path: str):
        self.json_path = json_path
        self.graph = nx.DiGraph()
        self.nodes_data: Dict[str, Node] = {}
        self.load_data()

    def load_data(self):
        with open(self.json_path, 'r') as f:
            data = json.load(f)
        
        for node_data in data.get('nodes', []):
            node = Node(**node_data)
            self.nodes_data[node.name] = node
            self.graph.add_node(node.name, **node.model_dump())
            
        for edge_data in data.get('edges', []):
            source = edge_data['from']
            targets = edge_data['to']
            if isinstance(targets, str):
                targets = [targets]
            
            # Ensure source exists
            if source not in self.nodes_data:
                # Create a placeholder node
                node = Node(name=source, kind="unknown")
                self.nodes_data[source] = node
                self.graph.add_node(source, **node.model_dump())

            for target in targets:
                # Ensure target exists
                if target not in self.nodes_data:
                    # Create a placeholder node
                    node = Node(name=target, kind="unknown")
                    self.nodes_data[target] = node
                    self.graph.add_node(target, **node.model_dump())
                
                self.graph.add_edge(source, target)

    def get_filtered_subgraph(self, start_public: bool = False, end_sink: bool = False, has_vulnerability: bool = False) -> GraphResponse:
        # 1. Identify Sources (S)
        if start_public:
            sources = {n for n, data in self.graph.nodes(data=True) if data.get('publicExposed')}
        else:
            sources = set(self.graph.nodes())

        # 2. Identify Targets (T)
        if end_sink:
            # Sinks are nodes with kind 'rds' or 'sqs' (based on observation) or maybe just leaf nodes?
            # Requirement says "Sink (rds/sql)".
            # Let's look for 'kind' in ['rds', 'sqs']
            targets = {n for n, data in self.graph.nodes(data=True) if data.get('kind') in ['rds', 'sqs']}
        else:
            targets = set(self.graph.nodes())

        # Helper to get reachable sets including the nodes themselves
        def get_descendants(nodes):
            result = set(nodes)
            for n in nodes:
                result.update(nx.descendants(self.graph, n))
            return result

        def get_ancestors(nodes):
            result = set(nodes)
            for n in nodes:
                result.update(nx.ancestors(self.graph, n))
            return result

        # 3. Calculate Valid Nodes
        if has_vulnerability:
            # Paths must go through a vulnerable node
            vulnerable_nodes = {n for n, data in self.graph.nodes(data=True) if data.get('vulnerabilities')}
            
            valid_nodes = set()
            
            # Optimization: If no vulnerable nodes, return empty
            if not vulnerable_nodes:
                return GraphResponse(nodes=[], edges=[])

            # For each vulnerable node v, we need paths S -> ... -> v -> ... -> T
            # Nodes involved = (Nodes on S->v) U (Nodes on v->T)
            # Nodes on S->v = Descendants(S) INTERSECT Ancestors(v)
            # Nodes on v->T = Descendants(v) INTERSECT Ancestors(T)
            
            reachable_from_S = get_descendants(sources)
            can_reach_T = get_ancestors(targets)
            
            for v in vulnerable_nodes:
                # Check if v is reachable from S and can reach T
                if v in reachable_from_S and v in can_reach_T:
                    # Nodes on path S -> v
                    nodes_to_v = reachable_from_S.intersection(get_ancestors([v]))
                    # Nodes on path v -> T
                    nodes_from_v = get_descendants([v]).intersection(can_reach_T)
                    
                    valid_nodes.update(nodes_to_v)
                    valid_nodes.update(nodes_from_v)
        else:
            # Standard flow: S -> ... -> T
            reachable_from_S = get_descendants(sources)
            can_reach_T = get_ancestors(targets)
            valid_nodes = reachable_from_S.intersection(can_reach_T)

        # 4. Construct Response
        subgraph = self.graph.subgraph(valid_nodes)
        
        response_nodes = []
        for n in subgraph.nodes():
            response_nodes.append(self.nodes_data[n])
            
        response_edges = []
        for u, v in subgraph.edges():
            response_edges.append(Edge(from_=u, to=v))
            
        return GraphResponse(nodes=response_nodes, edges=response_edges)
