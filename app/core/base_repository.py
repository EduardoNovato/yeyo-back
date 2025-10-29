"""
Patrón Repository: Capa de acceso a datos genérica
Separa la lógica de persistencia de la lógica de negocio
"""
from typing import TypeVar, Generic, Optional, List, Type, Dict, Any, Tuple
from pydantic import BaseModel
import logging
from app.core.database import get_db_connection
from app.core.exceptions import NotFoundError, DatabaseError

logger = logging.getLogger(__name__)

# Type variables para genéricos
T = TypeVar('T', bound=BaseModel)


# ============================================================================
# Funciones auxiliares para construcción dinámica de queries
# ============================================================================

def build_update_query(
    table_name: str,
    update_data: Dict[str, Any],
    id_field: str,
    id_value: Any
) -> Tuple[str, List[Any]]:
    """
    Construye una query de UPDATE dinámica basada en los campos proporcionados.
    
    Args:
        table_name: Nombre de la tabla a actualizar
        update_data: Diccionario con los campos a actualizar
        id_field: Nombre del campo ID
        id_value: Valor del ID
    
    Returns:
        Tupla con (query_string, lista_de_valores)
    
    Example:
        >>> query, values = build_update_query(
        ...     "users", 
        ...     {"name": "John", "age": 30}, 
        ...     "id", 
        ...     1
        ... )
        >>> print(query)
        'UPDATE users SET name = $1, age = $2 WHERE id = $3 RETURNING *'
        >>> print(values)
        ['John', 30, 1]
    """
    if not update_data:
        raise ValueError("No hay datos para actualizar")
    
    update_fields = []
    values = []
    
    for idx, (field, value) in enumerate(update_data.items(), start=1):
        update_fields.append(f"{field} = ${idx}")
        values.append(value)
    
    query = f"""
        UPDATE {table_name} 
        SET {', '.join(update_fields)}
        WHERE {id_field} = ${len(values) + 1}
        RETURNING *
    """
    values.append(id_value)
    
    return query, values


def build_insert_query(
    table_name: str,
    data: Dict[str, Any]
) -> Tuple[str, List[Any]]:
    """
    Construye una query de INSERT dinámica basada en los campos proporcionados.
    
    Args:
        table_name: Nombre de la tabla
        data: Diccionario con los campos y valores a insertar
    
    Returns:
        Tupla con (query_string, lista_de_valores)
    
    Example:
        >>> query, values = build_insert_query(
        ...     "users", 
        ...     {"name": "John", "age": 30}
        ... )
        >>> print(query)
        'INSERT INTO users (name, age) VALUES ($1, $2) RETURNING *'
        >>> print(values)
        ['John', 30]
    """
    if not data:
        raise ValueError("No hay datos para insertar")
    
    fields = list(data.keys())
    placeholders = [f"${i}" for i in range(1, len(fields) + 1)]
    values = list(data.values())
    
    query = f"""
        INSERT INTO {table_name} ({', '.join(fields)})
        VALUES ({', '.join(placeholders)})
        RETURNING *
    """
    
    return query, values


class BaseRepository(Generic[T]):
    """
    Repositorio base genérico para operaciones CRUD en base de datos.
    
    Este patrón Repository proporciona una abstracción sobre la capa de datos,
    permitiendo que los servicios de negocio trabajen sin conocer los detalles
    de la persistencia.
    
    Responsabilidades:
    - Acceso directo a base de datos
    - Queries SQL
    - Mapeo de datos a modelos Pydantic
    - NO contiene lógica de negocio
    """
    
    def __init__(
        self, 
        table_name: str,
        id_field: str,
        response_model: Type[T],
        schema: Optional[str] = None
    ):
        """
        Inicializa el repositorio base.
        
        Args:
            table_name: Nombre de la tabla en la base de datos
            id_field: Nombre del campo ID principal (ej: 'id_proveedor')
            response_model: Clase del modelo de respuesta Pydantic
            schema: Esquema de la base de datos (opcional)
        """
        self.table_name = table_name
        self.id_field = id_field
        self.response_model = response_model
        self.schema = schema
        self.full_table_name = f"{schema}.{table_name}" if schema else table_name
    
    async def find_by_id(self, id_value: Any) -> Optional[T]:
        """
        Busca un registro por su ID.
        
        Args:
            id_value: Valor del ID a buscar
            
        Returns:
            Modelo del registro o None si no existe
        """
        async with get_db_connection() as conn:
            try:
                query = f"SELECT * FROM {self.full_table_name} WHERE {self.id_field} = $1"
                row = await conn.fetchrow(query, id_value)
                return self.response_model(**dict(row)) if row else None
            except Exception as e:
                logger.error(f"Error al buscar registro con {self.id_field}={id_value}: {e}")
                raise DatabaseError(str(e))
    
    async def find_all(self, order_by: Optional[str] = None, limit: Optional[int] = None) -> List[T]:
        """
        Obtiene todos los registros de la tabla.
        
        Args:
            order_by: Campo por el cual ordenar (opcional)
            limit: Límite de registros a retornar (opcional)
            
        Returns:
            Lista de modelos
        """
        async with get_db_connection() as conn:
            try:
                order_clause = f"ORDER BY {order_by}" if order_by else f"ORDER BY {self.id_field}"
                limit_clause = f"LIMIT {limit}" if limit else ""
                query = f"SELECT * FROM {self.full_table_name} {order_clause} {limit_clause}"
                
                rows = await conn.fetch(query)
                return [self.response_model(**dict(row)) for row in rows]
            except Exception as e:
                logger.error(f"Error al obtener todos los registros de {self.table_name}: {e}")
                raise DatabaseError(str(e))
    
    async def create(self, data: Dict[str, Any]) -> T:
        """
        Crea un nuevo registro en la base de datos.
        
        Args:
            data: Diccionario con los datos a insertar
            
        Returns:
            Modelo del registro creado
        """
        async with get_db_connection() as conn:
            async with conn.transaction():
                try:
                    query, values = build_insert_query(self.full_table_name, data)
                    row = await conn.fetchrow(query, *values)
                    
                    if not row:
                        raise DatabaseError("No se pudo crear el registro")
                    
                    logger.info(f"Registro creado exitosamente en {self.table_name}")
                    return self.response_model(**dict(row))
                    
                except Exception as e:
                    logger.error(f"Error al crear registro en {self.table_name}: {e}")
                    raise
    
    async def update(self, id_value: Any, data: Dict[str, Any]) -> T:
        """
        Actualiza un registro existente.
        
        Args:
            id_value: Valor del ID del registro a actualizar
            data: Diccionario con los datos a actualizar
            
        Returns:
            Modelo del registro actualizado
        """
        async with get_db_connection() as conn:
            async with conn.transaction():
                try:
                    if not data:
                        # Si no hay datos para actualizar, retornar el existente
                        existing = await self.find_by_id(id_value)
                        if not existing:
                            raise NotFoundError(self.table_name, id_value)
                        return existing
                    
                    query, values = build_update_query(
                        self.full_table_name,
                        data,
                        self.id_field,
                        id_value
                    )
                    
                    row = await conn.fetchrow(query, *values)
                    
                    if not row:
                        raise NotFoundError(self.table_name, id_value)
                    
                    logger.info(f"Registro {id_value} actualizado en {self.table_name}")
                    return self.response_model(**dict(row))
                    
                except Exception as e:
                    logger.error(f"Error al actualizar registro en {self.table_name}: {e}")
                    raise
    
    async def delete(self, id_value: Any) -> bool:
        """
        Elimina un registro de la base de datos.
        
        Args:
            id_value: Valor del ID del registro a eliminar
            
        Returns:
            True si se eliminó correctamente
        """
        async with get_db_connection() as conn:
            async with conn.transaction():
                try:
                    query = f"DELETE FROM {self.full_table_name} WHERE {self.id_field} = $1"
                    result = await conn.execute(query, id_value)
                    
                    deleted_count = int(result.split()[-1])
                    if deleted_count == 0:
                        raise NotFoundError(self.table_name, id_value)
                    
                    logger.info(f"Registro {id_value} eliminado de {self.table_name}")
                    return True
                    
                except Exception as e:
                    logger.error(f"Error al eliminar registro de {self.table_name}: {e}")
                    raise
    
    async def exists(self, id_value: Any) -> bool:
        """
        Verifica si existe un registro con el ID dado.
        
        Args:
            id_value: Valor del ID a verificar
            
        Returns:
            True si existe, False en caso contrario
        """
        result = await self.find_by_id(id_value)
        return result is not None
    
    async def find_by_field(self, field: str, value: Any) -> Optional[T]:
        """
        Busca un registro por un campo específico.
        
        Args:
            field: Nombre del campo
            value: Valor a buscar
            
        Returns:
            Modelo del registro o None
        """
        async with get_db_connection() as conn:
            try:
                query = f"SELECT * FROM {self.full_table_name} WHERE {field} = $1"
                row = await conn.fetchrow(query, value)
                return self.response_model(**dict(row)) if row else None
            except Exception as e:
                logger.error(f"Error al buscar por {field}={value} en {self.table_name}: {e}")
                raise DatabaseError(str(e))
    
    async def find_many_by_field(self, field: str, value: Any, order_by: Optional[str] = None) -> List[T]:
        """
        Busca múltiples registros por un campo específico.
        
        Args:
            field: Nombre del campo
            value: Valor a buscar
            order_by: Campo por el cual ordenar (opcional)
            
        Returns:
            Lista de modelos
        """
        async with get_db_connection() as conn:
            try:
                order_clause = f"ORDER BY {order_by}" if order_by else f"ORDER BY {self.id_field}"
                query = f"SELECT * FROM {self.full_table_name} WHERE {field} = $1 {order_clause}"
                
                rows = await conn.fetch(query, value)
                return [self.response_model(**dict(row)) for row in rows]
            except Exception as e:
                logger.error(f"Error al buscar múltiples por {field}={value} en {self.table_name}: {e}")
                raise DatabaseError(str(e))
