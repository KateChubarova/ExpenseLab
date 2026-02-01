from .models import Expense


def map_db_to_ui(expense: Expense) -> dict:
    return {
        "transaction date": expense.transaction_date,
        "transaction_type": expense.transaction_type,
        "recipient": expense.recipient,
        "description": expense.description,
        "debits": expense.debits,
        "credits": expense.credits,
        "currency": expense.currency,
        "category": expense.category,
    }
