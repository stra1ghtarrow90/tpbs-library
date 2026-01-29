import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


class Assessment(Base):
    __tablename__ = "assessments"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String, default="Draft Assessment")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    assessed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    registry_hash: Mapped[str] = mapped_column(String)
    scope: Mapped[dict] = mapped_column(JSONB, default=dict)

    items: Mapped[list["AssessmentItem"]] = relationship(
        "AssessmentItem",
        back_populates="assessment",
        cascade="all, delete-orphan",
    )


class AssessmentItem(Base):
    __tablename__ = "assessment_items"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    assessment_id: Mapped[str] = mapped_column(ForeignKey("assessments.id"))
    control_id: Mapped[str] = mapped_column(String, index=True)
    domain: Mapped[str] = mapped_column(String, index=True)
    weight: Mapped[int] = mapped_column(Integer)

    status: Mapped[str] = mapped_column(String, default="not_assessed")
    score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    finding_text: Mapped[str] = mapped_column(Text, default="")
    evidence_refs: Mapped[list[str]] = mapped_column(JSONB, default=list)
    assessor_notes: Mapped[str] = mapped_column(Text, default="")

    control_raw: Mapped[dict] = mapped_column(JSONB, default=dict)

    assessment: Mapped[Assessment] = relationship("Assessment", back_populates="items")

