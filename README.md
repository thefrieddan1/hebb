# Backslash Backend Home Exercise

This project implements a RESTful API to query a microservices graph.

## Solution Design & Assumptions

### Design Decisions
*   **Graph Representation**: I chose to represent the "routes" as a **subgraph** (nodes and edges) rather than a list of individual paths. This avoids the combinatorial explosion of paths in highly connected graphs and provides a structure that is easier for clients to render visually.
*   **In-Memory Processing**: Given the dataset size, `networkx` in-memory processing provides the best balance of performance and simplicity.
*   **Robustness**: The loader handles data inconsistencies (e.g., edges pointing to undefined nodes) by creating placeholder nodes, ensuring the API remains functional even with imperfect data.

### Assumptions
*   **Filter Logic**: Multiple filters are applied as an **intersection** (AND logic). For example, selecting "Public" and "Sink" returns paths that *both* start at a public node AND end at a sink.
*   **Vulnerability Filter**: This filter restricts the result to paths that pass through *at least one* vulnerable node.
*   **Data Structure**: I assumed the provided JSON is the single source of truth, but the code is structured to easily swap the data source if needed.

## Setup

1.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Run the server:**
    ```bash
    uvicorn main:app --reload
    ```

## Graph Explorer UI

A simple web interface is available to explore the graph interactively.

1.  Start the server (if not already running).
2.  Open your browser and navigate to:
    `http://127.0.0.1:8000/`

You can use the checkboxes to toggle filters and view the resulting graph structure.

## API Usage

The API provides a single endpoint `/routes` to query the graph.

### Endpoint: `GET /routes`

**Query Parameters:**

*   `start_public` (bool, default: `False`): If `true`, returns routes that start in a public service (`publicExposed: true`).
*   `end_sink` (bool, default: `False`): If `true`, returns routes that end in a Sink service (RDS or SQS).
*   `has_vulnerability` (bool, default: `False`): If `true`, returns routes that involve a service with a known vulnerability.

**Response:**

Returns a JSON object representing the subgraph that satisfies the filters.

```json
{
  "nodes": [ ... ],
  "edges": [ ... ]
}
```

## Implementation Details

-   **Graph Library:** `networkx` is used for graph representation and algorithms.
-   **Web Framework:** `FastAPI` is used for the REST API.
-   **Logic:**
    -   The graph is loaded from the provided JSON file.
    -   Filtering is implemented by identifying valid source and target sets based on the parameters.
    -   The result is the intersection of paths from valid sources and paths to valid targets.
    -   If `has_vulnerability` is set, the paths are further restricted to those passing through at least one vulnerable node.
