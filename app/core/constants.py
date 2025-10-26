"""
Constantes de la aplicación
"""
from enum import IntEnum

# Estados de compra
class EstadoCompra(IntEnum):
    """Estados posibles de una compra"""
    PENDIENTE = 0
    EN_PROCESO = 1
    RECIBIDA = 2
    CANCELADA = 3
    DEVUELTA = 4

# Mensajes de error comunes
ERROR_MESSAGES = {
    "not_found": "{entity} con ID {id} no encontrado",
    "duplicate": "Ya existe un {entity} con {field}: {value}",
    "foreign_key": "El {entity} con ID {id} no existe",
    "database_error": "Error de base de datos: {detail}",
    "internal_error": "Error interno del servidor"
}

# Configuración de paginación
DEFAULT_PAGE_SIZE = 50
MAX_PAGE_SIZE = 100

# Esquema de base de datos
DB_SCHEMA = "psa_problems"
