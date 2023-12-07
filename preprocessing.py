 # preprocessing.py
import pandas as pd

def preprocess_data(market_data):
    market_data['timestamp'] = pd.to_datetime(market_data['timestamp'])
    market_data['priceSpread'] = market_data['askPrice'] - market_data['bidPrice']
    return market_data
