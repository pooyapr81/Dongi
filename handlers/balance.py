from telegram import Update
from telegram.ext import ContextTypes

from database import SessionLocal

from models import (
    Group,
    Expense,
    User
)

from services.balance_service import (
    calculate_balances,
    simplify_balances
)


async def balance(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
):

    db = SessionLocal()

    try:

        chat_id = update.effective_chat.id


        # پیدا کردن گروه
        group = (
            db.query(Group)
            .filter(
                Group.telegram_chat_id == chat_id
            )
            .first()
        )


        if not group:

            await update.message.reply_text(
                "❌ این گروه ثبت نشده است."
            )

            return



        # گرفتن هزینه‌های گروه
        expenses = (
            db.query(Expense)
            .filter(
                Expense.group_id == group.id
            )
            .all()
        )


        if not expenses:

            await update.message.reply_text(
                "📌 هنوز هزینه‌ای ثبت نشده است."
            )

            return



        # محاسبه تراز کاربران
        balances = calculate_balances(
            expenses,
            db
        )


        # ساده سازی بدهی‌ها
        payments = simplify_balances(
            balances
        )


        if not payments:

            await update.message.reply_text(
                "✅ همه حساب‌ها تسویه است."
            )

            return



        result = []


        for payment in payments:


            debtor = (
                db.query(User)
                .filter(
                    User.id ==
                    payment["from"]
                )
                .first()
            )


            creditor = (
                db.query(User)
                .filter(
                    User.id ==
                    payment["to"]
                )
                .first()
            )


            result.append(
                f" {debtor.full_name} "
                f"➡️ {creditor.full_name}\n"
                f"مبلغ: {payment['amount']:,}"
            )



        await update.message.reply_text(
            "📊 وضعیت حساب‌ها:\n\n"
            +
            "\n\n".join(result)
        )


    except Exception as e:

        print(
            "Balance Error:",
            e
        )


        await update.message.reply_text(
            "❌ خطا در محاسبه حساب‌ها"
        )


    finally:

        db.close()