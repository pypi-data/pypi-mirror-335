from .download_soql_bulk_job_results import sync as download_soql_bulk_job_results
from .download_soql_bulk_job_results import (
    asyncio as download_soql_bulk_job_results_async,
)

__all__ = [
    "download_soql_bulk_job_results",
    "download_soql_bulk_job_results_async",
]
