from telegram import Update
from telegram.ext import ContextTypes

from database import SessionLocal
from services.user_service import ensure_user_in_group

async def message_handler(update, context):

    print("MESSAGE RECEIVED")

    if not update.message:
        return
# async def message_handler(
#     update: Update,
#     context: ContextTypes.DEFAULT_TYPE
# ):

    # اگر پیام واقعی نبود
    if not update.message:
        return

    # فقط پیام‌های گروه
    chat = update.effective_chat

    if chat.type not in ["group", "supergroup"]:
        return

    # اگر کاربر وجود نداشت ثبت شود
    db = SessionLocal()

    try:
        ensure_user_in_group(
            db,
            update.effective_user,
            chat
        )
        print(
            "REGISTERED:",
            update.effective_user.id,
            update.effective_user.full_name
        )

    except Exception as e:
        print("User register error:", e)

    finally:
        db.close()
