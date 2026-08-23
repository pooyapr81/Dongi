from models import Expense, ExpenseShare


def create_equal_expense(
        db,
        group_id,
        payer_id,
        title,
        amount,
        user_ids
):

    # ساخت Expense اصلی
    expense = Expense(
        group_id=group_id,
        paid_by_user_id=payer_id,
        title=title,
        amount=amount,
        split_type="equal"
    )

    db.add(expense)
    db.commit()

    db.refresh(expense)


    # محاسبه سهم هر نفر
    share_amount = amount // len(user_ids)


    # ساخت سهم‌ها
    for user_id in user_ids:

        share = ExpenseShare(
            expense_id=expense.id,
            user_id=user_id,
            amount=share_amount
        )

        db.add(share)


    db.commit()


    return expense