# from telegram import Update
# from telegram.ext import ContextTypes
#
# from database import SessionLocal
# from models import User
#
#
# async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
#
#     telegram_user = update.effective_user
#
#     db = SessionLocal()
#
#     user = db.query(User).filter(
#         User.telegram_user_id == telegram_user.id
#     ).first()
#
#     if not user:
#         user = User(
#             telegram_user_id=telegram_user.id,
#             username=telegram_user.username,
#             full_name=telegram_user.full_name
#         )
#
#         db.add(user)
#         db.commit()
#
#         message = "✅ شما در Dongi ثبت شدید"
#
#     else:
#         message = "👋 خوش آمدید، شما قبلاً ثبت شده‌اید"
#
#     db.close()
#
#     await update.message.reply_text(message)


from telegram import Update
from telegram.ext import ContextTypes

from database import SessionLocal
from services.user_service import ensure_user_in_group


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    db = SessionLocal()

    try:
        user, group = ensure_user_in_group(
            db,
            update.effective_user,
            update.effective_chat
        )

        await update.message.reply_text(
            f"سلام {user.full_name} 👋\n"
            "✅ Dongi شما را ثبت کرد."
        )

    except Exception as e:
        await update.message.reply_text(
            "❌ خطایی در ثبت اطلاعات رخ داد."
        )
        print(e)

    finally:
        db.close()