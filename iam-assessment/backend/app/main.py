from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select

from .db import SessionLocal, engine, Base
from .models import Assessment, AssessmentItem
from .schemas import (
    AssessmentCreate,
    AssessmentItemOut,
    AssessmentItemUpdate,
    AssessmentListOut,
    AssessmentOut,
    ReportOut,
)
from .registry import load_registry, registry_hash
from .reporting import build_report


app = FastAPI(title="IAM Assessment Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def _startup() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/registry")
def get_registry() -> dict[str, Any]:
    return load_registry()


@app.get("/assessments", response_model=list[AssessmentListOut])
def list_assessments() -> list[AssessmentListOut]:
    with SessionLocal() as session:
        rows = session.execute(select(Assessment).order_by(Assessment.created_at.desc())).scalars().all()
        return [
            AssessmentListOut(
                id=row.id,
                name=row.name,
                created_at=row.created_at,
                registry_hash=row.registry_hash,
            )
            for row in rows
        ]


@app.post("/assessments", response_model=AssessmentOut)
def create_assessment(payload: AssessmentCreate) -> AssessmentOut:
    registry = load_registry()
    reg_hash = registry_hash(registry)

    with SessionLocal() as session:
        assessment = Assessment(
            name=payload.name,
            registry_hash=reg_hash,
            scope=payload.scope,
        )
        session.add(assessment)
        session.flush()

        items: list[AssessmentItem] = []
        for control in sorted(registry.get("controls", []), key=lambda x: x["id"]):
            items.append(
                AssessmentItem(
                    assessment_id=assessment.id,
                    control_id=control["id"],
                    domain=control["domain"],
                    weight=control["weight"],
                    status="not_assessed",
                    score=None,
                    finding_text="",
                    evidence_refs=[],
                    assessor_notes="",
                    control_raw=control,
                )
            )
        session.add_all(items)
        session.commit()

        return _assessment_out(session, assessment.id)


@app.get("/assessments/{assessment_id}", response_model=AssessmentOut)
def get_assessment(assessment_id: str) -> AssessmentOut:
    with SessionLocal() as session:
        return _assessment_out(session, assessment_id)


@app.patch("/assessments/{assessment_id}/items/{control_id}", response_model=AssessmentItemOut)
def update_item(assessment_id: str, control_id: str, payload: AssessmentItemUpdate) -> AssessmentItemOut:
    with SessionLocal() as session:
        item = session.execute(
            select(AssessmentItem)
            .where(AssessmentItem.assessment_id == assessment_id)
            .where(AssessmentItem.control_id == control_id)
        ).scalar_one_or_none()
        if not item:
            raise HTTPException(status_code=404, detail="assessment item not found")

        updates = payload.model_dump(exclude_unset=True)
        if "status" in updates:
            item.status = updates["status"]
        if "score" in updates:
            item.score = updates["score"]
        if "finding_text" in updates:
            item.finding_text = updates["finding_text"]
        if "evidence_refs" in updates:
            item.evidence_refs = updates["evidence_refs"]
        if "assessor_notes" in updates:
            item.assessor_notes = updates["assessor_notes"]

        if item.status == "assessed":
            item_updated = datetime.now(timezone.utc)
            assessment = session.get(Assessment, assessment_id)
            if assessment:
                assessment.assessed_at = item_updated

        session.commit()

        return _item_out(item)


@app.get("/assessments/{assessment_id}/report", response_model=ReportOut)
def get_report(assessment_id: str) -> ReportOut:
    registry = load_registry()
    reg_hash = registry_hash(registry)

    with SessionLocal() as session:
        assessment = session.get(Assessment, assessment_id)
        if not assessment:
            raise HTTPException(status_code=404, detail="assessment not found")
        if assessment.registry_hash != reg_hash:
            raise HTTPException(
                status_code=400,
                detail="registry_hash mismatch between assessment and current controls.json",
            )

        items = (
            session.execute(
                select(AssessmentItem)
                .where(AssessmentItem.assessment_id == assessment_id)
                .order_by(AssessmentItem.control_id)
            )
            .scalars()
            .all()
        )

        assessment_payload = {
            "id": assessment.id,
            "name": assessment.name,
            "created_at": assessment.created_at,
            "assessed_at": assessment.assessed_at,
            "registry_hash": assessment.registry_hash,
            "scope": assessment.scope,
            "items": [_item_out(item).model_dump() for item in items],
        }

        return build_report(registry, assessment_payload)


def _item_out(item: AssessmentItem) -> AssessmentItemOut:
    return AssessmentItemOut(
        control_id=item.control_id,
        domain=item.domain,
        weight=item.weight,
        status=item.status,
        score=item.score,
        finding_text=item.finding_text or "",
        evidence_refs=item.evidence_refs or [],
        assessor_notes=item.assessor_notes or "",
        control=item.control_raw or {},
    )


def _assessment_out(session: Any, assessment_id: str) -> AssessmentOut:
    assessment = session.get(Assessment, assessment_id)
    if not assessment:
        raise HTTPException(status_code=404, detail="assessment not found")

    items = (
        session.execute(
            select(AssessmentItem)
            .where(AssessmentItem.assessment_id == assessment_id)
            .order_by(AssessmentItem.control_id)
        )
        .scalars()
        .all()
    )
    return AssessmentOut(
        id=assessment.id,
        name=assessment.name,
        created_at=assessment.created_at,
        assessed_at=assessment.assessed_at,
        registry_hash=assessment.registry_hash,
        scope=assessment.scope,
        items=[_item_out(item) for item in items],
    )

