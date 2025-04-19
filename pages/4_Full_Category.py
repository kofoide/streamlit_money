# streamlit_app.py

import numpy as np
import pandas as pd
import streamlit as st
import sqlalchemy as sa
import plotly.graph_objects as go
from resources import *

st.set_page_config(layout="wide")

budget_categories = get_db_budget_categories()
categories = budget_categories['budget_category'].tolist()
categories.sort()


categories = ["Total", "Annual", "Rent", "Moving Transport", "Entertainment", "Grocery", "Eat Out", "Stuff"]
with st.sidebar:
    selected_category = st.selectbox('Select a category', categories)

st.header(f"{selected_category} for 2025")
budgets = get_db_budgets_for_year_and_category(2025, selected_category)

col1, col2, col3, col4 = st.columns(4)
col1.subheader("Month")
col2.subheader("Envelope In")
col3.subheader("Actual Monthly")
col4.subheader("Envelope Out")

#loop through rows in budgets and create a figure for each category
for index, row in budgets.iterrows():
    col1, col2, col3, col4 = st.columns(4)

    header = f"""<h3>{index}</h3>"""
    col1.markdown(header, unsafe_allow_html=True)
    envelope_in_amount = budgets.at[index, "envelope_in_amount"]
    actual_monthly_amount = budgets.at[index, "actual_monthly_amount"]
    envelope_out_amount = budgets.at[index, "envelope_out_amount"]
    
    red = """<p style="font-size: 30px; color:red">"""
    green = """<p style="font-size: 30px; color:green">"""
    blue = """<p style="font-size: 30px; color:blue">"""

    if envelope_in_amount < 0:
        in_text = f"""{red}{dollar_format_grid(envelope_in_amount)}</p>"""
    else:
        in_text = f"""{green}{dollar_format_grid(envelope_in_amount)}</p>"""
    
    if envelope_out_amount < 0:
        out_text = f"""{red}{dollar_format_grid(envelope_out_amount)}</p>"""
    else:
        out_text = f"""{green}{dollar_format_grid(envelope_out_amount)}</p>"""

    actual_text = f"""{blue}{dollar_format_grid(actual_monthly_amount)}</p>"""

    col2.markdown(in_text, unsafe_allow_html=True)
    col3.markdown(actual_text, unsafe_allow_html=True)
    col4.markdown(out_text, unsafe_allow_html=True)
    
    #endregion
