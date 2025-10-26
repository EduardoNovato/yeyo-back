from fastapi import APIRouter, HTTPException, Query, Path
from typing import List
from app.models.proveedor import ProveedorCreate, ProveedorUpdate, ProveedorResponse
from app.service.proveedor_service import (
    ProveedorService, 
    ProveedorServiceError, 
    ProveedorNotFoundError, 
    DuplicateProveedorError
)
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
        return await ProveedorService.create_proveedor(proveedor)
    except DuplicateProveedorError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except ProveedorServiceError as e:
        logger.error(f"Error del servicio al crear proveedor: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error inesperado al crear proveedor: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.get("/", response_model=List[ProveedorResponse])
async def obtener_proveedores():
    """Obtener todos los proveedores con paginación"""
    try:
        return await ProveedorService.get_all_proveedores()
    except ProveedorNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error al obtener proveedores: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.get("/{id_proveedor}", response_model=ProveedorResponse)
async def obtener_proveedor(
    id_proveedor: int = Path(..., gt=0, description="ID del proveedor")
):
    """Obtener un proveedor por su ID"""
    try:
        proveedor = await ProveedorService.get_proveedor_by_id(id_proveedor)
        if not proveedor:
            raise HTTPException(status_code=404, detail="Proveedor no encontrado")
        return proveedor
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener proveedor {id_proveedor}: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.put("/{id_proveedor}", response_model=ProveedorResponse)
async def actualizar_proveedor(
    proveedor_data: ProveedorUpdate,
    id_proveedor: int = Path(..., gt=0, description="ID del proveedor")
):
    """Actualizar un proveedor"""
    try:
        return await ProveedorService.update_proveedor(id_proveedor, proveedor_data)
    except ProveedorNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DuplicateProveedorError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except ProveedorServiceError as e:
        logger.error(f"Error del servicio al actualizar proveedor: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error inesperado al actualizar proveedor: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.delete("/{id_proveedor}", status_code=204)
async def eliminar_proveedor(
    id_proveedor: int = Path(..., gt=0, description="ID del proveedor")
):
    """Eliminar un proveedor"""
    try:
        await ProveedorService.delete_proveedor(id_proveedor)
    except ProveedorNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ProveedorServiceError as e:
        logger.error(f"Error del servicio al eliminar proveedor: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error inesperado al eliminar proveedor: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.get("/buscar/nombre", response_model=List[ProveedorResponse])
async def buscar_proveedores_por_nombre(
    nombre: str = Query(..., min_length=1, description="Nombre del proveedor a buscar")
):
    """Buscar proveedores por nombre"""
    try:
        return await ProveedorService.search_proveedores_by_name(nombre)
    except Exception as e:
        logger.error(f"Error al buscar proveedores por nombre '{nombre}': {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")