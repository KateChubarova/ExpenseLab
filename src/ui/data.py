import json

import streamlit as st

with open("category_rules.json") as f:
    CATEGORY_RULES = json.load(f)
    CATEGORIES = sorted(CATEGORY_RULES.keys())

    print(CATEGORIES)


def show_data(df):
    st.subheader("Данные")
    st.data_editor(
        df,
        use_container_width=True,
        num_rows="fixed",
        column_config={
            "category": st.column_config.SelectboxColumn(
                "category",
                options=CATEGORIES,
                required=True,
            ),
        },
        disabled=[c for c in df.columns if c != "category"],
        key="expense_editor",
    )


def load_data():
    st.title("📊 CSV Viewer")

    return st.file_uploader(
        "Загрузи CSV файл",
        type=["csv"]
    )
