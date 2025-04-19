# streamlit_app.py

import numpy as np
import pandas as pd
import streamlit as st
import sqlalchemy as sa
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from resources import *
import plotly.express as px

st.set_page_config(layout="wide")

# BEGINNING OF THE CODE

conn = get_db_connection()
sql = """
with step1 as (
select
    count(*) as day_count,
    ld.tag_where,
    bd.month_of_year_int,
    bd.month_of_year_name,
    bd.month_of_year_name_abbreviation,
    min(bd.the_date) as first_date,
    min(bd.day_of_month_int) as first_day,
    max(bd.day_of_month_int) as last_day
from
    landing.location_dates as ld
    inner join analytics_mart.dim_date as bd
        on bd.the_date between ld.begin_date and ld.end_date
group by
    ld.tag_where,
    bd.month_of_year_int,
    bd.month_of_year_name,
    bd.month_of_year_name_abbreviation
)

select
    tag_where || ' [' || last_day::varchar || ']' as group_header,
    tag_where || ' [' || first_day::varchar || ' to ' || last_day::varchar || ']' as hover_text,
    tag_where as color,
    day_count as y,
    month_of_year_int as x,
    month_of_year_name_abbreviation as x_name,
    row_number() over(partition by month_of_year_int order by first_date) as group_order
from step1
order by
    month_of_year_int, group_order

"""

locations = pd.read_sql_query(sql, conn)

hover_data = {
    "color": False,
    "group_name": True,
    "x_name": False,
    "y": False
}
fig = px.bar(
    locations,
    x="x_name",
    y="y",
    color="color",
    #hover_data=hover_data,
    barmode = 'stack',
    text="group_header",
    custom_data=["hover_text"]
)
fig.layout.update(
    showlegend=False,
    title="Locations",
    yaxis_title=None,
    xaxis_title=None,
)
# hide the y axis
fig.update_yaxes(showticklabels=False)
fig.update_traces(hovertemplate='<b>%{customdata[0]}</b>')
fig.update_layout(hoverlabel=dict(bgcolor="white",
                                  font=dict(size=16, family="Arial", color="black"),
                                  align="left"))
st.plotly_chart(fig, use_container_width=True)