"""
Factory Pattern para la creación y gestión de servicios
Centraliza la creación de servicios y sus dependencias
"""
from typing import TypeVar, Type, Generic, Dict, Any
from app.service.proveedor_service import ProveedorService, proveedor_service
from app.service.compra_proveedor_service import CompraProveedorService, compra_proveedor_service

T = TypeVar('T')


class ServiceFactory:
    """
    Factory para crear y gestionar instancias de servicios.
    
    Beneficios:
    - Centraliza la creación de servicios
    - Facilita el testing con mocks
    - Permite configuración dinámica
    - Gestiona el ciclo de vida de dependencias
    """
    
    _services: Dict[str, Any] = {}
    _initialized: bool = False
    
    @classmethod
    def initialize(cls):
        """Inicializa todos los servicios disponibles"""
        if not cls._initialized:
            cls._services = {
                'proveedor': proveedor_service,
                'compra_proveedor': compra_proveedor_service,
            }
            cls._initialized = True
    
    @classmethod
    def get_proveedor_service(cls) -> ProveedorService:
        """Obtiene el servicio de proveedor"""
        cls.initialize()
        return cls._services['proveedor']
    
    @classmethod
    def get_compra_proveedor_service(cls) -> CompraProveedorService:
        """Obtiene el servicio de compra proveedor"""
        cls.initialize()
        return cls._services['compra_proveedor']
    
    @classmethod
    def get_service(cls, service_name: str) -> Any:
        """
        Obtiene un servicio por nombre
        
        Args:
            service_name: Nombre del servicio ('proveedor', 'compra_proveedor')
            
        Returns:
            Instancia del servicio
            
        Raises:
            KeyError: Si el servicio no existe
        """
        cls.initialize()
        if service_name not in cls._services:
            raise KeyError(f"Servicio '{service_name}' no encontrado")
        return cls._services[service_name]
    
    @classmethod
    def register_service(cls, name: str, service_instance: Any):
        """
        Registra un nuevo servicio
        
        Args:
            name: Nombre del servicio
            service_instance: Instancia del servicio
        """
        cls.initialize()
        cls._services[name] = service_instance
    
    @classmethod
    def list_services(cls) -> list[str]:
        """Lista todos los servicios disponibles"""
        cls.initialize()
        return list(cls._services.keys())