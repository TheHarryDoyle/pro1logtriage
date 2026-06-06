from fastapi import FastAPI
from pydantic import BaseModel

class AnalyzeLogsRequest(baseModel):
    logs: list[str]


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

@app.post("/logs/analyze")
def analyze_logs(request: AnalyzeLogsRequest):
    return {
        "log_count": len(request.logs),
        "logs": request.logs
    }
    


@app.post("/logs/analyze-file")
def analyze_logs_file(file: bytes):
    return {"message": "analyze-file endpoint not built yet"}

@app.get("/logs/recent")
def get_recent_logs():
    return {"logs": []}

