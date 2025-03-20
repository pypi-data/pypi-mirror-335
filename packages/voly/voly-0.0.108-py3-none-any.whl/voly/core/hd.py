"""
This module handles calculating historical densities from
time series of prices and converting them to implied volatility smiles.
"""

import ccxt
import pandas as pd
import datetime as dt
from voly.utils.logger import logger, catch_exception
from voly.exceptions import VolyError


@catch_exception
def get_historical_data(currency, lookback_days, granularity, exchange_name):
    """
    Fetch historical OHLCV data for a cryptocurrency.

    Parameters:
    ----------
    currency : str
        The cryptocurrency to fetch data for (e.g., 'BTC', 'ETH').
    lookback_days : str
        The lookback period in days, formatted as '90d', '30d', etc.
    granularity : str
        The time interval for data points (e.g., '15m', '1h', '1d').
    exchange_name : str
        The exchange to fetch data from (default: 'binance').

    Returns:
    -------
    df_hist : pandas.DataFrame containing the historical price data with OHLCV columns.
    """

    try:
        # Get the exchange class from ccxt
        exchange_class = getattr(ccxt, exchange_name.lower())
        exchange = exchange_class({'enableRateLimit': True})
    except (AttributeError, TypeError):
        raise VolyError(f"Exchange '{exchange_name}' not found in ccxt. Please check the exchange name.")

    # Form the trading pair symbol
    symbol = currency + '/USDT'

    # Convert lookback_days to timestamp
    if lookback_days.endswith('d'):
        days_ago = int(lookback_days[:-1])
        date_start = (dt.datetime.now() - dt.timedelta(days=days_ago)).strftime('%Y-%m-%d %H:%M:%S')
    else:
        raise VolyError("lookback_days should be in format '90d', '30d', etc.")

    # Convert start date to timestamp
    from_ts = exchange.parse8601(date_start)

    # Fetch OHLCV data in batches
    ohlcv = []
    last_timestamp = from_ts

    while True:
        batch = exchange.fetch_ohlcv(symbol, granularity, since=last_timestamp, limit=1000)

        if len(batch) == 0:
            break

        if ohlcv and batch[0][0] == ohlcv[-1][0]:
            batch = batch[1:]  # Avoid duplicates

        ohlcv.extend(batch)

        # Update timestamp for next batch
        last_timestamp = batch[-1][0]

        # Break if we got less than the limit (reached the end)
        if len(batch) < 1000:
            break

    # Convert to DataFrame
    df_hist = pd.DataFrame(ohlcv, columns=['date', 'open', 'high', 'low', 'close', 'volume'])
    df_hist['date'] = pd.to_datetime(df_hist['date'], unit='ms')
    df_hist.set_index('date', inplace=True)
    df_hist = df_hist.sort_index(ascending=True)

    print(f"Data fetched successfully: {len(df_hist)} rows from {df_hist.index[0]} to {df_hist.index[-1]}")

    return df_hist
