from find_best_sl_cc_bb import find_best_SL_CC_BB
from binance.client import Client
import pandas as pd
import logging
# Replace with your own Binance API credentials
api_key = 'your_api_key'
api_secret = 'your_api_secret'

client = Client(api_key, api_secret)


symbol = 'SOLUSDT'
timeframe = '5m'
start_date =  "1 jan, 2023"
end_date = None
# Construct the filename

bb_std_dev = 2.8
bb_window = 16


klines = client.get_historical_klines(symbol, Client.KLINE_INTERVAL_5MINUTE, start_date,end_date)

df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])

cc_range = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
sl_range = [0.05,0.075,0.1,0.125,0.15,0.175,0.2]

best_pnl = float('-inf')
best_sl = None
best_cc = None

for cc in cc_range:
    for sl in sl_range:
        result_dict = find_best_SL_CC_BB(sl,cc,symbol,timeframe,klines,bb_std_dev,bb_window,start_date,end_date)
        pnl = result_dict["Total PNL"]
        if pnl > best_pnl:
            best_pnl = pnl
            best_sl = sl
            best_cc = cc

print(f"The best combination is: sl={best_sl}, cc={best_cc}, with Total PNL={best_pnl}")

