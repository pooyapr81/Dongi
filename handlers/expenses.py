from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from telegram.ext import (
    ContextTypes,
    CommandHandler,
    CallbackQueryHandler
)

from database import SessionLocal

from models import (
    User,
    Group,
    Expense,
    ExpenseShare
)

async def expenses_command(
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
            .order_by(
                Expense.created_at.desc()
            )
            .limit(10)
            .all()
        )

        if not expenses:

            await update.message.reply_text(
                "📌 هنوز هزینه‌ای ثبت نشده."
            )
            return

        keyboard = []

        for expense in expenses:

            keyboard.append(
                [
                    InlineKeyboardButton(
                        f"{expense.title} - {expense.amount:,}",
                        callback_data=f"expense_{expense.id}"
                    )
                ]
            )

        await update.message.reply_text(
            "📋 آخرین هزینه‌های گروه",
            reply_markup=InlineKeyboardMarkup(
                keyboard
            )
        )

    finally:

        db.close()


async def expense_detail(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    db = SessionLocal()

    try:

        expense_id = int(
            query.data.replace(
                "expense_",
                ""
            )
        )

        expense = (
            db.query(Expense)
            .filter(
                Expense.id == expense_id
            )
            .first()
        )

        if not expense:

            await query.edit_message_text(
                "❌ هزینه پیدا نشد."
            )

            return

        payer = (
            db.query(User)
            .filter(
                User.id ==
                expense.paid_by_user_id
            )
            .first()
        )

        text = ""

        text += "📄 جزئیات هزینه\n\n"

        text += f"📝 عنوان: {expense.title}\n"
        text += f"💰 مبلغ: {expense.amount:,}\n\n"

        text += (
            f"👤 پرداخت کننده:\n"
            f"{payer.full_name}\n\n"
        )

        text += (
            f"📊 نوع تقسیم:\n"
            f"{expense.split_type}\n\n"
        )

        text += "👥 سهم افراد:\n\n"

        for share in expense.shares:

            user = (
                db.query(User)
                .filter(
                    User.id == share.user_id
                )
                .first()
            )

            text += (
                f"{user.full_name}: "
                f"{share.amount:,}\n"
            )

        keyboard = [
            [
                InlineKeyboardButton(
                    "🗑 حذف هزینه",
                    callback_data=f"delete_expense_{expense.id}"
                )
            ]
        ]

        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(
                keyboard
            )
        )

    finally:

        db.close()

async def delete_expense(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    db = SessionLocal()

    try:

        print("DELETE CLICKED")
        print("CALLBACK DATA =", query.data)

        expense_id = int(
            query.data.replace(
                "delete_expense_",
                ""
            )
        )

        print("EXPENSE ID =", expense_id)

        expense = (
            db.query(Expense)
            .filter(
                Expense.id == expense_id
            )
            .first()
        )

        print("EXPENSE =", expense)

        if not expense:

            await query.edit_message_text(
                "❌ هزینه پیدا نشد."
            )

            return

        current_user = (
            db.query(User)
            .filter(
                User.telegram_user_id ==
                query.from_user.id
            )
            .first()
        )

        print("CURRENT USER =", current_user)

        if not current_user:

            await query.edit_message_text(
                "❌ کاربر پیدا نشد."
            )

            return

        print(
            "PAID BY USER ID =",
            expense.paid_by_user_id
        )

        print(
            "CURRENT USER ID =",
            current_user.id
        )

        # فعلاً برای تست مجوز حذف را غیرفعال می‌کنیم
        # if expense.paid_by_user_id != current_user.id:
        #
        #     await query.answer(
        #         "فقط ثبت کننده هزینه می‌تواند آن را حذف کند.",
        #         show_alert=True
        #     )
        #
        #     return

        shares_count = (
            db.query(ExpenseShare)
            .filter(
                ExpenseShare.expense_id == expense.id
            )
            .count()
        )

        print("SHARES =", shares_count)

        (
            db.query(ExpenseShare)
            .filter(
                ExpenseShare.expense_id == expense.id
            )
            .delete(
                synchronize_session=False
            )
        )

        print("SHARES DELETED")

        db.delete(expense)

        print("EXPENSE DELETED")

        db.commit()

        print("COMMIT DONE")

        await query.edit_message_text(
            "✅ هزینه با موفقیت حذف شد."
        )

    except Exception as e:

        db.rollback()

        print(
            "DELETE EXPENSE ERROR:",
            str(e)
        )

        await query.edit_message_text(
            f"❌ خطا در حذف هزینه\n\n{e}"
        )

    finally:

        db.close()




expenses_handler = CommandHandler(
    "expenses",
    expenses_command
)
delete_expense_handler = CallbackQueryHandler(
    delete_expense,
    pattern=r"^delete_expense_\d+$"
)
expense_detail_handler = CallbackQueryHandler(
    expense_detail,
    pattern=r"^expense_\d+$"
)