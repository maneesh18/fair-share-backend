"""Ledger service - maintains balances between users."""
from uuid import UUID
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.expense import Expense, ExpenseSplit
from app.models.ledger import LedgerBalance


def _get_or_create_balance(db: Session, group_id: UUID, from_user: UUID, to_user: UUID) -> LedgerBalance:
    row = db.query(LedgerBalance).filter(
        LedgerBalance.group_id == group_id,
        LedgerBalance.from_user_id == from_user,
        LedgerBalance.to_user_id == to_user,
    ).first()
    if row:
        return row
    row = LedgerBalance(group_id=group_id, from_user_id=from_user, to_user_id=to_user, amount=Decimal("0"))
    db.add(row)
    db.flush()
    return row


def update_ledger_on_expense(db: Session, expense_id: UUID) -> None:
    """Update ledger balances when an expense is created/updated.
    Payer is created_by. Each split user owes the payer their share.
    Net: payer paid total; each split user owes their amount.
    We track: from_user owes to_user.
    So: split_user owes payer -> from_user=split_user, to_user=payer, amount=split.amount
    """
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        return
    payer = expense.created_by
    for split in expense.splits:
        if split.user_id == payer:
            continue
        bal = _get_or_create_balance(db, expense.group_id, split.user_id, payer)
        bal.amount = (bal.amount or Decimal("0")) + split.amount
    # Optimize: net opposite direction to reduce entries
    _optimize_ledger(db, expense.group_id)
    db.commit()


def _optimize_ledger(db: Session, group_id: UUID) -> None:
    """Net opposite balances between same pair (A->B and B->A)."""
    rows = db.query(LedgerBalance).filter(LedgerBalance.group_id == group_id).all()
    for r in rows:
        if (r.amount or 0) <= 0:
            continue
        opp = db.query(LedgerBalance).filter(
            LedgerBalance.group_id == group_id,
            LedgerBalance.from_user_id == r.to_user_id,
            LedgerBalance.to_user_id == r.from_user_id,
        ).first()
        if not opp:
            continue
        opp_amt = opp.amount or Decimal("0")
        if opp_amt <= 0:
            continue
        diff = min(r.amount, opp_amt)
        r.amount -= diff
        opp.amount -= diff
        if (r.amount or 0) <= 0:
            r.amount = Decimal("0")
        if (opp.amount or 0) <= 0:
            opp.amount = Decimal("0")


def get_balances(db: Session, group_id: UUID) -> list[LedgerBalance]:
    """Return non-zero balances for the group."""
    return db.query(LedgerBalance).filter(
        LedgerBalance.group_id == group_id,
        LedgerBalance.amount > 0,
    ).all()
