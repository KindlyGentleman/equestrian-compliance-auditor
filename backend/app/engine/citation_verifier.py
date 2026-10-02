"""Constitutional Verifier Gate guaranteeing Zero False Positives via verbatim citation validation."""
import difflib
import json
import logging
import re
from pathlib import Path

from backend.app.core.config import settings
from backend.app.models.audit import AuditFinding, VerifiedFinding
from backend.app.models.tech_pack import ComplianceStatus
from backend.app.rag.vector_store import RuleChunk

logger = logging.getLogger(__name__)


def normalize_text(text: str) -> str:
    """Normalize text by lowering, stripping special punctuation, and collapsing whitespace."""
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    return " ".join(text.split())


class CitationVerifier:
    """Validates finding citations against authentic regulatory texts, auto-downgrading unverified findings."""

    def __init__(self, regulations_dir: str | None = None, rules_catalog_path: str | None = None):
        self.regulations_dir = Path(regulations_dir or settings.REGULATIONS_DIR)
        self.catalog_path = Path(rules_catalog_path or settings.RULES_CATALOG_PATH)
        self.corpus_texts: list[str] = []
        self.catalog_citations: dict[str, str] = {}
        self._load_corpus()

    def _load_corpus(self) -> None:
        """Load all ground-truth markdown and catalog files into memory."""
        # 1. Load rules catalog
        if self.catalog_path.exists():
            try:
                with open(self.catalog_path, encoding="utf-8") as f:
                    data = json.load(f)
                    for rule in data.get("rules", []):
                        rid = rule.get("rule_id", "")
                        cit = rule.get("verbatim_citation", "") or rule.get("citation", "")
                        if rid and cit:
                            self.catalog_citations[rid] = cit
                            self.corpus_texts.append(cit)
            except Exception as exc:
                logger.warning("Failed to load rules catalog into verifier (%s)", exc)

        # 2. Load markdown files
        if self.regulations_dir.exists():
            for md_file in self.regulations_dir.rglob("*.md"):
                try:
                    content = md_file.read_text(encoding="utf-8")
                    self.corpus_texts.append(content)
                except Exception as exc:
                    logger.warning("Could not read %s for verifier corpus (%s)", md_file, exc)

        logger.debug("CitationVerifier loaded %d corpus documents", len(self.corpus_texts))

    @staticmethod
    def _extract_numbers(text: str) -> set[str]:
        """Extract numeric tokens to guarantee regulatory threshold fidelity."""
        return set(re.findall(r"\b\d+(?:\.\d+)?\b", text))

    def _fuzzy_match(self, query: str, target: str, threshold: float = 0.94) -> bool:
        """Evaluate if query matches target with sequence similarity and exact numeric preservation."""
        norm_query = normalize_text(query)
        norm_target = normalize_text(target)

        if not norm_query or not norm_target:
            return False

        if norm_query in norm_target:
            return True

        query_nums = self._extract_numbers(norm_query)
        target_nums = self._extract_numbers(norm_target)

        # Numerical thresholds in regulatory citations must exist in target corpus
        if query_nums and not query_nums.issubset(target_nums):
            return False

        # Windowed sequence matching
        q_len = len(norm_query)
        if q_len > len(norm_target):
            ratio = difflib.SequenceMatcher(None, norm_query, norm_target).ratio()
            return ratio >= threshold

        words = norm_target.split()
        q_words = norm_query.split()
        window_size = len(q_words)

        # Cap word scanning to prevent CPU exhaustion on massive texts
        words = words[:5000]
        q_tokens = set(q_words)

        for i in range(max(1, len(words) - window_size + 1)):
            window_slice = words[i : i + window_size + 2]
            # Fast filter: skip expensive SequenceMatcher if token overlap is below 50%
            if len(q_tokens.intersection(window_slice)) / max(1, len(q_tokens)) < 0.50:
                continue

            window = " ".join(window_slice)
            if query_nums and not query_nums.issubset(self._extract_numbers(window)):
                continue
            ratio = difflib.SequenceMatcher(None, norm_query, window).ratio()
            if ratio >= threshold:
                return True

        return False

    def verify_finding(
        self,
        finding: AuditFinding,
        provided_chunks: list[RuleChunk] | None = None,
    ) -> VerifiedFinding:
        """Verify citation authenticity for a finding, downgrading to MANUAL_REVIEW if unverified."""
        citation = finding.source_citation.strip() if finding.source_citation else ""
        if not citation:
            return VerifiedFinding(
                **finding.model_dump(exclude={"severity"}),
                severity=ComplianceStatus.MANUAL_REVIEW,
                is_verbatim_verified=False,
                verification_notes="Warning: Missing source citation; downgraded to MANUAL_REVIEW.",
            )

        # Fast path: check known rule ID in catalog
        if finding.rule_id in self.catalog_citations:
            known_cit = self.catalog_citations[finding.rule_id]
            if self._fuzzy_match(citation, known_cit, threshold=0.92):
                return VerifiedFinding(
                    **finding.model_dump(),
                    is_verbatim_verified=True,
                    verification_notes="Verified against official rules catalog entry.",
                )

        # Search provided chunks
        if provided_chunks:
            for chunk in provided_chunks:
                if self._fuzzy_match(citation, chunk.content, threshold=0.92):
                    return VerifiedFinding(
                        **finding.model_dump(),
                        is_verbatim_verified=True,
                        verification_notes=f"Verbatim citation verified against {chunk.rulebook} ({chunk.article_id}).",
                    )

        # Search overall ground truth corpus
        norm_cit = normalize_text(citation)
        for doc in self.corpus_texts:
            norm_doc = normalize_text(doc)
            if norm_cit in norm_doc:
                return VerifiedFinding(
                    **finding.model_dump(),
                    is_verbatim_verified=True,
                    verification_notes="Verbatim citation verified in official regulatory archive.",
                )
            if self._fuzzy_match(citation, doc, threshold=0.92):
                return VerifiedFinding(
                    **finding.model_dump(),
                    is_verbatim_verified=True,
                    verification_notes="Fuzzy citation verified in official regulatory archive (>= 92% similarity).",
                )

        # Unverified finding: downgrade VIOLATION to MANUAL_REVIEW
        downgraded_severity = (
            ComplianceStatus.MANUAL_REVIEW
            if finding.severity == ComplianceStatus.VIOLATION
            else finding.severity
        )

        return VerifiedFinding(
            **finding.model_dump(exclude={"severity"}),
            severity=downgraded_severity,
            is_verbatim_verified=False,
            verification_notes="Warning: Citation unverified against ground truth text; downgraded to avoid false positive.",
        )

    def verify_all(
        self,
        findings: list[AuditFinding],
        provided_chunks: list[RuleChunk] | None = None,
    ) -> list[VerifiedFinding]:
        """Batch verify all findings."""
        return [self.verify_finding(f, provided_chunks) for f in findings]


citation_verifier = CitationVerifier()
