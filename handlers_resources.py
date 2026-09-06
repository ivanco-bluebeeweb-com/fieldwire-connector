"""Resource handlers for Fieldwire Connector."""
from __future__ import annotations
from typing import Any
from imperal_sdk import ActionResult
from app import chat
from schemas import (
    ListProjectRecordParams, GetProjectRecordParams,
    ProjectRecordRecord, ProjectRecordList, AuditHealthReport, ConnectionIdParams
)
from handlers_connection import resolve_client

@chat.function("list_projects", "List projects in Fieldwire.", action_type="read", chain_callable=True, event="fieldwire-connector.list_projects", effects=["read:projects"], data_model=ProjectRecordList)
async def list_projects(params: ListProjectRecordParams, ctx) -> ActionResult:
    client = await resolve_client(ctx, params.connection_id)
    try:
        raw_items = await client.list_projects(limit=params.limit)
        items = []
        for r in raw_items:
            rid = str(r.get("id") or r.get("key") or r.get("uuid") or "unknown")
            rname = r.get("name") or r.get("title") or r.get("label") or rid
            items.append({"id": rid, "name": rname, "status": r.get("status"), "created_at": r.get("createdAt") or r.get("created_at"), "raw": r})
        return ActionResult.ok({"projects": items, "total": len(items)}, summary=f"Found {len(items)} projects.")
    except Exception as e:
        return ActionResult.error(f"Error listing projects: {e}")

@chat.function("get_projectrecord", "Get details of one ProjectRecord in Fieldwire.", action_type="read", chain_callable=True, event="fieldwire-connector.get_projectrecord", effects=["read:projectrecord"], data_model=ProjectRecordRecord)
async def get_projectrecord(params: GetProjectRecordParams, ctx) -> ActionResult:
    client = await resolve_client(ctx, params.connection_id)
    try:
        r = await client.get_projectrecord(params.projectrecord_id)
        rid = str(r.get("id") or params.projectrecord_id)
        rname = r.get("name") or r.get("title") or rid
        return ActionResult.ok({"id": rid, "name": rname, "status": r.get("status"), "created_at": r.get("createdAt") or r.get("created_at"), "raw": r}, summary=f"Retrieved ProjectRecord {rid}.")
    except Exception as e:
        return ActionResult.error(f"Error retrieving ProjectRecord: {e}")

@chat.function("audit_projectrecord_health", "Audit health of Fieldwire projects and connectivity.", action_type="read", chain_callable=True, event="fieldwire-connector.audit_projectrecord_health", effects=["read:audit"], data_model=AuditHealthReport)
async def audit_projectrecord_health(params: ConnectionIdParams, ctx) -> ActionResult:
    client = await resolve_client(ctx, params.connection_id)
    try:
        items = await client.list_projects(limit=50)
        return ActionResult.ok({
            "healthy": True,
            "total_projects": len(items),
            "details": {"sample_count": len(items)},
            "summary": f"Fieldwire healthy. Sampled {len(items)} projects."
        }, summary=f"Fieldwire health check passed with {len(items)} projects.")
    except Exception as e:
        return ActionResult.error(f"Error auditing Fieldwire health: {e}")
