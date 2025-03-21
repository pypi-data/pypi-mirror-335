from .execute_query import sync as execute_query
from .execute_query import asyncio as execute_query_async

__all__ = [
    "execute_query",
    "execute_query_async",
]
