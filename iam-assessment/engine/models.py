from pydantic import BaseModel, Field
from typing import Any, Dict, Literal

class Evidence(BaseModel):
    source: Literal["entra", "ad"]
    collected_at: str  # ISO UTC string
    artifacts: Dict[str, Any] = Field(default_factory=dict)
    facts: Dict[str, Any] = Field(default_factory=dict)

class ControlResult(BaseModel):
    control_id: str
    domain: str
    score: int  # 0/1/2
    finding: str
    evidence_refs: list[str] = Field(default_factory=list)

class Assessment(BaseModel):
    assessed_at: str
    registry_hash: str
    scope: Dict[str, Any] = Field(default_factory=dict)
    domain_scores: Dict[str, float] = Field(default_factory=dict)
    control_results: list[ControlResult] = Field(default_factory=list)
    overall_score: float
    top_risks: list[str] = Field(default_factory=list)
