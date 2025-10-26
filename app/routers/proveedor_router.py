"""
Router para endpoints de Proveedor
"""
from fastapi import APIRouter, HTTPException, Query, Path
from typing import List
from app.models.proveedor import ProveedorCreate, ProveedorUpdate, ProveedorResponse
from app.service.proveedor_service import proveedor_service
from app.core.exceptions import NotFoundError, DuplicateError, DatabaseError
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/proveedores",
    tags=["Proveedores"],
    responses={404: {"description": "No encontrado"}}
)


@router.post("/", response_model=ProveedorResponse, status_code=201)
async def crear_proveedor(proveedor: ProveedorCreate):
    """Crear un nuevo proveedor"""
    try:
        return await proveedor_service.create(proveedor)
    except DuplicateError as e:
        raise HTTPException(status_code=409, detail=e.message)
    except DatabaseError as e:
        logger.error(f"Error de base de datos al crear proveedor: {e}")
        raise HTTPException(status_code=400, detail=e.message)
    except Exception as e:
        logger.error(f"Error inesperado al crear proveedor: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.get("/", response_model=List[ProveedorResponse])
async def obtener_proveedores():
    """Obtener todos los proveedores"""
    try:
        return await proveedor_service.get_all()
    except DatabaseError as e:
        logger.error(f"Error al obtener proveedores: {e}")
        raise HTTPException(status_code=500, detail=e.message)
    except Exception as e:
        logger.error(f"Error inesperado al obtener proveedores: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.get("/{id_proveedor}", response_model=ProveedorResponse)
async def obtener_proveedor(
    id_proveedor: int = Path(..., gt=0, description="ID del proveedor")
):
    """Obtener un proveedor por su ID"""
    try:
        return await proveedor_service.get_by_id(id_proveedor)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except DatabaseError as e:
        logger.error(f"Error al obtener proveedor {id_proveedor}: {e}")
        raise HTTPException(status_code=500, detail=e.message)
    except Exception as e:
        logger.error(f"Error inesperado al obtener proveedor {id_proveedor}: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.put("/{id_proveedor}", response_model=ProveedorResponse)
async def actualizar_proveedor(
    proveedor_data: ProveedorUpdate,
    id_proveedor: int = Path(..., gt=0, description="ID del proveedor")
):
    """Actualizar un proveedor"""
    try:
        return await proveedor_service.update(id_proveedor, proveedor_data)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except DuplicateError as e:
        raise HTTPException(status_code=409, detail=e.message)
    except DatabaseError as e:
        logger.error(f"Error al actualizar proveedor: {e}")
        raise HTTPException(status_code=400, detail=e.message)
    except Exception as e:
        logger.error(f"Error inesperado al actualizar proveedor: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.delete("/{id_proveedor}", status_code=204)
async def eliminar_proveedor(
    id_proveedor: int = Path(..., gt=0, description="ID del proveedor")
):
    """Eliminar un proveedor"""
    try:
        await proveedor_service.delete(id_proveedor)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except DatabaseError as e:
        logger.error(f"Error al eliminar proveedor: {e}")
        raise HTTPException(status_code=400, detail=e.message)
    except Exception as e:
        logger.error(f"Error inesperado al eliminar proveedor: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.get("/buscar/nombre", response_model=List[ProveedorResponse])
async def buscar_proveedores_por_nombre(
    nombre: str = Query(..., min_length=1, description="Nombre del proveedor a buscar")
):
    """Buscar proveedores por nombre"""
    try:
        return await proveedor_service.search_by_name(nombre)
    except DatabaseError as e:
        logger.error(f"Error al buscar proveedores por nombre: {e}")
        raise HTTPException(status_code=500, detail=e.message)
    except Exception as e:
        logger.error(f"Error inesperado al buscar proveedores: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")
