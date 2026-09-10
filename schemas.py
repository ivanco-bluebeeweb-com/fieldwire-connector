"""Pydantic schemas for Fieldwire Connector."""
from __future__ import annotations
from typing import Any, Optional, List, Dict
from pydantic import BaseModel, Field

class NoParams(BaseModel):
    """Empty parameters model."""
    pass

class ConnectParams(BaseModel):
    label: str = Field(default="", description="Friendly connection label, e.g. Primary Fieldwire.")
    api_token: str = Field(description="Platform Access Token / API Key")
    base_url: str = Field(default="https://app.fieldwire.com/api/v3", description="Fieldwire API base URL.")

class ConnectionIdParams(BaseModel):
    connection_id: str = Field(default="", description="Connection identifier (empty uses active connection).")

class ConnectionRecord(BaseModel):
    id: str
    label: str
    masked_key: str
    base_url: str
    is_active: bool

class ConnectionList(BaseModel):
    connections: list[ConnectionRecord]
    total: int

class DeleteResult(BaseModel):
    success: bool
    message: str

class ProjectRecordRecord(BaseModel):
    id: str
    name: Optional[str] = None
    status: Optional[str] = None
    created_at: Optional[str] = None
    raw: Dict[str, Any] = Field(default_factory=dict)

class ProjectRecordList(BaseModel):
    projects: list[ProjectRecordRecord]
    total: int

class ListProjectRecordParams(BaseModel):
    connection_id: str = Field(default="", description="Optional connection ID.")
    limit: int = Field(default=20, ge=1, le=100, description="Max records to return.")

class GetProjectRecordParams(BaseModel):
    connection_id: str = Field(default="", description="Optional connection ID.")
    projectrecord_id: str = Field(description="Fieldwire ProjectRecord ID.")

class AuditHealthReport(BaseModel):
    healthy: bool
    total_projects: int
    details: Dict[str, Any] = Field(default_factory=dict)
    summary: str
