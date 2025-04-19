# streamlit_app.py

import os
import pandas as pd
import streamlit as st
import sqlalchemy as sa
from resources import *

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

# get connection parameters using st.secrets.
secrets = st.secrets["connections"]["postgres"]

def editor_changed():
    st.write("Edited Rows:", ss.de["edited_rows"])
    # loop through edited rows
    for key, value   in ss.de["edited_rows"].items():
        row = df.iloc[key]
        id = row["id"]
        update_sql = []
        for col, new_value in value.items():
            st.write(row[col], new_value)
            update_sql.append("{} = '{}'".format(col, new_value))
        update_sql = ", ".join(update_sql)
        final_sql = "UPDATE warehouse.travel.daily_location2 SET {} WHERE id = {}".format(update_sql, id)
        st.write(final_sql)
        cur = conn.cursor()
        cur.execute(final_sql) 
        conn.commit()

def get_and_clean_data():
    """
    Reads data from a CSV file, processes it to handle split transactions,
    and formats columns appropriately. The function performs the following:
    - Reads specified columns from a CSV file with specified data types.
    - Converts the 'postedOn' column to datetime format and filters rows based on date.
    - Initializes additional columns for transaction processing and tagging.
    - Handles split transactions by propagating values from previous valid rows.
    - Splits the 'tags' column into separate tags and categorizes them.
    - Cleans and converts the 'amount' column to float.

    Returns:
        pd.DataFrame: A DataFrame containing cleaned and processed transaction data.
    """
    cols = ['account', 'state', 'postedOn', 'payee', 'category', 'tags', 'notes', 'amount']
    col_dtype = {
        'account': str,
        'state': str,
        'postedOn': str,
        'payee': str,
        'category': str,
        'tags': str,
        'notes': str,
        'amount': str,
    }
    
    # find the latest dated file in ~/Downloads that begins with "quicken"
    file_dir = "/Users/erickofoid/Downloads"
    file_list = [os.path.join(file_dir, f) for f in os.listdir(file_dir) if f.startswith("quicken")]
    file_list = sorted(file_list, key=os.path.getmtime, reverse=True)
    latest_file = file_list[0]
    st.write(latest_file)
    df = pd.read_csv(latest_file, usecols=cols, dtype=col_dtype, engine='python', dtype_backend='numpy_nullable')
    
    df.columns = df.columns.str.lower()
    df['postedon'] = pd.to_datetime(df['postedon'])

    row_number = 8
    # Transaction ID is used to group transactions that are split
    df.insert(row_number, 'budget_category', None)
    df.insert(row_number + 1, 'tag_array', df['tags'].str.split('/'))
    df.insert(row_number + 2, 'tag_when', None)
    df.insert(row_number + 3, 'tag_where', None)
    df.insert(row_number + 4, 'tag_what', None)
    df.insert(row_number + 5, 'tag_who', None)
    df.insert(row_number + 6, 'tag_unknown', None)
    df.insert(row_number + 7, 'transaction_id', df.index)
    df.insert(row_number + 8, 'row_id', df.index)
    df.insert(row_number + 9, 'is_split', False)

    known_tags = get_db_tags()
    known_categories = get_db_categories()
    
    # handle split transactions
    prev_id = 0
    prev_account = None
    prev_state = None
    prev_postedon = None
    prev_payee = None
    prev_notes = None

    # loop through the dataframe and handle split transactions
    for index, row in df.iterrows():
        account = row['account']
        category = row.category

        if category == 'SPLIT':
            df.loc[index, 'is_split'] = True

        known_category = known_categories[known_categories['category'] == category]
        if not known_category.empty:
            df.loc[index, 'budget_category'] = known_category['budget_category'].values[0]
        else:
            df.loc[index, 'budget_category'] = 'Unknown'

        # if the account is NaN, set the transaction_id to the previous transaction_id
        if pd.isnull(account):
            df.loc[index, 'transaction_id'] = prev_id
            df.loc[index, 'account'] = prev_account
            df.loc[index, 'state'] = prev_state
            df.loc[index, 'postedon'] = prev_postedon
            df.loc[index, 'payee'] = prev_payee
            df.loc[index, 'is_split'] = True
            df.loc[index, 'notes'] = prev_notes
        else:
            prev_id = row['transaction_id']
            prev_account = row['account']
            prev_state = row['state']
            prev_postedon = row['postedon']
            prev_payee = row['payee']
            prev_notes = row['notes']

        if not pd.isnull(row['tags']):
            for tag in row['tag_array']:
                # match tag to known tags
                known_tag = known_tags[known_tags['tag'] == tag]

                if not known_tag.empty:
                    tag_category = known_tag.iloc[0]['category']
                    if tag_category == 'when':
                        df.loc[index, 'tag_when'] = tag
                    elif tag_category == 'where':
                        df.loc[index, 'tag_where'] = tag
                    elif tag_category == 'what':
                        df.loc[index, 'tag_what'] = tag
                    elif tag_category == 'who':
                        df.loc[index, 'tag_who'] = tag
                else:
                    df.loc[index, 'tag_unknown'] = tag

    # update the amount column to remove $ and ,
    amount_df = df['amount'].str.replace('$', '')
    amount_df = amount_df.str.replace(',', '')
    amount_df = amount_df.astype(float)
    df.loc[:, 'amount'] = amount_df

    df_temp = df.drop(columns='tags')

    return df_temp

def save_to_database():
    # create a dataframe.to_sql dtype parameter to specify the data type of each column
    dtype = {
        'account': sa.types.VARCHAR(length=50),
        'state': sa.types.VARCHAR(length=50),
        'postedon': sa.types.DATE,
        'payee': sa.types.VARCHAR(length=100),
        'category': sa.types.VARCHAR(length=50),
        'notes': sa.types.VARCHAR(length=1000),
        'amount': sa.types.NUMERIC,
        'budget_category': sa.types.VARCHAR(length=50),
        'tag_array': sa.types.ARRAY(sa.types.VARCHAR(length=50)),
        'tag_when': sa.types.VARCHAR(length=50),
        'tag_where': sa.types.VARCHAR(length=50),
        'tag_what': sa.types.VARCHAR(length=50),
        'tag_who': sa.types.VARCHAR(length=50),
        'tag_unknown': sa.types.VARCHAR(length=50),
        'transaction_id': sa.types.INTEGER,
        'row_id': sa.types.INTEGER,
        'is_split': sa.types.BOOLEAN,
    }

    # write the dataframe to the temp table
    df.to_sql(name="quicken_temp", schema="landing", con=conn_pg, dtype=dtype, if_exists="replace", index=False)
    trunc_sql = "truncate table landing.quicken"

    insert_sql = "insert into landing.quicken select * from landing.quicken_temp"

    conn2 = sa.create_engine(
        f"postgresql+psycopg2://{secrets['username']}:{secrets['password']}@{secrets['host']}/{secrets['database']}"
    )

    with conn2.begin() as connection:
        connection.execute(sa.text(trunc_sql))
        connection.execute(sa.text(insert_sql))
    
    st.write("Dataframe is loaded into the database")

def compare_tags():
    # get distinct list of tags from df
    tags = df[df['tag_array'].notnull()]['tag_array'].explode().unique().tolist()
    # remove nan from the list
    tags = [tag for tag in tags if tag != 'nan']
    st.write(tags)
    tags.sort()

    known_tags = get_db_tags()

    # compare the known tags with the distinct list of tags from df
    difference = list(set(tags).difference(set(known_tags['tag'])))
    # if there is a difference, write the difference to the streamlit app
    if difference:
        st.write('Difference in tags:')
        st.write(difference)
    else:
        st.write('No difference in tags')

def compare_categories():
    # get distinct list of categories from df do not include anything that begins with "Old
    categories = df['category'].unique().tolist()
    #remove categories that begin with "Old"
    categories = [cat for cat in categories if not cat.startswith('Old')]
    categories.sort()

    known_categories = get_db_categories()

    difference = list(set(categories).difference(set(known_categories['category'])))
    # if there is a difference, write the difference to the streamlit app
    if difference:
        st.write('Difference in categories:')
        st.write(difference)
    else:
        st.write('No difference in categories')

st.set_page_config(layout="wide")

with st.sidebar:
    st.button('Save to database', on_click=save_to_database)
    st.button('Compare Categories', on_click=compare_categories)
    st.button('Compare Tags', on_click=compare_tags)

conn_pg = get_db_connection() 
df = get_and_clean_data()
st.dataframe(df)

# get list of unknown tags from tag_unknown column where the unknown tag is not null
unknown_tags = df[df['tag_unknown'].notnull()]['tag_unknown'].unique().tolist()

# get list of categories where the budget category is unknown
unknown_categories = df[df['budget_category'] == 'Unknown']['category'].unique().tolist()

# if unknown tags is not empty, write the unknown to the streamlit app
if unknown_tags:
    unknown_tags.sort()
    st.write('Unknown tags:')
    st.write(unknown_tags)
else:
    st.write('No unknown tags')

if unknown_categories:
    unknown_categories.sort()
    st.write('Unknown categories:')
    st.write(unknown_categories)
else:
    st.write('No unknown categories')
