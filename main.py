from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional


from services.log_parser import parse_log
from services.triage_engine import triage_log


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

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello, World!"}

@app.get("/health")
def health():
    return {"status": "OK"}

@app.get("/ready")
def ready():
    return {"ready": True}

@app.post("/logs/analyze", response_model=AnalyzeLogsResponse)
def analyze_logs(request: AnalyzeLogsRequest):
    lines = request.raw_log.splitlines()

    # Parse the log and triage it
    parsed_log = parse_log(request.raw_log)
    triage_result = triage_log(request.raw_log)

    response = AnalyzeLogsResponse(
        line_count=parsed_log["line_count"],
        timestamp=parsed_log["timestamp"],
        severity=parsed_log["severity"],
        component=parsed_log["component"],
        category=triage_result["category"],
        confidence=triage_result["confidence"],
        suggested_actions=triage_result["suggested_actions"],
        commands_to_check=triage_result["commands_to_check"],
        analyzed_lines=lines  # Just return the first 5 lines for analysis
    )
    return response
    


@app.post("/logs/analyze-file")
def analyze_logs_file(file: bytes):
    return {"message": "analyze-file endpoint not built yet"}

@app.get("/logs/recent")
def get_recent_logs():
    return {"logs": []}

