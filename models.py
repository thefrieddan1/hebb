from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class Node(BaseModel):
    name: str
    kind: str
    language: Optional[str] = None
    path: Optional[str] = None
    publicExposed: Optional[bool] = None
    vulnerabilities: Optional[List[Dict[str, Any]]] = None
    metadata: Optional[Dict[str, Any]] = None

class Edge(BaseModel):
    from_: str
    to: str

    class Config:
        populate_by_name = True
        fields = {'from_': 'from'}

class GraphResponse(BaseModel):
    nodes: List[Node]
    edges: List[Edge]
