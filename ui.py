# ui.py

import csv

def update_ui(market_data, action, trade_result, mcs_metrics, trade_log_path):
 # Print the market data
 print("Market Data:")
 for key, value in market_data.items():
     print(f"{key}: {value}")

 # Print the action taken by the bot
 print(f"\nAction Taken: {action}")

 # Print the MCS metrics
 print("\nMCS Metrics:")
 for key, value in mcs_metrics.items():
     print(f"{key}: {value}")

 # Print the trade result including profit or loss
 print("\nTrade Result:")
 for key, value in trade_result.items():
     if key == 'profit_loss':
         if trade_result['trade_executed']:
             print(f"Profit/Loss: {value}")
         else:
             print(f"No trades were closed. Reason: {trade_result.get('close_reason', 'N/A')}")
     else:
         print(f"{key}: {value}")

 # Print the open trades from trade_log.csv
 print("\nOpen Trades:")
 with open(trade_log_path, mode='r') as file:
     csv_reader = csv.DictReader(file)
     for row in csv_reader:
         if row['trade_status'] == 'open':
             # Print the decided action for each open trade
             # Use get method to safely access 'decided_action' and provide a default value if it's not present
             decided_action = trade_result.get('decided_action', 'N/A')
             print(f"Transaction ID: {row['transaction_id']}, Trade Price: {row['trade_price']}, Volume: {row['trade_volume']}, Timestamp: {row['timestamp']}, Status: {row['trade_status']}, Decided Action: {decided_action}")
