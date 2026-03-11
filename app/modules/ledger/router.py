"""Ledger router."""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.user import User
from app.schemas.ledger import LedgerBalancesResponse, BalanceItem
from app.services.ledger import get_balances
from app.modules.groups.service import is_member
from app.modules.auth.dependencies import get_current_user

router = APIRouter(tags=["ledger"])


@router.get("/groups/{group_id}/balances", response_model=LedgerBalancesResponse)
def get_group_balances(
    group_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if not is_member(db, group_id, user.id):
        raise HTTPException(status_code=403, detail="Not a member of this group")
    balances = get_balances(db, group_id)
    return LedgerBalancesResponse(
        group_id=group_id,
        balances=[BalanceItem(from_user_id=b.from_user_id, to_user_id=b.to_user_id, amount=b.amount, updated_at=b.updated_at) for b in balances],
    )
