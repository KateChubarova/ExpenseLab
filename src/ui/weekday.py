import streamlit as st
import pandas as pd
import altair as alt


def weekday_spend(df):
    limit = st.number_input(
        "Максимальный размер расхода для анализа",
        min_value=0,
        max_value=10000,
        value=1500,
        step=100
    )

    st.subheader(f"📊 Траты по дням недели (<{limit})")

    df["transaction date"] = pd.to_datetime(df["transaction date"], errors="coerce")

    filtered = df[
        (df["debits"] < 0) &
        (df["debits"] > -limit)
        ].copy()

    filtered["expense"] = filtered["debits"].abs()
    filtered["weekday"] = filtered["transaction date"].dt.day_name()

    weekday_order = [
        "Monday", "Tuesday", "Wednesday",
        "Thursday", "Friday", "Saturday", "Sunday"
    ]

    week_spend = (
        filtered.groupby("weekday")["expense"]
        .mean()
        .reindex(weekday_order)
    )

    chart = alt.Chart(week_spend.reset_index()).mark_bar().encode(
        x=alt.X("weekday", sort=weekday_order, title="Day of week"),
        y=alt.Y("expense", title="Expenses"),
    )

    st.altair_chart(chart, use_container_width=True)