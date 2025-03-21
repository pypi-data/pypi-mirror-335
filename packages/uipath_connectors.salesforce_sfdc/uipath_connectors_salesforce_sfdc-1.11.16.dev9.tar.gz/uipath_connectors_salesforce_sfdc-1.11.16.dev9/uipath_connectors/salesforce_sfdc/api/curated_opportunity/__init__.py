from .create_opportunity import sync as create_opportunity
from .create_opportunity import asyncio as create_opportunity_async
from .get_opportunity_by_id import sync as get_opportunity_by_id
from .get_opportunity_by_id import asyncio as get_opportunity_by_id_async

__all__ = [
    "create_opportunity",
    "create_opportunity_async",
    "get_opportunity_by_id",
    "get_opportunity_by_id_async",
]
