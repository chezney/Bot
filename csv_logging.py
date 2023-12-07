# csv_logging.py
import csv
import os

def log_to_csv(trade_result):
 # Define the CSV file path
 csv_file_path = 'trade_log.csv'
 # Check if the CSV file already exists to determine if we need to write headers
 file_exists = os.path.isfile(csv_file_path)

 # Define the headers for the CSV file including the transaction ID and trade status
 headers = ['transaction_id', 'action', 'trade_executed', 'trade_price', 'trade_volume', 'timestamp', 'profit_loss', 'closing_price', 'trade_status', 'decided_action']

 # Open the CSV file in append mode
 with open(csv_file_path, mode='a', newline='') as file:
     writer = csv.DictWriter(file, fieldnames=headers, extrasaction='ignore')
  
     # Write the header if the file is newly created
     if not file_exists:
         writer.writeheader()
  
     # Write the trade result to the CSV file with the transaction ID
     writer.writerow(trade_result)
