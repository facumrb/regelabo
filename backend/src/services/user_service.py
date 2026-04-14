from src.models.user_model import UserCreate, UserModel
from datetime import datetime
import uuid

class UserService:
    
    @staticmethod
    async def registrar_usuario(user_data: UserCreate) -> UserModel:
        """
        Esta función recibe los datos crudos, les agrega información del sistema
        y (en el futuro) los guardará en la base de datos.
        """
        nuevo_id = uuid.uuid4()
        fecha_creacion = datetime.now()
        
        usuario_final = UserModel(
            id=nuevo_id,
            email=user_data.email,
            name=user_data.name,
            role=user_data.role,
            created_at=fecha_creacion
        )

        return usuario_final