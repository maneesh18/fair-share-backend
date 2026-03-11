"""Trust score engine - recalculates trust scores based on behavior."""
from uuid import UUID
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.group import GroupMember
from app.models.expense import Expense, ExpenseSplit
from app.models.dispute import ExpenseDispute
from app.models.receipt import Receipt

DEFAULT_SCORE = Decimal("80")
MIN_SCORE = Decimal("0")
MAX_SCORE = Decimal("100")


def recalculate_trust_scores(db: Session, group_id: UUID) -> None:
    """Recalculate trust scores for all members in the group."""
    members = db.query(GroupMember).filter(GroupMember.group_id == group_id).all()
    for m in members:
        base = DEFAULT_SCORE
        # 1. Disputes raised against this user (expense creator)
        dispute_penalty = (
            db.query(func.count(ExpenseDispute.id))
            .join(Expense, ExpenseDispute.expense_id == Expense.id)
            .filter(
                Expense.group_id == group_id,
                Expense.created_by == m.user_id,
                ExpenseDispute.status == "open",
            )
            .scalar() or 0
        )
        base -= dispute_penalty * Decimal("5")

        # 2. Missing receipts (expenses without receipts)
        no_receipt_count = (
            db.query(func.count(Expense.id))
            .outerjoin(Receipt, Receipt.expense_id == Expense.id)
            .filter(
                Expense.group_id == group_id,
                Expense.created_by == m.user_id,
                Receipt.id.is_(None),
            )
            .scalar() or 0
        )
        base -= no_receipt_count * Decimal("2")

        # 3. Resolved disputes (creator corrected) - small boost
        resolved_against = (
            db.query(func.count(ExpenseDispute.id))
            .join(Expense, ExpenseDispute.expense_id == Expense.id)
            .filter(
                Expense.group_id == group_id,
                Expense.created_by == m.user_id,
                ExpenseDispute.status == "resolved",
            )
            .scalar() or 0
        )
        base += resolved_against * Decimal("1")

        # 4. Expense amount anomalies (simplified: very high amount vs avg)
        avg_amount = (
            db.query(func.avg(Expense.total_amount))
            .filter(Expense.group_id == group_id)
            .scalar() or Decimal("0")
        )
        anomaly_count = 0
        if avg_amount and avg_amount > 0:
            anomaly_count = (
                db.query(func.count(Expense.id))
                .filter(
                    Expense.group_id == group_id,
                    Expense.created_by == m.user_id,
                    Expense.total_amount > avg_amount * 3,
                )
                .scalar() or 0
            )
        base -= anomaly_count * Decimal("3")

        # 5. Uneven splits (simplified: one user gets >80% of total)
        uneven = 0
        for exp in db.query(Expense).filter(Expense.group_id == group_id, Expense.created_by == m.user_id).all():
            for s in exp.splits:
                if exp.total_amount and (s.amount or 0) / exp.total_amount > Decimal("0.8"):
                    uneven += 1
                    break
        base -= uneven * Decimal("4")

        score = max(MIN_SCORE, min(MAX_SCORE, base))
        m.trust_score = score
    db.commit()
