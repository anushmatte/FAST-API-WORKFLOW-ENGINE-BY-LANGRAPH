import asyncio, inspect
from typing import Dict, Any
from datetime import datetime
from .models import RunState, ExecutionLogItem

class Engine:
    def __init__(self):
        self.nodes = {}
        self.graphs = {}
        self.runs = {}
        self.subscribers = {}

    def register_node(self, name, func):
        self.nodes[name] = func

    def create_graph(self, graph_id, nodes, edges, entry):
        self.graphs[graph_id] = {"nodes": nodes, "edges": edges, "entry": entry}
        return graph_id

    def get_graph(self, graph_id):
        return self.graphs.get(graph_id)

    def create_run(self, graph_id, initial_state):
        run = RunState(graph_id=graph_id)
        run.state.update(initial_state)
        run.current_node = self.graphs[graph_id]["entry"]
        self.runs[run.run_id] = run
        return run

    async def _call_node(self, node_name, run: RunState):
        func = self.nodes[node_name]
        if inspect.iscoroutinefunction(func):
            res = await func(run.state)
        else:
            res = func(run.state)
            if inspect.isawaitable(res):
                res = await res
        return res or {}

    async def run_graph(self, run_id):
        run = self.runs[run_id]
        edges = self.graphs[run.graph_id]["edges"]

        while run.current_node and not run.completed:
            node = run.current_node
            await self._log(run, node, f"Running {node}")
            result = await self._call_node(node, run)

            if "state" in result:
                run.state.update(result["state"])

            next_node = result.get("next") or edges.get(node)

            if not next_node:
                run.completed = True
                await self._log(run, node, "Finished.")
                break

            run.current_node = next_node
            await asyncio.sleep(0)

        run.completed = True
        return run

    async def _log(self, run, node, msg):
        item = ExecutionLogItem(timestamp=datetime.utcnow(), node=node, message=msg, state_snapshot=run.state.copy())
        run.logs.append(item)

    def subscribe(self, run_id, cb):
        self.subscribers.setdefault(run_id, []).append(cb)

    def unsubscribe(self, run_id, cb):
        if run_id in self.subscribers:
            self.subscribers[run_id].remove(cb)
