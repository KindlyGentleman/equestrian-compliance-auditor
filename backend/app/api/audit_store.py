"""Thread-safe persistent audit storage for tech pack scorecards and specifications."""
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone

from backend.app.core.config import settings
from backend.app.models.audit import AuditScorecard
from backend.app.models.tech_pack import TechPackSpec

logger = logging.getLogger(__name__)


class AuditRecord:
    def __init__(
        self,
        audit_id: str,
        scorecard: AuditScorecard,
        spec: TechPackSpec,
        pdf_path: Optional[str] = None,
        created_at: Optional[str] = None,
    ):
        self.audit_id = audit_id
        self.scorecard = scorecard
        self.spec = spec
        self.pdf_path = pdf_path
        self.created_at = created_at or datetime.now(timezone.utc).isoformat()

    def to_summary(self) -> Dict[str, Any]:
        return {
            "audit_id": self.audit_id,
            "tech_pack_id": self.scorecard.tech_pack_id,
            "style_code": self.scorecard.style_code,
            "style_name": self.scorecard.style_name,
            "discipline": self.scorecard.discipline.value,
            "garment_type": self.scorecard.garment_type.value,
            "overall_status": self.scorecard.overall_status.value,
            "overall_score_pct": self.scorecard.overall_score_pct,
            "created_at": self.created_at,
            "issue_count": len(self.scorecard.findings),
            "execution_time_seconds": self.scorecard.execution_time_seconds,
        }


class AuditStore:
    """Manages in-memory and file-backed audit state."""

    def __init__(self, storage_dir: Optional[str] = None):
        self.storage_dir = Path(storage_dir or settings.CACHE_DIR) / "audits"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self._records: Dict[str, AuditRecord] = {}
        self._load_existing()

    def _load_existing(self) -> None:
        """Load cached audit records from disk."""
        for json_file in self.storage_dir.glob("*.json"):
            try:
                data = json.loads(json_file.read_text(encoding="utf-8"))
                aid = data.get("audit_id")
                sc = AuditScorecard.model_validate(data["scorecard"])
                sp = TechPackSpec.model_validate(data["spec"])
                self._records[aid] = AuditRecord(
                    audit_id=aid,
                    scorecard=sc,
                    spec=sp,
                    pdf_path=data.get("pdf_path"),
                    created_at=data.get("created_at"),
                )
            except Exception as exc:
                logger.warning("Failed to load audit file %s (%s)", json_file, exc)

    def save(self, record: AuditRecord) -> None:
        """Save audit record to memory and JSON file."""
        self._records[record.audit_id] = record
        json_file = self.storage_dir / f"{record.audit_id}.json"
        try:
            payload = {
                "audit_id": record.audit_id,
                "scorecard": record.scorecard.model_dump(),
                "spec": record.spec.model_dump(),
                "pdf_path": record.pdf_path,
                "created_at": record.created_at,
            }
            json_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        except Exception as exc:
            logger.error("Failed to write audit file %s (%s)", json_file, exc)

    def get(self, audit_id: str) -> Optional[AuditRecord]:
        return self._records.get(audit_id)

    def list_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        records = sorted(
            self._records.values(),
            key=lambda r: r.created_at,
            reverse=True,
        )
        return [r.to_summary() for r in records[:limit]]


audit_store = AuditStore()
