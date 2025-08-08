from .organization import router as org_router
from .user import router as user_router
from .auth import router as auth_router
from .doc import router as doc_router
from .query import router as query_router


__all__ = ["org_router","user_router","auth_router","doc_router", "query_router"]