# trading_logic.py
import time

import csv

def execute_trade(action, state_index, ql_model, current_market_price, trade_log_path):
    # Generate a unique transaction ID using the current timestamp
    transaction_id = int(time.time() * 1000)
    trade_result = {
        'transaction_id': transaction_id,
        'action': action,
        'trade_executed': False,
        'trade_price': current_market_price,
        'trade_volume': 1,
        'timestamp': time.time(),
        'profit_loss': 0,
        'closing_price': None,
        'trade_status': 'open',
        'decided_action': None  # Initialize decided_action with None
    }

    # Ensure trade_log_path is a string before opening the file
    if not isinstance(trade_log_path, str):
        raise TypeError(f"Expected trade_log_path to be a string, got {type(trade_log_path)} instead")

    # Read open trades from trade_log.csv
    with open(trade_log_path, mode='r') as file:
        csv_reader = csv.DictReader(file)
        open_trades = [row for row in csv_reader if row['trade_status'] == 'open']

    # Loop through open trades to decide whether to close them and update their status
    for open_trade in open_trades:
        # Use Q-learning model to decide whether to close the trade
        decided_action = ql_model.decide_action(state_index)
        if decided_action == 'sell':
            trade_executed = True
            closing_price = current_market_price
            profit_loss = (closing_price - float(open_trade['trade_price'])) * int(open_trade['trade_volume'])
            # Update the trade details with the new status and profit/loss
            open_trade['trade_status'] = 'closed'
            open_trade['closing_price'] = str(closing_price)
            open_trade['profit_loss'] = str(profit_loss)
            # Update the Q-table based on the trade outcome
            reward = profit_loss  # Reward is proportional to profit/loss
            ql_model.learn(state_index, action, reward, state_index)

    # Write the updated trades back to trade_log.csv, including the newly closed trades
    with open(trade_log_path, mode='w', newline='') as file:
        fieldnames = ['transaction_id', 'action', 'trade_executed', 'trade_price', 'trade_volume', 'timestamp', 'profit_loss', 'closing_price', 'trade_status', 'decided_action']
        csv_writer = csv.DictWriter(file, fieldnames=fieldnames)
        csv_writer.writeheader()
        # Write all trades, including the updated open trades and any new trades
        for trade in open_trades + [trade_result]:
            csv_writer.writerow(trade)

    # If no open trades were closed, check if we should open a new trade
    if not trade_result['trade_executed'] and action == 'buy':
        trade_result['trade_executed'] = True
        trade_result['trade_status'] = 'open'
        # Append the new trade to the CSV file
        with open(trade_log_path, mode='a', newline='') as file:
            csv_writer = csv.DictWriter(file, fieldnames=csv_reader.fieldnames)
            csv_writer.writerow(trade_result)

    # Update the Q-table based on the trade outcome
    reward = trade_result['profit_loss']  # Reward is proportional to profit/loss
    ql_model.learn(state_index, action, reward, state_index)

    return trade_result

    # If no open trades were closed, check if we should open a new trade
    if not trade_result['trade_executed'] and action == 'buy':
        trade_result['trade_executed'] = True
        trade_result['trade_status'] = 'open'
        open_trades.append({'transaction_id': trade_result['transaction_id'], 'trade_price': current_market_price, 'trade_volume': trade_result['trade_volume'], 'timestamp': trade_result['timestamp'], 'action': 'buy', 'trade_status': 'open'})

    # Update the Q-table based on the trade outcome
    reward = trade_result['profit_loss']  # Reward is proportional to profit/loss
    ql_model.learn(state_index, action, reward, state_index)

    return trade_result
