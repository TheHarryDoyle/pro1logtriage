from fastapi import FastAPI, HTTPException



from services.log_parser import parse_log
from services.triage_engine import triage_log
from models.log_models import AnalyzeLogsRequest, AnalyzeLogsResponse
from routers.Intro import router as intro_router
from routers.health import router as health_router  
from routers.logs import router as logs_router
from db.database import init_db


app = FastAPI()
init_db()

app.include_router(intro_router)
app.include_router(health_router)
app.include_router(logs_router)








