# backend/app/api/v1/endpoints/quarantine.py

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db, engine, Base
from app.models.quarantine import QuarantineItem

router = APIRouter()


@router.get("/summary", response_model=Dict[str, int])
def get_quarantine_summary(db: Session = Depends(get_db)):
    """
    Returns summary statistics for the quarantine queue.
    Guarded with a fallback to ensure the frontend never receives a 500.
    """
    try:
        total = db.query(QuarantineItem).count()
        pending = (
            db.query(QuarantineItem)
            .filter(QuarantineItem.status == "PENDING")
            .count()
        )
        resolved = (
            db.query(QuarantineItem)
            .filter(QuarantineItem.status == "RESOLVED")
            .count()
        )
        ignored = (
            db.query(QuarantineItem)
            .filter(QuarantineItem.status == "IGNORED")
            .count()
        )

        return {
            "total_quarantined": total,
            "pending_count": pending,
            "resolved_count": resolved,
            "ignored_count": ignored,
        }
    except Exception as exc:
        print(f"[Quarantine Summary Fallback]: {exc}")
        return {
            "total_quarantined": 0,
            "pending_count": 0,
            "resolved_count": 0,
            "ignored_count": 0,
        }


@router.get("", response_model=List[Dict[str, Any]])
def list_quarantine_items(
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Lists quarantined records filtered optionally by status."""
    try:
        query = db.query(QuarantineItem)
        if status:
            query = query.filter(QuarantineItem.status == status.upper())
        items = query.order_by(QuarantineItem.created_at.desc()).all()
        return [
            {
                "id": item.id,
                "sync_direction": item.sync_direction,
                "lesson_id": item.lesson_id,
                "entity_type": item.entity_type,
                "error_type": item.error_type,
                "details": item.details,
                "raw_payload": item.raw_payload,
                "status": item.status,
                "resolved_override": item.resolved_override,
                "created_at": item.created_at.isoformat() if item.created_at is not None else None,
            }
            for item in items
        ]
    except Exception as exc:
        print(f"[Quarantine List Fallback]: {exc}")
        return []


@router.get("/{item_id}")
def get_quarantine_item(item_id: int, db: Session = Depends(get_db)):
    """Retrieves a single quarantine record by ID."""
    item = db.query(QuarantineItem).filter(QuarantineItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Quarantine item not found")
    return item


@router.patch("/{item_id}/resolve")
def resolve_quarantine_item(
    item_id: int,
    override: Dict[str, Any],
    db: Session = Depends(get_db),
):
    """Applies resolution override payload and marks status as RESOLVED."""
    item = db.query(QuarantineItem).filter(QuarantineItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Quarantine item not found")

    setattr(item, "resolved_override", override)
    setattr(item, "status", "RESOLVED")
    db.commit()
    db.refresh(item)
    return {"status": "success", "item_id": item.id, "new_status": item.status}