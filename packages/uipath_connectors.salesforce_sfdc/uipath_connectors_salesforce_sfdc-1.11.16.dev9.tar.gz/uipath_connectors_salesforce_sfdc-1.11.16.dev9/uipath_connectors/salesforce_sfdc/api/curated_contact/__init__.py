from .create_contact import sync as create_contact
from .create_contact import asyncio as create_contact_async
from .get_contact_by_id import sync as get_contact_by_id
from .get_contact_by_id import asyncio as get_contact_by_id_async
from .update_contact import sync as update_contact
from .update_contact import asyncio as update_contact_async

__all__ = [
    "create_contact",
    "create_contact_async",
    "get_contact_by_id",
    "get_contact_by_id_async",
    "update_contact",
    "update_contact_async",
]
