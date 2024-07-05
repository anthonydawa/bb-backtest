from binance.client import Client
import pandas as pd
import logging
# Replace with your own Binance API credentials
api_key = 'your_api_key'
api_secret = 'your_api_secret'

client = Client(api_key, api_secret)

def find_best_SL_CC_BB(SL,CC,symbol,timeframe,klines,bb_std_dev,bb_window,start_date,end_date):

    position = None
    pnl = 0
    balance = 1000
    balance_long = 1000
    balance_short = 1000
    entry = None
    stopLoss = None
    takeProfit = None
    atr_multiplier = 1.9
    candle_count = 0
    candle_closed = 0
    short_pnl = 0
    long_pnl = 0
    total_long_trades = 0 
    total_short_trades = 0
    total_short_loss = 0
    total_short_wins = 0
    total_long_loss = 0
    total_long_wins = 0
    fees = 0.045 + 0.045 + 0.1
    avg_percent_wins = []
    # Define symbol and interval
    symbol = symbol
    timeframe = timeframe
    start_date =  start_date
    end_date = end_date
    # Construct the filename

    bb_std_dev = bb_std_dev
    bb_window = bb_window
    SL_PERCENT = SL
    TP_PERCENT = CC

    # Fetch historical Klines
    klines = klines
    filename = f"backtest/TEST-{symbol}-{timeframe}-{start_date}-{end_date}-{bb_std_dev}-{bb_window}.csv"
    df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])

    print(SL,CC,bb_std_dev,bb_window)

    # Configure logging
    logging.basicConfig(filename=filename, level=logging.INFO, format='%(message)s')
    # Write the header to the CSV file
    # header = "Timestamp,Open,High,Low,Close,ATR,UpperBand,MiddleBand,LowerBand,RSI,StochRSI,K,D,Short PNL,Long PNL,Total PNL,Candle Closed,Position,Entry,Stop Loss,Take Profit,ATR Multiplier,Candle Count,Short PnL,Long PnL,Total Long Trades,Total Short Trades,Total Short Loss,Total Short Wins,Total Long Loss,Total Long Wins"
    header = "Timestamp,PNL,LongPNL,ShortPNL,balance,balancelong,balanceshort"
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
    calculate_bollinger_bands(df,bb_window,bb_std_dev)

    # Print OHLC, ATR, and Bollinger Bands data
    for index, row in df.iterrows():

        # Concatenate all the values in one line
        # log_line = f"{row['timestamp']},{row['open']},{row['high']},{row['low']},{row['close']},{row['ATR']},{row['UpperBand']},{row['MiddleBand']},{row['LowerBand']},{row['RSI']},{row['StochRSI']},{row['K']},{row['D']},{short_pnl},{long_pnl},{pnl},{candle_closed},{position},{entry},{stopLoss},{takeProfit},{atr_multiplier},{candle_count},{candle_closed},{short_pnl},{long_pnl},{total_long_trades},{total_short_trades},{total_short_loss},{total_short_wins},{total_long_loss},{total_long_wins}"
        log_line = f"{row['timestamp']},{pnl},{long_pnl},{short_pnl},{balance},{balance_long},{balance_short}"
        # Log the line
        logging.info(log_line)
        
        if candle_closed > 0:
            candle_closed = candle_closed - 1

        elif candle_closed == 0:

            if position is None :

                # Check if close is within range of high and low

                if float(row['low']) <= float(row['LowerBand']) <= float(row['high']) and float(row['low']) <= float(row['UpperBand']) <= float(row['high']):
                    pass

                # elif float(row['low']) <= float(row['LowerBand']) <= float(row['high']) and row['K'] <= 20:
                elif float(row['low']) <= float(row['LowerBand']) <= float(row['high']):
                    # Enter a long position
                    entry = float(row['LowerBand'])
                    position = 'Long'
                    stopLoss = entry - (entry * SL_PERCENT)
                    takeProfit = entry + (entry * TP_PERCENT)

                elif float(row['low']) <= float(row['UpperBand']) <= float(row['high']):
                    # Enter a short position
                    entry = float(row['UpperBand'])
                    position = 'Short'
                    stopLoss = entry + (entry * SL_PERCENT)
                    takeProfit = entry - (entry * TP_PERCENT)

            elif position is not None:
                # Check if take profit is within range of high and low

                if position == "Long":

                    if float(row['low']) <= float(row['UpperBand']) <= float(row['high']):

                        if entry > float(row['UpperBand']) and entry < float(row['UpperBand']):
                            pass

                        elif entry > float(row['UpperBand']):

                            percent_difference = abs(((float(row['UpperBand']) - entry) / entry) * 100)
                            position = "Short"
                            net_percentage = percent_difference + fees
                            pnl -= net_percentage
                            long_pnl -= net_percentage                   
                            net_difference = abs((balance * ( net_percentage / 100) )) 
                            net_difference2 = abs((balance_long * ( net_percentage / 100) )) 
                            balance_long = balance_long - net_difference2
                            balance = balance - net_difference
                            entry = float(row['UpperBand'])
                            stopLoss = entry + (entry * SL_PERCENT)
                            total_long_loss += 1 
                            total_long_trades += 1
                            takeProfit = entry - (entry * TP_PERCENT)
                            

                        elif entry < float(row['UpperBand']):

                            percent_difference = abs(((float(row['UpperBand']) - entry) / entry) * 100)

                            if fees > percent_difference:
                                position = "Short"
                                net_percentage = abs( percent_difference - fees)
                                avg_percent_wins.append(percent_difference)            
                                pnl -= net_percentage
                                long_pnl -= net_percentage
                                net_difference = abs((balance * ( net_percentage / 100) )) 
                                net_difference2 = abs((balance_long * ( net_percentage / 100) )) 
                                entry = float(row['UpperBand'])
                                stopLoss = entry + (entry * SL_PERCENT)
                                total_long_loss += 1
                                total_long_trades += 1
                                balance_long = balance_long - net_difference2
                                balance = balance - net_difference
                                takeProfit = entry - (entry * TP_PERCENT)
                                
                            
                            elif fees < percent_difference:

                                position = "Short"
                                net_percentage = percent_difference - fees
                                avg_percent_wins.append(percent_difference)            
                                pnl += net_percentage
                                long_pnl += net_percentage
                                net_difference = abs((balance * ( net_percentage / 100) )) 
                                net_difference2 = abs((balance_long * ( net_percentage / 100) )) 
                                entry = float(row['UpperBand'])
                                stopLoss = entry + (entry * SL_PERCENT)
                                total_long_wins += 1
                                total_long_trades += 1
                                balance_long = balance_long + net_difference2
                                balance = balance + net_difference
                                takeProfit = entry - (entry * TP_PERCENT)




                            

                elif position == "Short":

                    if float(row['low']) <= float(row['LowerBand']) <= float(row['high']):


                        if entry > float(row['LowerBand']) and entry < float(row['LowerBand']):
                            pass
                        elif entry > float(row['LowerBand']):

                            percent_difference = abs(((float(row['LowerBand']) - entry) / entry) * 100)

                            if fees > percent_difference:

                                position = "Long"
                                net_percentage = abs(percent_difference - fees)
                                pnl -= net_percentage
                                short_pnl -= net_percentage
                                net_difference = abs((balance * ( net_percentage / 100) )) 
                                net_difference2 = abs((balance_short * ( net_percentage / 100) )) 
                                avg_percent_wins.append(percent_difference) 
                                entry = float(row['LowerBand'])
                                stopLoss = entry - (entry * SL_PERCENT)
                                total_short_loss += 1
                                balance_short = balance_short - net_difference2
                                balance = balance - net_difference
                                total_short_trades += 1
                                takeProfit = entry + (entry * TP_PERCENT)
                                
                            elif fees < percent_difference:

                                position = "Long"
                                net_percentage = percent_difference - fees
                                pnl += net_percentage
                                short_pnl += net_percentage
                                net_difference = abs((balance * ( net_percentage / 100) )) 
                                net_difference2 = abs((balance_short * ( net_percentage / 100) )) 
                                avg_percent_wins.append(percent_difference) 
                                entry = float(row['LowerBand'])
                                stopLoss = entry - (entry * SL_PERCENT)
                                total_short_wins += 1
                                balance_short = balance_short + net_difference2
                                balance = balance + net_difference   
                                total_short_trades += 1      
                                takeProfit = entry + (entry * TP_PERCENT)                  
                            

                        elif entry < float(row['LowerBand']):

                            percent_difference = abs(((float(row['LowerBand']) - entry) / entry) * 100)
                            position = "Long"    
                            net_percentage = percent_difference + fees
                            pnl -= net_percentage
                            short_pnl -= net_percentage
                            net_difference = abs((balance * ( net_percentage / 100) ))
                            net_difference2 = abs((balance_short * ( net_percentage / 100) ))
                            balance_short = balance_short - net_difference2
                            balance = balance - net_difference                
                            entry = float(row['LowerBand'])
                            takeProfit = entry + (entry * TP_PERCENT)
                            stopLoss = entry - (entry * SL_PERCENT)
                            total_short_loss += 1
                            total_short_trades += 1


                if position == "Long":
                    if float(row['low']) <= stopLoss <= float(row['high']) and float(row['low']) <= takeProfit <= float(row['high']):
                        pass

                    elif float(row['low']) <= stopLoss <= float(row['high']):
                        percent_difference = abs(((stopLoss - entry) / entry) * 100)
                        net_percentage = percent_difference + fees
                        pnl -= net_percentage
                        long_pnl -= net_percentage
                        net_difference = abs((balance * ( net_percentage / 100) ))
                        net_difference2 = abs((balance_long * ( net_percentage / 100) ))
                        balance_long = balance_long - net_difference2
                        balance = balance - net_difference  
                        position = None
                        entry = None
                        stopLoss = None
                        takeProfit = None
                        total_long_loss += 1
                        total_long_trades += 1
                        candle_closed = 0

                    elif float(row['low']) <= takeProfit <= float(row['high']):
                        percent_difference = abs(((takeProfit - entry) / entry) * 100)
                        net_percentage = percent_difference - fees
                        pnl += net_percentage
                        long_pnl += net_percentage
                        net_difference = abs((balance * ( net_percentage / 100) ))
                        net_difference2 = abs((balance_long * ( net_percentage / 100) ))
                        balance_long = balance_long + net_difference2
                        balance = balance + net_difference  
                        position = None
                        entry = None
                        stopLoss = None
                        takeProfit = None
                        total_long_wins += 1
                        total_long_trades += 1
            

                elif position == "Short":
                    if float(row['low']) <= stopLoss <= float(row['high']) and float(row['low']) <= takeProfit <= float(row['high']):
                        pass

                    elif float(row['low']) <= stopLoss <= float(row['high']):
                        percent_difference = abs(((stopLoss - entry) / entry) * 100)
                        net_percentage = percent_difference + fees
                        pnl -= net_percentage
                        short_pnl -= net_percentage
                        net_difference = abs((balance * ( net_percentage / 100) ))
                        net_difference2 = abs((balance_short * ( net_percentage / 100) ))
                        balance_short = balance_short - net_difference2
                        balance = balance - net_difference  
                        position = None
                        entry = None
                        stopLoss = None
                        takeProfit = None
                        total_short_loss += 1
                        total_short_trades += 1       
                        candle_closed = 0

                    elif float(row['low']) <= takeProfit <= float(row['high']):
                        percent_difference = abs(((takeProfit - entry) / entry) * 100)
                        net_percentage = percent_difference - fees
                        pnl += net_percentage
                        short_pnl += net_percentage
                        net_difference = abs((balance * ( net_percentage / 100) ))
                        net_difference2 = abs((balance_short * ( net_percentage / 100) ))
                        balance_short = balance_short + net_difference2
                        balance = balance + net_difference  
                        position = None
                        entry = None
                        stopLoss = None
                        takeProfit = None
                        total_short_wins += 1
                        total_short_trades += 1       

            
    try:              
        win_rate_long = (total_long_wins / total_long_trades) * 100
        win_rate_short = (total_short_wins / total_short_trades) * 100
        avg_percentage = sum(avg_percent_wins) / len(avg_percent_wins)
    except:
        win_rate_long = 0
        win_rate_short = 0
        avg_percentage = 0

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
    print(f"win_rate_long: {win_rate_long}")
    print(f"win_rate_short: {win_rate_short}")
    print(f"avg_percentage: {avg_percentage}")
    print(f"balance: {balance}")
    print(f"balance_short: {balance_short}")
    print(f"balance_long: {balance_long}")

    # After the loop, close the logging file
    result_dict = {
        "Timestamp": row['timestamp'],
        "Open": row['open'],
        "High": row['high'],
        "Low": row['low'],
        "Close": row['close'],
        "ATR": row['ATR'],
        "Upper Band": row['UpperBand'],
        "Middle Band": row['MiddleBand'],
        "Lower Band": row['LowerBand'],
        "RSI": row['RSI'],
        "StochRSI": row['StochRSI'],
        "K": row['K'],
        "D": row['D'],
        "Short PNL": short_pnl,
        "Long PNL": long_pnl,
        "Total PNL": pnl,
        "candle_closed": candle_closed,
        "total_long_trades": total_long_trades,
        "total_short_trades": total_short_trades,
        "total_short_loss": total_short_loss,
        "total_short_wins": total_short_wins,
        "total_long_loss": total_long_loss,
        "total_long_wins": total_long_wins,
        "win_rate_long": win_rate_long,
        "avg_percentage": avg_percentage,
        "balance": balance,
        "balance_short": balance_short,
        "balance_long": balance_long
    }

    logging.shutdown()

    return result_dict


if __name__ == "__main__":
    #def find_best_SL_CC_BB(SL,CC,symbol,timeframe,klines,bb_std_dev,bb_window,start_date,end_date):
    klines = client.get_historical_klines('INJUSDT', Client.KLINE_INTERVAL_5MINUTE, "1 nov, 2023", None)
    print(find_best_SL_CC_BB(0.15,0.04,'INJUSDT','5m',klines,3.0,17,"1 nov, 2023",None))


