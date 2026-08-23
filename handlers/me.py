from telegram import Update
from telegram.ext import ContextTypes

from database import SessionLocal

from models import (
    Group,
    User,
    Expense
)

from services.balance_service import (
    calculate_balances,
    simplify_balances
)


async def me(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
):

    db = SessionLocal()

    try:

        chat_id = update.effective_chat.id

        telegram_id = update.effective_user.id


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


        # پیدا کردن کاربر
        user = (
            db.query(User)
            .filter(
                User.telegram_user_id == telegram_id
            )
            .first()
        )


        if not user:

            await update.message.reply_text(
                "❌ شما ثبت نشده‌اید."
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
                "📌 هنوز هزینه‌ای ثبت نشده."
            )

            return



        # محاسبه بالانس‌ها
        balances = calculate_balances(
            expenses,
            db
        )


        payments = simplify_balances(
            balances
        )



        owes = []
        gets = []


        for payment in payments:


            # این شخص باید پول بدهد
            if payment["from"] == user.id:

                to_user = (
                    db.query(User)
                    .filter(
                        User.id ==
                        payment["to"]
                    )
                    .first()
                )


                owes.append(
                    f"💸 be {to_user.full_name} "
                    f":{payment['amount']:,} toman"
                )



            # این شخص باید پول بگیرد
            elif payment["to"] == user.id:


                from_user = (
                    db.query(User)
                    .filter(
                        User.id ==
                        payment["from"]
                    )
                    .first()
                )


                gets.append(
                    f"💰 az {from_user.full_name} "
                    f":{payment['amount']:,} toman"
                )



        text = "📊 وضعیت مالی شما:\n\n"



        if gets:

            text += "طلبکار هستید:\n"

            text += "\n".join(gets)

            text += "\n\n"


        if owes:

            text += "بدهکار هستید:\n"

            text += "\n".join(owes)



        if not gets and not owes:

            text += "✅ حساب شما تسویه است."



        await update.message.reply_text(
            text
        )


    except Exception as e:

        print(
            "ME Error:",
            e
        )

        await update.message.reply_text(
            "❌ خطا در دریافت وضعیت مالی"
        )


    finally:

        db.close()