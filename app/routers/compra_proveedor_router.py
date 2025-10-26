"""
Router para endpoints de CompraProveedor
"""
from fastapi import APIRouter, HTTPException, Path
from typing import List
from app.models.compra_proveedor import CompraProveedorCreate, CompraProveedorUpdate, CompraProveedorResponse
from app.service.compra_proveedor_service import compra_proveedor_service
from app.core.exceptions import NotFoundError, DuplicateError, ForeignKeyError, DatabaseError
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
        return await compra_proveedor_service.create(compra)
    except DuplicateError as e:
        raise HTTPException(status_code=409, detail=e.message)
    except ForeignKeyError as e:
        raise HTTPException(status_code=400, detail=e.message)
    except DatabaseError as e:
        logger.error(f"Error al crear compra: {e}")
        raise HTTPException(status_code=400, detail=e.message)
    except Exception as e:
        logger.error(f"Error inesperado al crear compra: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.get("/", response_model=List[CompraProveedorResponse])
async def obtener_compras_proveedor():
    """Obtener todas las compras de proveedor"""
    try:
        return await compra_proveedor_service.get_all()
    except DatabaseError as e:
        logger.error(f"Error al obtener compras: {e}")
        raise HTTPException(status_code=500, detail=e.message)
    except Exception as e:
        logger.error(f"Error inesperado al obtener compras: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.get("/{id_compra}", response_model=CompraProveedorResponse)
async def obtener_compra_proveedor(
    id_compra: int = Path(..., gt=0, description="ID de la compra")
):
    """Obtener una compra de proveedor por su ID"""
    try:
        return await compra_proveedor_service.get_by_id(id_compra)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except DatabaseError as e:
        logger.error(f"Error al obtener compra {id_compra}: {e}")
        raise HTTPException(status_code=500, detail=e.message)
    except Exception as e:
        logger.error(f"Error inesperado al obtener compra {id_compra}: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.get("/proveedor/{id_proveedor}", response_model=List[CompraProveedorResponse])
async def obtener_compras_por_proveedor(
    id_proveedor: int = Path(..., gt=0, description="ID del proveedor")
):
    """Obtener todas las compras de un proveedor específico"""
    try:
        return await compra_proveedor_service.get_by_proveedor(id_proveedor)
    except DatabaseError as e:
        logger.error(f"Error al obtener compras del proveedor {id_proveedor}: {e}")
        raise HTTPException(status_code=500, detail=e.message)
    except Exception as e:
        logger.error(f"Error inesperado al obtener compras del proveedor {id_proveedor}: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.put("/{id_compra}", response_model=CompraProveedorResponse)
async def actualizar_compra_proveedor(
    compra_data: CompraProveedorUpdate,
    id_compra: int = Path(..., gt=0, description="ID de la compra")
):
    """Actualizar una compra de proveedor"""
    try:
        return await compra_proveedor_service.update(id_compra, compra_data)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except DuplicateError as e:
        raise HTTPException(status_code=409, detail=e.message)
    except ForeignKeyError as e:
        raise HTTPException(status_code=400, detail=e.message)
    except DatabaseError as e:
        logger.error(f"Error al actualizar compra: {e}")
        raise HTTPException(status_code=400, detail=e.message)
    except Exception as e:
        logger.error(f"Error inesperado al actualizar compra: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.delete("/{id_compra}", status_code=204)
async def eliminar_compra_proveedor(
    id_compra: int = Path(..., gt=0, description="ID de la compra")
):
    """Eliminar una compra de proveedor"""
    try:
        await compra_proveedor_service.delete(id_compra)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except DatabaseError as e:
        logger.error(f"Error al eliminar compra: {e}")
        raise HTTPException(status_code=400, detail=e.message)
    except Exception as e:
        logger.error(f"Error inesperado al eliminar compra: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")
