import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class DatabaseConfig:
    """Configuración de la base de datos usando variables de entorno"""
    
    HOST: str = os.getenv("HOST_DB")
    PORT: int = int(os.getenv("PORT_DB"))
    DATABASE: str = os.getenv("NAME_DB")
    USERNAME: str = os.getenv("USER_DB")
    PASSWORD: str = os.getenv("PASSWORD_DB")
    SCHEMA: str = os.getenv("SCHEMA_DB")
    
    # @classmethod
    # def get_database_url(cls) -> str:
    #     """Construye la URL de conexión a PostgreSQL"""
    #     return f"postgresql://{cls.USERNAME}:{cls.PASSWORD}@{cls.HOST}:{cls.PORT}/{cls.DATABASE}"
    
    @classmethod
    def get_async_database_url(cls) -> str:
        """Construye la URL de conexión asíncrona a PostgreSQL"""
        return f"postgresql+asyncpg://{cls.USERNAME}:{cls.PASSWORD}@{cls.HOST}:{cls.PORT}/{cls.DATABASE}"

# Instancia global de configuración
db_config = DatabaseConfig()