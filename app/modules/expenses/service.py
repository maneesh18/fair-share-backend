"""Expenses service."""
from uuid import UUID
from decimal import Decimal
from sqlalchemy.orm import Session
from app.models.expense import Expense, ExpenseSplit
from app.models.group import GroupMember
from app.schemas.expense import ExpenseCreate, ExpenseUpdate
from app.services.ledger import update_ledger_on_expense
from app.workers.tasks import recalc_trust_score_task


def create_expense(db: Session, data: ExpenseCreate, created_by: UUID) -> Expense:
    total = sum(s.amount for s in data.splits)
    if abs(total - data.total_amount) > Decimal("0.01"):
        raise ValueError("Split amounts must sum to total amount")
    expense = Expense(
        group_id=data.group_id,
        created_by=created_by,
        total_amount=data.total_amount,
        currency=data.currency,
        category=data.category,
        description=data.description,
    )
    db.add(expense)
    db.commit()
    db.refresh(expense)
    for s in data.splits:
        split = ExpenseSplit(expense_id=expense.id, user_id=s.user_id, amount=s.amount)
        db.add(split)
    db.commit()
    update_ledger_on_expense(db, expense.id)
    recalc_trust_score_task.delay(str(data.group_id))
    return expense


def get_expense(db: Session, expense_id: UUID) -> Expense | None:
    return db.query(Expense).filter(Expense.id == expense_id).first()


def get_group_expenses(db: Session, group_id: UUID) -> list[Expense]:
    return db.query(Expense).filter(Expense.group_id == group_id).order_by(Expense.created_at.desc()).all()


def update_expense(db: Session, expense_id: UUID, data: ExpenseUpdate, user_id: UUID) -> Expense | None:
    expense = get_expense(db, expense_id)
    if not expense or expense.created_by != user_id:
        return None
    if data.total_amount is not None:
        expense.total_amount = data.total_amount
    if data.category is not None:
        expense.category = data.category
    if data.description is not None:
        expense.description = data.description
    if data.splits is not None:
        db.query(ExpenseSplit).filter(ExpenseSplit.expense_id == expense_id).delete()
        total = sum(s.amount for s in data.splits)
        if abs(total - expense.total_amount) > Decimal("0.01"):
            raise ValueError("Split amounts must sum to total amount")
        for s in data.splits:
            split = ExpenseSplit(expense_id=expense_id, user_id=s.user_id, amount=s.amount)
            db.add(split)
    db.commit()
    db.refresh(expense)
    update_ledger_on_expense(db, expense.id)
    recalc_trust_score_task.delay(str(expense.group_id))
    return expense
