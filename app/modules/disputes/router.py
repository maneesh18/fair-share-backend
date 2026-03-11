"""Disputes router."""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.user import User
from app.schemas.dispute import DisputeCreate, DisputeResponse
from app.modules.disputes.service import create_dispute
from app.modules.groups.service import is_member
from app.models.expense import Expense
from app.modules.auth.dependencies import get_current_user

router = APIRouter(prefix="/expenses", tags=["disputes"])


@router.post("/{expense_id}/dispute", response_model=DisputeResponse)
def create(
    expense_id: UUID,
    data: DisputeCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    if not is_member(db, expense.group_id, user.id):
        raise HTTPException(status_code=403, detail="Not a member of this group")
    dispute = create_dispute(db, expense_id, data, user.id)
    if not dispute:
        raise HTTPException(status_code=404, detail="Expense not found")
    return dispute
