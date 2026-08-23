from telegram import Update
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters
)
from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler
from database import SessionLocal
from models import (
    Group,
    GroupMember,
    User,
    Expense,
    ExpenseShare
)
from services.expense_service import create_equal_expense

AMOUNT, TITLE, SPLIT_TYPE, MEMBERS, CUSTOM_SHARE = range(5)

async def expense_start(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
):
    await update.message.reply_text(
        "💰 مبلغ هزینه را وارد کنید:"
    )

    return AMOUNT


async def get_amount(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
):
    amount = update.message.text

    context.user_data["amount"] = amount

    await update.message.reply_text(
        "📝 عنوان هزینه را وارد کنید:"
    )

    return TITLE


async def get_title(update, context):
    title = update.message.text

    context.user_data["title"] = title

    keyboard = [
        [
            InlineKeyboardButton(
                "➗ تقسیم مساوی",
                callback_data="equal"
            )
        ],
        [
            InlineKeyboardButton(
                "✍️ تقسیم سفارشی",
                callback_data="custom"
            )
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "نوع تقسیم را انتخاب کنید:",
        reply_markup=reply_markup
    )

    return SPLIT_TYPE


from telegram import CallbackQuery


async def choose_split_type(
        update,
        context
):
    query = update.callback_query

    await query.answer()

    split_type = query.data

    context.user_data["split_type"] = split_type

    if split_type == "equal":

        await query.edit_message_text(
            "✅ تقسیم مساوی انتخاب شد."
        )

    else:

        await query.edit_message_text(
            "✅ تقسیم سفارشی انتخاب شد."
        )

    print(context.user_data)

    db = SessionLocal()

    try:

        chat_id = update.effective_chat.id

        group = (
            db.query(Group)
            .filter(Group.telegram_chat_id == chat_id)
            .first()
        )

        members = (
            db.query(GroupMember)
            .filter(GroupMember.group_id == group.id)
            .all()
        )

        payer_telegram_id = update.effective_user.id

        payer = (
            db.query(User)
            .filter(User.telegram_user_id == payer_telegram_id)
            .first()
        )

        # پرداخت کننده از اول انتخاب شده
        context.user_data["selected_users"] = [payer.id]

        await query.message.reply_text(
            "👥 اعضای هزینه را انتخاب کنید:",
            reply_markup=build_members_keyboard(
                members,
                context.user_data["selected_users"]
            )
        )

    finally:
        db.close()

    return MEMBERS


async def custom_share_handler(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
):
    db = SessionLocal()

    try:

        try:
            amount = int(update.message.text)
        except ValueError:
            await update.message.reply_text(
                "❌ لطفاً فقط عدد وارد کنید."
            )
            return CUSTOM_SHARE

        user_ids = context.user_data["custom_users"]

        index = context.user_data["custom_index"]

        current_user_id = user_ids[index]

        context.user_data["custom_amounts"][
            current_user_id
        ] = amount

        index += 1

        context.user_data["custom_index"] = index

        # هنوز اعضا باقی مانده‌اند
        if index < len(user_ids):

            next_user = (
                db.query(User)
                .filter(
                    User.id == user_ids[index]
                )
                .first()
            )

            await update.message.reply_text(
                f"💰 سهم {next_user.full_name} را وارد کنید:"
            )

            return CUSTOM_SHARE

        # -------------------------
        # همه سهم‌ها دریافت شدند
        # -------------------------

        total_shares = sum(
            context.user_data["custom_amounts"].values()
        )

        expense_amount = int(
            context.user_data["amount"]
        )

        if total_shares != expense_amount:

            await update.message.reply_text(
                f"❌ مجموع سهم‌ها برابر مبلغ کل نیست.\n\n"
                f"مبلغ کل: {expense_amount:,}\n"
                f"مجموع سهم‌ها: {total_shares:,}"
            )

            return ConversationHandler.END

        # -------------------------
        # ذخیره Expense
        # -------------------------

        group = (
            db.query(Group)
            .filter(
                Group.id ==
                context.user_data["group_id"]
            )
            .first()
        )

        expense = Expense(
            group_id=group.id,
            title=context.user_data["title"],
            amount=expense_amount,
            paid_by_user_id=context.user_data["payer_id"],
            split_type=2  # custom
        )

        db.add(expense)
        db.commit()
        db.refresh(expense)

        # -------------------------
        # ذخیره ExpenseShare
        # -------------------------

        for user_id, share_amount in (
                context.user_data[
                    "custom_amounts"
                ].items()
        ):

            share = ExpenseShare(
                expense_id=expense.id,
                user_id=user_id,
                amount=share_amount
            )

            db.add(share)

        db.commit()

        # -------------------------
        # پیام موفقیت
        # -------------------------

        msg = (
            "✅ هزینه با موفقیت ثبت شد\n\n"
            f"📝 {expense.title}\n"
            f"💰 {expense.amount:,} تومان"
        )

        await update.message.reply_text(msg)

        context.user_data.clear()

        return ConversationHandler.END

    except Exception as e:

        db.rollback()

        print("CUSTOM SHARE ERROR:", e)

        await update.message.reply_text(
            "❌ خطا در ثبت هزینه"
        )

        return ConversationHandler.END

    finally:

        db.close()


def build_members_keyboard(members, selected_users):
    keyboard = []

    for member in members:
        mark = "☑️" if member.user_id in selected_users else "☐"

        keyboard.append([
            InlineKeyboardButton(
                f"{mark} {member.user.full_name}",
                callback_data=f"member_{member.user_id}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            "✅ تایید",
            callback_data="confirm_members"
        )
    ])

    return InlineKeyboardMarkup(keyboard)


async def cancel(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
):
    await update.message.reply_text(
        "❌ عملیات لغو شد."
    )

    return ConversationHandler.END


async def members_handler(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    data = query.data

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

        members = (
            db.query(GroupMember)
            .filter(
                GroupMember.group_id == group.id
            )
            .all()
        )

        selected_users = context.user_data.get(
            "selected_users",
            []
        )

        # انتخاب / لغو انتخاب عضو
        if data.startswith("member_"):

            user_id = int(
                data.replace(
                    "member_",
                    ""
                )
            )

            if user_id in selected_users:
                selected_users.remove(user_id)
            else:
                selected_users.append(user_id)

            context.user_data[
                "selected_users"
            ] = selected_users

            await query.edit_message_reply_markup(
                reply_markup=build_members_keyboard(
                    members,
                    selected_users
                )
            )

            return MEMBERS

        # تایید اعضا
        if data == "confirm_members":

            payer = (
                db.query(User)
                .filter(
                    User.telegram_user_id ==
                    update.effective_user.id
                )
                .first()
            )

            payer_id = payer.id

            others = [
                x for x in selected_users
                if x != payer_id
            ]

            if len(others) == 0:

                await query.answer(
                    "حداقل یک نفر دیگر انتخاب کنید",
                    show_alert=True
                )

                return MEMBERS

            split_type = context.user_data["split_type"]

            if split_type == "equal":
                expense = create_equal_expense(
                    db=db,
                    group_id=group.id,
                    payer_id=payer_id,
                    title=context.user_data["title"],
                    amount=int(
                        context.user_data["amount"]
                    ),
                    user_ids=selected_users
                )

                await query.edit_message_text(
                    f"✅ هزینه ثبت شد\n\n"
                    f"عنوان: {expense.title}\n"
                    f"مبلغ: {expense.amount:,}"
                )

                return ConversationHandler.END
            else:

                context.user_data["group_id"] = group.id

                context.user_data["payer_id"] = payer_id

                context.user_data["custom_users"] = selected_users

                context.user_data["custom_index"] = 0

                context.user_data["custom_amounts"] = {}

                first_user = (
                    db.query(User)
                    .filter(
                        User.id == selected_users[0]
                    )
                    .first()
                )

                await query.edit_message_text(
                    f"💰 سهم {first_user.full_name} را وارد کنید:"
                )

                return CUSTOM_SHARE

    except Exception as e:

        print("Expense Error:", e)

        await query.message.reply_text(
            "❌ خطا در ثبت هزینه"
        )

        return ConversationHandler.END

    finally:

        db.close()


expense_handler = ConversationHandler(
    entry_points=[
        CommandHandler(
            "expense",
            expense_start
        )
    ],
    states={

        AMOUNT: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                get_amount
            )
        ],

        TITLE: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                get_title
            )
        ],

        SPLIT_TYPE: [
            CallbackQueryHandler(
                choose_split_type,
                pattern="^(equal|custom)$"
            )
        ],

        MEMBERS: [
            CallbackQueryHandler(
                members_handler
            )
        ],
CUSTOM_SHARE: [
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        custom_share_handler
    )
]
    },

    fallbacks=[
        CommandHandler(
            "cancel",
            cancel
        )
    ]
)
