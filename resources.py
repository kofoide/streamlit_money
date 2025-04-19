import numpy as np
import pandas as pd
import streamlit as st
import sqlalchemy as sa
import plotly.graph_objects as go

#region Constants
ROUNDING = 0
METRIC_FONT = {'size': 40}
METRIC_TITLE_FONT = {'size': 15, 'weight': 'bold', 'color': 'black'}
METRIC_Y = [.25, 1]
BULLET_Y = [0, .2]
ROUNDED_DOLLAR_FORMAT = "$,.0f"

PRE_FONT = {'size': 12}
PRE_TITLE_FONT = {'size': 15, 'weight': 'bold', 'color': 'black'}
#endregion

def dollar_format(num):
    return '\${:,.0f}'.format(num)

def dollar_format_grid(num):
    return '${:,.0f}'.format(num)

def get_db_connection():
    # pulls from the secrets.toml file in the .streamlit directory
    secrets = st.secrets["connections"]["postgres"]
    conn = sa.create_engine(
        f"postgresql://{secrets['username']}:{secrets['password']}@{secrets['host']}/{secrets['database']}"
    )
    return conn

def get_db_tags():
    conn = get_db_connection()
    tags = pd.read_sql_query("select * from warehouse.money.stg_landing__quicken_tag", conn)

    return tags

def get_db_categories():
    conn = get_db_connection()
    categories = pd.read_sql_query("select * from warehouse.money.stg_landing__quicken_category", conn)

    return categories

def get_db_budget_categories():
    conn = get_db_connection()
    categories = pd.read_sql_query("select * from warehouse.money.stg_landing__quicken_budget where is_budgeted", conn)

    return categories

def get_db_transactions_month(month_tag):
    conn = get_db_connection()
    sql = f"""select * from warehouse.money.quicken_transactions where tag_when = '{month_tag}'"""
    
    transactions = pd.read_sql_query(
        sql,
        conn,
        parse_dates=['postedon', 'tag_month']
    )

    return transactions

def get_db_transactions_year(year_tag):
    conn = get_db_connection()
    sql = f"""
    select *
    from landing.quicken as qt
    where
        qt.tag_when = '{year_tag}'
    """
    transactions = pd.read_sql_query(sql, conn)

    return transactions

def get_db_budgets_for_month(selected_tag_month):
    conn = get_db_connection()
    sql = f"""
    select *
    from warehouse.money.budget_numbers_all_months
    where tag_month = '{selected_tag_month}'
    order by budget_sort_order
    """
    df = pd.read_sql_query(sql, conn)
    df.set_index("budget_category", inplace=True)

    return df

def get_db_budgets_for_year_and_category(selected_tag_year, budget_category):
    conn = get_db_connection()

    sql = f"""
    select *
    from warehouse.money.budget_numbers_all_months
    where
        tag_year = {selected_tag_year}
        and budget_category = '{budget_category}'
    order by budget_sort_order
    """
    df = pd.read_sql_query(sql, conn)
    df.set_index("tag_month", inplace=True)

    return df

def get_db_transactions(tag, category):
    conn = get_db_connection()

    category_where_sql = ""
    if category == 'Total':
        category_where_sql = ""
    elif category == 'FUTURE':
        category_where_sql = " and state = 'FUTURE' "
    else:
        category_where_sql = f" and budget_category = '{category}' "

    month_where_sql = ""
    if len(tag) > 4:
        tag_month = tag + '-01'
        month_where_sql = f" and tag_month = '{tag_month}' "
    else:
        month_where_sql = f" and tag_year = '{tag}'"
    
    sql = f"""
        select
            state,
            postedon,
            payee,
            budget_category,
            category,
            notes,
            tag_month,
            amount,
            sum(amount) over(partition by tag_month order by row_order rows between unbounded preceding and current row) as month_accum,
            sum(amount) over(order by row_order rows between unbounded preceding and current row) as total_accum,
            is_split
        from warehouse.money.quicken_transactions
        where 1 = 1
            {category_where_sql}
            {month_where_sql}
        order by row_order desc
    """

    df = pd.read_sql_query(sql, conn)
    # convert the amount column to dollar format
    #df['amount'] = df['amount'].apply(dollar_format_grid)
    #df['month_accum'] = df['month_accum'].apply(dollar_format_grid)
    #df['total_accum'] = df['total_accum'].apply(dollar_format_grid)
    return df

def get_db_months():
    conn = get_db_connection()
    sql = """
    select
        tag_month,
        month_first_date as the_date,
        month_relative_int
    from warehouse.money.tag_months
    order by month_first_date;
    """
    dates = pd.read_sql(sql, conn, parse_dates=['month_first_date'])
    return dates

def get_db_daily():
    conn = get_db_connection()
    df = pd.read_sql_query("select * from warehouse.money.daily_actuals", conn)
    return df

def big_ass_number_with_row(num_value, title_value, row, column, key_name):
    ban = go.Indicator(
        mode = "number",
        value = num_value,
        domain = {'y': METRIC_Y, 'row': row, 'column': column},
        title = {'text': f"{title_value}", 'font': METRIC_TITLE_FONT},
        number = {'valueformat': ROUNDED_DOLLAR_FORMAT, 'font': METRIC_FONT},
        name = key_name
    )
    return ban

def big_ass_number_with_row_with_delta(num_value, delta_value, title_value, row, column, key_name):
    ban = go.Indicator(
        mode = "number+delta",
        value = num_value,
        delta = {
            'reference': delta_value,
            'valueformat': ROUNDED_DOLLAR_FORMAT, 
            'increasing': {'color': "green"},
            'decreasing': {'color': "red"},
            'font': {'color': "darkblue"}
        },
        domain = {'y': METRIC_Y, 'row': row, 'column': column},
        title = {'text': f"{title_value}", 'font': METRIC_TITLE_FONT},
        number = {'valueformat': ROUNDED_DOLLAR_FORMAT, 'font': METRIC_FONT},
        name = key_name
    )
    return ban

def bullet_indicator(full_month_budget, mtd_budget, mtd_spend):
    bullet = go.Indicator(
        mode = "number+gauge+delta",
        gauge = {
            'shape': "bullet",
            'axis': {
                'range': [0, full_month_budget + full_month_budget/10],
                'tickprefix': "$"
            },
            'bar': {'color': "darkblue", 'thickness': 0.4},
            'steps': [
                {'range': [0, mtd_budget], 'color': "lightgray"}
            ],
            'threshold' : {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': full_month_budget}
        },
        value = mtd_spend,
        domain = {'x': [0, 1], 'y': BULLET_Y, 'row': 1},
        number = {'valueformat': ROUNDED_DOLLAR_FORMAT}
    )
    return bullet

def highlight_future_transactions(s):
    if s.state == "FUTURE":
        ret_val = ['background-color: azure']*len(s)
    elif s.is_split == True:
        ret_val = ['background-color: beige']*len(s)
    else:
        ret_val = ['background-color: transparent']*len(s)
    return ret_val

def get_db_all_transactions():
    conn = get_db_connection()
    df = pd.read_sql_query("select * from warehouse.money.quicken_transactions", conn)
    return df