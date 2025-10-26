import asyncpg
import logging
from typing import Optional
from contextlib import asynccontextmanager
from app.core.config import db_config

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseConnection:
    """
    Singleton para manejar la conexión a la base de datos PostgreSQL
    
    Este patrón Singleton garantiza que solo exista una instancia del pool
    de conexiones a la base de datos durante toda la ejecución de la aplicación.
    """
    _instance: Optional['DatabaseConnection'] = None
    _connection_pool: Optional[asyncpg.Pool] = None
    _initialized: bool = False
    
    def __new__(cls) -> 'DatabaseConnection':
        """Implementación del patrón Singleton"""
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """
        Inicializador que se ejecuta solo una vez gracias al flag _initialized.
        Esto evita reinicializar la instancia en llamadas posteriores.
        """
        if not DatabaseConnection._initialized:
            DatabaseConnection._initialized = True
            logger.info("Instancia Singleton de DatabaseConnection inicializada")
    
    async def connect(self) -> None:
        """Establece la conexión pool a la base de datos"""
        if self._connection_pool is None:
            try:
                self._connection_pool = await asyncpg.create_pool(
                    host=db_config.HOST,
                    port=db_config.PORT,
                    user=db_config.USERNAME,
                    password=db_config.PASSWORD,
                    database=db_config.DATABASE,
                    # min_size=5,  # Mínimo de conexiones en el pool
                    # max_size=20,  # Máximo de conexiones en el pool
                    # command_timeout=60,
                    server_settings={
                        'jit': 'off'  # Mejora performance para queries simples
                    }
                )
                logger.info("Conexión a la base de datos establecida exitosamente")
            except Exception as e:
                logger.error(f"Error al conectar a la base de datos: {e}")
                raise
    
    async def disconnect(self) -> None:
        """Cierra la conexión pool a la base de datos"""
        if self._connection_pool:
            await self._connection_pool.close()
            self._connection_pool = None
            logger.info("Conexión a la base de datos cerrada")
    
    @asynccontextmanager
    async def get_connection(self):
        """
        Context manager para obtener una conexión del pool
        
        Usage:
            async with db.get_connection() as conn:
                result = await conn.fetch("SELECT * FROM users")
        """
        if self._connection_pool is None:
            await self.connect()
        
        async with self._connection_pool.acquire() as connection:
            try:
                yield connection
            except Exception as e:
                logger.error(f"Error en la operación de base de datos: {e}")
                raise
    
    @asynccontextmanager
    async def get_transaction(self):
        """
        Context manager para manejar transacciones
        
        Usage:
            async with db.get_transaction() as transaction:
                await transaction.execute("INSERT INTO users ...")
                await transaction.execute("UPDATE users ...")
                # Auto-commit al final, auto-rollback en caso de error
        """
        async with self.get_connection() as connection:
            async with connection.transaction():
                yield connection
    
    async def execute(self, query: str, *args) -> str:
        """
        Ejecuta una query que no devuelve resultados (INSERT, UPDATE, DELETE)
        
        Args:
            query: SQL query string
            *args: Parámetros para la query
            
        Returns:
            Status string de la operación
        """
        async with self.get_connection() as conn:
            return await conn.execute(query, *args)
    
    async def fetch_one(self, query: str, *args) -> Optional[dict]:
        """
        Ejecuta una query y devuelve un solo resultado
        
        Args:
            query: SQL query string
            *args: Parámetros para la query
            
        Returns:
            Un diccionario con el resultado o None
        """
        async with self.get_connection() as conn:
            row = await conn.fetchrow(query, *args)
            return dict(row) if row else None
    
    async def fetch_all(self, query: str, *args) -> list[dict]:
        """
        Ejecuta una query y devuelve todos los resultados
        
        Args:
            query: SQL query string
            *args: Parámetros para la query
            
        Returns:
            Lista de diccionarios con los resultados
        """
        async with self.get_connection() as conn:
            rows = await conn.fetch(query, *args)
            return [dict(row) for row in rows]
    
    async def health_check(self) -> bool:
        """
        Verifica si la conexión a la base de datos está funcionando
        
        Returns:
            True si la conexión está OK, False en caso contrario
        """
        try:
            async with self.get_connection() as conn:
                await conn.fetchval("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"Health check falló: {e}")
            return False
    
    @property
    def is_connected(self) -> bool:
        """Verifica si el pool de conexiones está activo"""
        return self._connection_pool is not None and not self._connection_pool._closed

# Instancia global del singleton
db = DatabaseConnection()

# Función de conveniencia para obtener una conexión
def get_db_connection():
    """Función para obtener una conexión de la base de datos"""
    return db.get_connection()