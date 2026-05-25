"""
GhoraGhuri — Common Pydantic Schemas
"""
from __future__ import annotations

from pydantic import BaseModel


class ApiResponse(BaseModel):
    """Standard API response wrapper."""
    success: bool
    message: str
    message_bn: str | None = None
    data: dict | list | None = None


class ErrorResponse(BaseModel):
    """Standard error response."""
    success: bool = False
    error_code: str
    message: str
    message_bn: str | None = None


class PaginatedResponse(BaseModel):
    """Paginated list response."""
    items: list
    total: int
    page: int
    page_size: int
    has_next: bool
