"""Receipts router."""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.user import User
from app.schemas.receipt import ReceiptCreate, ReceiptResponse
from app.modules.receipts.service import add_receipt
from app.modules.groups.service import is_member
from app.models.expense import Expense
from app.modules.auth.dependencies import get_current_user

router = APIRouter(prefix="/expenses", tags=["receipts"])


@router.post("/{expense_id}/receipt", response_model=ReceiptResponse)
def upload_receipt(
    expense_id: UUID,
    data: ReceiptCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    if not is_member(db, expense.group_id, user.id):
        raise HTTPException(status_code=403, detail="Not a member of this group")
    receipt = add_receipt(db, expense_id, data, user.id)
    if not receipt:
        raise HTTPException(status_code=404, detail="Expense not found")
    return receipt
