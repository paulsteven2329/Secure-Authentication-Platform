# backend/app/models/__init__.py
from .user import User  # Import your models if you add more
from app.db.base_class import Base  # Re-export Base

__all__ = ["Base", "User"]