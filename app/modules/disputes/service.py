"""Disputes service."""
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.dispute import ExpenseDispute
from app.models.expense import Expense
from app.schemas.dispute import DisputeCreate
from app.workers.tasks import recalc_trust_score_task


def create_dispute(db: Session, expense_id: UUID, data: DisputeCreate, raised_by: UUID) -> ExpenseDispute | None:
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        return None
    dispute = ExpenseDispute(
        expense_id=expense_id,
        raised_by=raised_by,
        reason=data.reason,
    )
    db.add(dispute)
    expense.status = "disputed"
    db.commit()
    db.refresh(dispute)
    recalc_trust_score_task.delay(str(expense.group_id))
    return dispute


def get_disputes_for_expense(db: Session, expense_id: UUID) -> list[ExpenseDispute]:
    return db.query(ExpenseDispute).filter(ExpenseDispute.expense_id == expense_id).all()
