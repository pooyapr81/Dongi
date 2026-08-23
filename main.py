from database import engine, Base
import models

Base.metadata.create_all(bind=engine)

print("Database Created Successfully")


import os
from telegram.ext import MessageHandler, filters
from handlers.expense import expense_handler
from handlers.message import message_handler
from dotenv import load_dotenv
from handlers.balance import balance
from handlers.settle import settle_handler
from handlers.me import me
from telegram.ext import (
    Application,
    CommandHandler
)
from handlers.report import (
    report_handler
)
from handlers.expenses import (
    expenses_handler,
    expense_detail_handler,
    delete_expense_handler
)
from handlers.help import (
    help_handler
)
from handlers.start import start
from telegram_commands import (
    setup_commands
)

# Load environment variables
load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
PROXY = os.getenv("PROXY")


if not TOKEN:
    raise ValueError("BOT_TOKEN is not set in .env")


from telegram_commands import setup_commands

app = (
    Application.builder()
    .token(TOKEN)
    #.proxy(PROXY)
    #.get_updates_proxy(PROXY)
    .post_init(setup_commands)
    .build()
)


# Commands

app.add_handler(
    CommandHandler("start", start)
)
app.add_handler(expense_handler)
app.add_handler(
    CommandHandler(
        "balance",
        balance
    )
)
app.add_handler(settle_handler)
app.add_handler(
    CommandHandler(
        "me",
        me
    )
)
app.add_handler(expenses_handler)

app.add_handler(expenses_handler)

app.add_handler(expense_detail_handler)

app.add_handler(delete_expense_handler)
app.add_handler(
    report_handler
)
app.add_handler(
    help_handler
)
app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        message_handler
    )
)

print("🚀 Dongi Bot Started...")


app.run_polling()