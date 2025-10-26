"""
Clase base para todos los servicios
"""
from typing import TypeVar, Generic, Optional, List, Type, Dict, Any
from pydantic import BaseModel
import asyncpg
import logging
from app.core.database import get_db_connection
from app.core.utils import build_update_query

logger = logging.getLogger(__name__)

# Type variables para genéricos
CreateSchema = TypeVar('CreateSchema', bound=BaseModel)
UpdateSchema = TypeVar('UpdateSchema', bound=BaseModel)
ResponseSchema = TypeVar('ResponseSchema', bound=BaseModel)


class BaseService(Generic[CreateSchema, UpdateSchema, ResponseSchema]):
    """
    Clase base genérica para servicios CRUD.
    
    Proporciona métodos comunes para operaciones de base de datos.
    """
    
    def __init__(
        self, 
        table_name: str,
        id_field: str,
        response_model: Type[ResponseSchema]
    ):
        """
        Inicializa el servicio base.
        
        Args:
            table_name: Nombre de la tabla en la base de datos
            id_field: Nombre del campo ID principal
            response_model: Clase del modelo de respuesta
        """
        self.table_name = table_name
        self.id_field = id_field
        self.response_model = response_model
    
    async def get_by_id(self, id_value: Any) -> Optional[ResponseSchema]:
        """Obtiene un registro por su ID"""
        async with get_db_connection() as conn:
            try:
                query = f"SELECT * FROM {self.table_name} WHERE {self.id_field} = $1"
                row = await conn.fetchrow(query, id_value)
                return self.response_model(**dict(row)) if row else None
            except Exception as e:
                logger.error(f"Error al obtener registro {id_value}: {e}")
                raise
    
    async def get_all(self, order_by: Optional[str] = None) -> List[ResponseSchema]:
        """Obtiene todos los registros"""
        async with get_db_connection() as conn:
            try:
                order_clause = f"ORDER BY {order_by}" if order_by else f"ORDER BY {self.id_field}"
                query = f"SELECT * FROM {self.table_name} {order_clause}"
                rows = await conn.fetch(query)
                return [self.response_model(**dict(row)) for row in rows]
            except Exception as e:
                logger.error(f"Error al obtener registros: {e}")
                raise
    
    async def update(
        self, 
        id_value: Any, 
        update_data: UpdateSchema,
        not_found_error: Optional[Exception] = None
    ) -> ResponseSchema:
        """
        Actualiza un registro de forma genérica.
        
        Args:
            id_value: Valor del ID del registro a actualizar
            update_data: Datos a actualizar
            not_found_error: Excepción a lanzar si no se encuentra el registro
        
        Returns:
            Modelo actualizado
        """
        async with get_db_connection() as conn:
            async with conn.transaction():
                try:
                    # Verificar si existe
                    existing = await self.get_by_id(id_value)
                    if not existing:
                        if not_found_error:
                            raise not_found_error
                        raise ValueError(f"Registro con {self.id_field}={id_value} no encontrado")
                    
                    # Obtener datos a actualizar
                    update_dict = update_data.model_dump(exclude_unset=True)
                    
                    if not update_dict:
                        return existing
                    
                    # Construir y ejecutar query
                    query, values = build_update_query(
                        self.table_name,
                        update_dict,
                        self.id_field,
                        id_value
                    )
                    
                    row = await conn.fetchrow(query, *values)
                    
                    if not row:
                        raise ValueError("No se pudo actualizar el registro")
                    
                    logger.info(f"Registro {id_value} actualizado exitosamente en {self.table_name}")
                    return self.response_model(**dict(row))
                    
                except Exception as e:
                    logger.error(f"Error al actualizar registro: {e}")
                    raise
    
    async def delete(
        self, 
        id_value: Any,
        not_found_error: Optional[Exception] = None
    ) -> bool:
        """
        Elimina un registro de forma genérica.
        
        Args:
            id_value: Valor del ID del registro a eliminar
            not_found_error: Excepción a lanzar si no se encuentra el registro
        
        Returns:
            True si se eliminó correctamente
        """
        async with get_db_connection() as conn:
            async with conn.transaction():
                try:
                    # Verificar si existe
                    existing = await self.get_by_id(id_value)
                    if not existing:
                        if not_found_error:
                            raise not_found_error
                        raise ValueError(f"Registro con {self.id_field}={id_value} no encontrado")
                    
                    query = f"DELETE FROM {self.table_name} WHERE {self.id_field} = $1"
                    result = await conn.execute(query, id_value)
                    
                    deleted_count = int(result.split()[-1])
                    if deleted_count == 0:
                        raise ValueError("No se pudo eliminar el registro")
                    
                    logger.info(f"Registro {id_value} eliminado exitosamente de {self.table_name}")
                    return True
                    
                except Exception as e:
                    logger.error(f"Error al eliminar registro: {e}")
                    raise
