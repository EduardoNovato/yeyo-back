"""
Servicio de CompraProveedor - Contiene lógica de negocio específica
Hereda operaciones CRUD genéricas de BaseService
"""
from typing import List
from datetime import datetime, timezone
import asyncpg
import logging
from app.core.base_service import BaseService
from app.core.base_repository import BaseRepository
from app.core.constants import DB_SCHEMA
from app.core.exceptions import NotFoundError, DuplicateError, ForeignKeyError, DatabaseError
from app.models.compra_proveedor import CompraProveedorCreate, CompraProveedorUpdate, CompraProveedorResponse

logger = logging.getLogger(__name__)


class CompraProveedorRepository(BaseRepository[CompraProveedorResponse]):
    """
    Repositorio específico para CompraProveedor.
    Extiende BaseRepository con métodos específicos de búsqueda.
    """
    
    def __init__(self):
        super().__init__(
            table_name="compra_proveedor",
            id_field="id_compra",
            response_model=CompraProveedorResponse,
            schema=DB_SCHEMA
        )
    
    async def find_by_proveedor(self, id_proveedor: int) -> List[CompraProveedorResponse]:
        """Obtiene todas las compras de un proveedor específico"""
        return await self.find_many_by_field(
            "id_proveedor", 
            id_proveedor, 
            order_by="fecha_compra DESC, id_compra DESC"
        )
    
    async def find_by_factura(self, factura: str) -> CompraProveedorResponse | None:
        """Busca una compra por número de factura"""
        return await self.find_by_field("factura", factura)
    
    async def find_all_ordered(self) -> List[CompraProveedorResponse]:
        """Obtiene todas las compras ordenadas por fecha descendente"""
        return await self.find_all(order_by="fecha_compra DESC, id_compra DESC")


class CompraProveedorService(BaseService[CompraProveedorCreate, CompraProveedorUpdate, CompraProveedorResponse]):
    """
    Servicio de CompraProveedor con lógica de negocio específica.
    
    Hereda operaciones CRUD genéricas de BaseService y agrega:
    - Validación de factura duplicada
    - Normalización de fechas
    - Búsqueda por proveedor
    - Verificación de proveedor existente
    """
    
    def __init__(self):
        repository = CompraProveedorRepository()
        super().__init__(repository=repository, entity_name="CompraProveedor")
        self._compra_repo = repository
    
    async def create(self, create_data: CompraProveedorCreate) -> CompraProveedorResponse:
        """
        Crea una nueva compra de proveedor.
        
        Args:
            create_data: Datos de la compra a crear
            
        Returns:
            Compra creada
            
        Raises:
            DuplicateError: Si ya existe una compra con esa factura
            ForeignKeyError: Si el proveedor no existe
        """
        try:
            # Validación de negocio: verificar factura única
            existing_factura = await self._compra_repo.find_by_factura(create_data.factura)
            if existing_factura:
                raise DuplicateError("CompraProveedor", "factura", create_data.factura)
            
            # Normalizar fecha_compra si no se proporciona
            data_dict = create_data.model_dump(exclude_unset=True)
            if "fecha_compra" not in data_dict or data_dict["fecha_compra"] is None:
                data_dict["fecha_compra"] = datetime.now(timezone.utc).replace(tzinfo=None)
            
            # Crear usando el repository
            return await self.repository.create(data_dict)
            
        except DuplicateError:
            raise
        except asyncpg.UniqueViolationError:
            logger.warning(f"Intento de crear compra con factura duplicada: {create_data.factura}")
            raise DuplicateError("CompraProveedor", "factura", create_data.factura)
        except asyncpg.ForeignKeyViolationError:
            logger.warning(f"ID de proveedor no válido: {create_data.id_proveedor}")
            raise ForeignKeyError("Proveedor", create_data.id_proveedor)
        except asyncpg.PostgresError as e:
            logger.error(f"Error de PostgreSQL al crear compra: {e}")
            raise DatabaseError(str(e))
        except Exception as e:
            logger.error(f"Error inesperado al crear compra: {e}")
            raise DatabaseError(str(e))
    
    async def update(self, id_compra: int, update_data: CompraProveedorUpdate) -> CompraProveedorResponse:
        """
        Actualiza una compra de proveedor.
        
        Args:
            id_compra: ID de la compra a actualizar
            update_data: Datos a actualizar
            
        Returns:
            Compra actualizada
            
        Raises:
            NotFoundError: Si no existe la compra
            ForeignKeyError: Si el proveedor no existe
        """
        try:
            # Si se está actualizando la factura, validar que no exista
            update_dict = update_data.model_dump(exclude_unset=True)
            if "factura" in update_dict:
                existing_factura = await self._compra_repo.find_by_factura(update_dict["factura"])
                if existing_factura and existing_factura.id_compra != id_compra:
                    raise DuplicateError("CompraProveedor", "factura", update_dict["factura"])
            
            return await super().update(id_compra, update_data)
            
        except (NotFoundError, DuplicateError):
            raise
        except asyncpg.ForeignKeyViolationError:
            logger.warning("Error de clave foránea al actualizar compra")
            raise ForeignKeyError("Proveedor", "id no válido")
        except asyncpg.PostgresError as e:
            logger.error(f"Error de PostgreSQL al actualizar compra: {e}")
            raise DatabaseError(str(e))
        except Exception as e:
            logger.error(f"Error inesperado al actualizar compra: {e}")
            raise DatabaseError(str(e))
    
    async def get_all(self) -> List[CompraProveedorResponse]:
        """
        Obtiene todas las compras ordenadas por fecha descendente.
        
        Returns:
            Lista de compras ordenadas
        """
        try:
            return await self._compra_repo.find_all_ordered()
        except Exception as e:
            logger.error(f"Error al obtener todas las compras: {e}")
            raise DatabaseError(str(e))
    
    async def get_by_proveedor(self, id_proveedor: int) -> List[CompraProveedorResponse]:
        """
        Obtiene todas las compras de un proveedor específico.
        
        Args:
            id_proveedor: ID del proveedor
            
        Returns:
            Lista de compras del proveedor
        """
        try:
            return await self._compra_repo.find_by_proveedor(id_proveedor)
        except Exception as e:
            logger.error(f"Error al obtener compras del proveedor {id_proveedor}: {e}")
            raise DatabaseError(str(e))


# Instancia única del servicio (patrón Singleton a nivel de aplicación)
compra_proveedor_service = CompraProveedorService()
