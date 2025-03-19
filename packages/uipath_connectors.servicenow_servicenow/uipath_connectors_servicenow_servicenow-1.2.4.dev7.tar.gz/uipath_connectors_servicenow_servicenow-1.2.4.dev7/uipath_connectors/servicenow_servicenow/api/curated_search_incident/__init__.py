from .search_incidents import sync as search_incidents
from .search_incidents import asyncio as search_incidents_async

__all__ = [
    "search_incidents",
    "search_incidents_async",
]
