from fastapi import APIRouter, HTTPException

from db.database import is_database_ready

router = APIRouter(tags=["intro"])

#@router.get("/")
#def root():
    #return {"message": "Hello, World!"}

@router.get("/ready")
def ready():
	if not is_database_ready():
		raise HTTPException(
			status_code=503,
			detail="Database is not ready"
		)

	return {
		"ready": True,
		"database": "ready"
	}