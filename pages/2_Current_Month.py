# streamlit_app.py

import numpy as np
import pandas as pd
import streamlit as st
import sqlalchemy as sa
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from resources import *

st.set_page_config(layout="wide")

# BEGINNING OF THE CODE
current_month_tag = str(pd.to_datetime('now').year) + '-' + str(pd.to_datetime('now').month).zfill(2)
numbers_df = get_db_budgets_for_month(current_month_tag)
daily_df = get_db_daily()

total = dollar_format(numbers_df.at['Total', 'actual_monthly_amount'])
annual = dollar_format(numbers_df.at['Annual', 'actual_monthly_amount'])
header = f"""Total Spend {total} Annual Spend {annual}"""
st.header(header)

top_col1, top_gap1_col, top_col2, top_gap_col2, top_col3 = st.columns([.29, .01, .29, .01, .3])

with top_col1:
    st.subheader(f"Rent ({dollar_format(numbers_df.at['Rent', 'budget_monthly_amount'])})")   
    rent_metrics_figure = go.Figure()
    rent_metrics_figure.add_trace(
        big_ass_number_with_row_with_delta(
            num_value = numbers_df.at["Rent", "actual_monthly_amount"],
            delta_value = numbers_df.at["Rent", "delta_monthly_amount"],
            title_value = "Rent",
            row = 0,
            column = 0,
            key_name = "rent_spend"
        )
    )
    rent_metrics_figure.update_layout(
        grid = {'rows': 1, 'columns': 1},
        margin=dict(t=0, b=0, l=0, r=0),
        height=275
    )
    st.plotly_chart(rent_metrics_figure)

with top_gap1_col:
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

with top_col2:
    st.subheader(f"Moving Transport ({dollar_format(numbers_df.at['Moving Transport', 'budget_monthly_amount'])})")
    moving_transport_metrics_figure = go.Figure()
    moving_transport_metrics_figure.update_layout(
        grid = {'rows': 1, 'columns': 1},
        margin=dict(t=0, b=0, l=0, r=0),
        height=275
    )
    moving_transport_metrics_figure.add_trace(
        big_ass_number_with_row_with_delta(
            num_value = numbers_df.at["Moving Transport", "actual_monthly_amount"],
            delta_value = numbers_df.at["Moving Transport", "delta_monthly_amount"],
            title_value = "Moving<br>Transport",
            row = 0,
            column = 0,
            key_name = "moving_transport_spend"
        )
    )
    st.plotly_chart(moving_transport_metrics_figure)

with top_gap_col2:
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

with top_col3:
    #region Stuff Metrics
    st.subheader(f"Stuff ({dollar_format(numbers_df.at['Stuff', 'budget_monthly_amount'])})")
    stuff_metrics_figure = go.Figure()
    stuff_metrics_figure.update_layout(
        grid = {'rows': 2, 'columns': 4},
        margin=dict(t=0, b=0, l=0, r=0),
        height=275
    )
    stuff_metrics_figure.add_trace(
        big_ass_number_with_row(
            numbers_df.at["Stuff", "actual_monthly_amount"],
            f"MTD<br>Actual<br>Spend", 0, 0, 'stuff_spend_indicator'
        )
    )
    stuff_metrics_figure.add_trace(
        big_ass_number_with_row(
            numbers_df.at["Stuff", "budget_mtd_amount"],
            f"MTD<br>Budget", 0, 1, 'stuff_budget_indicator'
        )
    )
    stuff_metrics_figure.add_trace(
        big_ass_number_with_row_with_delta(
            numbers_df.at["Stuff", "actual_daily_average_amount"],
            numbers_df.at["Stuff", "delta_daily_average_amount"],
            f"Daily<br>Average<br>Spend", 0, 2, 'stuff_daily_average_spend_indicator'
        )
    )
    stuff_metrics_figure.add_trace(
        big_ass_number_with_row(
            numbers_df.at["Stuff", "actual_daily_average_remaining_amount"],
            f"Daily<br>Budget<br>Remaining", 0, 3, 'stuff_remaining_indicator'
        )
    )
    stuff_metrics_figure.add_trace(
        bullet_indicator(
            numbers_df.at["Stuff", "budget_monthly_amount"],
            numbers_df.at["Stuff", "budget_mtd_amount"],
            numbers_df.at["Stuff", "actual_monthly_amount"]
        )
    )
    st.plotly_chart(stuff_metrics_figure)
    #endregion

bottom_col1, bottom_gap_col1, bottom_col2, bottom_gap_col2, bottom_col3 = st.columns([.29, .01, .29, .01, .3])

with bottom_col1:
    #region Entertainment Metrics
    st.subheader(f"Entertainment ({dollar_format(numbers_df.at['Entertainment', 'budget_monthly_amount'])})")
    entertainment_metrics_figure = go.Figure()
    entertainment_metrics_figure.add_trace(
        big_ass_number_with_row(
            numbers_df.at["Entertainment", "actual_monthly_amount"],
            f"MTD<br>Actual<br>Spend", 0, 0, 'entertainment_spend_indicator'
        )
    )
    entertainment_metrics_figure.add_trace(
        big_ass_number_with_row(
            numbers_df.at["Entertainment", "budget_mtd_amount"],
            f"MTD<br>Budget", 0, 1, 'entertainment_budget_indicator'
        )
    )
    entertainment_metrics_figure.add_trace(
        big_ass_number_with_row_with_delta(
            numbers_df.at["Entertainment", "actual_daily_average_amount"],
            numbers_df.at["Entertainment", "delta_daily_average_amount"],
            f"Daily<br>Average<br>Spend", 0, 2, 'entertainment_daily_average_spend_indicator'
        )
    )
    entertainment_metrics_figure.add_trace(
        big_ass_number_with_row(
            numbers_df.at["Entertainment", "actual_daily_average_remaining_amount"],
            f"Daily<br>Budget<br>Remaining", 0, 3, 'entertainment_remaining_indicator'
        )
    )
    entertainment_metrics_figure.add_trace(
        bullet_indicator(
            numbers_df.at["Entertainment", "budget_monthly_amount"],
            numbers_df.at["Entertainment", "budget_mtd_amount"],
            numbers_df.at["Entertainment", "actual_monthly_amount"]
        )
    )
    entertainment_metrics_figure.update_layout(
        grid = {'rows': 2, 'columns': 4},
        margin=dict(t=0, b=0, l=0, r=0),
        height = 275
    )
    st.plotly_chart(entertainment_metrics_figure)
    #endregion

    #region Entertainment Daily Histogram
    # Daily Data
    entertainment_daily_df = daily_df.query('budget_category == "Entertainment"').copy()
    # get the maximum of the daily average column
    entertainment_daily_average_max = entertainment_daily_df['daily_average'].max()
    entertainment_daily_average_min = entertainment_daily_df['daily_average'].min()

    entertainment_bar_chart = go.Bar(
        x = entertainment_daily_df['the_date'],
        y = entertainment_daily_df['spend'],
        name = 'Entertainment_Bar',
        marker_color = 'rgb(50, 102, 193)'
    )
    entertainment_line_chart = go.Line(
        x = entertainment_daily_df['the_date'],
        y = entertainment_daily_df['daily_average'],
        name = 'Entertainment_Line'
    )
    entertainment_pre_indicator = go.Indicator(
        mode = "number",
        value = numbers_df.at["Entertainment", "actual_pre_month_amount"],
        title = {'text': f"Pre<br> ", 'font': PRE_TITLE_FONT},
        number = {'valueformat': ROUNDED_DOLLAR_FORMAT, 'font': PRE_FONT},
        align = 'center'
    )
    fig = make_subplots(
        rows=1,
        cols=2,
        specs=[[{"type": "indicator"}, {"type": "xy"}]],
        column_widths=[.2, .8],
        horizontal_spacing = .1,
        vertical_spacing = .1,
    )
    fig.add_trace(entertainment_pre_indicator, row=1, col=1)
    fig.add_trace(entertainment_bar_chart, row=1, col=2)
    fig.add_trace(entertainment_line_chart, row=1, col=2)
    fig.update_layout(
        margin=dict(t=0, b=0, l=0, r=0),
        height = 120,
        showlegend=False
    )
    fig.update_xaxes(
        tickangle=-45,
        tickformat="%b - %d",
    )
    st.plotly_chart(fig, use_container_width=True)
    #endregion

with bottom_gap_col1:
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

with bottom_col2:
    #region Eat Out Metrics
    st.subheader(f"Eat Out ({dollar_format(numbers_df.at['Eat Out', 'budget_monthly_amount'])})")
    eatout_metrics_figure = go.Figure()
    eatout_metrics_figure.update_layout(
        grid = {'rows': 2, 'columns': 4},
        margin=dict(t=0, b=0, l=0, r=0),
        height = 275
    )
    eatout_metrics_figure.add_trace(
        big_ass_number_with_row(
            numbers_df.at["Eat Out", "actual_monthly_amount"],
            f"MTD<br>Actual<br>Spend", 0, 0,'eatout_spend_indicator'
        )
    )
    eatout_metrics_figure.add_trace(
        big_ass_number_with_row(
            numbers_df.at["Eat Out", "budget_mtd_amount"],
            f"MTD<br>Budget", 0, 1, 'eatout_budget_indicator'
        )
    )
    eatout_metrics_figure.add_trace(
        big_ass_number_with_row_with_delta(
            numbers_df.at["Eat Out", "actual_daily_average_amount"],
            numbers_df.at["Eat Out", "delta_daily_average_amount"],
            f"Daily<br>Average<br>Spend", 0, 2, 'eatout_daily_average_spend_indicator'
        )
    )
    eatout_metrics_figure.add_trace(
        big_ass_number_with_row(
            numbers_df.at["Eat Out", "actual_daily_average_remaining_amount"],
            "Daily<br>Budget<br>Remaining", 0, 3, 'eatout_remaining_indicator'
        )
    )
    eatout_metrics_figure.add_trace(
        bullet_indicator(
            numbers_df.at["Eat Out", "budget_monthly_amount"],
            numbers_df.at["Eat Out", "budget_mtd_amount"],
            numbers_df.at["Eat Out", "actual_monthly_amount"]
        )
    )
    st.plotly_chart(eatout_metrics_figure)
    #endregion

    #region Eat Out Daily Histogram
    eatout_daily_df = daily_df.query('budget_category == "Eat Out"').copy()

    eatout_daily_figure = go.Figure()
    eatout_bar_chart = go.Bar(
        x = eatout_daily_df['the_date'],
        y = eatout_daily_df['spend'],
        name = 'Eat Out',
        marker_color = 'rgb(50, 102, 193)',
    )
    eatout_line_chart = go.Line(
        x = eatout_daily_df['the_date'],
        y = eatout_daily_df['daily_average'],
        name = 'Eat Out_Line'
    )
    eatout_daily_figure.add_trace(eatout_bar_chart)
    eatout_daily_figure.add_trace(eatout_line_chart)
    eatout_daily_figure.update_xaxes(
        tickangle=-45,
        tickformat="%b - %d",
    )
    eatout_daily_figure.update_layout(
        margin=dict(t=0, b=0, l=0, r=0),
        height = 125,
        showlegend=False
    )
    st.plotly_chart(eatout_daily_figure)
    #endregion

with bottom_gap_col2:
    st.html(
        '''
            <div class="divider-vertical-line"></div>
            <style>
                .divider-vertical-line {
                    border-left: 2px solid rgba(49, 51, 63, 0.2);
                    height: 400;
                    margin: auto;
                }
            </style>
        '''
    )

with bottom_col3:
    #region Groceries Metrics
    st.subheader(f"Grocery ({dollar_format(numbers_df.at['Grocery', 'budget_monthly_amount'])})")
    groceries_metrics_figure = go.Figure()
    groceries_metrics_figure.update_layout(
        grid = {'rows': 2, 'columns': 4},
        margin=dict(t=0, b=0, l=0, r=0),
        height = 275
    )
    groceries_metrics_figure.add_trace(
        big_ass_number_with_row(
            numbers_df.at["Grocery", "actual_monthly_amount"],
            f"MTD<br>Actual<br>Spend", 0, 0, 'groceries_spend_indicator'
        )
    )
    groceries_metrics_figure.add_trace(
        big_ass_number_with_row(
            numbers_df.at["Grocery", "budget_mtd_amount"],
            f"MTD<br>Budget", 0, 1, 'groceries_budget_indicator'
        )
    )
    groceries_metrics_figure.add_trace(
        big_ass_number_with_row_with_delta(
            numbers_df.at["Grocery", "actual_daily_average_amount"],
            numbers_df.at["Grocery", "delta_daily_average_amount"],
            f"Daily<br>Average<br>Spend", 0, 2, 'groceries_daily_average_spend_indicator'
        )
    )
    groceries_metrics_figure.add_trace(
        big_ass_number_with_row(
            numbers_df.at["Grocery", "actual_daily_average_remaining_amount"],
            f"Daily<br>Budget<br>Remaining", 0, 3, 'groceries_remaining_indicator'
        )
    )
    groceries_metrics_figure.add_trace(
        bullet_indicator(
            numbers_df.at["Grocery", "budget_monthly_amount"],
            numbers_df.at["Grocery", "budget_mtd_amount"],
            numbers_df.at["Grocery", "actual_monthly_amount"]
        )
    )
    st.plotly_chart(groceries_metrics_figure)
    #endregion

    #region Groceries Daily Histogram
    groceries_daily_df = daily_df.query('budget_category == "Grocery"').copy()

    groceries_daily_figure = go.Figure()
    groceries_daily_figure.update_layout(
        margin=dict(t=0, b=0, l=0, r=0),
        height = 125,
        showlegend=False
    )
    groceries_bar_chart = go.Bar(
        x = groceries_daily_df['the_date'],
        y = groceries_daily_df['spend'],
        name = 'Groceries_Bar',
        marker_color = 'rgb(50, 102, 193)'
    )
    groceries_line_chart = go.Line(
        x = groceries_daily_df['the_date'],
        y = groceries_daily_df['daily_average'],
        name = 'Groceries_Line'
    )
    groceries_daily_figure.add_trace(groceries_bar_chart)
    groceries_daily_figure.add_trace(groceries_line_chart)
    groceries_daily_figure.update_xaxes(
        tickangle=-45,
        tickformat="%b - %d",
    )
    st.plotly_chart(groceries_daily_figure)
    #endregion

#region Individual Transaction Selection
options = numbers_df.index.tolist()
options.append("FUTURE")
transaction_category_selected = st.radio(label="Select a category", options=options, horizontal=True)

transactions_df = get_db_transactions(current_month_tag, transaction_category_selected)
st.dataframe(
    transactions_df.style.apply(highlight_future_transactions, axis=1),
    column_config={
        "is_split": None,
        "total_accum": None,
        "budget_category": None,
        "amount": st.column_config.NumberColumn(
            "Amount",
            min_value=0,
            max_value=1000000,
            format="$%d"
        ),
        "month_accum": st.column_config.NumberColumn(
            "Month Accum",
            min_value=0,
            max_value=1000000,
            format="$%d"
        )
    }
)
#endregion