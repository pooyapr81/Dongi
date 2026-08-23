from telegram import Update
from telegram.ext import (
    ContextTypes,
    CommandHandler
)

from database import SessionLocal

from models import (
    Group,
    User,
    Expense
)

from services.balance_service import (
    calculate_balances
)


async def report_command(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
):

    db = SessionLocal()

    try:

        chat_id = update.effective_chat.id

        group = (
            db.query(Group)
            .filter(
                Group.telegram_chat_id == chat_id
            )
            .first()
        )

        if not group:

            await update.message.reply_text(
                "❌ گروه پیدا نشد."
            )

            return

        expenses = (
            db.query(Expense)
            .filter(
                Expense.group_id == group.id
            )
            .all()
        )

        if not expenses:

            await update.message.reply_text(
                "📌 هنوز هزینه‌ای ثبت نشده."
            )

            return

        # -------------------------
        # کل هزینه ها
        # -------------------------

        total_expenses = sum(
            expense.amount
            for expense in expenses
        )

        expense_count = len(
            expenses
        )

        # -------------------------
        # پرداخت هر شخص
        # -------------------------

        paid_totals = {}

        for expense in expenses:

            paid_totals[
                expense.paid_by_user_id
            ] = (

                paid_totals.get(
                    expense.paid_by_user_id,
                    0
                )

                + expense.amount
            )

        max_paid_user = None
        max_paid_amount = 0

        min_paid_user = None
        min_paid_amount = None

        for user_id, amount in paid_totals.items():

            if amount > max_paid_amount:

                max_paid_amount = amount
                max_paid_user = user_id

            if (
                min_paid_amount is None
                or
                amount < min_paid_amount
            ):

                min_paid_amount = amount
                min_paid_user = user_id

        # -------------------------
        # بالانس ها
        # -------------------------

        balances = calculate_balances(
            expenses,
            db
        )

        max_creditor = None
        max_creditor_amount = 0

        max_debtor = None
        max_debtor_amount = 0

        for user_id, amount in balances.items():

            if amount > max_creditor_amount:

                max_creditor_amount = amount
                max_creditor = user_id

            if amount < 0:

                debt = abs(amount)

                if debt > max_debtor_amount:

                    max_debtor_amount = debt
                    max_debtor = user_id

        # -------------------------
        # نام افراد
        # -------------------------

        max_paid_name = "-"
        min_paid_name = "-"
        creditor_name = "-"
        debtor_name = "-"

        if max_paid_user:

            user = (
                db.query(User)
                .filter(
                    User.id == max_paid_user
                )
                .first()
            )

            if user:
                max_paid_name = (
                    user.full_name
                )

        if min_paid_user:

            user = (
                db.query(User)
                .filter(
                    User.id == min_paid_user
                )
                .first()
            )

            if user:
                min_paid_name = (
                    user.full_name
                )

        if max_creditor:

            user = (
                db.query(User)
                .filter(
                    User.id == max_creditor
                )
                .first()
            )

            if user:
                creditor_name = (
                    user.full_name
                )

        if max_debtor:

            user = (
                db.query(User)
                .filter(
                    User.id == max_debtor
                )
                .first()
            )

            if user:
                debtor_name = (
                    user.full_name
                )

        # -------------------------
        # خروجی
        # -------------------------

        text = ""

        text += "📊 گزارش گروه\n\n"

        text += (
            f"💰 کل هزینه‌ها:\n"
            f"{total_expenses:,} تومان\n\n"
        )

        text += (
            f"🧾 تعداد هزینه‌ها:\n"
            f"{expense_count}\n\n"
        )

        text += (
            f"🏆 بیشترین پرداخت:\n"
            f"{max_paid_name}\n"
            f"{max_paid_amount:,} تومان\n\n"
        )

        text += (
            f"📉 کمترین پرداخت:\n"
            f"{min_paid_name}\n"
            f"{min_paid_amount:,} تومان\n\n"
        )

        text += (
            f"💸 بیشترین بدهکار:\n"
            f"{debtor_name}\n"
            f"{max_debtor_amount:,} تومان\n\n"
        )

        text += (
            f"💵 بیشترین طلبکار:\n"
            f"{creditor_name}\n"
            f"{max_creditor_amount:,} تومان"
        )

        await update.message.reply_text(
            text
        )

    except Exception as e:

        print(
            "REPORT ERROR:",
            e
        )

        await update.message.reply_text(
            "❌ خطا در تولید گزارش."
        )

    finally:

        db.close()


report_handler = CommandHandler(
    "report",
    report_command
)