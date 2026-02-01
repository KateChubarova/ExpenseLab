import hashlib
import pandas as pd
import streamlit as st
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import select, update

from .mapper import map_db_to_ui
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


@st.cache_data
def get_expenses() -> pd.DataFrame:
    db = SessionLocal()
    try:
        stmt = select(Expense)
        result = db.execute(stmt)
        rows = result.scalars().all()

        return pd.DataFrame([map_db_to_ui(row) for row in rows]
                            )
    finally:
        db.close()


def rename_category(old_name: str, new_name: str) -> int:
    with SessionLocal() as db:
        try:
            stmt = (
                update(Expense)
                .where(Expense.category == old_name)
                .values(category=new_name)
                .execution_options(synchronize_session="fetch")
            )
            res = db.execute(stmt)
            db.commit()
            db.close()
            return res.rowcount or 0
        except Exception:
            db.rollback()
            raise

