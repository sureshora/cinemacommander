"""Minimal evidence/trace primitives shared by the UI demo."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from hashlib import sha256
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class EvidenceRecord:
    evidence_id: str
    source_url: str
    title: str = ""
    snippet: str = ""
    category: str = "GENERAL"
    confidence: float = 0.0
    retrieved_at: str = field(default_factory=utc_now)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class TraceEvent:
    sequence: int
    event_type: str
    actor: str
    timestamp: str
    execution_id: str
    summary: str
    evidence_ids: list[str] = field(default_factory=list)
    data: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class EvidenceTrace:
    def __init__(self, execution_id: str):
        self.execution_id = execution_id
        self._events: list[TraceEvent] = []
        self._evidence: dict[str, EvidenceRecord] = {}

    @staticmethod
    def evidence_id(source_url: str, title: str = "") -> str:
        digest = sha256(f"{source_url}|{title}".encode()).hexdigest()[:12]
        return f"EVD-{digest}"

    def add_evidence(self, source_url: str, title: str = "", snippet: str = "",
                     category: str = "GENERAL", confidence: float = 0.0) -> EvidenceRecord:
        item = EvidenceRecord(
            self.evidence_id(source_url, title), source_url, title, snippet,
            category, max(0.0, min(1.0, confidence))
        )
        self._evidence[item.evidence_id] = item
        return item

    def add_event(self, event_type: str, actor: str, summary: str,
                  evidence_ids: list[str] | None = None,
                  data: dict[str, Any] | None = None) -> TraceEvent:
        event = TraceEvent(
            len(self._events) + 1, event_type, actor, utc_now(),
            self.execution_id, summary, evidence_ids or [], data or {}
        )
        self._events.append(event)
        return event

    def export(self) -> dict[str, Any]:
        known = set(self._evidence)
        missing = sorted({
            eid for event in self._events for eid in event.evidence_ids
            if eid not in known
        })
        return {
            "execution_id": self.execution_id,
            "event_count": len(self._events),
            "evidence_count": len(self._evidence),
            "trace_integrity": "VALID" if not missing else "BROKEN",
            "missing_evidence_ids": missing,
            "events": [x.to_dict() for x in self._events],
            "evidence": [x.to_dict() for x in self._evidence.values()],
        }
