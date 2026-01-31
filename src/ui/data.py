import streamlit as st


def show_data(df):
    st.subheader("Данные")
    st.dataframe(df, use_container_width=True, height=600)


def load_data():
    st.title("📊 CSV Viewer")

    return st.file_uploader(
        "Загрузи CSV файл",
        type=["csv"]
    )
