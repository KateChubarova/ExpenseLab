import streamlit as st
import pandas as pd
import altair as alt

from etl import run_pipeline

st.title("📊 CSV Viewer")

# Загрузка файла
uploaded_file = st.file_uploader(
    "Загрузи CSV файл",
    type=["csv"]
)

# Приводим к числу (на всякий случай)
if uploaded_file is not None:
    # Чтение CSV
    df = pd.read_csv(uploaded_file)

    # Вся таблица на одной странице
    st.subheader("Данные")

    df = run_pipeline(df)

    st.dataframe(df, use_container_width=True, height=600)

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

    st.subheader("📊 Доходы (→) и расходы (←) по категориям")

    tmp = df.copy()
    tmp["Debits"] = pd.to_numeric(tmp["Debits"], errors="coerce")
    tmp["Credits"] = pd.to_numeric(tmp["Credits"], errors="coerce")

    tmp["category"] = tmp["category"].fillna("Other")

    # агрегируем отдельно
    exp = (
        tmp[tmp["Debits"] < 0]
        .assign(amount=lambda d: d["Debits"].abs())
        .groupby("category", as_index=False)["amount"].sum()
        .assign(side="expense", value_signed=lambda d: -d["amount"])
    )

    inc = (
        tmp[tmp["Credits"] > 0]
        .assign(amount=lambda d: d["Credits"])
        .groupby("category", as_index=False)["amount"].sum()
        .assign(side="income", value_signed=lambda d: d["amount"])
    )

    by_cat = pd.concat([exp, inc], ignore_index=True)

    chart = alt.Chart(by_cat).mark_bar().encode(
        y=alt.Y("category:N", sort=alt.EncodingSortField(field="value_signed", op="sum", order="descending"),
                title="Category"),
        x=alt.X("value_signed:Q", title="PLN (← expenses | income →)"),
        tooltip=[
            "category:N",
            "side:N",
            alt.Tooltip("amount:Q", format=".2f", title="amount"),
            alt.Tooltip("value_signed:Q", format=".2f", title="signed")
        ]
    )

    st.altair_chart(chart, use_container_width=True)


