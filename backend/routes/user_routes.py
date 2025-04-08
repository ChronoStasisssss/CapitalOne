from fastapi import APIRouter
from models.user import User
from services.ai_service import process_with_langchain

router = APIRouter()

@router.post("/analyze")
async def analyze_user(user: User):
    response = process_with_langchain(user.description)
    return {"result": response}
