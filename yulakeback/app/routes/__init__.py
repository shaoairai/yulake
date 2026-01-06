# Routes package
from app.routes.health import health_ns
from app.routes.auth import auth_ns
from app.routes.public import public_ns
from app.routes.salon import salon_ns

__all__ = ['health_ns', 'auth_ns', 'public_ns', 'salon_ns']
