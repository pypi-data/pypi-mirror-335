# hashai/storage/__init__.py
from .base_storage import BaseMemoryStorage
from .in_memory_storage import InMemoryStorage
from .local_storage import FileStorage

__all__ = ['BaseMemoryStorage', 'InMemoryStorage', 'FileStorage']