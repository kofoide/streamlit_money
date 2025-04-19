# streamlit_app.py

import numpy as np
import pandas as pd
import streamlit as st
import sqlalchemy as sa
import plotly.graph_objects as go
from resources import *

st.set_page_config(layout="wide")

months = get_db_months()

# get the index of the current month tag for the default selection
current_month_tag = str(pd.to_datetime('now').year) + '-' + str(pd.to_datetime('now').month).zfill(2)
tag_index = months[months['tag_month'] == current_month_tag].index[0]

with st.sidebar:
    tag_month_selected = st.selectbox('Select a tag', months['tag_month'].tolist(), index=int(tag_index))
    tag_year_selected = tag_month_selected[:4]
    is_full_year_selected = st.checkbox('Transactions Full Year?', value=False)

budgets = get_db_budgets_for_month(tag_month_selected)

df_month = get_db_transactions_month(tag_month_selected)


top_col1, top_col2 = st.columns(2)

#region Total Variables
with top_col1:
    totals_figure = go.Figure()
    totals_figure.update_layout(
        grid = {'rows': 1, 'columns': 3},
        margin=dict(t=0, b=0, l=0, r=0),
        height=225,
    )
    totals_figure.add_trace(
        big_ass_number_with_row(
            budgets.at["Total", "envelope_in_amount"],
            "Envelope<br>In",
            0,
            0,
            "Total_Envelope_in"
        )
    )
    totals_figure.add_trace(
        big_ass_number_with_row_with_delta(
            budgets.at["Total", "actual_monthly_amount"],
            budgets.at["Total", "delta_monthly_amount"],
            "Spent Total",
            0,
            1,
            "Total"
        )
    )
    totals_figure.add_trace(
        big_ass_number_with_row(
            budgets.at["Total", "envelope_out_amount"],
            "Envelope<br>Out",
            0,
            2,
            "Total_Envelope_out"
        )
    )
    st.plotly_chart(totals_figure, use_container_width=True)

with top_col2:
    annual_figure = go.Figure()
    annual_figure.update_layout(
        grid = {'rows': 1, 'columns': 3},
        margin=dict(t=0, b=0, l=0, r=0),
        height=225,
    )
    annual_figure.add_trace(
        big_ass_number_with_row(
            budgets.at["Annual", "envelope_in_amount"],
            "Envelope<br>In",
            0,
            0,
            "Annual_Envelope_in"
        )
    )
    annual_figure.add_trace(
        big_ass_number_with_row_with_delta(
            budgets.at["Annual", "actual_monthly_amount"],
            budgets.at["Annual", "delta_monthly_amount"],
            "Annual",
            0,
            1,
            "Annual"
        )
    )
    annual_figure.add_trace(
        big_ass_number_with_row(
            budgets.at["Annual", "envelope_out_amount"],
            "Envelope<br>Out",
            0,
            2,
            "Annual_Envelope_out"
        )
    )
    st.plotly_chart(annual_figure, use_container_width=True)
#endregion

col1, gap1_col, col2, gap2_col, col3 = st.columns([.29, .01, .29, .01, .3])

with col1:
    #new_title = '<p style="font-family:sans-serif; color:Black; font-size: 42px;">Rent</p><p style="font-family:sans-serif; color:Black; font-size: 30px;">Rent</p>'
    #st.markdown(new_title, unsafe_allow_html=True)

    rent_header = f"Rent ({dollar_format(budgets.at['Rent', 'budget_monthly_amount'])})"
    st.header(rent_header)
    rent_metrics_figure = go.Figure()
    rent_metrics_figure.update_layout(
        grid = {'rows': 2, 'columns': 3},
        margin=dict(t=0, b=0, l=0, r=0),
        height = 170
    )
    rent_metrics_figure.add_trace(
        big_ass_number_with_row(
            budgets.at["Rent", "envelope_in_amount"],
            "Envelope<br>In",
            0,
            0,
            "Rent_envelope_in"
        )
    )
    rent_metrics_figure.add_trace(
        big_ass_number_with_row_with_delta(
            budgets.at["Rent", "actual_monthly_amount"],
            budgets.at["Rent", "delta_monthly_amount"],
            "<br>Spent",
            0,
            1,
            "Rent"
        )
    )
    rent_metrics_figure.add_trace(
        big_ass_number_with_row(
            budgets.at["Rent", "envelope_out_amount"],
            "Envelope<br>Out",
            0,
            2,
            "Rent_envelope_out"
        )
    )
    rent_metrics_figure.add_trace(
        bullet_indicator(
            budgets.at["Rent", "budget_monthly_amount"],
            budgets.at["Rent", "budget_monthly_amount"],
            budgets.at["Rent", "actual_monthly_amount"]
        )
    )
    st.plotly_chart(rent_metrics_figure, use_container_width=True)

    st.header('Entertainment')

    entertainment_metrics_figure = go.Figure()
    entertainment_metrics_figure.update_layout(
        grid = {'rows': 2, 'columns': 3},
        margin=dict(t=0, b=0, l=0, r=0),
        height = 170
    )
    entertainment_metrics_figure.add_trace(
        big_ass_number_with_row(
            budgets.at["Entertainment", "envelope_in_amount"],
            "Envelope<br>In",
            0,
            0,
            "entertainment_envelope_in"
        )
    )
    entertainment_metrics_figure.add_trace(
        big_ass_number_with_row_with_delta(
            budgets.at["Entertainment", "actual_monthly_amount"],
            budgets.at["Entertainment", "delta_monthly_amount"],
            "Spent",
            0,
            1,
            'entertainment_spend_indicator'
        )
    )
    entertainment_metrics_figure.add_trace(
        big_ass_number_with_row(
            budgets.at["Entertainment", "envelope_out_amount"],
            "Envelope<br>Out",
            0,
            2,
            "entertainment_envelope_out"
        )
    )
    entertainment_metrics_figure.add_trace(
        bullet_indicator(
            budgets.at["Entertainment", "budget_monthly_amount"],
            budgets.at["Entertainment", "budget_monthly_amount"],
            budgets.at["Entertainment", "actual_monthly_amount"]
        )
    )
    st.plotly_chart(entertainment_metrics_figure)

with gap1_col:
    st.html(
        '''
            <div class="divider-vertical-line"></div>
            <style>
                .divider-vertical-line {
                    border-left: 2px solid rgba(49, 51, 63, 0.2);
                    height: 400px;
                    margin: auto;
                }
            </style>
        '''
    )

with col2:
    st.header("Moving Transport")
    moving_transport_metrics_figure = go.Figure()
    moving_transport_metrics_figure.update_layout(
        grid = {'rows': 2, 'columns': 3},
        margin=dict(t=0, b=0, l=0, r=0),
        height = 170
    )
    moving_transport_metrics_figure.add_trace(
        big_ass_number_with_row(
            budgets.at["Moving Transport", "envelope_in_amount"],
            "Envelope<br>In",
            0,
            0,
            "moving_transport_envelope_in"
        )
    )
    moving_transport_metrics_figure.add_trace(
        big_ass_number_with_row_with_delta(
            budgets.at["Moving Transport", "actual_monthly_amount"],
            budgets.at["Moving Transport", "delta_monthly_amount"],
            "Spent",
            0,
            1, 
            "Moving Transport"
        )
    )
    moving_transport_metrics_figure.add_trace(
        big_ass_number_with_row(
            budgets.at["Moving Transport", "envelope_out_amount"],
            "Envelope<br>Out",
            0,
            2,
            "moving_transport_envelope_out"
        )
    )
    moving_transport_metrics_figure.add_trace(
        bullet_indicator(
            budgets.at["Moving Transport", "budget_monthly_amount"],
            budgets.at["Moving Transport", "budget_monthly_amount"],
            budgets.at["Moving Transport", "actual_monthly_amount"]
        )
    )

    st.plotly_chart(moving_transport_metrics_figure)

    st.header('Eat Out')

    eatout_metrics_figure = go.Figure()
    eatout_metrics_figure.update_layout(
        grid = {'rows': 2, 'columns': 3},
        margin=dict(t=0, b=0, l=0, r=0),
        height = 170
    )
    eatout_metrics_figure.add_trace(
        big_ass_number_with_row(
            budgets.at["Eat Out", "envelope_in_amount"],
            "Envelope<br>In",
            0,
            0,
            "eatout_envelope_in"
        )
    )
    eatout_metrics_figure.add_trace(
        big_ass_number_with_row_with_delta(
            budgets.at["Eat Out", "actual_monthly_amount"],
            budgets.at["Eat Out", "delta_monthly_amount"],
            "Spent",
            0,
            1, 
            "eatout_spend_indicator"
        )
    )
    eatout_metrics_figure.add_trace(
        big_ass_number_with_row(
            budgets.at["Eat Out", "envelope_out_amount"],
            "Envelope<br>Out",
            0,
            2,
            "eatout_envelope_out"
        )
    )
    eatout_metrics_figure.add_trace(
        bullet_indicator(
            budgets.at["Eat Out", "budget_monthly_amount"],
            budgets.at["Eat Out", "budget_monthly_amount"],
            budgets.at["Eat Out", "actual_monthly_amount"]
        )
    )
    st.plotly_chart(eatout_metrics_figure)

with gap2_col:
    st.html(
        '''
            <div class="divider-vertical-line"></div>
            <style>
                .divider-vertical-line {
                    border-left: 2px solid rgba(49, 51, 63, 0.2);
                    height: 340px;
                    margin: auto;
                }
            </style>
        '''
    )

with col3:
    st.header("Stuff")
    stuff_metrics_figure = go.Figure()
    stuff_metrics_figure.update_layout(
        grid = {'rows': 2, 'columns': 3},
        margin=dict(t=0, b=0, l=0, r=0),
        height = 170
    )
    stuff_metrics_figure.add_trace(
        big_ass_number_with_row(
            budgets.at["Stuff", "envelope_in_amount"],
            "Envelope<br>In",
            0,
            0,
            "stuff_envelope_in"
        )
    )
    stuff_metrics_figure.add_trace(
        big_ass_number_with_row_with_delta(
            budgets.at["Stuff", "actual_monthly_amount"],
            budgets.at["Stuff", "delta_monthly_amount"],
            "Spent",
            0,
            1, 
            "stuff_spend_indicator"
        )
    )
    stuff_metrics_figure.add_trace(
        big_ass_number_with_row(
            budgets.at["Stuff", "envelope_out_amount"],
            "Envelope<br>Out",
            0,
            2,
            "stuff_envelope_out"
        )
    )
    stuff_metrics_figure.add_trace(
        bullet_indicator(
            budgets.at["Stuff", "budget_monthly_amount"],
            budgets.at["Stuff", "budget_monthly_amount"],
            budgets.at["Stuff", "actual_monthly_amount"]
        )
    )
    st.plotly_chart(stuff_metrics_figure)

    st.header('Groceries')

    groceries_metrics_figure = go.Figure()
    groceries_metrics_figure.update_layout(
        grid = {'rows': 2, 'columns': 3},
        margin=dict(t=0, b=0, l=0, r=0),
        height = 170
    )
    groceries_metrics_figure.add_trace(
        big_ass_number_with_row(
            budgets.at["Grocery", "envelope_in_amount"],
            "Envelope<br>In",
            0,
            0,
             "groceries_envelope_in"
        )
    )
    groceries_metrics_figure.add_trace(
        big_ass_number_with_row_with_delta(
            budgets.at["Grocery", "actual_monthly_amount"],
            budgets.at["Grocery", "delta_monthly_amount"],
            "Spent",
            0,
            1, 
            "groceries_spend_indicator"
        )
    )
    groceries_metrics_figure.add_trace(
        big_ass_number_with_row(
            budgets.at["Grocery", "envelope_out_amount"],
            "Envelope<br>Out",
            0,
            2,
            "groceries_envelope"
        )
    )
    groceries_metrics_figure.add_trace(
        bullet_indicator(
            budgets.at["Grocery", "budget_monthly_amount"],
            budgets.at["Grocery", "budget_monthly_amount"],
            budgets.at["Grocery", "actual_monthly_amount"]
        )
    )
    st.plotly_chart(groceries_metrics_figure)

#region Individual Transaction Selection
options = budgets.index.tolist()
options.append("FUTURE")
choice = st.radio(
    label="Select a category",
    options= options,
    horizontal=True,
    key="transactions"
)

# If this the full year, extract year from tag
if is_full_year_selected:
    tag_month_selected = tag_year_selected

trans = get_db_transactions(tag_month_selected, choice)
st.dataframe(trans.style.apply(highlight_future_transactions, axis=1))
#endregion