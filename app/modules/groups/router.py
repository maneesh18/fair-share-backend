"""Groups router."""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.user import User
from app.models.group import GroupMember
from app.schemas.group import GroupCreate, GroupResponse, GroupMemberAdd, GroupMemberResponse, GroupMemberWithUser
from app.modules.groups.service import create_group, get_user_groups, add_member, get_group, is_member
from app.modules.auth.dependencies import get_current_user

router = APIRouter(prefix="/groups", tags=["groups"])


@router.post("", response_model=GroupResponse)
def create(data: GroupCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return create_group(db, data, user.id)


@router.get("", response_model=list[GroupResponse])
def list_groups(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return get_user_groups(db, user.id)


@router.get("/{group_id}/members", response_model=list[GroupMemberWithUser])
def list_members(
    group_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if not is_member(db, group_id, user.id):
        raise HTTPException(status_code=403, detail="Not a member of this group")
    members = db.query(GroupMember).filter(GroupMember.group_id == group_id).all()
    result = []
    for m in members:
        u = db.query(User).filter(User.id == m.user_id).first()
        result.append(GroupMemberWithUser(
            id=m.id, user_id=m.user_id, role=m.role, trust_score=m.trust_score,
            joined_at=m.joined_at, name=u.name if u else None, email=u.email if u else None,
        ))
    return result


@router.post("/{group_id}/members", response_model=GroupMemberResponse)
def add_group_member(
    group_id: UUID,
    data: GroupMemberAdd,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    group = get_group(db, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    if not is_member(db, group_id, user.id):
        raise HTTPException(status_code=403, detail="Not a member of this group")
    return add_member(db, group_id, data)
