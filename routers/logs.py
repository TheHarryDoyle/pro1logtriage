from fastapi import APIRouter

from models.log_models import AnalyzeLogsRequest, AnalyzeLogsResponse
from services.log_parser import parse_log
from services.triage_engine import triage_log

router = APIRouter(prefix="/logs", tags=["logs"])

@router.post("/analyze", response_model=AnalyzeLogsResponse)
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
        analyzed_lines=lines  
    )
    return response
    


@router.post("/analyze-file")
def analyze_logs_file(file: bytes):
    return {"message": "analyze-file endpoint not built yet"}

@router.get("/recent")
def get_recent_logs():
    return {"logs": []}
