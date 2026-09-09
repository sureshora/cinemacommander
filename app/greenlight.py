from __future__ import annotations
from dataclasses import asdict, dataclass, field
from typing import Any

@dataclass
class ApprovalCondition:
    condition: str
    priority: str = "HIGH"

@dataclass
class GreenlightDecision:
    decision: str
    score: int
    confidence: float
    blockers: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    approval_conditions: list[ApprovalCondition] = field(default_factory=list)
    evidence_gaps: list[str] = field(default_factory=list)
    recommended_action: str = ""

    def to_dict(self):
        return {
            "decision": self.decision,
            "score": self.score,
            "confidence": self.confidence,
            "blockers": self.blockers,
            "warnings": self.warnings,
            "approval_conditions": [asdict(x) for x in self.approval_conditions],
            "evidence_gaps": self.evidence_gaps,
            "recommended_action": self.recommended_action,
        }


def decide_greenlight(
    risk: dict[str, Any],
    schedule: dict[str, Any],
    limitations: list[str] | None = None,
) -> GreenlightDecision:
    limitations = limitations or []
    blockers: list[str] = []
    warnings: list[str] = []
    conditions: list[ApprovalCondition] = []

    for r in risk.get("risks", []):
        severity = str(r.get("severity", "")).upper()
        title = r.get("title", "Material production risk")
        if severity == "CRITICAL":
            blockers.append(title)
        elif severity in {"HIGH", "MEDIUM"}:
            warnings.append(title)

    schedule_status = str(schedule.get("status", ""))
    if schedule_status == "CONFLICT":
        blockers.append("Schedule conflict")
    elif schedule_status == "INSUFFICIENT_EVIDENCE":
        warnings.append("Schedule evidence gap")

    if limitations:
        warnings.extend(limitations)

    # A material risk is not automatically a stop condition. A production can
    # proceed when risks are mitigable and the deterministic schedule is feasible.
    if blockers:
        decision = "BLOCKED"
        score = 20
        confidence = 0.87
        action = "Resolve blocking production constraints before shooting."
    elif schedule_status == "FEASIBLE":
        decision = "GREENLIGHT"
        score = 87
        confidence = 0.87
        action = "Proceed with production after completing the listed approval conditions."
    else:
        decision = "WARNING"
        score = 68
        confidence = 0.87
        action = "Proceed only after the listed verification conditions are satisfied."

    if warnings:
        conditions.append(
            ApprovalCondition(
                "Verify permits, access, operating-hour, safety, and logistics conditions before call time."
            )
        )

    return GreenlightDecision(
        decision,
        score,
        confidence,
        blockers,
        warnings,
        conditions,
        limitations,
        action,
    )


def greenlight_engine_tool(
    objective: str,
    risk_assessment: dict[str, Any],
    schedule_plan: dict[str, Any],
    intelligence_limitations: list[str] | None = None,
) -> dict[str, Any]:
    return decide_greenlight(
        risk_assessment,
        schedule_plan,
        intelligence_limitations,
    ).to_dict()
