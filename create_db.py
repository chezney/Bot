import sqlite3
from q_learning import state_space_size

def create_database(db_path):
    # Connect to the new database. If it doesn't exist, it will be created.
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create the Q-table schema
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS q_table (
        state INTEGER PRIMARY KEY,
        buy REAL,
        sell REAL,
        hold REAL
    )
    ''')
    
    # Initialize the Q-table with default values for all states
    for state in range(state_space_size):
        cursor.execute('''
        INSERT INTO q_table (state, buy, sell, hold) VALUES (?, 0, 0, 0)
        ''', (state,))
    
    # Commit the changes and close the connection
    conn.commit()
    conn.close()

if __name__ == '__main__':
    # Define the path for the new database
    new_db_path = 'q_learning.db'
    # Call the function to create the database and Q-table
    create_database(new_db_path)
