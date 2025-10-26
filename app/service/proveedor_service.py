from typing import List, Optional
from decimal import Decimal
import asyncpg
from app.core.database import get_db_connection
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
                    query = """
                        INSERT INTO psa_problems.proveedor (
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
                query = "SELECT * FROM psa_problems.proveedor WHERE id_proveedor = $1"
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
                query = """
                    SELECT * FROM psa_problems.proveedor 
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
            try:
                # Construir la query dinámicamente solo con los campos que se van a actualizar
                update_fields = []
                values = []
                param_counter = 1
                
                if proveedor_data.nombre is not None:
                    update_fields.append(f"nombre = ${param_counter}")
                    values.append(proveedor_data.nombre)
                    param_counter += 1
                
                if proveedor_data.nit is not None:
                    update_fields.append(f"nit = ${param_counter}")
                    values.append(proveedor_data.nit)
                    param_counter += 1
                
                if proveedor_data.descripcion is not None:
                    update_fields.append(f"descripcion = ${param_counter}")
                    values.append(proveedor_data.descripcion)
                    param_counter += 1
                
                if proveedor_data.num_art_comprados is not None:
                    update_fields.append(f"num_art_comprados = ${param_counter}")
                    values.append(proveedor_data.num_art_comprados)
                    param_counter += 1
                
                if proveedor_data.num_art_devoluciones is not None:
                    update_fields.append(f"num_art_devoluciones = ${param_counter}")
                    values.append(proveedor_data.num_art_devoluciones)
                    param_counter += 1
                
                if proveedor_data.num_art_vendidas is not None:
                    update_fields.append(f"num_art_vendidas = ${param_counter}")
                    values.append(proveedor_data.num_art_vendidas)
                    param_counter += 1
                
                if proveedor_data.num_compras is not None:
                    update_fields.append(f"num_compras = ${param_counter}")
                    values.append(proveedor_data.num_compras)
                    param_counter += 1
                
                if proveedor_data.valor_comprado is not None:
                    update_fields.append(f"valor_comprado = ${param_counter}")
                    values.append(proveedor_data.valor_comprado)
                    param_counter += 1
                
                if proveedor_data.num_devoluciones is not None:
                    update_fields.append(f"num_devoluciones = ${param_counter}")
                    values.append(proveedor_data.num_devoluciones)
                    param_counter += 1
                
                if proveedor_data.valor_devuelto is not None:
                    update_fields.append(f"valor_devuelto = ${param_counter}")
                    values.append(proveedor_data.valor_devuelto)
                    param_counter += 1
                
                if proveedor_data.num_ventas is not None:
                    update_fields.append(f"num_ventas = ${param_counter}")
                    values.append(proveedor_data.num_ventas)
                    param_counter += 1
                
                if proveedor_data.valor_vendido is not None:
                    update_fields.append(f"valor_vendido = ${param_counter}")
                    values.append(proveedor_data.valor_vendido)
                    param_counter += 1
                
                if proveedor_data.rating_art_provedor is not None:
                    update_fields.append(f"rating_art_provedor = ${param_counter}")
                    values.append(proveedor_data.rating_art_provedor)
                    param_counter += 1
                
                if not update_fields:
                    # Si no hay campos para actualizar, devolver el proveedor actual
                    return await ProveedorService.get_proveedor_by_id(id_proveedor)
                
                query = f"""
                    UPDATE psa_problems.proveedor 
                    SET {', '.join(update_fields)}
                    WHERE id_proveedor = ${param_counter}
                    RETURNING *
                """
                values.append(id_proveedor)
                
                row = await conn.fetchrow(query, *values)
                return ProveedorResponse(**dict(row)) if row else None
            except asyncpg.UniqueViolationError:
                raise ValueError("Ya existe un proveedor con ese NIT")
            except Exception as e:
                logger.error(f"Error al actualizar proveedor {id_proveedor}: {e}")
                raise
    
    @staticmethod
    async def delete_proveedor(id_proveedor: int) -> bool:
        """Eliminar un proveedor"""
        async with get_db_connection() as conn:
            try:
                query = "DELETE FROM psa_problems.proveedor WHERE id_proveedor = $1"
                result = await conn.execute(query, id_proveedor)
                return result == "DELETE 1"
            except Exception as e:
                logger.error(f"Error al eliminar proveedor {id_proveedor}: {e}")
                raise
    
    @staticmethod
    async def search_proveedores_by_name(nombre: str) -> List[ProveedorResponse]:
        """Buscar proveedores por nombre"""
        async with get_db_connection() as conn:
            try:
                query = """
                    SELECT * FROM psa_problems.proveedor 
                    WHERE nombre ILIKE $1 
                    ORDER BY nombre
                """
                rows = await conn.fetch(query, f"%{nombre}%")
                return [ProveedorResponse(**dict(row)) for row in rows]
            except Exception as e:
                logger.error(f"Error al buscar proveedores por nombre '{nombre}': {e}")
                raise