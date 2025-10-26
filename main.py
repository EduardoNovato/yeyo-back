from fastapi import FastAPI
from contextlib import asynccontextmanager
import uvicorn
from app.routers import proveedor_router
from app.core.database import db

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Maneja el ciclo de vida de la aplicación"""
    # Startup: se ejecuta al iniciar la aplicación
    await db.connect()
    yield
    # Shutdown: se ejecuta al cerrar la aplicación
    await db.disconnect()

app = FastAPI(
    title="Api de servicios tienda online",
    description="API para gestionar los servicios de una tienda online.",
    version="1.0.0",
    lifespan=lifespan
)

# Incluir routers
app.include_router(proveedor_router.router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)