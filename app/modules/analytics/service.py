"""Analytics service."""
from uuid import UUID
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.expense import Expense, ExpenseSplit
from app.models.group import GroupMember
from app.models.user import User
from app.models.dispute import ExpenseDispute
from app.models.analytics import AnalyticsSnapshot


def get_or_compute_analytics(db: Session, group_id: UUID, period: str = "all") -> dict:
    """Get analytics from snapshot or compute synchronously for MVP."""
    snap = db.query(AnalyticsSnapshot).filter(
        AnalyticsSnapshot.group_id == group_id,
        AnalyticsSnapshot.period == period,
    ).order_by(AnalyticsSnapshot.computed_at.desc()).first()
    if snap:
        return dict(snap.metrics_json)
    return compute_analytics(db, group_id, period)


def compute_analytics(db: Session, group_id: UUID, period: str = "all") -> dict:
    """Compute analytics metrics."""
    q = db.query(Expense).filter(Expense.group_id == group_id)
    expenses = q.all()

    total_spend = float(sum(e.total_amount or 0 for e in expenses))
    spend_by_user: dict[str, float] = {}
    spend_by_category: dict[str, float] = {}

    member_ids = [m.user_id for m in db.query(GroupMember).filter(GroupMember.group_id == group_id).all()]
    users = {u.id: u.name for u in db.query(User).filter(User.id.in_(member_ids)).all()} if member_ids else {}

    for e in expenses:
        cat = e.category or "Other"
        spend_by_category[cat] = spend_by_category.get(cat, 0) + float(e.total_amount or 0)
        for s in e.splits:
            uid = str(s.user_id)
            spend_by_user[uid] = spend_by_user.get(uid, 0) + float(s.amount or 0)

    spend_by_user_named = {users.get(k) or str(k): v for k, v in spend_by_user.items()}
    spend_by_category = {k: round(v, 2) for k, v in spend_by_category.items()}

    members = db.query(GroupMember).filter(GroupMember.group_id == group_id).order_by(GroupMember.trust_score.desc()).all()
    highest = members[0] if members else None
    lowest = members[-1] if members else None
    highest_trust = users.get(highest.user_id) if highest else None
    lowest_trust = users.get(lowest.user_id) if lowest else None

    dispute_counts: dict[UUID, int] = {}
    for d in db.query(ExpenseDispute).join(Expense, ExpenseDispute.expense_id == Expense.id).filter(Expense.group_id == group_id).all():
        exp = db.query(Expense).filter(Expense.id == d.expense_id).first()
        if exp:
            dispute_counts[exp.created_by] = dispute_counts.get(exp.created_by, 0) + 1
    most_disputed_id = max(dispute_counts.keys(), key=lambda k: dispute_counts[k]) if dispute_counts else None
    most_disputed = users.get(most_disputed_id) if most_disputed_id else None

    metrics = {
        "total_spend": round(total_spend, 2),
        "spend_by_user": spend_by_user_named,
        "spend_by_category": spend_by_category,
        "highest_trust_user": highest_trust,
        "lowest_trust_user": lowest_trust,
        "most_disputed_user": most_disputed,
    }
    snap = AnalyticsSnapshot(group_id=group_id, period=period, metrics_json=metrics)
    db.add(snap)
    db.commit()
    return metrics
