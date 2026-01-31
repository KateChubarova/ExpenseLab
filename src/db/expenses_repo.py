import hashlib
import pandas as pd
from sqlalchemy.dialects.postgresql import insert

from .models import Expense
from .session import SessionLocal


def make_id(item: pd.Series) -> str:
    raw = "|".join([
        str(item["transaction date"]),
        str(item["recipient"]),
        str(item["description"]),
        str(item["debits"]),
        str(item["credits"]),
        str(item["saldo"])
    ])

    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def save_expenses(df: pd.DataFrame) -> int:
    db = SessionLocal()

    df = df.copy()
    df["id"] = df.apply(make_id, axis=1)

    # Собираем записи напрямую (без Expense(...))
    cols = [
        "id", "saldo", "account",
        "transaction date", "settlement date", "transaction type",
        "recipient", "description", "debits", "credits", "currency",
        "description_norm", "category",
    ]

    records = df[cols].rename(columns={
        "transaction date": "transaction_date",
        "settlement date": "settlement_date",
        "transaction type": "transaction_type",
    }).to_dict("records")

    try:
        stmt = insert(Expense).values(records)
        stmt = stmt.on_conflict_do_nothing(index_elements=["id"])  # игнор дубликатов

        result = db.execute(stmt)
        db.commit()

        return int(result.rowcount or 0)

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()
