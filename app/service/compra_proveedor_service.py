from typing import List, Optional
from decimal import Decimal
from datetime import datetime
import asyncpg
from app.core.database import get_db_connection
from app.core.constants import DB_SCHEMA
from app.models.compra_proveedor import CompraProveedorCreate, CompraProveedorUpdate, CompraProveedorResponse
import logging

logger = logging.getLogger(__name__)

class CompraProveedorServiceError(Exception):
    """Excepción personalizada para errores del servicio de compras de proveedor"""
    pass

class CompraProveedorNotFoundError(CompraProveedorServiceError):
    """Excepción cuando no se encuentra una compra de proveedor"""
    pass

class DuplicateCompraProveedorError(CompraProveedorServiceError):
    """Excepción cuando ya existe una compra con la misma factura"""
    pass

class CompraProveedorService:
    """Servicio para manejar las operaciones CRUD de compras de proveedor"""
    
    @staticmethod
    async def create_compra_proveedor(compra_data: CompraProveedorCreate) -> CompraProveedorResponse:
        """Crear una nueva compra de proveedor"""
        async with get_db_connection() as conn:
            async with conn.transaction():
                try:
                    query = f"""
                        INSERT INTO {DB_SCHEMA}.compra_proveedor (
                            id_proveedor, 
                            valor_compra, 
                            factura, 
                            fecha_compra, 
                            fecha_recibido, 
                            destino, 
                            estado
                        )
                        VALUES ($1, $2, $3, $4, $5, $6, $7)
                        RETURNING *
                    """
                    row = await conn.fetchrow(
                        query, 
                        compra_data.id_proveedor, 
                        compra_data.valor_compra, 
                        compra_data.factura,
                        compra_data.fecha_compra,
                        compra_data.fecha_recibido,
                        compra_data.destino,
                        compra_data.estado
                    )
                    
                    if not row:
                        raise CompraProveedorServiceError("No se pudo crear la compra de proveedor")
                    
                    logger.info(f"Compra de proveedor creada exitosamente: Factura {compra_data.factura}")
                    return CompraProveedorResponse(**dict(row))
                    
                except asyncpg.UniqueViolationError:
                    logger.warning(f"Intento de crear compra con factura duplicada: {compra_data.factura}")
                    raise DuplicateCompraProveedorError(f"Ya existe una compra con la factura: {compra_data.factura}")
                except asyncpg.ForeignKeyViolationError:
                    logger.warning(f"ID de proveedor no válido: {compra_data.id_proveedor}")
                    raise CompraProveedorServiceError(f"El proveedor con ID {compra_data.id_proveedor} no existe")
                except asyncpg.PostgresError as e:
                    logger.error(f"Error de base de datos al crear compra: {e}")
                    raise CompraProveedorServiceError(f"Error de base de datos: {str(e)}")
                except Exception as e:
                    logger.error(f"Error inesperado al crear compra: {e}")
                    raise CompraProveedorServiceError(f"Error interno: {str(e)}")
    
    @staticmethod
    async def get_compra_proveedor_by_id(id_compra: int) -> Optional[CompraProveedorResponse]:
        """Obtener una compra de proveedor por su ID"""
        async with get_db_connection() as conn:
            try:
                query = f"SELECT * FROM {DB_SCHEMA}.compra_proveedor WHERE id_compra = $1"
                row = await conn.fetchrow(query, id_compra)
                return CompraProveedorResponse(**dict(row)) if row else None
            except Exception as e:
                logger.error(f"Error al obtener compra {id_compra}: {e}")
                raise
    
    @staticmethod
    async def get_all_compras_proveedor() -> List[CompraProveedorResponse]:
        """Obtener todas las compras de proveedor"""
        async with get_db_connection() as conn:
            try:
                query = f"""
                    SELECT * FROM {DB_SCHEMA}.compra_proveedor 
                    ORDER BY fecha_compra DESC, id_compra DESC
                """
                rows = await conn.fetch(query)
                return [CompraProveedorResponse(**dict(row)) for row in rows]
            except Exception as e:
                logger.error(f"Error al obtener compras: {e}")
                raise
    
    @staticmethod
    async def get_compras_by_proveedor(id_proveedor: int) -> List[CompraProveedorResponse]:
        """Obtener todas las compras de un proveedor específico"""
        async with get_db_connection() as conn:
            try:
                query = f"""
                    SELECT * FROM {DB_SCHEMA}.compra_proveedor 
                    WHERE id_proveedor = $1 
                    ORDER BY fecha_compra DESC, id_compra DESC
                """
                rows = await conn.fetch(query, id_proveedor)
                return [CompraProveedorResponse(**dict(row)) for row in rows]
            except Exception as e:
                logger.error(f"Error al obtener compras del proveedor {id_proveedor}: {e}")
                raise
    
    @staticmethod
    async def update_compra_proveedor(id_compra: int, compra_data: CompraProveedorUpdate) -> Optional[CompraProveedorResponse]:
        """Actualizar una compra de proveedor"""
        async with get_db_connection() as conn:
            async with conn.transaction():
                try:
                    # Verificar si la compra existe
                    existing_compra = await CompraProveedorService.get_compra_proveedor_by_id(id_compra)
                    if not existing_compra:
                        raise CompraProveedorNotFoundError(f"Compra con ID {id_compra} no encontrada")
                    
                    # Construir la consulta de actualización dinámicamente
                    update_data = compra_data.model_dump(exclude_unset=True)
                    
                    if not update_data:
                        return existing_compra
                    
                    update_fields = []
                    values = []
                    for idx, (field, value) in enumerate(update_data.items(), start=1):
                        update_fields.append(f"{field} = ${idx}")
                        values.append(value)
                    
                    query = f"""
                        UPDATE {DB_SCHEMA}.compra_proveedor 
                        SET {', '.join(update_fields)}
                        WHERE id_compra = ${len(values) + 1}
                        RETURNING *
                    """
                    values.append(id_compra)
                    
                    row = await conn.fetchrow(query, *values)
                    if not row:
                        raise CompraProveedorServiceError("No se pudo actualizar la compra")
                    
                    logger.info(f"Compra {id_compra} actualizada exitosamente")
                    return CompraProveedorResponse(**dict(row))
                    
                except CompraProveedorNotFoundError:
                    raise
                except asyncpg.ForeignKeyViolationError:
                    raise CompraProveedorServiceError("El proveedor especificado no existe")
                except asyncpg.PostgresError as e:
                    logger.error(f"Error de base de datos al actualizar compra: {e}")
                    raise CompraProveedorServiceError(f"Error de base de datos: {str(e)}")
                except Exception as e:
                    logger.error(f"Error inesperado al actualizar compra: {e}")
                    raise CompraProveedorServiceError(f"Error interno: {str(e)}")
    
    @staticmethod
    async def delete_compra_proveedor(id_compra: int) -> bool:
        """Eliminar una compra de proveedor"""
        async with get_db_connection() as conn:
            async with conn.transaction():
                try:
                    # Verificar si la compra existe
                    existing_compra = await CompraProveedorService.get_compra_proveedor_by_id(id_compra)
                    if not existing_compra:
                        raise CompraProveedorNotFoundError(f"Compra con ID {id_compra} no encontrada")
                    
                    query = f"DELETE FROM {DB_SCHEMA}.compra_proveedor WHERE id_compra = $1"
                    result = await conn.execute(query, id_compra)
                    
                    # Verificar si se eliminó alguna fila
                    deleted_count = int(result.split()[-1])
                    if deleted_count == 0:
                        raise CompraProveedorServiceError("No se pudo eliminar la compra")
                    
                    logger.info(f"Compra {id_compra} eliminada exitosamente")
                    return True
                    
                except CompraProveedorNotFoundError:
                    raise
                except asyncpg.PostgresError as e:
                    logger.error(f"Error de base de datos al eliminar compra: {e}")
                    raise CompraProveedorServiceError(f"Error de base de datos: {str(e)}")
                except Exception as e:
                    logger.error(f"Error inesperado al eliminar compra: {e}")
                    raise CompraProveedorServiceError(f"Error interno: {str(e)}")