"""
TurboAPI: A high-performance web framework with elegant syntax and powerful validation.

Built on Starlette and using satya for data validation.
"""

__version__ = "0.1.0"

from .applications import TurboAPI
from .routing import APIRouter
from .params import Path, Query, Header, Cookie, Body, Depends, Security
from .responses import JSONResponse, HTMLResponse, PlainTextResponse, RedirectResponse, Response
from starlette.requests import Request
# Import middleware directly from starlette to ensure compatibility
from starlette.middleware.authentication import AuthenticationMiddleware
from .middleware import Middleware, JWTAuthMiddleware, BasicAuthMiddleware
from .exceptions import HTTPException
from .background import BackgroundTasks
from .authentication import (
    AuthCredentials, 
    BaseUser, 
    SimpleUser, 
    UnauthenticatedUser,
    BaseAuthentication,
    JWTAuthentication,
    OAuth2PasswordRequestForm,
    OAuth2PasswordBearer
)

# For WebSocket support
from starlette.websockets import WebSocket
