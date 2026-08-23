from models import User, Group, GroupMember


def ensure_user_in_group(db, telegram_user, chat):
    """
    ثبت کاربر و عضویت در گروه در صورت نیاز
    """

    # ----------------------
    # 1. پیدا کردن یا ساخت User
    # ----------------------

    user = (
        db.query(User)
        .filter(
            User.telegram_user_id == telegram_user.id
        )
        .first()
    )

    if not user:
        user = User(
            telegram_user_id=telegram_user.id,
            username=telegram_user.username,
            full_name=telegram_user.full_name
        )

        db.add(user)
        db.commit()
        db.refresh(user)


    # ----------------------
    # 2. پیدا کردن یا ساخت Group
    # ----------------------

    group = (
        db.query(Group)
        .filter(
            Group.telegram_chat_id == chat.id
        )
        .first()
    )

    if not group:

        group = Group(
            telegram_chat_id=chat.id,
            group_name=chat.title or "Unknown"
        )

        db.add(group)
        db.commit()
        db.refresh(group)


    # ----------------------
    # 3. بررسی عضویت کاربر در گروه
    # ----------------------

    membership = (
        db.query(GroupMember)
        .filter(
            GroupMember.group_id == group.id,
            GroupMember.user_id == user.id
        )
        .first()
    )


    if not membership:

        membership = GroupMember(
            group_id=group.id,
            user_id=user.id
        )

        db.add(membership)
        db.commit()


    return user, group