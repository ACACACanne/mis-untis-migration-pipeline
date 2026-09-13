from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.quarantine import QuarantineItem
from app.schemas.quarantine import (
    QuarantineItemResponse,
    QuarantineResolutionPayload,
    QuarantineSummaryStats,
)
from app.pipeline.quarantine.resolver import QuarantineResolver

router = APIRouter()


@router.get("", response_model=List[QuarantineItemResponse])
def list_quarantine_items(
    status_filter: Optional[str] = Query(None, regex="^(PENDING|RESOLVED|IGNORED)$"),
    db: Session = Depends(get_db),
) -> List[QuarantineItem]:
    query = db.query(QuarantineItem)
    if status_filter:
        query = query.filter(QuarantineItem.status == status_filter.upper())
    return query.order_by(QuarantineItem.created_at.desc()).all()


@router.get("/summary", response_model=QuarantineSummaryStats)
def get_quarantine_summary(db: Session = Depends(get_db)) -> Dict[str, int]:
    total = db.query(QuarantineItem).count()
    pending = db.query(QuarantineItem).filter(QuarantineItem.status == "PENDING").count()
    resolved = db.query(QuarantineItem).filter(QuarantineItem.status == "RESOLVED").count()
    ignored = db.query(QuarantineItem).filter(QuarantineItem.status == "IGNORED").count()

    return {
        "total_quarantined": total,
        "pending_count": pending,
        "resolved_count": resolved,
        "ignored_count": ignored,
    }


@router.patch("/{item_id}/resolve", response_model=QuarantineItemResponse)
def resolve_quarantine_entry(
    item_id: int,
    payload: QuarantineResolutionPayload,
    db: Session = Depends(get_db),
) -> QuarantineItem:
    resolver = QuarantineResolver(db)
    resolved = resolver.resolve_item(
        item_id=item_id,
        status=payload.status,
        override_data=payload.resolved_override,
    )
    if not resolved:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Quarantine record #{item_id} not found.",
        )
    return resolved