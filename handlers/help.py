from telegram import Update
from telegram.ext import (
    ContextTypes,
    CommandHandler
)


async def help_command(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
):

    text = """
📚 راهنمای ربات دونگی

/start
ثبت کاربر در سیستم

/expense
ثبت هزینه جدید

/balance
نمایش بدهی‌های گروه

/settle
ثبت تسویه حساب

/expenses
مشاهده هزینه‌های ثبت شده

/report
گزارش کلی گروه

/me
وضعیت شخصی شما

/help
نمایش این راهنما
"""

    await update.message.reply_text(text)


help_handler = CommandHandler(
    "help",
    help_command
)