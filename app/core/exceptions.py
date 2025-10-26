"""
Sistema centralizado de excepciones para toda la aplicación
"""
from typing import Optional


class BaseServiceError(Exception):
    """Excepción base para todos los errores de servicio"""
    def __init__(self, message: str, entity: Optional[str] = None):
        self.message = message
        self.entity = entity
        super().__init__(self.message)


class NotFoundError(BaseServiceError):
    """Excepción cuando no se encuentra un recurso"""
    def __init__(self, entity: str, id_value: any):
        message = f"{entity} con ID {id_value} no encontrado"
        super().__init__(message, entity)
        self.id_value = id_value


class DuplicateError(BaseServiceError):
    """Excepción cuando ya existe un recurso duplicado"""
    def __init__(self, entity: str, field: str, value: any):
        message = f"Ya existe un {entity} con {field}: {value}"
        super().__init__(message, entity)
        self.field = field
        self.value = value


class ForeignKeyError(BaseServiceError):
    """Excepción cuando hay un error de clave foránea"""
    def __init__(self, entity: str, id_value: any):
        message = f"El {entity} con ID {id_value} no existe"
        super().__init__(message, entity)
        self.id_value = id_value


class DatabaseError(BaseServiceError):
    """Excepción para errores generales de base de datos"""
    def __init__(self, detail: str):
        message = f"Error de base de datos: {detail}"
        super().__init__(message)
        self.detail = detail


class ValidationError(BaseServiceError):
    """Excepción para errores de validación"""
    def __init__(self, message: str, field: Optional[str] = None):
        super().__init__(message)
        self.field = field
