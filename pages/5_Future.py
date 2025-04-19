import os
import pandas as pd
import streamlit as st
from streamlit import session_state as ss
import sqlalchemy as sa
from sqlalchemy.sql import text
from resources import *

def editor_changed():
    st.write("Edited Rows:", ss.de["edited_rows"])

    # loop through edited rows
    for key, row in ss.de["edited_rows"].items():
        id = key
        update_sql = []
        for col, new_value in row.items():
            update_sql.append("{} = '{}'".format(col, new_value))
        update_sql = ", ".join(update_sql)
        final_sql = "UPDATE warehouse.landing.learn_update SET {} WHERE id = {}".format(update_sql, id)
        st.write(final_sql)

        # run the final_sql statement
        with conn.begin() as transaction:
            transaction.execute(text(final_sql))
            transaction.commit()

        # clear out the ss.de        
        ss.de["edited_rows"] = {}

def insert_row(my_dict):
    insert_sql = "INSERT INTO warehouse.landing.quicken_future (" + ", ".join(my_dict.keys()) + ") VALUES (" + ", ".join([f"'{v}'" for v in my_dict.values()]) + ")"
    st.write(insert_sql)
    with conn.begin() as transaction:
        transaction.execute(text(insert_sql))
        transaction.commit()


st.set_page_config(
    page_title="Streamlit and PostgreSQL",
    page_icon="📊",
    layout="wide",
)


conn = get_db_connection()
df = pd.read_sql_query("SELECT * FROM warehouse.landing.learn_update", conn)
# set the index column of df to id
#df.set_index("id", inplace=True)
# add df to session state



# my_dict = {}
# # create variable with the column count from df
# num_cols = len(df.columns)

# cols = st.columns(num_cols)

# counter = 0
# for col in df.columns:
#     if col == "id":
#         continue
#     with cols[counter]:
#         my_dict[col] =  st.text_input(label=col, max_chars=5, key=f'{col}')
#     counter += 1

# st.button("Insert", on_click=insert_row, key="insert", args=(my_dict,))







# Display with data_editor
edited_df = st.data_editor(df, key="de", num_rows="dynamic")  # Allow adding/deleting rows

# --- Detect changes ---
if edited_df is not None:
    # Find added rows
    new_rows = edited_df[~edited_df.index.isin(df.index)]

    # Find deleted rows
    deleted_rows = df[~df.index.isin(edited_df.index)]

    # Find updated rows
    # get the edited rows
    edited_rows = ss.de["edited_rows"]
    st.write(edited_rows)

    #test if edited rows is empty
    
    #updated_rows = edited_df[df.index.isin(edited_df.index)]
    #st.write(updated_rows)
    #changed = df.compare(updated_rows)
    #st.write(changed)
    # --- Generate SQL statements ---
    with conn.connect() as conn:
        # Handle new rows (INSERT)
        if not new_rows.empty:
            new_rows.to_sql('your_table', conn, if_exists='append', index=False)

        # Handle deleted rows (DELETE)
        if not deleted_rows.empty:
            ids = tuple(deleted_rows['id'].tolist())
            conn.execute(f"DELETE FROM your_table WHERE id IN {ids}")

        # Handle updated rows (UPDATE)
        if len(edited_rows) > 0:
            #st.write(changed)
            for idx, row in edited_rows.items():
                # return the id column value from df using index idx
                id = df.at[idx, 'id']
                st.write(id)
                update_sql = []
                for col, new_value in row.items():
                    st.write(col, new_value)
                    update_sql.append("{} = '{}'".format(col, new_value))
                update_sql = ", ".join(update_sql)

                
                #set_clause = ", ".join([f"{col} = %s" for col in row.index])
                #values = tuple(row.values)
                st.write(update_sql)
                final_sql = text(f"UPDATE landing.learn_update SET {update_sql} WHERE id = {id}")
                st.write(final_sql)
                conn.execute(final_sql)

        conn.commit()

    st.success("Database updated successfully!")

