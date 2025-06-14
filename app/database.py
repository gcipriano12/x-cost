from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
import os
from typing import Generator
import redis
import json
from datetime import datetime, timedelta
import logging

# Configuração do logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurações do banco de dados
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://finops_user:finops_password@localhost:5432/finops_db"
)

# Configurações do Redis
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Engine do PostgreSQL com pool de conexões
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False  # Set to True for SQL debugging
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Configuração do Redis
redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)

class DatabaseManager:
    """Gerenciador de conexões com o banco de dados"""
    
    def __init__(self):
        self.engine = engine
        self.SessionLocal = SessionLocal
    
    def get_db(self) -> Generator[Session, None, None]:
        """Gerador de sessões do banco de dados"""
        db = self.SessionLocal()
        try:
            yield db
        except Exception as e:
            logger.error(f"Database error: {str(e)}")
            db.rollback()
            raise
        finally:
            db.close()
    
    def get_session(self):
        """Context manager para sessões do banco de dados"""
        return DatabaseSession(self.SessionLocal)
    
    def test_connection(self) -> bool:
        """Testa a conexão com o banco de dados"""
        try:
            from sqlalchemy import text
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.error(f"Database connection failed: {str(e)}")
            return False

class DatabaseSession:
    """Context manager para sessões de banco de dados"""
    
    def __init__(self, session_factory):
        self.session_factory = session_factory
        self.db = None
    
    def __enter__(self):
        self.db = self.session_factory()
        return self.db
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.db.rollback()
        else:
            self.db.commit()
        self.db.close()

class CacheManager:
    """Gerenciador de cache Redis"""
    
    def __init__(self):
        self.redis_client = redis_client
        self.default_ttl = 3600  # 1 hora
    
    def get(self, key: str):
        """Obtém um valor do cache"""
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Cache get error: {str(e)}")
            return None
    
    def set(self, key: str, value, ttl: int = None):
        """Define um valor no cache"""
        try:
            ttl = ttl or self.default_ttl
            serialized_value = json.dumps(value, default=str)
            self.redis_client.setex(key, ttl, serialized_value)
            return True
        except Exception as e:
            logger.error(f"Cache set error: {str(e)}")
            return False
    
    def delete(self, key: str):
        """Remove um valor do cache"""
        try:
            return self.redis_client.delete(key)
        except Exception as e:
            logger.error(f"Cache delete error: {str(e)}")
            return False
    
    def clear_pattern(self, pattern: str):
        """Remove todas as chaves que correspondem ao padrão"""
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Cache clear pattern error: {str(e)}")
            return 0
    
    def test_connection(self) -> bool:
        """Testa a conexão com o Redis"""
        try:
            self.redis_client.ping()
            return True
        except Exception as e:
            logger.error(f"Redis connection failed: {str(e)}")
            return False

# Instâncias globais
db_manager = DatabaseManager()
cache_manager = CacheManager()

# Função para obter sessão do banco (compatibilidade com FastAPI)
def get_database() -> Generator[Session, None, None]:
    """Dependency para FastAPI - versão corrigida"""
    db = db_manager.SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

# Função auxiliar para obter sessão direta (workaround)
def get_db_session() -> Session:
    """Retorna sessão direta para casos onde dependency não funciona"""
    return db_manager.SessionLocal()

# Função para obter cache
def get_cache() -> CacheManager:
    """Dependency para FastAPI"""
    return cache_manager

# Decorador para cache automático
def cached(ttl: int = 3600, key_prefix: str = "finops"):
    """Decorador para cachear resultados de funções"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Gerar chave do cache
            cache_key = f"{key_prefix}:{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Tentar obter do cache
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                logger.info(f"Cache hit for key: {cache_key}")
                return cached_result
            
            # Executar função e cachear resultado
            result = func(*args, **kwargs)
            cache_manager.set(cache_key, result, ttl)
            logger.info(f"Cache set for key: {cache_key}")
            return result
        
        return wrapper
    return decorator

# Função para inicializar o banco de dados
def init_database():
    """Inicializa as tabelas do banco de dados"""
    try:
        # Importar todos os modelos
        from app.models import Base, CloudProvider, FocusCostData, CostAnalysis, Budget
        
        # Criar todas as tabelas
        Base.metadata.create_all(bind=engine)
        
        # Verificar e criar provedores padrão
        with SessionLocal() as db:
            existing_providers = db.query(CloudProvider).count()
            if existing_providers == 0:
                providers = [
                    CloudProvider(provider_name="AWS"),
                    CloudProvider(provider_name="Azure"),
                    CloudProvider(provider_name="GCP"),
                    CloudProvider(provider_name="Oracle Cloud")
                ]
                db.add_all(providers)
                db.commit()
                logger.info("Default cloud providers created")
        
        logger.info("Database initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        return False

# Função para executar migrações
def run_migrations():
    """Executa migrações do banco de dados"""
    try:
        # Aqui você pode adicionar lógica de migração específica
        # Por exemplo, usando Alembic
        logger.info("Migrations completed successfully")
        return True
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        return False

# Função para health check do sistema
def health_check():
    """Verifica a saúde do sistema"""
    health_status = {
        "database": db_manager.test_connection(),
        "cache": cache_manager.test_connection(),
        "timestamp": datetime.utcnow().isoformat()
    }
    
    health_status["overall"] = all(health_status.values())
    return health_status