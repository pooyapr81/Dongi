from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters
)

from database import SessionLocal

from models import (
    User,
    Group,
    Expense,
    Settlement
)

from services.balance_service import (
    calculate_balances,
    simplify_balances
)


# =========================================================
# Conversation States
# =========================================================

SELECT_USER, SELECT_TYPE, ENTER_AMOUNT = range(3)


# =========================================================
# /settle
# =========================================================

async def settle_start(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
):

    db = SessionLocal()

    try:

        chat_id = update.effective_chat.id
        telegram_id = update.effective_user.id

        # -------------------------------------------------
        # پیدا کردن گروه
        # -------------------------------------------------

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

            return ConversationHandler.END

        # -------------------------------------------------
        # پیدا کردن کاربر
        # -------------------------------------------------

        user = (
            db.query(User)
            .filter(
                User.telegram_user_id == telegram_id
            )
            .first()
        )

        if not user:

            await update.message.reply_text(
                "❌ شما در سیستم ثبت نشده‌اید."
            )

            return ConversationHandler.END

        # -------------------------------------------------
        # گرفتن هزینه‌های گروه
        # -------------------------------------------------

        expenses = (
            db.query(Expense)
            .filter(
                Expense.group_id == group.id
            )
            .all()
        )

        if not expenses:

            await update.message.reply_text(
                "📌 هنوز هیچ هزینه‌ای ثبت نشده است."
            )

            return ConversationHandler.END

        # -------------------------------------------------
        # محاسبه بالانس
        # -------------------------------------------------

        balances = calculate_balances(
            expenses,
            db
        )

        payments = simplify_balances(
            balances
        )

        # -------------------------------------------------
        # فقط بدهی‌های خود کاربر
        # -------------------------------------------------

        my_debts = []

        for payment in payments:

            if payment["from"] == user.id:

                my_debts.append(payment)

        # -------------------------------------------------
        # کاربر بدهی ندارد
        # -------------------------------------------------

        if not my_debts:

            await update.message.reply_text(
                "🎉 شما در حال حاضر بدهی‌ای ندارید."
            )

            return ConversationHandler.END

        # -------------------------------------------------
        # ذخیره اطلاعات
        # -------------------------------------------------

        context.user_data.clear()

        context.user_data["group_id"] = group.id

        context.user_data["from_user_id"] = user.id

        # -------------------------------------------------
        # ساخت دکمه‌های بدهی
        # -------------------------------------------------

        keyboard = []

        for payment in my_debts:

            to_user_id = payment["to"]
            amount = payment["amount"]

            to_user = (
                db.query(User)
                .filter(
                    User.id == to_user_id
                )
                .first()
            )

            if not to_user:
                continue

            keyboard.append(
                [
                    InlineKeyboardButton(
                        f"💸 {to_user.full_name} - "
                        f"{amount:,} تومان",
                        callback_data=(
                            f"settle_user_{to_user.id}"
                        )
                    )
                ]
            )

        if not keyboard:

            await update.message.reply_text(
                "❌ بدهی قابل تسویه‌ای پیدا نشد."
            )

            return ConversationHandler.END

        await update.message.reply_text(
            "💸 بدهی مورد نظر برای تسویه را انتخاب کنید:",
            reply_markup=InlineKeyboardMarkup(
                keyboard
            )
        )

        return SELECT_USER

    except Exception as e:

        print(
            "SETTLE START ERROR:",
            e
        )

        await update.message.reply_text(
            "❌ خطا در دریافت بدهی‌ها."
        )

        return ConversationHandler.END

    finally:

        db.close()


# =========================================================
# انتخاب طلبکار
# =========================================================

async def settle_select_user(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    db = SessionLocal()

    try:

        to_user_id = int(
            query.data.replace(
                "settle_user_",
                ""
            )
        )

        # -------------------------------------------------
        # پیدا کردن طرف مقابل
        # -------------------------------------------------

        to_user = (
            db.query(User)
            .filter(
                User.id == to_user_id
            )
            .first()
        )

        if not to_user:

            await query.edit_message_text(
                "❌ کاربر پیدا نشد."
            )

            return ConversationHandler.END

        # -------------------------------------------------
        # بررسی بدهی واقعی
        # -------------------------------------------------

        group_id = context.user_data["group_id"]

        from_user_id = context.user_data[
            "from_user_id"
        ]

        expenses = (
            db.query(Expense)
            .filter(
                Expense.group_id == group_id
            )
            .all()
        )

        balances = calculate_balances(
            expenses,
            db
        )

        payments = simplify_balances(
            balances
        )

        current_debt = 0

        for payment in payments:

            if (
                payment["from"] == from_user_id
                and
                payment["to"] == to_user_id
            ):

                current_debt = payment["amount"]

                break

        if current_debt <= 0:

            await query.edit_message_text(
                "❌ این بدهی دیگر وجود ندارد."
            )

            context.user_data.clear()

            return ConversationHandler.END

        # -------------------------------------------------
        # ذخیره اطلاعات
        # -------------------------------------------------

        context.user_data[
            "to_user_id"
        ] = to_user_id

        context.user_data[
            "current_debt"
        ] = current_debt

        # -------------------------------------------------
        # نمایش گزینه‌های تسویه
        # -------------------------------------------------

        keyboard = [

            [
                InlineKeyboardButton(
                    "✅ تسویه کامل",
                    callback_data="settle_full"
                )
            ],

            [
                InlineKeyboardButton(
                    "💰 تسویه بخشی",
                    callback_data="settle_partial"
                )
            ],

            [
                InlineKeyboardButton(
                    "❌ لغو",
                    callback_data="settle_cancel"
                )
            ]

        ]

        await query.edit_message_text(

            f"💸 بدهی شما به {to_user.full_name}\n\n"
            f"💰 مبلغ بدهی:\n"
            f"{current_debt:,} تومان\n\n"
            f"نوع تسویه را انتخاب کنید:",

            reply_markup=InlineKeyboardMarkup(
                keyboard
            )
        )

        return SELECT_TYPE

    except Exception as e:

        print(
            "SETTLE SELECT USER ERROR:",
            e
        )

        await query.edit_message_text(
            "❌ خطا در انتخاب بدهی."
        )

        return ConversationHandler.END

    finally:

        db.close()


# =========================================================
# انتخاب نوع تسویه
# =========================================================

async def settle_select_type(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    # =====================================================
    # لغو
    # =====================================================

    if query.data == "settle_cancel":

        context.user_data.clear()

        await query.edit_message_text(
            "❌ عملیات تسویه لغو شد."
        )

        return ConversationHandler.END

    # =====================================================
    # تسویه کامل
    # =====================================================

    if query.data == "settle_full":

        db = SessionLocal()

        try:

            group_id = context.user_data[
                "group_id"
            ]

            from_user_id = context.user_data[
                "from_user_id"
            ]

            to_user_id = context.user_data[
                "to_user_id"
            ]

            amount = context.user_data[
                "current_debt"
            ]

            # ---------------------------------------------
            # ثبت Settlement
            # ---------------------------------------------

            settlement = Settlement(

                group_id=group_id,

                from_user_id=from_user_id,

                to_user_id=to_user_id,

                amount=amount
            )

            db.add(settlement)

            db.commit()

            # ---------------------------------------------
            # پیدا کردن نام طرف مقابل
            # ---------------------------------------------

            to_user = (
                db.query(User)
                .filter(
                    User.id == to_user_id
                )
                .first()
            )

            await query.edit_message_text(

                "✅ بدهی به طور کامل تسویه شد.\n\n"

                f"💸 پرداخت به: "
                f"{to_user.full_name}\n"

                f"💰 مبلغ: "
                f"{amount:,} تومان"
            )

            context.user_data.clear()

            return ConversationHandler.END

        except Exception as e:

            db.rollback()

            print(
                "SETTLE FULL ERROR:",
                e
            )

            await query.edit_message_text(
                "❌ خطا در ثبت تسویه."
            )

            return ConversationHandler.END

        finally:

            db.close()

    # =====================================================
    # تسویه بخشی
    # =====================================================

    if query.data == "settle_partial":

        current_debt = context.user_data[
            "current_debt"
        ]

        await query.edit_message_text(

            f"💰 بدهی فعلی شما:\n"
            f"{current_debt:,} تومان\n\n"

            f"مبلغی که پرداخت کرده‌اید را وارد کنید:"
        )

        return ENTER_AMOUNT

    return SELECT_TYPE


# =========================================================
# دریافت مبلغ تسویه بخشی
# =========================================================

async def settle_amount(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
):

    db = SessionLocal()

    try:

        text = update.message.text.strip()

        # -------------------------------------------------
        # تبدیل به عدد
        # -------------------------------------------------

        try:

            amount = int(text)

        except ValueError:

            await update.message.reply_text(

                "❌ مبلغ باید فقط عدد باشد.\n\n"

                "مثال:\n"
                "250000"
            )

            return ENTER_AMOUNT

        # -------------------------------------------------
        # مبلغ مثبت باشد
        # -------------------------------------------------

        if amount <= 0:

            await update.message.reply_text(
                "❌ مبلغ باید بیشتر از صفر باشد."
            )

            return ENTER_AMOUNT

        # -------------------------------------------------
        # اطلاعات
        # -------------------------------------------------

        group_id = context.user_data[
            "group_id"
        ]

        from_user_id = context.user_data[
            "from_user_id"
        ]

        to_user_id = context.user_data[
            "to_user_id"
        ]

        current_debt = context.user_data[
            "current_debt"
        ]

        # -------------------------------------------------
        # بیشتر از بدهی نباشد
        # -------------------------------------------------

        if amount > current_debt:

            await update.message.reply_text(

                "❌ مبلغ پرداختی نمی‌تواند "
                "بیشتر از بدهی باشد.\n\n"

                f"بدهی فعلی:\n"
                f"{current_debt:,} تومان"
            )

            return ENTER_AMOUNT

        # -------------------------------------------------
        # ثبت Settlement
        # -------------------------------------------------

        settlement = Settlement(

            group_id=group_id,

            from_user_id=from_user_id,

            to_user_id=to_user_id,

            amount=amount
        )

        db.add(settlement)

        db.commit()

        # -------------------------------------------------
        # پیدا کردن طرف مقابل
        # -------------------------------------------------

        to_user = (
            db.query(User)
            .filter(
                User.id == to_user_id
            )
            .first()
        )

        remaining = (
            current_debt - amount
        )

        # -------------------------------------------------
        # پیام موفقیت
        # -------------------------------------------------

        if remaining > 0:

            await update.message.reply_text(

                "✅ تسویه ثبت شد.\n\n"

                f"💸 پرداخت به: "
                f"{to_user.full_name}\n"

                f"💰 مبلغ پرداختی: "
                f"{amount:,} تومان\n\n"

                f"📌 بدهی باقی‌مانده: "
                f"{remaining:,} تومان"
            )

        else:

            await update.message.reply_text(

                "✅ بدهی به طور کامل تسویه شد.\n\n"

                f"💸 پرداخت به: "
                f"{to_user.full_name}\n"

                f"💰 مبلغ: "
                f"{amount:,} تومان"
            )

        context.user_data.clear()

        return ConversationHandler.END

    except Exception as e:

        db.rollback()

        print(
            "SETTLE AMOUNT ERROR:",
            e
        )

        await update.message.reply_text(
            "❌ خطا در ثبت تسویه."
        )

        return ConversationHandler.END

    finally:

        db.close()


# =========================================================
# Conversation Handler
# =========================================================

settle_handler = ConversationHandler(

    entry_points=[

        CommandHandler(
            "settle",
            settle_start
        )

    ],

    states={

        # -----------------------------------------------
        # انتخاب شخص
        # -----------------------------------------------

        SELECT_USER: [

            CallbackQueryHandler(
                settle_select_user,
                pattern=r"^settle_user_\d+$"
            )

        ],

        # -----------------------------------------------
        # انتخاب نوع تسویه
        # -----------------------------------------------

        SELECT_TYPE: [

            CallbackQueryHandler(
                settle_select_type,
                pattern=r"^settle_(full|partial|cancel)$"
            )

        ],

        # -----------------------------------------------
        # وارد کردن مبلغ
        # -----------------------------------------------

        ENTER_AMOUNT: [

            MessageHandler(
                filters.TEXT &
                ~filters.COMMAND,
                settle_amount
            )

        ]

    },

    fallbacks=[]
)