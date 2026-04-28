from fastapi import FastAPI
from src.api.user_controller import router as user_router

# 1. Creamos la aplicación central
app = FastAPI(title="Laboratorio Virtual Auditivo - Backend")

# 2. Conectamos el controlador de usuarios
app.include_router(user_router)

# 3. Ruta de bienvenida (para probar que anda)
@app.get("/")
def home():
    return {"status": "Servidor funcionando correctamente"}