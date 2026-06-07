from pydantic import BaseModel
from typing import Optional


class AnalyzeLogsRequest(BaseModel):
    raw_log: str


class AnalyzeLogsResponse(BaseModel):
    line_count: int
    timestamp: Optional[str] = None
    severity: str
    component: str
    category: str
    confidence: float
    suggested_actions: str
    commands_to_check: list[str]
    analyzed_lines: list[str]