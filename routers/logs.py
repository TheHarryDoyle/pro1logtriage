from fastapi import APIRouter, UploadFile, File

from models.log_models import AnalyzeLogsRequest, AnalyzeLogsResponse
from services.log_parser import parse_log
from services.triage_engine import triage_log
from repositories.log_repository import save_log_analysis, get_recent_log_analyses

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
    save_log_analysis(request.raw_log, response)
    return response
    


@router.post("/analyze-file", response_model=AnalyzeLogsResponse)
async def analyze_logs_file(file: UploadFile = File(...)):
    content = await file.read()
    raw_log = content.decode("utf-8", errors="replace")

    lines = raw_log.splitlines()

    parsed_log = parse_log(raw_log)
    triage_result = triage_log(raw_log)

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
    save_log_analysis(raw_log, response)
    return response

@router.get("/recent")
def get_recent_logs():
    return {"logs": get_recent_log_analyses()}