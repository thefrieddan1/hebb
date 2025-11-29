from fastapi import FastAPI, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.graph_manager import GraphManager
from app.models import GraphResponse, GraphQuery
import os

app = FastAPI(title="Backslash Backend Exercise API")

# Initialize GraphManager
# JSON file is in data/
JSON_PATH = os.path.join(os.path.dirname(__file__), "data", "train-ticket-be (1).json")
graph_manager = GraphManager(JSON_PATH)

# Mount static directory
static_dir = os.path.join(os.path.dirname(__file__), "app", "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
async def read_index():
    return FileResponse(os.path.join(static_dir, "index.html"))


@app.post("/routes/search", response_model=GraphResponse)
async def search_routes(query: GraphQuery):
    return graph_manager.search(query)

# Legacy support (optional, but good for backward compatibility during dev)
@app.get("/routes", response_model=GraphResponse)
async def get_routes(
    start_public: bool = Query(False, description="Filter routes starting in a public service"),
    end_sink: bool = Query(False, description="Filter routes ending in a Sink (rds/sql)"),
    has_vulnerability: bool = Query(False, description="Filter routes that have a vulnerability in one of the nodes")
):
    # Map legacy params to new query structure
    query = GraphQuery()
    
    if start_public:
        query.start_filters.append({"field": "publicExposed", "operator": "eq", "value": True})
        
    if end_sink:
        query.end_filters.append({"field": "kind", "operator": "in", "value": ["rds", "sqs"]})
        
    if has_vulnerability:
        query.path_filters.append({"field": "vulnerabilities", "operator": "neq", "value": None})
    
    return graph_manager.search(query)
