import streamlit as st
import pandas as pd
import altair as alt

from etl import run_pipeline


def data(df):
    st.subheader("Данные")
    st.dataframe(df, use_container_width=True, height=600)


def week_day_spend(df):
    limit = st.number_input(
        "Максимальный размер расхода для анализа",
        min_value=0,
        max_value=10000,
        value=1500,
        step=100
    )

    st.subheader(f"📊 Траты по дням недели (<{limit})")

    df["Transaction date"] = pd.to_datetime(df["Transaction date"], errors="coerce")

    # Берем только расходы < 5000
    filtered = df[
        (df["Debits"] < 0) &
        (df["Debits"] > -limit)
        ].copy()

    # Сумма расходов
    filtered["expense"] = filtered["Debits"].abs()

    # День недели
    filtered["weekday"] = filtered["Transaction date"].dt.day_name()

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


def category_spend(df):
    st.subheader("📊 Сумма трат по категориям")

    # на всякий случай привести к числу
    df["Debits"] = pd.to_numeric(df["Debits"], errors="coerce")

    # расходы = отрицательные Debits
    cat_df = df[df["Debits"] < 0].copy()
    cat_df["expense"] = cat_df["Debits"].abs()

    by_cat = (
        cat_df.groupby("category", as_index=False)["expense"]
        .sum()
    )

    chart = alt.Chart(by_cat).mark_bar().encode(
        x=alt.X("expense:Q", title="Total expenses (PLN)"),
        y=alt.Y("category:N", sort="-x", title="Category"),
        tooltip=["category:N", alt.Tooltip("expense:Q", format=".2f")]
    )

    st.altair_chart(chart, use_container_width=True)


st.title("📊 CSV Viewer")

uploaded_file = st.file_uploader(
    "Загрузи CSV файл",
    type=["csv"]
)

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    df = run_pipeline(df)

    data(df)
    week_day_spend(df)
    category_spend(df)
