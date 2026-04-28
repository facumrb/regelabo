from fastapi import APIRouter, HTTPException
from src.models.user_model import UserCreate, UserModel
from src.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/register", response_model=UserModel, status_code=201)
async def create_user(user: UserCreate):
    try:
        nuevo_usuario = await UserService.registrar_usuario(user)
        return nuevo_usuario
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))