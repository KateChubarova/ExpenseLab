import streamlit as st
import pandas as pd
import altair as alt


def weekday_spend(df):
    if df is None or df.empty:
        st.info("Нет данных для анализа расходов по дням недели")
        return

    limit = st.number_input(
        "Максимальный размер расхода для анализа",
        min_value=0,
        max_value=10000,
        value=1500,
        step=100
    )

    st.subheader(f"📊 Траты по дням недели (<{limit})")

    df = df.copy()

    df["transaction date"] = pd.to_datetime(df["transaction date"], errors="coerce")
    df["debits"] = pd.to_numeric(df["debits"], errors="coerce")

    filtered = df[(df["debits"] < 0) & (df["debits"].abs() < limit)].copy()

    if filtered.empty:
        st.warning("Нет расходов, подходящих под выбранный лимит")
        return

    filtered["expense"] = filtered["debits"].abs()
    filtered["weekday"] = filtered["transaction date"].dt.day_name()

    weekday_order = [
        "Monday", "Tuesday", "Wednesday",
        "Thursday", "Friday", "Saturday", "Sunday"
    ]

    week_spend = (
        filtered
        .groupby("weekday", as_index=False)["expense"]
        .sum()
    )

    week_spend["weekday"] = pd.Categorical(
        week_spend["weekday"],
        categories=weekday_order,
        ordered=True
    )

    week_spend = week_spend.sort_values("weekday")

    chart = (
        alt.Chart(week_spend)
        .mark_bar()
        .encode(
            x=alt.X("weekday:N", sort=weekday_order, title="Day of week"),
            y=alt.Y("expense:Q", title="Expenses"),
            tooltip=[
                alt.Tooltip("weekday:N", title="Day"),
                alt.Tooltip("expense:Q", title="Expenses", format=",.2f"),
            ],
        )
    )

    st.altair_chart(chart, use_container_width=True)
