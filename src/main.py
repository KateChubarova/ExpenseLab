import streamlit as st
import pandas as pd
import altair as alt

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
    st.dataframe(df, use_container_width=True, height=600)

    df["Data transakcji"] = pd.to_datetime(df["Data transakcji"], errors="coerce")

    # Берем только расходы < 5000
    filtered = df[
        (df["Obciążenia"] < 0) &
        (df["Obciążenia"] > -1500)
        ].copy()

    # Сумма расходов
    filtered["expense"] = filtered["Obciążenia"].abs()

    # День недели
    filtered["weekday"] = filtered["Data transakcji"].dt.day_name()

    weekday_order = [
        "Monday", "Tuesday", "Wednesday",
        "Thursday", "Friday", "Saturday", "Sunday"
    ]

    week_spend = (
        filtered.groupby("weekday")["expense"]
        .mean()
        .reindex(weekday_order)
    )

    st.subheader("📊 Траты по дням недели (<1500)")

    chart = alt.Chart(week_spend.reset_index()).mark_bar().encode(
        x=alt.X("weekday", sort=weekday_order, title="Day of week"),
        y=alt.Y("expense", title="Expenses"),
    )

    st.altair_chart(chart, use_container_width=True)


