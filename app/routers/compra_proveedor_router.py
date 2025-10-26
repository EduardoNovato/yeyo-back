from fastapi import APIRouter, HTTPException, Query, Path
from typing import List
from app.models.compra_proveedor import CompraProveedorCreate, CompraProveedorUpdate, CompraProveedorResponse
from app.service.compra_proveedor_service import (
    CompraProveedorService, 
    CompraProveedorServiceError, 
    CompraProveedorNotFoundError, 
    DuplicateCompraProveedorError
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/compras-proveedor",
    tags=["Compras de Proveedor"],
    responses={404: {"description": "No encontrado"}}
)

@router.post("/", response_model=CompraProveedorResponse, status_code=201)
async def crear_compra_proveedor(compra: CompraProveedorCreate):
    """Crear una nueva compra de proveedor"""
    try:
        return await CompraProveedorService.create_compra_proveedor(compra)
    except DuplicateCompraProveedorError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except CompraProveedorServiceError as e:
        logger.error(f"Error del servicio al crear compra: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error inesperado al crear compra: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.get("/", response_model=List[CompraProveedorResponse])
async def obtener_compras_proveedor():
    """Obtener todas las compras de proveedor"""
    try:
        return await CompraProveedorService.get_all_compras_proveedor()
    except CompraProveedorNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error al obtener compras: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.get("/{id_compra}", response_model=CompraProveedorResponse)
async def obtener_compra_proveedor(
    id_compra: int = Path(..., gt=0, description="ID de la compra")
):
    """Obtener una compra de proveedor por su ID"""
    try:
        compra = await CompraProveedorService.get_compra_proveedor_by_id(id_compra)
        if not compra:
            raise HTTPException(status_code=404, detail=f"Compra con ID {id_compra} no encontrada")
        return compra
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener compra {id_compra}: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.get("/proveedor/{id_proveedor}", response_model=List[CompraProveedorResponse])
async def obtener_compras_por_proveedor(
    id_proveedor: int = Path(..., gt=0, description="ID del proveedor")
):
    """Obtener todas las compras de un proveedor específico"""
    try:
        return await CompraProveedorService.get_compras_by_proveedor(id_proveedor)
    except Exception as e:
        logger.error(f"Error al obtener compras del proveedor {id_proveedor}: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.put("/{id_compra}", response_model=CompraProveedorResponse)
async def actualizar_compra_proveedor(
    compra_data: CompraProveedorUpdate,
    id_compra: int = Path(..., gt=0, description="ID de la compra")
):
    """Actualizar una compra de proveedor"""
    try:
        return await CompraProveedorService.update_compra_proveedor(id_compra, compra_data)
    except CompraProveedorNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except CompraProveedorServiceError as e:
        logger.error(f"Error del servicio al actualizar compra: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error inesperado al actualizar compra: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.delete("/{id_compra}", status_code=204)
async def eliminar_compra_proveedor(
    id_compra: int = Path(..., gt=0, description="ID de la compra")
):
    """Eliminar una compra de proveedor"""
    try:
        await CompraProveedorService.delete_compra_proveedor(id_compra)
    except CompraProveedorNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except CompraProveedorServiceError as e:
        logger.error(f"Error del servicio al eliminar compra: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error inesperado al eliminar compra: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")