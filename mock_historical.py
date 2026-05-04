import pandas as pd
import numpy as np
import datetime

def get_mock_historical_data(days_back=1, interval_minutes=5):
    """
    Generates realistic looking mock candlestick data (OHLCV)
    for testing the dashboard charting without needing an API key.
    """
    to_date = datetime.datetime.now()
    # Ensure we generate timestamps for market hours only (mocking continuous for simplicity)
    from_date = to_date - datetime.timedelta(days=days_back)
    
    # Generate timestamp index
    timestamps = pd.date_range(start=from_date, end=to_date, freq=f'{interval_minutes}T')
    
    # Generate a random walk for prices
    steps = len(timestamps)
    returns = np.random.normal(loc=0.0001, scale=0.002, size=steps)
    price_series = 22400.0 * np.exp(np.cumsum(returns))
    
    # Construct OHLC
    data = []
    for i in range(steps):
        base_price = price_series[i]
        high = base_price + np.random.uniform(5, 20)
        low = base_price - np.random.uniform(5, 20)
        open_p = base_price + np.random.uniform(-5, 5)
        close_p = base_price + np.random.uniform(-5, 5)
        
        # Ensure High/Low constraints
        high = max(high, open_p, close_p)
        low = min(low, open_p, close_p)
        
        data.append({
            "date": timestamps[i],
            "open": round(open_p, 2),
            "high": round(high, 2),
            "low": round(low, 2),
            "close": round(close_p, 2),
            "volume": int(np.random.uniform(10000, 50000))
        })
        
    df = pd.DataFrame(data)
    return df
