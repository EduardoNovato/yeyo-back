"""
Servicio de Proveedor - Contiene lógica de negocio específica
Hereda operaciones CRUD genéricas de BaseService
"""
from typing import List
import asyncpg
import logging
from app.core.base_service import BaseService
from app.core.base_repository import BaseRepository
from app.core.config import db_config
from app.core.exceptions import NotFoundError, DuplicateError, DatabaseError
from app.models.proveedor import ProveedorCreate, ProveedorUpdate, ProveedorResponse

logger = logging.getLogger(__name__)


class ProveedorRepository(BaseRepository[ProveedorResponse]):
    """
    Repositorio específico para Proveedor.
    Extiende BaseRepository con métodos específicos de búsqueda.
    """
    
    def __init__(self):
        super().__init__(
            table_name="proveedor",
            id_field="id_proveedor",
            response_model=ProveedorResponse,
            schema=db_config.SCHEMA
        )
    
    async def search_by_name(self, nombre: str) -> List[ProveedorResponse]:
        """Busca proveedores por nombre (búsqueda parcial)"""
        from app.core.database import get_db_connection
        
        async with get_db_connection() as conn:
            try:
                query = f"""
                    SELECT * FROM {self.full_table_name} 
                    WHERE LOWER(nombre) LIKE LOWER($1)
                    ORDER BY nombre
                """
                rows = await conn.fetch(query, f"%{nombre}%")
                return [self.response_model(**dict(row)) for row in rows]
            except Exception as e:
                logger.error(f"Error al buscar proveedores por nombre: {e}")
                raise DatabaseError(str(e))
    
    async def find_by_nit(self, nit: str) -> ProveedorResponse | None:
        """Busca un proveedor por NIT"""
        return await self.find_by_field("nit", nit)


class ProveedorService(BaseService[ProveedorCreate, ProveedorUpdate, ProveedorResponse]):
    """
    Servicio de Proveedor con lógica de negocio específica.
    
    Hereda operaciones CRUD genéricas de BaseService y agrega:
    - Validación de NIT duplicado al crear
    - Búsqueda por nombre
    - Búsqueda por NIT
    """
    
    def __init__(self):
        repository = ProveedorRepository()
        super().__init__(repository=repository, entity_name="Proveedor")
        # Mantener referencia al repositorio específico para métodos personalizados
        self._proveedor_repo = repository
    
    async def create(self, create_data: ProveedorCreate) -> ProveedorResponse:
        """
        Crea un nuevo proveedor con validación de NIT único.
        
        Args:
            create_data: Datos del proveedor a crear
            
        Returns:
            Proveedor creado
            
        Raises:
            DuplicateError: Si ya existe un proveedor con ese NIT
        """
        try:
            # Validación de negocio: verificar NIT único
            existing_nit = await self._proveedor_repo.find_by_nit(create_data.nit)
            if existing_nit:
                raise DuplicateError("Proveedor", "NIT", create_data.nit)
            
            # Delegar creación al método base
            return await super().create(create_data)
            
        except DuplicateError:
            raise
        except asyncpg.UniqueViolationError:
            logger.warning(f"Intento de crear proveedor con NIT duplicado: {create_data.nit}")
            raise DuplicateError("Proveedor", "NIT", create_data.nit)
        except asyncpg.PostgresError as e:
            logger.error(f"Error de PostgreSQL al crear proveedor: {e}")
            raise DatabaseError(str(e))
        except Exception as e:
            logger.error(f"Error inesperado al crear proveedor: {e}")
            raise DatabaseError(str(e))
    
    async def update(self, id_proveedor: int, update_data: ProveedorUpdate) -> ProveedorResponse:
        """
        Actualiza un proveedor con validación de NIT único.
        
        Args:
            id_proveedor: ID del proveedor a actualizar
            update_data: Datos a actualizar
            
        Returns:
            Proveedor actualizado
            
        Raises:
            NotFoundError: Si no existe el proveedor
            DuplicateError: Si el NIT ya existe en otro proveedor
        """
        try:
            # Si se está actualizando el NIT, validar que no exista
            update_dict = update_data.model_dump(exclude_unset=True)
            if "nit" in update_dict:
                existing_nit = await self._proveedor_repo.find_by_nit(update_dict["nit"])
                if existing_nit and existing_nit.id_proveedor != id_proveedor:
                    raise DuplicateError("Proveedor", "NIT", update_dict["nit"])
            
            # Delegar actualización al método base
            return await super().update(id_proveedor, update_data)
            
        except (NotFoundError, DuplicateError):
            raise
        except asyncpg.UniqueViolationError:
            logger.warning(f"Intento de actualizar con NIT duplicado")
            raise DuplicateError("Proveedor", "NIT", "valor duplicado")
        except asyncpg.PostgresError as e:
            logger.error(f"Error de PostgreSQL al actualizar proveedor: {e}")
            raise DatabaseError(str(e))
        except Exception as e:
            logger.error(f"Error inesperado al actualizar proveedor: {e}")
            raise DatabaseError(str(e))
    
    async def delete(self, id_proveedor: int) -> bool:
        """
        Elimina un proveedor.
        
        Args:
            id_proveedor: ID del proveedor a eliminar
            
        Returns:
            True si se eliminó correctamente
            
        Raises:
            NotFoundError: Si no existe el proveedor
            DatabaseError: Si tiene compras asociadas
        """
        try:
            return await super().delete(id_proveedor)
        except NotFoundError:
            raise
        except asyncpg.ForeignKeyViolationError:
            logger.warning(f"No se puede eliminar proveedor {id_proveedor}: tiene compras asociadas")
            raise DatabaseError("No se puede eliminar el proveedor porque tiene compras asociadas")
        except Exception as e:
            logger.error(f"Error al eliminar proveedor {id_proveedor}: {e}")
            raise DatabaseError(str(e))
    
    async def search_by_name(self, nombre: str) -> List[ProveedorResponse]:
        """
        Busca proveedores por nombre (búsqueda parcial).
        
        Args:
            nombre: Nombre o parte del nombre a buscar
            
        Returns:
            Lista de proveedores que coinciden
        """
        try:
            return await self._proveedor_repo.search_by_name(nombre)
        except Exception as e:
            logger.error(f"Error al buscar proveedores por nombre '{nombre}': {e}")
            raise DatabaseError(str(e))
    
    async def find_by_nit(self, nit: str) -> ProveedorResponse | None:
        """
        Busca un proveedor por NIT exacto.
        
        Args:
            nit: NIT a buscar
            
        Returns:
            Proveedor encontrado o None
        """
        try:
            return await self._proveedor_repo.find_by_nit(nit)
        except Exception as e:
            logger.error(f"Error al buscar proveedor por NIT '{nit}': {e}")
            raise DatabaseError(str(e))


# Instancia única del servicio (patrón Singleton a nivel de aplicación)
proveedor_service = ProveedorService()
