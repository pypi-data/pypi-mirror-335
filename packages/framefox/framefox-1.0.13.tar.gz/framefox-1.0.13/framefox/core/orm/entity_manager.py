import logging
import contextlib
from typing import Any, Generator, Type
from sqlmodel import SQLModel, Session
from framefox.core.di.service_container import ServiceContainer
from framefox.core.orm.entity_manager_registry import EntityManagerRegistry


"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: LEUROND Raphaël & BOUMAZA Rayen
Github: https://github.com/Vasulvius & https://github.com/RayenBou
"""


class EntityManager:
    """
    Entity manager scoped to the current request.
    """

    def __init__(self, connection_name: str = "default"):
        self.registry = EntityManagerRegistry.get_instance()
        self.logger = logging.getLogger(__name__)
        self.engine = self.registry.get_engine(connection_name)
        self._session = None
        self._transaction_depth = 0

    @property
    def session(self) -> Session:
        """Returns the active session or creates a new one"""
        if self._session is None:
            self._session = Session(self.engine)
        return self._session

    def close_session(self):
        """Closes the active session if it exists"""
        if self._session is not None:
            self._session.close()
            self._session = None

    @contextlib.contextmanager
    def transaction(self) -> Generator[Session, None, None]:
        """Context manager for transactions"""
        session = self.session
        self._transaction_depth += 1
        try:
            yield session
            if self._transaction_depth == 1:
                session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            self._transaction_depth -= 1

    def commit(self) -> None:
        """Commit if we are not in a nested transaction"""
        if self._transaction_depth <= 1:
            self.session.commit()

    def rollback(self) -> None:
        """Rolls back the current transaction"""
        self.session.rollback()

    def persist(self, entity) -> None:
        self.session.add(entity)

    def delete(self, entity) -> None:
        self.session.delete(entity)

    def refresh(self, entity) -> None:
        self.session.refresh(entity)

    def exec_statement(self, statement) -> list:
        return self.session.exec(statement).all()

    def find(self, entity_class, primary_keys) -> Any:
        return self.session.get(entity_class, primary_keys)

    def find_existing_entity(self, entity) -> Any:
        primary_keys = entity.get_primary_keys()
        keys = {key: getattr(entity, key) for key in primary_keys}
        return self.find(entity.__class__, keys)

    def create_all_tables(self) -> None:
        SQLModel.metadata.create_all(self.engine)

    def drop_all_tables(self) -> None:
        SQLModel.metadata.drop_all(self.engine)

    def get_repository(self, entity_class: Type) -> Any:
        container = ServiceContainer()
        repositories = container.get_by_tag_prefix("repository.")

        for repo in repositories:
            if getattr(repo, "model", None) == entity_class:
                return repo
        return None
