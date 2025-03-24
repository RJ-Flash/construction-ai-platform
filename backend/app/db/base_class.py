"""
SQLAlchemy base model class.
"""
from typing import Any

from sqlalchemy.ext.declarative import as_declarative, declared_attr


@as_declarative()
class Base:
    """
    SQLAlchemy declarative base.
    
    All models inherit from this class.
    """
    
    id: Any
    __name__: str
    
    # Generate tablename automatically
    @declared_attr
    def __tablename__(cls) -> str:
        """
        Generate table name automatically.
        
        By default, uses the lowercase class name.
        """
        return cls.__name__.lower()
