from concurrent.futures import ThreadPoolExecutor
import threading
from find_best_sl_cc_bb_4 import find_best_SL_CC_BB
from binance.client import Client
import pandas as pd
import logging
import csv

# Replace with your own Binance API credentials
api_key = 'your_api_key'
api_secret = 'your_api_secret'

client = Client(api_key, api_secret)

symbol = 'INJUSDT'
timeframe = '5m'
start_date = "1 nov, 2023"
end_date = None

bb_std_dev = 3.0
bb_window = 16

klines = client.get_historical_klines(symbol, Client.KLINE_INTERVAL_5MINUTE, start_date, end_date)

cc_range = [0.005,0.01,0.015,0.02,0.025,0.03,0.035,0.04,0.045,0.05,0.055,0.06,0.065,0.07,0.075,0.08,0.085,0.09,0.095,0.1,0.125,0.15,0.175,0.2,0.225,0.25,0.275,0.3,1]
sl_range = [0.005,0.01,0.015,0.02,0.025,0.03,0.035,0.04,0.045,0.05,0.055,0.06,0.065,0.07,0.075,0.08,0.085,0.09,0.095,0.1,0.125,0.15,0.175,0.2,0.225,0.25,0.275,0.3,1]
std_range = [2.6,2.7,2.8,2.9,3.0,3.1,3.2,3.3,3.4,3.5,3.6,3.7,3.8,3.9,4.0]
wd_range = [16,17,18,19]

csv_lock = threading.Lock()

best_combinations = {}

metrics = ["Total PNL", "Long PNL", "Short PNL", "Total PNL Balance", "Long PNL Balance", "Short PNL Balance"]

# Initialize best combinations for each metric
for metric in metrics:
    best_combinations[metric] = {
        "SL": None,
        "CC": None,
        "STD": None,
        "WD": None,
        "Value": float('-inf')
    }

def process_combination(cc, sl, std, wr):
    global best_combinations

    result_dict = find_best_SL_CC_BB(sl, cc, symbol, timeframe, klines, std, wr, start_date, end_date)
    
    for metric in metrics:
        metric_value = result_dict[metric]
        with csv_lock:
            if metric_value > best_combinations[metric]["Value"]:
                best_combinations[metric]["Value"] = metric_value
                best_combinations[metric]["SL"] = sl
                best_combinations[metric]["CC"] = cc
                best_combinations[metric]["STD"] = std
                best_combinations[metric]["WD"] = wr

def save_results_to_csv():
    data = [["Metric", "SL", "CC", "STD", "WD", "Value"]]
    
    for metric in metrics:
        row = [metric,
               best_combinations[metric]["SL"],
               best_combinations[metric]["CC"],
               best_combinations[metric]["STD"],
               best_combinations[metric]["WD"],
               best_combinations[metric]["Value"]]
        data.append(row)

    with csv_lock:
        file_path = f"best_data/{symbol}-{timeframe}-{start_date}-{end_date}-{bb_std_dev}-{bb_window}-best_combinations.csv"
        with open(file_path, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(data)

num_threads = 10

with ThreadPoolExecutor(max_workers=num_threads) as executor:
    for std in std_range:
        for wr in wd_range:
            for cc in cc_range:
                for sl in sl_range:
                    executor.submit(process_combination, cc, sl, std, wr)

save_results_to_csv()

# Print the best combinations for each metric
for metric in metrics:
    print(f"Best combination for {metric}:")
    print(f"SL: {best_combinations[metric]['SL']}, CC: {best_combinations[metric]['CC']}, "
          f"STD: {best_combinations[metric]['STD']}, WD: {best_combinations[metric]['WD']}, "
          f"Value: {best_combinations[metric]['Value']}")
