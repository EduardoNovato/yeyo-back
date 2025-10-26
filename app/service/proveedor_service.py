from typing import List, Optional
from decimal import Decimal
import asyncpg
from app.core.database import get_db_connection
from app.core.constants import DB_SCHEMA
from app.models.proveedor import ProveedorCreate, ProveedorUpdate, ProveedorResponse
import logging

logger = logging.getLogger(__name__)

class ProveedorServiceError(Exception):
    """Excepción personalizada para errores del servicio de proveedores"""
    pass

class ProveedorNotFoundError(ProveedorServiceError):
    """Excepción cuando no se encuentra un proveedor"""
    pass

class DuplicateProveedorError(ProveedorServiceError):
    """Excepción cuando ya existe un proveedor con el mismo NIT"""
    pass

class ProveedorService:
    """Servicio para manejar las operaciones CRUD de proveedores"""
    
    @staticmethod
    async def create_proveedor(proveedor_data: ProveedorCreate) -> ProveedorResponse:
        """Crear un nuevo proveedor"""
        async with get_db_connection() as conn:
            async with conn.transaction():  # Uso de transacciones explícitas
                try:
                    query = f"""
                        INSERT INTO {DB_SCHEMA}.proveedor (
                            nombre, 
                            nit, 
                            descripcion, 
                            num_art_comprados, 
                            num_art_devoluciones, 
                            num_art_vendidas, 
                            num_compras, 
                            valor_comprado, 
                            num_devoluciones, 
                            valor_devuelto, 
                            num_ventas, 
                            valor_vendido, 
                            rating_art_provedor
                        )
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
                        RETURNING *
                    """
                    row = await conn.fetchrow(
                        query, 
                        proveedor_data.nombre, 
                        proveedor_data.nit, 
                        proveedor_data.descripcion,
                        proveedor_data.num_art_comprados,
                        proveedor_data.num_art_devoluciones,
                        proveedor_data.num_art_vendidas,
                        proveedor_data.num_compras,
                        proveedor_data.valor_comprado,
                        proveedor_data.num_devoluciones,
                        proveedor_data.valor_devuelto,
                        proveedor_data.num_ventas,
                        proveedor_data.valor_vendido,
                        proveedor_data.rating_art_provedor
                    )
                    
                    if not row:
                        raise ProveedorServiceError("No se pudo crear el proveedor")
                    
                    logger.info(f"Proveedor creado exitosamente: {proveedor_data.nombre} (NIT: {proveedor_data.nit})")
                    return ProveedorResponse(**dict(row))
                    
                except asyncpg.UniqueViolationError:
                    logger.warning(f"Intento de crear proveedor con NIT duplicado: {proveedor_data.nit}")
                    raise DuplicateProveedorError(f"Ya existe un proveedor con el NIT: {proveedor_data.nit}")
                except asyncpg.PostgresError as e:
                    logger.error(f"Error de base de datos al crear proveedor: {e}")
                    raise ProveedorServiceError(f"Error de base de datos: {str(e)}")
                except Exception as e:
                    logger.error(f"Error inesperado al crear proveedor: {e}")
                    raise ProveedorServiceError(f"Error interno: {str(e)}")
    
    @staticmethod
    async def get_proveedor_by_id(id_proveedor: int) -> Optional[ProveedorResponse]:
        """Obtener un proveedor por su ID"""
        async with get_db_connection() as conn:
            try:
                query = f"SELECT * FROM {DB_SCHEMA}.proveedor WHERE id_proveedor = $1"
                row = await conn.fetchrow(query, id_proveedor)
                return ProveedorResponse(**dict(row)) if row else None
            except Exception as e:
                logger.error(f"Error al obtener proveedor {id_proveedor}: {e}")
                raise
    
    @staticmethod
    async def get_all_proveedores() -> List[ProveedorResponse]:
        """Obtener todos los proveedores con paginación"""
        async with get_db_connection() as conn:
            try:
                query = f"""
                    SELECT * FROM {DB_SCHEMA}.proveedor 
                    ORDER BY id_proveedor 
                """
                rows = await conn.fetch(query)
                return [ProveedorResponse(**dict(row)) for row in rows]
            except asyncpg.PostgresError as e:
                logger.error(f"Error de base de datos al obtener proveedores: {e}")
                raise ProveedorServiceError(f"Error de base de datos: {str(e)}")
            except Exception as e:
                logger.error(f"Error inesperado al obtener proveedores: {e}")
                raise ProveedorServiceError(f"Error interno: {str(e)}")
    
    @staticmethod
    async def update_proveedor(id_proveedor: int, proveedor_data: ProveedorUpdate) -> Optional[ProveedorResponse]:
        """Actualizar un proveedor"""
        async with get_db_connection() as conn:
            async with conn.transaction():
                try:
                    # Verificar si el proveedor existe
                    existing = await ProveedorService.get_proveedor_by_id(id_proveedor)
                    if not existing:
                        raise ProveedorNotFoundError(f"Proveedor con ID {id_proveedor} no encontrado")
                    
                    # Construir la query dinámicamente usando model_dump(exclude_unset=True)
                    update_data = proveedor_data.model_dump(exclude_unset=True)
                    
                    if not update_data:
                        return existing
                    
                    update_fields = []
                    values = []
                    for idx, (field, value) in enumerate(update_data.items(), start=1):
                        update_fields.append(f"{field} = ${idx}")
                        values.append(value)
                    
                    query = f"""
                        UPDATE {DB_SCHEMA}.proveedor 
                        SET {', '.join(update_fields)}
                        WHERE id_proveedor = ${len(values) + 1}
                        RETURNING *
                    """
                    values.append(id_proveedor)
                    
                    row = await conn.fetchrow(query, *values)
                    
                    if not row:
                        raise ProveedorServiceError("No se pudo actualizar el proveedor")
                    
                    logger.info(f"Proveedor {id_proveedor} actualizado exitosamente")
                    return ProveedorResponse(**dict(row))
                    
                except ProveedorNotFoundError:
                    raise
                except asyncpg.UniqueViolationError:
                    logger.warning(f"Intento de actualizar con NIT duplicado")
                    raise DuplicateProveedorError("Ya existe un proveedor con ese NIT")
                except asyncpg.PostgresError as e:
                    logger.error(f"Error de base de datos al actualizar proveedor: {e}")
                    raise ProveedorServiceError(f"Error de base de datos: {str(e)}")
                except Exception as e:
                    logger.error(f"Error al actualizar proveedor {id_proveedor}: {e}")
                    raise ProveedorServiceError(f"Error interno: {str(e)}")
    
    @staticmethod
    async def delete_proveedor(id_proveedor: int) -> bool:
        """Eliminar un proveedor"""
        async with get_db_connection() as conn:
            async with conn.transaction():
                try:
                    # Verificar si el proveedor existe
                    existing = await ProveedorService.get_proveedor_by_id(id_proveedor)
                    if not existing:
                        raise ProveedorNotFoundError(f"Proveedor con ID {id_proveedor} no encontrado")
                    
                    query = f"DELETE FROM {DB_SCHEMA}.proveedor WHERE id_proveedor = $1"
                    result = await conn.execute(query, id_proveedor)
                    
                    deleted_count = int(result.split()[-1])
                    if deleted_count == 0:
                        raise ProveedorServiceError("No se pudo eliminar el proveedor")
                    
                    logger.info(f"Proveedor {id_proveedor} eliminado exitosamente")
                    return True
                    
                except ProveedorNotFoundError:
                    raise
                except asyncpg.ForeignKeyViolationError:
                    logger.warning(f"No se puede eliminar el proveedor {id_proveedor}: tiene compras asociadas")
                    raise ProveedorServiceError("No se puede eliminar el proveedor porque tiene compras asociadas")
                except asyncpg.PostgresError as e:
                    logger.error(f"Error de base de datos al eliminar proveedor: {e}")
                    raise ProveedorServiceError(f"Error de base de datos: {str(e)}")
                except Exception as e:
                    logger.error(f"Error al eliminar proveedor {id_proveedor}: {e}")
                    raise ProveedorServiceError(f"Error interno: {str(e)}")
    
    @staticmethod
    async def search_proveedores_by_name(nombre: str) -> List[ProveedorResponse]:
        """Buscar proveedores por nombre"""
        async with get_db_connection() as conn:
            try:
                query = f"""
                    SELECT * FROM {DB_SCHEMA}.proveedor 
                    WHERE nombre ILIKE $1 
                    ORDER BY nombre
                """
                rows = await conn.fetch(query, f"%{nombre}%")
                return [ProveedorResponse(**dict(row)) for row in rows]
            except Exception as e:
                logger.error(f"Error al buscar proveedores por nombre '{nombre}': {e}")
                raise