import streamlit as st
import pandas as pd
import altair as alt


def category_spend(df):
    st.subheader("📊 Сумма трат по категориям")

    df["debits"] = pd.to_numeric(df["debits"], errors="coerce")

    cat_df = df[df["debits"] < 0].copy()
    cat_df["expense"] = cat_df["debits"].abs()

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
