"""Receipts service."""
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.receipt import Receipt
from app.models.expense import Expense
from app.schemas.receipt import ReceiptCreate


def add_receipt(db: Session, expense_id: UUID, data: ReceiptCreate, uploaded_by: UUID) -> Receipt | None:
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        return None
    receipt = Receipt(
        expense_id=expense_id,
        image_url=data.image_url,
        uploaded_by=uploaded_by,
    )
    db.add(receipt)
    db.commit()
    db.refresh(receipt)
    return receipt


def get_receipts_for_expense(db: Session, expense_id: UUID) -> list[Receipt]:
    return db.query(Receipt).filter(Receipt.expense_id == expense_id).all()
