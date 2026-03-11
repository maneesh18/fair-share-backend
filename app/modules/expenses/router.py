"""Expenses router."""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.user import User
from app.schemas.expense import ExpenseCreate, ExpenseResponse, ExpenseUpdate
from app.modules.expenses.service import create_expense, get_group_expenses, get_expense, update_expense
from app.modules.groups.service import is_member
from app.modules.auth.dependencies import get_current_user

router = APIRouter(prefix="/expenses", tags=["expenses"])


@router.post("", response_model=ExpenseResponse)
def create(data: ExpenseCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if not is_member(db, data.group_id, user.id):
        raise HTTPException(status_code=403, detail="Not a member of this group")
    try:
        expense = create_expense(db, data, user.id)
        return expense
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/groups/{group_id}", response_model=list[ExpenseResponse])
def list_expenses(
    group_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if not is_member(db, group_id, user.id):
        raise HTTPException(status_code=403, detail="Not a member of this group")
    return get_group_expenses(db, group_id)
