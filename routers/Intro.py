from fastapi import APIRouter

router = APIRouter(tags=["intro"])

@router.get("/")
def root():
    return {"message": "Hello, World!"}

@router.get("/ready")
def ready():
    return {"ready": True}