from telegram import BotCommand


async def setup_commands(app):
    commands = [
        BotCommand("expense", "ثبت هزینه"),
        BotCommand("balance", "نمایش بدهی‌ها"),
        BotCommand("settle", "ثبت تسویه"),
        BotCommand("expenses", "هزینه‌ها"),
        BotCommand("report", "گزارش"),
        BotCommand("help", "راهنما"),
    ]

    await app.bot.set_my_commands(commands)