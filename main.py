from fastapi import FastAPI



from routers.intro import router as intro_router
from routers.health import router as health_router  
from routers.logs import router as logs_router
from db.database import init_db
from routers.rules import router as rules_router


app = FastAPI()
init_db()

app.include_router(intro_router)
app.include_router(health_router)
app.include_router(logs_router)
app.include_router(rules_router)








