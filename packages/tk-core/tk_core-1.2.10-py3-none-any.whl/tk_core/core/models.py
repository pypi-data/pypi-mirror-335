"""
Base model for all Terakeet endpoints.
Requires an application name to be passed in the request body.
"""

import datetime as dt

from pydantic import BaseModel, Field


class AuditTableOutput(BaseModel):
    request_id: str
    request_time: dt.datetime
    consumer_application: str
    request_metadata: dict = Field(default={})
    processing_application: str
    cached_results: int | None = Field(default=None)
    needed_results: int | None = Field(default=None)
    errors: bool = False
    job_params: dict = Field(default={})
