import hmac
import hashlib
import time
import json
import sqlite3
from websocket import create_connection
import pandas as pd

# Your API key and secret
api_key = "4ecbe52cbb00a42a3ddcd2597b7974c6f4d181b2664bb780ae1dc29e86b9d51d"
api_secret = "cc5ddcb2a23b35ff39bd0107b0c8f1d8c9c36f09ada9a3b8195540fc1aeeec4e"

# Function to generate a signature for the VALR API
def generate_signature(api_secret, timestamp, verb, path, body=""):
    message = str(timestamp) + verb.upper() + path + body
    return hmac.new(api_secret.encode(), message.encode(), hashlib.sha512).hexdigest()

# Function to get headers for authentication
def get_auth_headers(path):
    timestamp = int(time.time() * 1000)
    signature = generate_signature(api_secret, timestamp, "GET", path)
    return {
        "X-VALR-API-KEY": api_key,
        "X-VALR-SIGNATURE": signature,
        "X-VALR-TIMESTAMP": str(timestamp)
    }

# Function to establish a WebSocket connection
def connect_to_valr_websocket(path, headers):
    ws = create_connection(f"wss://api.valr.com{path}", header=headers)
    return ws

# Function to subscribe to market data for a list of pairs
def subscribe_to_market_data(ws, pairs_list):
    message = {
        "type": "SUBSCRIBE",
        "subscriptions": [
            {
                "event": "MARKET_SUMMARY_UPDATE",
                "pairs": pairs_list
            }
        ]
    }
    ws.send(json.dumps(message))

# Function to create the database and table
def create_database():
    conn = sqlite3.connect('valr_data.db')
    c = conn.cursor()
    # Uncomment the lines below to create the database and table
    c.execute('''CREATE TABLE IF NOT EXISTS market_summary_updates
                 (timestamp TEXT, currencyPairSymbol TEXT, askPrice REAL, bidPrice REAL, lastTradedPrice REAL, baseVolume REAL, quoteVolume REAL)''')
    conn.commit()
    conn.close()

# Function to insert data into the database
def insert_data_to_db(data):
    conn = sqlite3.connect('valr_data.db')
    c = conn.cursor()
    c.execute("INSERT INTO market_summary_updates VALUES (?, ?, ?, ?, ?, ?, ?)", data)
    conn.commit()
    conn.close()

# Main function
def main():
    create_database()  # Ensure this function creates the table with the correct schema
    pairs_list = ['BTCZAR']
    headers = get_auth_headers("/ws/trade")
    formatted_headers = [f"{key}: {value}" for key, value in headers.items()]
    ws = connect_to_valr_websocket("/ws/trade", formatted_headers)
    
    subscribe_to_market_data(ws, pairs_list)

    try:
        while True:
            result = ws.recv()
            print(result)
            data = json.loads(result)
            if data['type'] == 'MARKET_SUMMARY_UPDATE':
                market_data = data['data']
                db_data = (market_data['created'], market_data['currencyPairSymbol'], market_data['askPrice'], 
                           market_data['bidPrice'], market_data['lastTradedPrice'], market_data['baseVolume'], 
                           market_data['quoteVolume'])
                insert_data_to_db(db_data)
    except Exception as e:
        print("Error:", e)
    finally:
        ws.close()

if __name__ == "__main__":
    main()
