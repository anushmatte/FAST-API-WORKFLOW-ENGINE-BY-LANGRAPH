from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse
from .engine import Engine
from .models import RunRequest, GraphDef
from .workflows import node_extract, node_analyze_complexity, node_detect_issues, node_suggest

app = FastAPI(title="Quantum Workflow Backend")
engine = Engine()

# Register nodes
engine.register_node("extract", node_extract)
engine.register_node("analyze_complexity", node_analyze_complexity)
engine.register_node("detect_issues", node_detect_issues)
engine.register_node("suggest", node_suggest)

# Pre-create a default graph
engine.create_graph(
    "code_review_v1",
    [{"name":"extract"}, {"name":"analyze_complexity"}, {"name":"detect_issues"}, {"name":"suggest"}],
    {
        "extract": "analyze_complexity",
        "analyze_complexity": "detect_issues",
        "detect_issues": "suggest",
        "suggest": None
    },
    entry="extract"
)

@app.post("/graph/create")
async def create_graph(defn: GraphDef):
    """
    Create a new graph at runtime.
    Example GraphDef body:
    {
      "graph_id": "code_review_v2",
      "nodes": [{"name":"extract"}, {"name":"analyze_complexity"}, {"name":"detect_issues"}, {"name":"suggest"}],
      "edges": {"extract":"analyze_complexity","analyze_complexity":"detect_issues","detect_issues":"suggest","suggest":null},
      "entry": "extract"
    }
    """
    if engine.get_graph(defn.graph_id):
        raise HTTPException(status_code=400, detail="graph already exists")

    # Convert NodeDef list to the structure engine expects
    nodes = [{"name": n.name, "condition": n.condition} for n in defn.nodes]
    engine.create_graph(defn.graph_id, nodes, defn.edges, entry=defn.entry)
    return {"graph_id": defn.graph_id, "message": "graph created"}

@app.post("/graph/run")
async def run_graph(req: RunRequest, bg: BackgroundTasks):
    g = engine.get_graph(req.graph_id)
    if not g:
        return JSONResponse({"error": "graph not found"}, status_code=404)
    run = engine.create_run(req.graph_id, req.initial_state)
    # schedule execution in background
    bg.add_task(engine.run_graph, run.run_id)
    return {"run_id": run.run_id}

@app.get("/graph/result/{run_id}")
async def res(run_id: str):
    """
    Return final state and logs for a run_id.

    This function will try:
     1) engine.runs in-memory (default simple engine),
     2) engine._load_run(run_id) if you're using the DB-backed engine version.
    """
    # 1) prefer in-memory store if available
    r = None
    try:
        r = engine.runs.get(run_id)  # may raise AttributeError if no attribute
    except Exception:
        r = None

    # 2) fallback to engine loader if implemented (SQLite persistence engine)
    if not r and hasattr(engine, "_load_run"):
        try:
            r = engine._load_run(run_id)
        except Exception:
            r = None

    if not r:
        return JSONResponse({"error": "not found"}, status_code=404)

    # Build readable logs
    logs = []
    for l in getattr(r, "logs", []):
        # ExecutionLogItem may be pydantic model or dict-like
        node = getattr(l, "node", l.get("node") if isinstance(l, dict) else str(l))
        msg = getattr(l, "message", l.get("message") if isinstance(l, dict) else "")
        logs.append(f"{node}: {msg}")

    return {"state": getattr(r, "state", {}) , "logs": logs}
