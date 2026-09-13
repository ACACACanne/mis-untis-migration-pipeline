from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.key_registry import KeyRegistry

router = APIRouter()


class KeyRegistryCreatePayload(BaseModel):
    entity_type: str
    untis_id: str
    arbor_id: Optional[str] = None
    bromcom_id: Optional[str] = None
    short_code: Optional[str] = None
    display_name: Optional[str] = None


@router.get("", response_model=List[Dict[str, Any]])
def search_key_registry(
    entity_type: Optional[str] = Query(None),
    query: Optional[str] = Query(None),
    db: Session = Depends(get_db),
) -> List[Dict[str, Any]]:
    stmt = db.query(KeyRegistry)
    if entity_type:
        stmt = stmt.filter(KeyRegistry.entity_type == entity_type.lower())
    if query:
        stmt = stmt.filter(
            (KeyRegistry.untis_id.ilike(f"%{query}%"))
            | (KeyRegistry.display_name.ilike(f"%{query}%"))
            | (KeyRegistry.short_code.ilike(f"%{query}%"))
        )

    records = stmt.limit(100).all()
    return [
        {
            "id": r.id,
            "entity_type": r.entity_type,
            "untis_id": r.untis_id,
            "arbor_id": r.arbor_id,
            "bromcom_id": r.bromcom_id,
            "short_code": r.short_code,
            "display_name": r.display_name,
            "updated_at": r.updated_at,
        }
        for r in records
    ]


@router.post("", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
def create_key_mapping(
    payload: KeyRegistryCreatePayload,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    existing = (
        db.query(KeyRegistry)
        .filter(
            KeyRegistry.entity_type == payload.entity_type.lower(),
            KeyRegistry.untis_id == payload.untis_id,
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Mapping for {payload.entity_type} '{payload.untis_id}' already exists.",
        )

    mapping = KeyRegistry(
        entity_type=payload.entity_type.lower(),
        untis_id=payload.untis_id,
        arbor_id=payload.arbor_id,
        bromcom_id=payload.bromcom_id,
        short_code=payload.short_code,
        display_name=payload.display_name,
    )
    db.add(mapping)
    db.commit()
    db.refresh(mapping)

    return {"message": "Mapping registered successfully", "id": mapping.id}