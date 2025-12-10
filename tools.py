from typing import Dict, Any, Awaitable, Callable, Union
import asyncio

ToolResult = Dict[str, Any]
ToolCallable = Callable[[Dict[str, Any]], Union[ToolResult, Awaitable[ToolResult]]]

_tools: Dict[str, ToolCallable] = {}

def register_tool(name: str):
    def deco(func: ToolCallable):
        _tools[name] = func
        return func
    return deco

def get_tool(name: str) -> ToolCallable:
    return _tools[name]

def list_tools():
    return list(_tools.keys())

@register_tool("extract_functions")
async def extract_functions(state: Dict[str, Any]) -> ToolResult:
    code = state.get("code", "")
    funcs = []
    parts = code.split("\n")
    cur = None
    for line in parts:
        if line.strip().startswith("def "):
            if cur:
                funcs.append(cur)
            cur = line + "\n"
        elif cur is not None:
            cur += line + "\n"
    if cur:
        funcs.append(cur)
    return {"functions": funcs, "function_count": len(funcs)}

@register_tool("check_complexity")
def check_complexity(state: Dict[str, Any]) -> ToolResult:
    funcs = state.get("functions", [])
    issues = []
    threshold = state.get("complexity_threshold", 20)
    for i, f in enumerate(funcs):
        lines = len([l for l in f.splitlines() if l.strip()])
        if lines > threshold:
            issues.append({"function_index": i, "lines": lines})
    return {"complexity_issues": issues}

@register_tool("detect_issues")
def detect_issues(state: Dict[str, Any]) -> ToolResult:
    funcs = state.get("functions", [])
    issues = []
    for i, f in enumerate(funcs):
        msgs = []
        if "TODO" in f or "FIXME" in f:
            msgs.append("todo")
        if f.count("return") > 3:
            msgs.append("many_returns")
        if msgs:
            issues.append({"function_index": i, "issues": msgs})
    return {"basic_issues": issues}

@register_tool("suggest_improvements")
def suggest_improvements(state: Dict[str, Any]) -> ToolResult:
    c = len(state.get("complexity_issues", []))
    b = len(state.get("basic_issues", []))
    score = 100 - c*10 - b*5
    return {"quality_score": max(0, score)}
