"""
Clase base para todos los servicios - Contiene lógica de negocio
Usa el patrón Repository para acceso a datos
"""
from typing import TypeVar, Generic, Optional, List, Type
from pydantic import BaseModel
import asyncpg
import logging
from app.core.base_repository import BaseRepository
from app.core.exceptions import NotFoundError, DuplicateError, ForeignKeyError, DatabaseError

logger = logging.getLogger(__name__)

# Type variables para genéricos
CreateSchema = TypeVar('CreateSchema', bound=BaseModel)
UpdateSchema = TypeVar('UpdateSchema', bound=BaseModel)
ResponseSchema = TypeVar('ResponseSchema', bound=BaseModel)


class BaseService(Generic[CreateSchema, UpdateSchema, ResponseSchema]):
    """
    Clase base genérica para servicios con lógica de negocio.
    
    Este servicio delega las operaciones de persistencia al Repository
    y se enfoca únicamente en la lógica de negocio y validaciones.
    
    Responsabilidades:
    - Validaciones de negocio
    - Orquestación de operaciones complejas
    - Manejo de excepciones de negocio
    - NO maneja SQL directamente (usa Repository)
    """
    
    def __init__(
        self, 
        repository: BaseRepository[ResponseSchema],
        entity_name: str
    ):
        """
        Inicializa el servicio base.
        
        Args:
            repository: Instancia del repositorio a usar
            entity_name: Nombre de la entidad para mensajes de error (ej: "Proveedor")
        """
        self.repository = repository
        self.entity_name = entity_name
    
    async def get_by_id(self, id_value: any) -> ResponseSchema:
        """
        Obtiene un registro por su ID.
        
        Args:
            id_value: Valor del ID
            
        Returns:
            Modelo del registro
            
        Raises:
            NotFoundError: Si no se encuentra el registro
        """
        try:
            result = await self.repository.find_by_id(id_value)
            if not result:
                raise NotFoundError(self.entity_name, id_value)
            return result
        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error al obtener {self.entity_name} {id_value}: {e}")
            raise DatabaseError(str(e))
    
    async def get_all(self, order_by: Optional[str] = None) -> List[ResponseSchema]:
        """
        Obtiene todos los registros.
        
        Args:
            order_by: Campo por el cual ordenar (opcional)
            
        Returns:
            Lista de modelos
        """
        try:
            return await self.repository.find_all(order_by=order_by)
        except Exception as e:
            logger.error(f"Error al obtener todos los {self.entity_name}: {e}")
            raise DatabaseError(str(e))
    
    async def create(self, create_data: CreateSchema) -> ResponseSchema:
        """
        Crea un nuevo registro.
        
        Args:
            create_data: Datos para crear el registro
            
        Returns:
            Modelo del registro creado
            
        Raises:
            DuplicateError: Si existe un registro duplicado
            ForeignKeyError: Si hay error de clave foránea
            DatabaseError: Para otros errores de BD
        """
        try:
            # Validaciones de negocio adicionales pueden ir aquí
            data_dict = create_data.model_dump(exclude_unset=True)
            return await self.repository.create(data_dict)
            
        except asyncpg.UniqueViolationError as e:
            logger.warning(f"Intento de crear {self.entity_name} duplicado: {e}")
            raise DuplicateError(self.entity_name, "campo único", "valor duplicado")
        except asyncpg.ForeignKeyViolationError as e:
            logger.warning(f"Error de clave foránea al crear {self.entity_name}: {e}")
            raise ForeignKeyError("registro relacionado", "id")
        except asyncpg.PostgresError as e:
            logger.error(f"Error de PostgreSQL al crear {self.entity_name}: {e}")
            raise DatabaseError(str(e))
        except Exception as e:
            logger.error(f"Error inesperado al crear {self.entity_name}: {e}")
            raise DatabaseError(str(e))
    
    async def update(self, id_value: any, update_data: UpdateSchema) -> ResponseSchema:
        """
        Actualiza un registro existente.
        
        Args:
            id_value: ID del registro a actualizar
            update_data: Datos a actualizar
            
        Returns:
            Modelo del registro actualizado
            
        Raises:
            NotFoundError: Si no existe el registro
            DuplicateError: Si la actualización viola restricciones únicas
            ForeignKeyError: Si hay error de clave foránea
        """
        try:
            # Verificar que existe
            await self.get_by_id(id_value)
            
            # Obtener solo los campos que se van a actualizar
            update_dict = update_data.model_dump(exclude_unset=True)
            
            if not update_dict:
                # Si no hay cambios, retornar el existente
                return await self.get_by_id(id_value)
            
            # Validaciones de negocio adicionales pueden ir aquí
            
            return await self.repository.update(id_value, update_dict)
            
        except NotFoundError:
            raise
        except asyncpg.UniqueViolationError:
            logger.warning(f"Intento de actualizar con valor duplicado en {self.entity_name}")
            raise DuplicateError(self.entity_name, "campo único", "valor duplicado")
        except asyncpg.ForeignKeyViolationError:
            logger.warning(f"Error de clave foránea al actualizar {self.entity_name}")
            raise ForeignKeyError("registro relacionado", "id")
        except asyncpg.PostgresError as e:
            logger.error(f"Error de PostgreSQL al actualizar {self.entity_name}: {e}")
            raise DatabaseError(str(e))
        except Exception as e:
            logger.error(f"Error inesperado al actualizar {self.entity_name}: {e}")
            raise DatabaseError(str(e))
    
    async def delete(self, id_value: any) -> bool:
        """
        Elimina un registro.
        
        Args:
            id_value: ID del registro a eliminar
            
        Returns:
            True si se eliminó correctamente
            
        Raises:
            NotFoundError: Si no existe el registro
            DatabaseError: Si hay error al eliminar (ej: clave foránea)
        """
        try:
            # Verificar que existe
            await self.get_by_id(id_value)
            
            # Validaciones de negocio antes de eliminar pueden ir aquí
            
            return await self.repository.delete(id_value)
            
        except NotFoundError:
            raise
        except asyncpg.ForeignKeyViolationError:
            logger.warning(f"No se puede eliminar {self.entity_name} {id_value}: tiene registros relacionados")
            raise DatabaseError(f"No se puede eliminar el {self.entity_name} porque tiene registros relacionados")
        except asyncpg.PostgresError as e:
            logger.error(f"Error de PostgreSQL al eliminar {self.entity_name}: {e}")
            raise DatabaseError(str(e))
        except Exception as e:
            logger.error(f"Error inesperado al eliminar {self.entity_name}: {e}")
            raise DatabaseError(str(e))

