import json
import networkx as nx
from typing import List, Dict, Any, Set
from .models import Node, Edge, GraphResponse, Operator, FilterCriteria, GraphQuery

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

    def _evaluate_filter(self, node_data: dict, criteria: FilterCriteria) -> bool:
        val = node_data.get(criteria.field)
        
        if criteria.operator == Operator.EQ:
            return val == criteria.value
        elif criteria.operator == Operator.NEQ:
            return val != criteria.value
        elif criteria.operator == Operator.IN:
            return val in criteria.value
        elif criteria.operator == Operator.CONTAINS:
            if isinstance(val, list):
                return criteria.value in val
            return False
        return False

    def _get_matching_nodes(self, filters: List[FilterCriteria]) -> Set[str]:
        if not filters:
            return set(self.graph.nodes())
            
        matches = set()
        for n, data in self.graph.nodes(data=True):
            # Check if node satisfies ALL filters (AND logic)
            if all(self._evaluate_filter(data, f) for f in filters):
                matches.add(n)
        return matches

    def search(self, query: GraphQuery) -> GraphResponse:
        # 1. Identify Sources dynamically
        sources = self._get_matching_nodes(query.start_filters)

        # 2. Identify Targets dynamically
        targets = self._get_matching_nodes(query.end_filters)

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
        # If there are path filters, we treat them as "must pass through at least one node satisfying these"
        # Similar to the vulnerability logic
        
        valid_nodes = set()
        
        if query.path_filters:
            constraint_nodes = self._get_matching_nodes(query.path_filters)
            
            # Optimization: If no constraint nodes, return empty
            if not constraint_nodes:
                return GraphResponse(nodes=[], edges=[])

            reachable_from_S = get_descendants(sources)
            can_reach_T = get_ancestors(targets)
            
            for v in constraint_nodes:
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
