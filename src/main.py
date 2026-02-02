import logging

import pandas as pd

import streamlit as st
from preprocessing.etl import run_pipeline
from db.expenses_repo import save_expenses
from db.expenses_repo import get_expenses
from ui.categories import render_category_manager_minimal
from ui.data import show_data, load_data
from ui.category import category_spend
from ui.weekday import weekday_spend

uploaded_file = load_data()

if uploaded_file is not None:
    file_bytes = uploaded_file.getvalue()
    file_key = hash(file_bytes)

    if st.session_state.get("last_upload_key") != file_key:
        st.session_state["last_upload_key"] = file_key

        df = pd.read_csv(uploaded_file)
        df = run_pipeline(df)
        save_expenses(df)

        try:
            get_expenses.clear()
        except Exception as e:
            logging.exception(e)

        st.rerun()

df_ui = get_expenses()

render_category_manager_minimal()
selected = st.session_state.get("selected_category")
df_view = df_ui if not selected else df_ui[df_ui["category"] == selected]
show_data(df_view)

weekday_spend(df_ui)
category_spend(df_ui)
