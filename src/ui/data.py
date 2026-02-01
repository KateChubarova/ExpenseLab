import json
import streamlit as st

RULES_PATH = "category_rules.json"


@st.cache_data
def load_category_rules_cached() -> dict:
    with open(RULES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def show_data(df):
    rules = load_category_rules_cached()
    categories = sorted(rules.keys())

    st.data_editor(
        df,
        column_config={
            "category": st.column_config.SelectboxColumn(
                "category", options=categories, required=True
            )
        },
        disabled=[c for c in df.columns if c != "category"],
        key="expense_editor",
        width="stretch",
        num_rows="fixed",
    )


def load_data():
    st.title("📊 CSV Viewer")

    return st.file_uploader(
        "Загрузи CSV файл",
        type=["csv"]
    )
