"""Trust scores router."""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.user import User
from app.models.group import GroupMember
from app.schemas.trust import TrustScoresResponse, TrustScoreItem
from app.modules.groups.service import is_member
from app.modules.auth.dependencies import get_current_user

router = APIRouter(tags=["trust"])


@router.get("/groups/{group_id}/trust", response_model=TrustScoresResponse)
def get_trust_scores(
    group_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if not is_member(db, group_id, user.id):
        raise HTTPException(status_code=403, detail="Not a member of this group")
    members = db.query(GroupMember).filter(GroupMember.group_id == group_id).order_by(GroupMember.trust_score.desc()).all()
    from app.models.user import User as UserModel
    users = {u.id: u for u in db.query(UserModel).filter(UserModel.id.in_([m.user_id for m in members])).all()}
    scores = []
    for i, m in enumerate(members):
        u = users.get(m.user_id)
        scores.append(TrustScoreItem(
            user_id=m.user_id,
            name=u.name if u else None,
            trust_score=m.trust_score,
            rank=i + 1,
        ))
    return TrustScoresResponse(group_id=group_id, scores=scores)
