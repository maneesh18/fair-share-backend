"""Groups service."""
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.group import Group, GroupMember
from app.models.user import User
from app.schemas.group import GroupCreate, GroupMemberAdd
from app.models.group import MemberRole


def create_group(db: Session, data: GroupCreate, created_by: UUID) -> Group:
    group = Group(name=data.name, created_by=created_by)
    db.add(group)
    db.commit()
    db.refresh(group)
    # Add creator as admin member
    member = GroupMember(
        group_id=group.id,
        user_id=created_by,
        role=MemberRole.admin.value,
    )
    db.add(member)
    db.commit()
    return group


def get_user_groups(db: Session, user_id: UUID) -> list[Group]:
    return db.query(Group).join(GroupMember).filter(GroupMember.user_id == user_id).all()


def add_member(db: Session, group_id: UUID, data: GroupMemberAdd) -> GroupMember:
    member = GroupMember(group_id=group_id, user_id=data.user_id, role=MemberRole.member.value)
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


def get_group(db: Session, group_id: UUID) -> Group | None:
    return db.query(Group).filter(Group.id == group_id).first()


def is_member(db: Session, group_id: UUID, user_id: UUID) -> bool:
    return db.query(GroupMember).filter(
        GroupMember.group_id == group_id, GroupMember.user_id == user_id
    ).first() is not None
