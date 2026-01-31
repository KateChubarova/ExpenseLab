# src/db/models.py

from sqlalchemy import Column, String, Date, Numeric, Index, Text
from .base import Base


class Expense(Base):
    __tablename__ = "expense"
    __table_args__ = (
        Index("ix_expense_transaction_date", "transaction_date"),
        Index("ix_expense_category", "category"),
        {"schema": "public"},
    )

    id = Column(String(64), primary_key=True)

    account = Column(String(64))
    transaction_date = Column(Date)
    settlement_date = Column(Date)

    transaction_type = Column(String(64))
    recipient = Column(String(128))

    debits = Column(Numeric(12, 2))
    credits = Column(Numeric(12, 2))
    saldo = Column(Numeric(12, 2))
    currency = Column(String(3))

    description = Column(Text)  # TEXT
    description_norm = Column(Text)  # TEXT
    category = Column(String(64))
