from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from uuid import uuid4
from datetime import datetime

class NodeDef(BaseModel):
    name: str
    condition: Optional[str] = None

class GraphDef(BaseModel):
    graph_id: str
    nodes: List[NodeDef]
    edges: Dict[str, str]
    entry: str

class RunRequest(BaseModel):
    graph_id: str
    initial_state: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        json_schema_extra = {
            "example": {
                "graph_id": "code_review_v1",
                "initial_state": {
                    "code": "def foo(x):\\n    # TODO: improve\\n    a = x + 1\\n    return a\\n\\ndef bar(y):\\n    return y",
                    "quality_threshold": 85,
                    "complexity_threshold": 3
                }
            }
        }


class ExecutionLogItem(BaseModel):
    timestamp: datetime
    node: str
    message: str
    state_snapshot: Dict[str, Any] = Field(default_factory=dict)

class RunState(BaseModel):
    run_id: str = Field(default_factory=lambda: str(uuid4()))
    graph_id: str
    current_node: Optional[str] = None
    state: Dict[str, Any] = Field(default_factory=dict)
    completed: bool = False
    logs: List[ExecutionLogItem] = Field(default_factory=list)
