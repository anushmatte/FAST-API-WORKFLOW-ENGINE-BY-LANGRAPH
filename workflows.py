from .tools import get_tool

async def node_extract(state):
    t = get_tool("extract_functions")
    res = await t(state)
    state.update(res)
    return {"log": f"Extracted {res.get('function_count',0)}"}

def node_analyze_complexity(state):
    t = get_tool("check_complexity")
    res = t(state)
    state.update(res)
    return {"log": "Complexity analyzed"}

def node_detect_issues(state):
    t = get_tool("detect_issues")
    res = t(state)
    state.update(res)
    return {"log": "Issues detected"}

def node_suggest(state):
    t = get_tool("suggest_improvements")
    res = t(state)
    state.update(res)
    return {"log": f"Score {res.get('quality_score')}"}