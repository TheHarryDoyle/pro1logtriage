from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path



from routers.intro import router as intro_router
from routers.health import router as health_router  
from routers.logs import router as logs_router
from db.database import init_db
from routers.rules import router as rules_router


BASE_DIR = Path(__file__).resolve().parent

app = FastAPI()
init_db()

app.include_router(intro_router)
app.include_router(health_router)
app.include_router(logs_router)
app.include_router(rules_router)

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


@app.get("/", include_in_schema=False)
def website():
	return FileResponse(BASE_DIR / "static" / "index.html")








