import logging
import datetime
import pandas as pd
from kiteconnect import KiteConnect

class HistoricalDataEngine:
    def __init__(self, api_key, access_token):
        self.kite = KiteConnect(api_key=api_key)
        self.kite.set_access_token(access_token)

    def fetch_candles(self, instrument_token, interval="minute", days_back=1):
        """
        Fetches historical data for a given instrument.
        Requires Historical API Add-on subscription from Zerodha.
        """
        try:
            to_date = datetime.datetime.now()
            from_date = to_date - datetime.timedelta(days=days_back)
            
            # This will fail with a PermissionException if the add-on is not active
            data = self.kite.historical_data(
                instrument_token=instrument_token,
                from_date=from_date,
                to_date=to_date,
                interval=interval
            )
            
            if data:
                df = pd.DataFrame(data)
                df['date'] = pd.to_datetime(df['date'])
                return df
            return pd.DataFrame()
        except Exception as e:
            logging.error(f"Failed to fetch historical data: {e}")
            return pd.DataFrame()
