from models import Settlement


def calculate_balances(expenses, db):

    balances = {}

    # ==========================================
    # محاسبه وضعیت مالی از روی هزینه‌ها
    # ==========================================

    for expense in expenses:

        payer_id = expense.paid_by_user_id

        # پولی که پرداخت‌کننده داده
        balances[payer_id] = (
            balances.get(payer_id, 0)
            + expense.amount
        )

        # سهم هر شخص از هزینه
        for share in expense.shares:

            user_id = share.user_id

            balances[user_id] = (
                balances.get(user_id, 0)
                - share.amount
            )

    # ==========================================
    # اعمال تسویه‌های قبلی
    # ==========================================

    if expenses:

        group_id = expenses[0].group_id

        settlements = (
            db.query(Settlement)
            .filter(
                Settlement.group_id == group_id
            )
            .all()
        )

        for settlement in settlements:

            from_user = settlement.from_user_id
            to_user = settlement.to_user_id
            amount = settlement.amount

            # بدهکار پول پرداخت کرده
            balances[from_user] = (
                balances.get(from_user, 0)
                + amount
            )

            # طلبکار پول دریافت کرده
            balances[to_user] = (
                balances.get(to_user, 0)
                - amount
            )

    return balances


def simplify_balances(balances):

    creditors = []
    debtors = []

    # ==========================================
    # جدا کردن طلبکارها و بدهکارها
    # ==========================================

    for user_id, amount in balances.items():

        if amount > 0:

            creditors.append(
                [user_id, amount]
            )

        elif amount < 0:

            debtors.append(
                [user_id, -amount]
            )

    result = []

    i = 0
    j = 0

    # ==========================================
    # ساده کردن بدهی‌ها
    # ==========================================

    while (
        i < len(debtors)
        and
        j < len(creditors)
    ):

        debtor = debtors[i]
        creditor = creditors[j]

        amount = min(
            debtor[1],
            creditor[1]
        )

        result.append(
            {
                "from": debtor[0],
                "to": creditor[0],
                "amount": amount
            }
        )

        debtor[1] -= amount
        creditor[1] -= amount

        if debtor[1] == 0:
            i += 1

        if creditor[1] == 0:
            j += 1

    return result