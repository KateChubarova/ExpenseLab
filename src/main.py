import pandas as pd

from preprocessing.etl import run_pipeline
from db.expenses_repo import save_expenses
from ui.data import show_data, load_data
from ui.category import category_spend
from ui.weekday import weekday_spend

uploaded_file = load_data()
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    df = run_pipeline(df)

    show_data(df)
    weekday_spend(df)
    category_spend(df)

    save_expenses(df)
