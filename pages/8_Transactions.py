# streamlit_app.py

import numpy as np
import pandas as pd
import streamlit as st
import sqlalchemy as sa
import plotly.graph_objects as go
from resources import *

st.set_page_config(layout="wide")

months = get_db_months()
df_transactions = get_db_all_transactions()

category_list = df_transactions['category'].unique().tolist()
category_list.append(" All")
category_list.sort()

budget_category_list = df_transactions['budget_category'].unique().tolist()
budget_category_list.append(" All")
budget_category_list.sort()

month_list = df_transactions['tag_when'].unique().tolist()
month_list.append(" All")
month_list.sort()


with st.sidebar:
    month_selected = st.selectbox('Filter when', month_list)
    category_selected = st.selectbox('Filter category', category_list)
    budget_category_selected = st.selectbox('Filter budget category', budget_category_list)



#region Individual Transaction Selection

st.dataframe(df_transactions.style.apply(highlight_future_transactions, axis=1))
#endregion