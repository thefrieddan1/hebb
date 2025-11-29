from fastapi import FastAPI, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from graph_manager import GraphManager
from models import GraphResponse
import os

app = FastAPI(title="Backslash Backend Exercise API")

# Initialize GraphManager
# Assuming the JSON file is in the same directory for now, or passed via env var
JSON_PATH = os.path.join(os.path.dirname(__file__), "train-ticket-be (1).json")
graph_manager = GraphManager(JSON_PATH)

# Mount static directory
static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
async def read_index():
    return FileResponse(os.path.join(static_dir, "index.html"))


@app.get("/routes", response_model=GraphResponse)
async def get_routes(
    start_public: bool = Query(False, description="Filter routes starting in a public service"),
    end_sink: bool = Query(False, description="Filter routes ending in a Sink (rds/sql)"),
    has_vulnerability: bool = Query(False, description="Filter routes that have a vulnerability in one of the nodes")
):
    return graph_manager.get_filtered_subgraph(
        start_public=start_public,
        end_sink=end_sink,
        has_vulnerability=has_vulnerability
    )
