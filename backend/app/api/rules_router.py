"""FastAPI endpoints for regulatory catalog inspection and ad-hoc hybrid knowledge search."""
import json
import logging
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from backend.app.core.config import settings
from backend.app.rag.retriever import retriever
from backend.app.rag.vector_store import RuleChunk

logger = logging.getLogger(__name__)

router = APIRouter()


class RuleSearchRequest(BaseModel):
    query: str = Field(description="Search text or query")
    discipline: str | None = Field(default=None, description="JUMPING, DRESSAGE, EVENTING, or ALL")
    top_k: int = Field(default=5, ge=1, le=20)


def load_catalog_rules() -> list[dict[str, Any]]:
    path = Path(settings.RULES_CATALOG_PATH)
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data.get("rules", [])
    except Exception as exc:
        logger.error("Failed to read rules catalog (%s)", exc)
        return []


@router.get("", response_model=list[dict[str, Any]])
def list_rules(
    discipline: str | None = Query(None, description="Filter by discipline e.g. JUMPING, DRESSAGE"),
    category: str | None = Query(None, description="Filter by category e.g. BRANDING_LOGO"),
) -> list[dict[str, Any]]:
    """List all codified quantitative rules with optional discipline and category filters."""
    rules = load_catalog_rules()
    if discipline:
        disc_norm = discipline.upper()
        rules = [
            r for r in rules
            if r.get("discipline") in (disc_norm, "ALL") or disc_norm in [str(d).upper() for d in r.get("applicable_disciplines", [])]
        ]
    if category:
        cat_norm = category.lower()
        rules = [r for r in rules if cat_norm in r.get("category", "").lower()]

    return rules


@router.get("/{rule_id}", response_model=dict[str, Any])
def get_rule_by_id(rule_id: str) -> dict[str, Any]:
    """Retrieve details for a specific codified rule."""
    rules = load_catalog_rules()
    rule = next((r for r in rules if r.get("rule_id", "").upper() == rule_id.upper()), None)
    if not rule:
        raise HTTPException(status_code=404, detail=f"Rule '{rule_id}' not found in catalog.")
    return rule


@router.post("/search", response_model=list[RuleChunk])
def search_regulations(req: RuleSearchRequest) -> list[RuleChunk]:
    """Perform ad-hoc hybrid semantic search across FEI regulations and Brand SOPs."""
    return retriever.retrieve_rules(
        query=req.query,
        discipline=req.discipline,
        top_k=req.top_k,
    )
