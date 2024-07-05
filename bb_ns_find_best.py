import csv
from binance.client import Client
import pandas as pd
import logging
# Replace with your own Binance API credentials
api_key = 'your_api_key'
api_secret = 'your_api_secret'

client = Client(api_key, api_secret)


# Define symbol and interval
symbol = 'BTCUSDT'
timeframe = '5m'
start_date = "1 jan, 2023"
end_date = None
# Construct the filename
filename = f"backtest/TEST4-{symbol}-{timeframe}-{start_date}-{end_date}.csv"           

# Fetch historical Klines
klines = client.get_historical_klines(symbol, Client.KLINE_INTERVAL_5MINUTE, start_date, end_date)

# Convert to DataFrame
df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])

with open(filename, mode='w', newline='') as file:
    writer = csv.writer(file)
    header = ["std","wr","PNL"]
    writer.writerow(header)

    
def calculate_bollinger_bands(df, window=20, num_std_dev=2):
    df['Close'] = df['close'].astype(float)  # Ensure 'close' column is numeric

    # Calculate the rolling mean and standard deviation
    df['RollingMean'] = df['Close'].rolling(window=window).mean()
    df['RollingStd'] = df['Close'].rolling(window=window).std()

    # Calculate Bollinger Bands
    df['UpperBand'] = df['RollingMean'] + (df['RollingStd'] * num_std_dev)
    df['LowerBand'] = df['RollingMean'] - (df['RollingStd'] * num_std_dev)
    df['MiddleBand'] = df['RollingMean']  # Middle Band is just the rolling mean

    # Drop the intermediate columns if you don't need them
    df.drop(['RollingMean', 'RollingStd'], axis=1, inplace=True)

bb_std_range = [1.6,1.7,1.8,1.9,2.0,2.1,2.2,2.3,2.4,2.5,2.6,2.7,2.8,2.9,3.0,3.1,3.2,3.3,3.4,3.5]
bb_window_range = [16,17,18,19,20,21,22,23,24,25,26,27,28,29,30]
# Assuming df already contains the historical data
result = []

for std in bb_std_range:
    for wr in bb_window_range:
        print(std,wr)
        position = None
        pnl = 0
        entry = None
        short_pnl = 0
        long_pnl = 0
        fees = 0.25
        total_fees = fees 
        calculate_bollinger_bands(df,window=wr,num_std_dev=std)
        # Print OHLC, ATR, and Bollinger Bands data
        for index, row in df.iterrows():
            if position is None :

                # Check if close is within range of high and low

                if float(row['low']) <= float(row['LowerBand']) <= float(row['high']) and float(row['low']) <= float(row['UpperBand']) <= float(row['high']):
                    continue

                # elif float(row['low']) <= float(row['LowerBand']) <= float(row['high']) and row['K'] <= 20:
                elif float(row['low']) <= float(row['LowerBand']) <= float(row['high']):
                    # Enter a long position
                    entry = float(row['LowerBand'])
                    position = 'Long'

                elif float(row['low']) <= float(row['UpperBand']) <= float(row['high']):
                    # Enter a short position
                    entry = float(row['UpperBand'])
                    position = 'Short'

            elif position is not None:
                # Check if take profit is within range of high and low

                if position == "Long":

                    if float(row['low']) <= float(row['UpperBand']) <= float(row['high']):

                        if entry > float(row['UpperBand']) and entry < float(row['UpperBand']):
                            continue

                        elif entry > float(row['UpperBand']):
                            percent_difference = abs(((float(row['UpperBand']) - entry) / entry) * 100)
                            position = "Short"
                            pnl -= percent_difference + total_fees
                            entry = float(row['UpperBand'])
                            continue

                        elif entry < float(row['UpperBand']):
                            percent_difference = abs(((float(row['UpperBand']) - entry) / entry) * 100)
                            position = "Short"            
                            pnl += percent_difference - total_fees
                            entry = float(row['UpperBand'])
                            continue

                elif position == "Short":

                    if float(row['low']) <= float(row['LowerBand']) <= float(row['high']):


                        if entry > float(row['LowerBand']) and entry < float(row['LowerBand']):
                            continue
                        elif entry > float(row['LowerBand']):
                            percent_difference = abs(((float(row['LowerBand']) - entry) / entry) * 100)
                            position = "Long"
                            pnl += percent_difference - total_fees
                            entry = float(row['LowerBand'])
                            continue

                        elif entry < float(row['LowerBand']):
                            percent_difference = abs(((float(row['LowerBand']) - entry) / entry) * 100)
                            position = "Long"            
                            pnl -= percent_difference + total_fees
                            entry = float(row['LowerBand'])
                            continue


        result_row = [std,wr,pnl]

        with open(filename, mode='a', newline='') as file:

            writer = csv.writer(file)
            writer.writerow(result_row)











