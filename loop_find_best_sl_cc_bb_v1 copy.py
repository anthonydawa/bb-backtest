from find_best_sl_cc_bb import find_best_SL_CC_BB
from binance.client import Client
import pandas as pd
import logging
import csv
# Replace with your own Binance API credentials
api_key = 'your_api_key'
api_secret = 'your_api_secret'

client = Client(api_key, api_secret)

symbol = 'AXSUSDT'
timeframe = '5m'
start_date = "1 jan, 2019"
end_date = None

# Construct the filename
bb_std_dev = 2.8
bb_window = 16

klines = client.get_historical_klines(symbol, Client.KLINE_INTERVAL_5MINUTE, start_date, end_date)

df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])

cc_range = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,15,16,17,19,20]
sl_range = [0,0.05,0.075,0.1,0.125,0.15,0.175,0.2,0.225,0.25,0.275,0.3]
# sl_range = [0.250,]
best_total_pnl = float('-inf')
best_long_pnl = float('-inf')
best_short_pnl = float('-inf')
best_balance = float('-inf')
best_short_balance = float('-inf')
best_long_balance = float('-inf')

best_sl_total = None
best_cc_total = None
best_sl_long = None
best_cc_long = None
best_sl_short = None
best_cc_short = None
best_sl_total_balance = None
best_cc_total_balance = None
best_sl_long_balance = None
best_cc_long_balance = None
best_sl_short_balance = None
best_cc_short_balance = None

for cc in cc_range:
    for sl in sl_range:
        result_dict = find_best_SL_CC_BB(sl, cc, symbol, timeframe, klines, bb_std_dev, bb_window, start_date, end_date)
        total_pnl = result_dict["Total PNL"]
        long_pnl = result_dict["Long PNL"]
        short_pnl = result_dict["Short PNL"]
        balance = result_dict["balance"]
        short_balance = result_dict["balance_short"]
        long_balance = result_dict["balance_long"]
        
        # Check for best Total PNL
        if total_pnl > best_total_pnl:
            best_total_pnl = total_pnl
            best_sl_total = sl
            best_cc_total = cc
        
        # Check for best Long PNL
        if long_pnl > best_long_pnl:
            best_long_pnl = long_pnl
            best_sl_long = sl
            best_cc_long = cc

        # Check for best Short PNL
        if short_pnl > best_short_pnl:
            best_short_pnl = short_pnl
            best_sl_short = sl
            best_cc_short = cc

        # Check for best balance
        if balance > best_balance:
            best_balance = balance
            best_sl_total_balance = sl
            best_cc_total_balance = cc


        # Check for best Short balance
        if short_balance > best_short_balance:
            best_short_balance = short_balance
            best_sl_short_balance = sl
            best_cc_short_balance = cc

        # Check for best Long balance
        if long_balance > best_long_balance:
            best_long_balance = long_balance
            best_sl_long_balance = sl
            best_cc_long_balance = cc

print(f"The best combination for Total PNL is: sl={best_sl_total}, cc={best_cc_total}, with Total PNL={best_total_pnl}")
print(f"The best combination for Long PNL is: sl={best_sl_long}, cc={best_cc_long}, with Long PNL={best_long_pnl}")
print(f"The best combination for Short PNL is: sl={best_sl_short}, cc={best_cc_short}, with Short PNL={best_short_pnl}")
print(f"The best combination for Total PNL is: sl={best_sl_total_balance}, cc={best_cc_total_balance}, with Total PNL={best_balance}")
print(f"The best combination for Long PNL is: sl={best_sl_long_balance}, cc={best_cc_long_balance}, with Long PNL={best_long_balance}")
print(f"The best combination for Short PNL is: sl={best_sl_short_balance}, cc={best_cc_short_balance}, with Short PNL={best_short_balance}")

data = [
    ["Metric", "SL", "CC", "Value"],
    ["Total PNL", best_sl_total, best_cc_total, best_total_pnl],
    ["Long PNL", best_sl_long, best_cc_long, best_long_pnl],
    ["Short PNL", best_sl_short, best_cc_short, best_short_pnl],
    ["Total PNL Balance", best_sl_total_balance, best_cc_total_balance, best_balance],
    ["Long PNL Balance", best_sl_long_balance, best_cc_long_balance, best_long_balance],
    ["Short PNL Balance", best_sl_short_balance, best_cc_short_balance, best_short_balance]
]

# Specify the file path
file_path = f"{symbol}-{timeframe}-{start_date}-{end_date}-{bb_std_dev}-{bb_window}-best_combinations.csv"

# Write the data to the CSV file
with open(file_path, mode='a', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(data)

print(f"Results saved to {file_path}")