import logging
import contextlib
from typing import Any, Dict, Generator, Optional, Type
from sqlalchemy.engine import Engine
from sqlmodel import Session, create_engine
from starlette.requests import Request
from framefox.core.config.settings import Settings
from framefox.core.di.service_container import ServiceContainer
from framefox.core.orm.connection_manager import ConnectionManager


class EntityManagerRegistry:
    """Manages EntityManager instances and their configurations"""

    _instance = None
    _engines: Dict[str, Engine] = {}

    @classmethod
    def get_instance(cls) -> "EntityManagerRegistry":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized") and self._initialized:
            return
        self.settings = ServiceContainer().get(Settings)
        self.logger = logging.getLogger(__name__)
        self._initialized = True

    def get_engine(self, connection_name: str = "default") -> Engine:
        """Retrieves or creates a configured database engine"""
        if connection_name not in self._engines:
            db_url = self._get_database_url_string(connection_name)
            self._engines[connection_name] = create_engine(
                db_url,
                echo=self.settings.database_echo,
                pool_size=20,  # Maximum number of connections in the pool
                max_overflow=10,  # Additional connections allowed
                pool_timeout=30,  # Wait time for a connection
                pool_recycle=1800,  # Recycle connections after 30 min
                pool_pre_ping=True,  # Check connections before use
            )
        return self._engines[connection_name]

    def _get_database_url_string(self, connection_name: str = "default") -> str:
        """Retrieves the database URL according to the configuration"""
        db_config = self.settings.database_url

        if isinstance(db_config, str):
            return db_config

        if db_config.driver == "sqlite":
            return f"sqlite:///{db_config.database}"

        dialect = "mysql+pymysql" if db_config.driver == "mysql" else db_config.driver

        username = str(db_config.username) if db_config.username else ""
        password = str(db_config.password) if db_config.password else ""
        host = str(db_config.host) if db_config.host else "localhost"
        port = str(db_config.port) if db_config.port else "3306"
        database = str(db_config.database) if db_config.database else ""

        return f"{dialect}://{username}:{password}@{host}:{port}/{database}"
