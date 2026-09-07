"""Connection management for Fieldwire Connector."""
from __future__ import annotations
import uuid, json
from typing import Any
from imperal_sdk import ActionResult
from app import chat
from schemas import NoParams, ConnectParams, ConnectionIdParams, ConnectionRecord, ConnectionList, DeleteResult
from fieldwire_connector_client import FieldwireClient

_SECRET = "fieldwire_connector_connections"

def _mask(v: str) -> str:
    return v[:4] + "…" + v[-4:] if len(v) > 8 else "***"

async def _load_conns(ctx) -> list[dict]:
    raw = await ctx.secrets.get(_SECRET)
    if not raw: return []
    try: data = json.loads(raw)
    except: return []
    return data if isinstance(data, list) else []

async def _save_conns(ctx, conns: list[dict]) -> None:
    await ctx.secrets.set(_SECRET, json.dumps(conns))

async def resolve_client(ctx, connection_id: str = "") -> FieldwireClient:
    conns = await _load_conns(ctx)
    if not conns:
        raise ValueError("No Fieldwire connections configured. Use connect_fieldwire_connector first.")
    conn = conns[0]
    if connection_id:
        for c in conns:
            if c["id"] == connection_id:
                conn = c
                break
    return FieldwireClient(api_token=conn["api_token"], base_url=conn.get("base_url", ""))

@chat.function("connect_fieldwire_connector", "Connect Fieldwire account via credentials.", action_type="write", chain_callable=True, event="fieldwire-connector.connect_fieldwire_connector", effects=["create:connection"], data_model=ConnectionRecord)
async def connect_fieldwire_connector(ctx, params: ConnectParams) -> ActionResult:
    client = FieldwireClient(api_token=params.api_token, base_url=params.base_url)
    res = await client.verify_auth()
    if res.get("status") == "error":
        return ActionResult.error(f"Failed to connect to Fieldwire: {res.get('error')}")
    conns = await _load_conns(ctx)
    cid = f"conn_{uuid.uuid4().hex[:8]}"
    rec = {
        "id": cid,
        "label": params.label or "Primary Fieldwire",
        "api_token": params.api_token,
        "masked_key": _mask(params.api_token),
        "base_url": params.base_url,
        "is_active": True
    }
    for c in conns: c["is_active"] = False
    conns.append(rec)
    await _save_conns(ctx, conns)
    return ActionResult.success(rec, summary=f"Connected Fieldwire ({rec['label']}).")

@chat.function("list_connections", "List configured Fieldwire connections.", action_type="read", chain_callable=True, event="fieldwire-connector.list_connections", effects=["read:connections"], data_model=ConnectionList)
async def list_connections(ctx, params: NoParams) -> ActionResult:
    conns = await _load_conns(ctx)
    items = [{
        "id": c["id"],
        "label": c["label"],
        "masked_key": c.get("masked_key", "***"),
        "base_url": c.get("base_url", "https://api.fieldwire.com/api/v3"),
        "is_active": c.get("is_active", False)
    } for c in conns]
    return ActionResult.success({"connections": items, "total": len(items)}, summary=f"Found {len(items)} connection(s).")

@chat.function("disconnect_fieldwire_connector", "Disconnect Fieldwire account and delete stored credentials.", action_type="destructive", chain_callable=True, event="fieldwire-connector.disconnect_fieldwire_connector", effects=["delete:connection"], data_model=DeleteResult)
async def disconnect_fieldwire_connector(ctx, params: ConnectionIdParams) -> ActionResult:
    conns = await _load_conns(ctx)
    if not conns:
        return ActionResult.error("No connections to disconnect.")
    if params.connection_id:
        conns = [c for c in conns if c["id"] != params.connection_id]
    else:
        conns.clear()
    await _save_conns(ctx, conns)
    return ActionResult.success({"success": True, "message": "Disconnected successfully."}, summary="Disconnected Fieldwire connection.")
