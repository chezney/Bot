
import sqlite3
import numpy as np
import pandas as pd
from q_learning import state_space_size, action_space

# Function to save the Q-table to the database
def save_q_table(q_table, db_path='q_learning.db'):
    conn = sqlite3.connect(db_path)
    # Save the Q-table with the index labeled as 'state'
    q_table.to_sql('q_table', conn, if_exists='replace', index=True, index_label='state')
    conn.close()

# Function to load the Q-table from the database
def load_q_table(db_path='q_learning.db'):
    conn = sqlite3.connect(db_path)
    try:
        # Load the Q-table and set the 'state' column as the index
        q_table = pd.read_sql('SELECT * FROM q_table', conn, index_col='state')
    except (sqlite3.OperationalError, pd.io.sql.DatabaseError) as e:
        # If the table does not exist, log the error and return None
        logging.error(f"Failed to load Q-table: {e}")
        q_table = None
    conn.close()
    return q_table

def fetch_data(query, db_path):
    conn = sqlite3.connect(db_path)
    data = pd.read_sql_query(query, conn)
    conn.close()
    return data
