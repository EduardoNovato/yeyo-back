from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
from app.routers import proveedor_router, compra_proveedor_router
from app.core.database import db
from app.core.service_factory import ServiceFactory

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Maneja el ciclo de vida de la aplicación"""
    # Startup: se ejecuta al iniciar la aplicación
    await db.connect()
    
    # Inicializar factory de servicios
    ServiceFactory.initialize()
    
    yield
    
    # Shutdown: se ejecuta al cerrar la aplicación
    await db.disconnect()

app = FastAPI(
    title="API de servicios tienda online",
    description="API para gestionar los servicios de una tienda online.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar orígenes permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(proveedor_router.router)
app.include_router(compra_proveedor_router.router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)