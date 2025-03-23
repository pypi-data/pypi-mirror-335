from fastapi import Request
from framefox.core.orm.entity_manager import EntityManager


class EntityManagerMiddleware:
    """Middleware that manages the lifecycle of sessions for each request"""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        # Create a new EntityManager for this request
        entity_manager = EntityManager()

        # Store the EntityManager in the request state
        request = Request(scope)
        request.state.entity_manager = entity_manager

        try:
            # Call the application
            await self.app(scope, receive, send)
        finally:
            # Cleanup: close the session
            entity_manager.close_session()
