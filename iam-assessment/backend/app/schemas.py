from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field


class AssessmentCreate(BaseModel):
    name: str = "Draft Assessment"
    scope: dict[str, Any] = Field(default_factory=dict)


class AssessmentItemUpdate(BaseModel):
    status: Optional[str] = None
    score: Optional[int] = None
    finding_text: Optional[str] = None
    evidence_refs: Optional[list[str]] = None
    assessor_notes: Optional[str] = None


class AssessmentItemOut(BaseModel):
    control_id: str
    domain: str
    weight: int
    status: str
    score: Optional[int] = None
    finding_text: str
    evidence_refs: list[str]
    assessor_notes: str
    control: dict[str, Any]


class AssessmentOut(BaseModel):
    id: str
    name: str
    created_at: datetime
    assessed_at: Optional[datetime] = None
    registry_hash: str
    scope: dict[str, Any]
    items: list[AssessmentItemOut]


class AssessmentListOut(BaseModel):
    id: str
    name: str
    created_at: datetime
    registry_hash: str


class ReportOut(BaseModel):
    registry_hash: str
    assessed_at: Optional[datetime] = None
    summary: dict[str, Any]
    domains: list[dict[str, Any]]
    top_risks: list[dict[str, Any]]

