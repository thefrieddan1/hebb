from graph_manager import GraphManager
import os

JSON_PATH = "train-ticket-be (1).json"
gm = GraphManager(JSON_PATH)

print(f"Nodes: {len(gm.graph.nodes)}")
print(f"Edges: {len(gm.graph.edges)}")

public_nodes = [n for n, d in gm.graph.nodes(data=True) if d.get('publicExposed')]
sink_nodes = [n for n, d in gm.graph.nodes(data=True) if d.get('kind') in ['rds', 'sqs']]
vulnerable_nodes = [n for n, d in gm.graph.nodes(data=True) if d.get('vulnerabilities')]

print(f"Public Nodes: {public_nodes}")
print(f"Sink Nodes: {sink_nodes}")
print(f"Vulnerable Nodes: {vulnerable_nodes}")

import networkx as nx

# Check reachability
for p in public_nodes:
    descendants = nx.descendants(gm.graph, p)
    print(f"Nodes reachable from {p}: {len(descendants)}")
    # print(descendants)
    
    for v in vulnerable_nodes:
        if v in descendants:
            print(f"  {p} can reach vulnerable node {v}")
            
    for s in sink_nodes:
        if s in descendants:
            print(f"  {p} can reach sink node {s}")

    for s in sink_nodes:
        if nx.has_path(gm.graph, p, s):
            print(f"Path exists from {p} to {s}")
            for path in nx.all_simple_paths(gm.graph, p, s):
                # Check if any vulnerable node is in the path
                vuln_in_path = [n for n in path if n in vulnerable_nodes]
                if vuln_in_path:
                    print(f"  FOUND PATH WITH VULNERABILITY: {path}")
                    print(f"  Vulnerable nodes: {vuln_in_path}")

# Check Vuln + Sink
print("Checking Vuln + Sink...")
for v in vulnerable_nodes:
    # Check if v can reach any sink
    for s in sink_nodes:
        if nx.has_path(gm.graph, v, s):
             print(f"Vulnerable node {v} can reach sink {s}")
