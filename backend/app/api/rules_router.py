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


class RuleCreateRequest(BaseModel):
    rule_id: str = Field(description="Unique rule ID e.g. BRAND-SS26-LINING")
    source: str = Field(default="BRAND", description="FEI or BRAND")
    rulebook: str = Field(description="Rulebook or policy title e.g. Maison Équestre Brand Standard")
    article: str = Field(default="", description="Article or section reference e.g. Art. 4.2")
    discipline: str = Field(default="ALL", description="JUMPING, DRESSAGE, EVENTING, or ALL")
    target_field: str = Field(description="Specification dot-path e.g. materials.lining_silk_pct")
    operator: str = Field(default="<=", description="Comparison operator: <=, >=, ==, in")
    threshold: Any = Field(description="Threshold value: number, string, or boolean")
    unit: str = Field(default="", description="Unit of measurement e.g. cm2, %, EUR")
    severity_if_violated: str = Field(default="VIOLATION", description="VIOLATION or WARNING")
    verbatim_citation: str = Field(description="Official regulatory text or policy quotation")
    remedy_template: str = Field(description="Prescribed remedy suggestion")


class RuleUpdateRequest(BaseModel):
    source: str | None = None
    rulebook: str | None = None
    article: str | None = None
    discipline: str | None = None
    target_field: str | None = None
    operator: str | None = None
    threshold: Any | None = None
    unit: str | None = None
    severity_if_violated: str | None = None
    verbatim_citation: str | None = None
    remedy_template: str | None = None


class RuleSearchRequest(BaseModel):
    query: str
    discipline: str | None = None
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


def save_catalog_rules(rules: list[dict[str, Any]]) -> None:
    path = Path(settings.RULES_CATALOG_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    catalog = {
        "catalog_version": "2026.1",
        "rules": rules,
    }
    path.write_text(json.dumps(catalog, indent=2, ensure_ascii=False), encoding="utf-8")


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


@router.post("", response_model=dict[str, Any], status_code=201)
def create_rule(req: RuleCreateRequest) -> dict[str, Any]:
    """Dynamically register a new regulatory or brand rule into the catalog."""
    rules = load_catalog_rules()
    normalized_id = req.rule_id.strip().upper()
    if any(r.get("rule_id", "").upper() == normalized_id for r in rules):
        raise HTTPException(status_code=409, detail=f"Rule ID '{normalized_id}' already exists in catalog.")

    new_rule = req.model_dump()
    new_rule["rule_id"] = normalized_id
    rules.append(new_rule)
    save_catalog_rules(rules)
    logger.info("Created new rule: %s", normalized_id)
    return new_rule


@router.get("/{rule_id}", response_model=dict[str, Any])
def get_rule_by_id(rule_id: str) -> dict[str, Any]:
    """Retrieve details for a specific codified rule."""
    rules = load_catalog_rules()
    rule = next((r for r in rules if r.get("rule_id", "").upper() == rule_id.upper()), None)
    if not rule:
        raise HTTPException(status_code=404, detail=f"Rule '{rule_id}' not found in catalog.")
    return rule


@router.put("/{rule_id}", response_model=dict[str, Any])
def update_rule(rule_id: str, req: RuleUpdateRequest) -> dict[str, Any]:
    """Update threshold, citation, or properties of an existing codified rule."""
    rules = load_catalog_rules()
    idx = next((i for i, r in enumerate(rules) if r.get("rule_id", "").upper() == rule_id.upper()), None)
    if idx is None:
        raise HTTPException(status_code=404, detail=f"Rule '{rule_id}' not found in catalog.")

    target = rules[idx]
    update_data = req.model_dump(exclude_unset=True)
    target.update(update_data)
    rules[idx] = target
    save_catalog_rules(rules)
    logger.info("Updated rule: %s", rule_id)
    return target


@router.delete("/{rule_id}", response_model=dict[str, Any])
def delete_rule(rule_id: str) -> dict[str, Any]:
    """Remove a codified rule from the active catalog."""
    if rule_id.upper().startswith("FEI-"):
        raise HTTPException(
            status_code=403,
            detail=f"Cannot delete baseline Olympic FEI regulation '{rule_id}'. Baseline regulatory rules are protected.",
        )

    rules = load_catalog_rules()
    initial_len = len(rules)
    rules = [r for r in rules if r.get("rule_id", "").upper() != rule_id.upper()]
    if len(rules) == initial_len:
        raise HTTPException(status_code=404, detail=f"Rule '{rule_id}' not found in catalog.")

    save_catalog_rules(rules)
    logger.info("Deleted rule: %s", rule_id)
    return {"deleted": True, "rule_id": rule_id.upper()}


@router.post("/search", response_model=list[RuleChunk])
def search_regulations(req: RuleSearchRequest) -> list[RuleChunk]:
    """Perform ad-hoc hybrid semantic search across FEI regulations and Brand SOPs."""
    return retriever.retrieve_rules(
        query=req.query,
        discipline=req.discipline,
        top_k=req.top_k,
    )
