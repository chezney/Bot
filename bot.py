# bot.py
import time
import logging
import traceback
import sqlite3
from db_connection import fetch_data
# Removed incorrect import for create_database
from preprocessing import preprocess_data
from monte_carlo import run_monte_carlo_simulations
from q_learning import QLearningModel
from trading_logic import execute_trade
from csv_logging import log_to_csv
from ui import update_ui

from db_connection import fetch_data, save_q_table, load_q_table
from q_learning import QLearningModel, state_space_size, action_space, learning_rate, discount_factor, epsilon

import logging

def discretize_mcs_statistics(mcs_data, num_states, min_price, max_price):
    # Example: Discretize based on the mean expected price
    mean_expected_price = mcs_data['mean_expected_price']
    # Ensure the price range is properly defined to cover all possible prices
    price_range = max_price - min_price
    if price_range <= 0:
        raise ValueError("max_price must be greater than min_price")
    price_interval = price_range / (num_states - 1)
    # Calculate the state index by finding where the mean expected price falls within the range
    state_index = int((mean_expected_price - min_price) / price_interval)
    # Ensure the state index is within bounds
    state_index = max(0, min(state_index, num_states - 1))
    return state_index

# Define the function at the module level
def fetch_min_max_prices(trading_pair):
    min_max_query = f"""
    SELECT MIN(lastTradedPrice) AS min_price, MAX(lastTradedPrice) AS max_price
    FROM market_summary_updates
    WHERE currencyPairSymbol = '{trading_pair}'
    """
    min_max_data = fetch_data(min_max_query, 'valr_data.db')
    return min_max_data['min_price'].iloc[0], min_max_data['max_price'].iloc[0]

def main():
    # Configure logging
    logging.basicConfig(filename='bot.log', level=logging.INFO, format='%(asctime)s %(levelname)s:%(message)s')

    # Fetch the minimum and maximum prices from the database
    min_price, max_price = fetch_min_max_prices(trading_pair)
# Define the number of hours to forecast in the Monte Carlo simulations
forecast_hours = 24

# Attempt to load the Q-table from the database
db_path = 'q_learning.db'
q_table = load_q_table(db_path)

# Check if the Q-table was loaded successfully
if q_table is not None:
    # Initialize the Q-Learning model with the loaded Q-table
    ql_model = QLearningModel(state_space_size, action_space, learning_rate, discount_factor, epsilon, q_table)
else:
    # Initialize the Q-Learning model without a Q-table (it will be created with default values)
    ql_model = QLearningModel(state_space_size, action_space, learning_rate, discount_factor, epsilon)

# Define the trading pair
trading_pair = 'BTCZAR'

# Main trading loop
print("Starting main trading loop...")
try:
    while True:
        try:
            print("New iteration of the trading loop...")
            # Debugging: Print a message indicating the start of a new iteration
            # Fetch new market data from the database
            mcs_data_query = f"SELECT * FROM market_summary_updates WHERE currencyPairSymbol = '{trading_pair}' ORDER BY timestamp DESC LIMIT 1000"  # Adjust the limit as needed
            mcs_data = fetch_data(mcs_data_query, 'valr_data.db')

            market_data_query = f"SELECT * FROM market_summary_updates WHERE currencyPairSymbol = '{trading_pair}' ORDER BY timestamp DESC LIMIT 1"
            market_data = fetch_data(market_data_query, 'valr_data.db')

            # Convert the database row to a dictionary to preprocess the data
            market_data_dict = {
                'timestamp': market_data['timestamp'].iloc[0],
                'askPrice': market_data['askPrice'].iloc[0],
                'bidPrice': market_data['bidPrice'].iloc[0],
                'lastTradedPrice': market_data['lastTradedPrice'].iloc[0],
                'baseVolume': market_data['baseVolume'].iloc[0],
                'quoteVolume': market_data['quoteVolume'].iloc[0]
            }
            # Preprocess the data for the MCS and QL models
            preprocessed_data = preprocess_data(market_data_dict)


            # Define a function to get the state based on the market data and MCS data
            def get_state(market_data, mcs_data):
                # Use the mean expected price from the MCS data as the state
                state = mcs_data['mean_expected_price']
                # Discretize this continuous value into 100 distinct states
                state = int(state / 100)
                return state

            # Run Monte Carlo Simulation to generate future price scenarios and additional statistics
            simulated_price_paths, mean_expected_price, percentile_5, percentile_95, var, expected_shortfall = run_monte_carlo_simulations(preprocessed_data, num_simulations=1000, forecast_hours=forecast_hours)

            # Run Monte Carlo Simulation to generate future price scenarios and additional statistics
            simulated_price_paths, mean_expected_price, percentile_5, percentile_95, var, expected_shortfall = run_monte_carlo_simulations(preprocessed_data, num_simulations=1000, forecast_hours=forecast_hours)

            # Prepare MCS data for inclusion in the trade result
            mcs_data = {
                'mean_expected_price': mean_expected_price,
                'percentile_5': percentile_5,
                'percentile_95': percentile_95,
                'var': var,
                'expected_shortfall': expected_shortfall,
                'simulated_price_paths': simulated_price_paths.tolist()  # Convert numpy array to list for JSON serialization
            }
            # Fetch the minimum and maximum prices from the database
            min_price, max_price = fetch_min_max_prices(trading_pair)
            # Determine the current state index based on MCS statistics
            state_index = discretize_mcs_statistics(mcs_data, state_space_size, min_price, max_price)
            current_price = preprocessed_data['lastTradedPrice']
            action = ql_model.decide_action(state_index)
            print(f"Current price: {current_price}")
            print(f"Action decided by QL model: {action}")
            if action == 'buy':
                print("Reasoning: The mean expected price from MCS is higher than the current price, indicating potential profit.")
            elif action == 'sell':
                print("Reasoning: The mean expected price from MCS is lower than the current price, indicating potential loss.")
            else:
                print("Reasoning: The mean expected price from MCS is close to the current price, suggesting to hold.")

            # Run Monte Carlo Simulation to generate future price scenarios and additional statistics
            simulated_price_paths, mean_expected_price, percentile_5, percentile_95, var, expected_shortfall = run_monte_carlo_simulations(preprocessed_data, num_simulations=1000, forecast_hours=forecast_hours)

            # Prepare MCS data for inclusion in the trade result
            mcs_data = {
                'mean_expected_price': mean_expected_price,
                'percentile_5': percentile_5,
                'percentile_95': percentile_95,
                'var': var,
                'expected_shortfall': expected_shortfall,
                'simulated_price_paths': simulated_price_paths.tolist()  # Convert numpy array to list for JSON serialization
            }
            # Execute the trading action (simulated) and include MCS data
            # Assuming open_trades is a list that should be passed to execute_trade
            # and current_market_price is the current price from the market data
            # Check if the list of open trades exists, if not, initialize it.
            # This list will be updated with the details of each trade.
            if 'open_trades' not in locals():
                open_trades = []  # Example: [{'trade_price': 100, 'trade_volume': 1, 'timestamp': 1701812833, 'action': 'buy'}]
            current_market_price = preprocessed_data['lastTradedPrice']  # Assuming this is the current market price
            # Define the path to the trade log CSV
            trade_log_path = 'trade_log.csv'
            # Execute the trade and pass the path to the trade log CSV to be updated
            trade_result = execute_trade(action, state_index, ql_model, current_market_price, trade_log_path)

            # Define the reward function using MCS data
            def calculate_reward(action, mcs_mean_expected_price, trade_price):
                if action == 'buy':
                    return max(0, mcs_mean_expected_price - trade_price)
                elif action == 'sell':
                    return max(0, trade_price - mcs_mean_expected_price)
                else:  # 'hold' action
                    return -0.1  # A small negative reward for holding

            # Calculate the reward based on the trade result
            reward = calculate_reward(action, mcs_data['mean_expected_price'], trade_result['trade_price'])


            # Fetch new market data for the next state
            # This is a placeholder for fetching new market data, you will need to implement the actual data fetching logic
            next_market_data = fetch_data(market_data_query, 'valr_data.db')
            # Convert the database row to a dictionary to preprocess the data
            next_market_data_dict = {
                'timestamp': next_market_data['timestamp'].iloc[0],
                'askPrice': next_market_data['askPrice'].iloc[0],
                'bidPrice': next_market_data['bidPrice'].iloc[0],
                'lastTradedPrice': next_market_data['lastTradedPrice'].iloc[0],
                'baseVolume': next_market_data['baseVolume'].iloc[0],
                'quoteVolume': next_market_data['quoteVolume'].iloc[0]
            }
            # Preprocess the data for the MCS and QL models
            next_preprocessed_data = preprocess_data(next_market_data_dict)
            # Determine the next state index based on MCS statistics
            next_state_index = discretize_mcs_statistics(mcs_data, state_space_size, min_price, max_price)
            
            # Update the Q-Learning model with the reward and next state index
            ql_model.learn(state_index, action, reward, next_state_index)

            # Save the updated Q-table to the database
            save_q_table(ql_model.q_table, db_path)

            # Log the trade action and result
            log_to_csv(trade_result)

            # Prepare MCS metrics for display in the UI
            mcs_metrics = {
                'mean_expected_price': mcs_data['mean_expected_price'],
                'percentile_5': mcs_data['percentile_5'],
                'percentile_95': mcs_data['percentile_95'],
                'var': mcs_data['var'],
                'expected_shortfall': mcs_data['expected_shortfall']
            }

            # Update the UI with the latest data, bot actions, and MCS metrics
            trade_log_path = 'trade_log.csv'  # Define the path to the trade log CSV
            update_ui(market_data, action, trade_result, mcs_metrics, trade_log_path)

            # Sleep for a defined interval before the next iteration
            time.sleep(5)  # Example: 60 seconds
        except KeyboardInterrupt:
            logging.info("Shutdown signal received. Exiting the trading loop.")
            break
        except sqlite3.DatabaseError as db_err:
            logging.error(f"Database error occurred: {db_err}")
            time.sleep(300)  # Sleep before retrying to prevent immediate retry on persistent errors
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}\n{traceback.format_exc()}")
            time.sleep(300)  # Sleep before retrying to prevent immediate retry on persistent errors
finally:
    logging.info("Trading bot has stopped.")
if __name__ == "__main__":
    main()
