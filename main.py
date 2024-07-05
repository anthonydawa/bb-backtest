from binance.client import Client
import pandas as pd
import logging
# Replace with your own Binance API credentials
api_key = 'your_api_key'
api_secret = 'your_api_secret'

client = Client(api_key, api_secret)

position = None
pnl = 0
entry = None
stopLoss = None
takeProfit = None
atr_multiplier = 1.3
candle_count = 1
candle_closed = 0
short_pnl = 0
long_pnl = 0
total_long_trades = 0 
total_short_trades = 0
total_short_loss = 0
total_short_wins = 0
total_long_loss = 0
total_long_wins = 0

# Define symbol and interval
symbol = 'ETHUSDT'
timeframe = '4h'
start_date = "1 jan, 2023"
end_date = '20 oct, 2023'
# Construct the filename
filename = f"backtest/{symbol}-{timeframe}-{start_date}-{end_date}.csv"

# Fetch historical Klines
klines = client.get_historical_klines(symbol, Client.KLINE_INTERVAL_4HOUR, start_date, end_date)

# Convert to DataFrame
df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])



# Configure logging
logging.basicConfig(filename=filename, level=logging.INFO, format='%(message)s')
# Write the header to the CSV file
header = "Timestamp,Open,High,Low,Close,ATR,UpperBand,MiddleBand,LowerBand,RSI,StochRSI,K,D,Short PNL,Long PNL,Total PNL,Candle Closed,Position,Entry,Stop Loss,Take Profit,ATR Multiplier,Candle Count,Short PnL,Long PnL,Total Long Trades,Total Short Trades,Total Short Loss,Total Short Wins,Total Long Loss,Total Long Wins"
logging.info(header)


def calculate_rsi(df, window=14):
    delta = df['close'].astype(float).diff()
    gain = (delta.where(delta > 0, 0)).fillna(0)
    loss = (-delta.where(delta < 0, 0)).fillna(0)
    avg_gain = gain.rolling(window=window, min_periods=1).mean()
    avg_loss = loss.rolling(window=window, min_periods=1).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    df['RSI'] = rsi

def calculate_stoch_rsi(df, window=14, k=3, d=3):
    rsi = df['RSI'].astype(float)
    min_rsi = rsi.rolling(window=window).min()
    max_rsi = rsi.rolling(window=window).max()

    stoch_rsi = ((rsi - min_rsi) / (max_rsi - min_rsi)) * 100
    df['StochRSI'] = stoch_rsi
    df['K'] = stoch_rsi.rolling(window=k).mean()
    df['D'] = df['K'].rolling(window=d).mean()

calculate_rsi(df)
calculate_stoch_rsi(df) 

# Define a function to calculate ATR
def calculate_atr(df, window=14):
    df[['open', 'high', 'low', 'close']] = df[['open', 'high', 'low', 'close']].apply(pd.to_numeric)
    df['TR'] = df.apply(lambda row: max(row['high'] - row['low'], abs(row['high'] - row['close']), abs(row['low'] - row['close'])), axis=1)
    df['ATR'] = df['TR'].rolling(window=window).mean()
    df['ATR'] = df['ATR'] * atr_multiplier

calculate_atr(df)

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

# Assuming df already contains the historical data
calculate_bollinger_bands(df)

# Print OHLC, ATR, and Bollinger Bands data
for index, row in df.iterrows():

    # Concatenate all the values in one line
    log_line = f"{row['timestamp']},{row['open']},{row['high']},{row['low']},{row['close']},{row['ATR']},{row['UpperBand']},{row['MiddleBand']},{row['LowerBand']},{row['RSI']},{row['StochRSI']},{row['K']},{row['D']},{short_pnl},{long_pnl},{pnl},{candle_closed},{position},{entry},{stopLoss},{takeProfit},{atr_multiplier},{candle_count},{candle_closed},{short_pnl},{long_pnl},{total_long_trades},{total_short_trades},{total_short_loss},{total_short_wins},{total_long_loss},{total_long_wins}"

    # Log the line
    logging.info(log_line)


    if candle_closed > 0:
        candle_closed -= 1

    if position is None and candle_closed == 0:

            # Check if close is within range of high and low

            if float(row['low']) <= float(row['LowerBand']) <= float(row['high']) and float(row['low']) <= float(row['UpperBand']) <= float(row['high']):
                continue

            # elif float(row['low']) <= float(row['LowerBand']) <= float(row['high']) and row['K'] <= 20:
            elif float(row['low']) <= float(row['LowerBand']) <= float(row['high']):
                # Enter a long position
                entry = float(row['LowerBand'])
                stopLoss = entry - df['ATR'][index]  # Set stop loss
                takeProfit = float(row['MiddleBand'])  # Set take profit to middle band
                position = 'Long'
                total_long_trades += 1

            # elif float(row['low']) <= float(row['UpperBand']) <= float(row['high']) and row['K'] >= 80:
            #     # Enter a short position
            #     entry = float(row['UpperBand'])
            #     stopLoss = entry + df['ATR'][index]  # Set stop loss
            #     takeProfit = float(row['MiddleBand'])  # Set take profit to middle band
            #     position = 'Short'
            #     total_short_trades += 1


    elif position is not None:
            # Check if take profit is within range of high and low
            takeProfit = float(row['MiddleBand'])


            if float(row['low']) <= takeProfit <= float(row['high']) and float(row['low']) <= stopLoss <= float(row['high']):
                position = None  
                entry = None
                takeProfit = None
                stopLoss = None  
                continue  

            elif float(row['low']) <= takeProfit <= float(row['high']):

                if takeProfit < entry and position == 'Short':

                    percent_difference = abs(((takeProfit - entry) / entry) * 100)
                    pnl += percent_difference
                    short_pnl += percent_difference
                    total_short_wins += 1 
                    position = None  
                    entry = None
                    takeProfit = None
                    stopLoss = None  
                    continue                   

                elif takeProfit > entry and position == 'Long':

                    percent_difference = abs(((takeProfit - entry) / entry) * 100)
                    pnl += percent_difference
                    long_pnl += percent_difference
                    total_long_wins += 1
                    position = None  
                    entry = None
                    takeProfit = None
                    stopLoss = None
                    continue 

                elif takeProfit > entry and position == 'Short':

                    percent_difference = abs(((takeProfit - entry) / entry) * 100)
                    pnl -= percent_difference
                    short_pnl -= percent_difference
                    total_short_loss += 1
                    candle_closed = candle_count
                    position = None  
                    entry = None
                    takeProfit = None
                    stopLoss = None   
                    continue                 

                elif takeProfit < entry and position == 'Long':    

                    percent_difference = abs(((takeProfit - entry) / entry) * 100)
                    pnl -= percent_difference
                    long_pnl -= percent_difference
                    total_long_loss += 1
                    candle_closed = candle_count
                    position = None  
                    entry = None
                    takeProfit = None
                    stopLoss = None
                    continue 


            elif float(row['low']) <= stopLoss <= float(row['high']):

                percent_difference = abs(((stopLoss - entry) / entry) * 100)

                if position == 'Long':
                    long_pnl -= percent_difference
                    pnl -= percent_difference
                    total_long_loss += 1
                elif position == 'Short':
                    short_pnl -= percent_difference
                    pnl -= percent_difference
                    total_short_loss += 1

                candle_closed = candle_count
                position = None  
                entry = None
                takeProfit = None
                stopLoss = None
                continue 

print(f"Timestamp: {row['timestamp']}")
print(f"Open: {row['open']}")
print(f"High: {row['high']}")
print(f"Low: {row['low']}")
print(f"Close: {row['close']}")
print(f"ATR: {row['ATR']}")
print(f"Upper Band: {row['UpperBand']}")
print(f"Middle Band: {row['MiddleBand']}")
print(f"Lower Band: {row['LowerBand']}")
print(f"RSI: {row['RSI']}")
print(f"StochRSI: {row['StochRSI']}")
print(f"K: {row['K']}")
print(f"D: {row['D']}")
print(f"Short PNL: {short_pnl}")
print(f"Long PNL: {long_pnl}")
print(f"Total PNL: {pnl}")
print(f"candle_closed: {candle_closed}")
print(f"total_long_trades: {total_long_trades}")
print(f"total_short_trades: {total_short_trades}")
print(f"total_short_loss: {total_short_loss}")
print(f"total_short_wins: {total_short_wins}")
print(f"total_long_loss: {total_long_loss}")
print(f"total_long_wins: {total_long_wins}")
print()

# After the loop, close the logging file
logging.shutdown()








