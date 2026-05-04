import logging
from py_vollib.black_scholes.implied_volatility import implied_volatility

class SignalEngine:
    def __init__(self, strike_step=50, risk_free_rate=0.07):
        self.strike_step = strike_step
        self.risk_free_rate = risk_free_rate
        
    def get_atm_strike(self, ltp):
        """Calculate the nearest At-The-Money strike based on LTP and strike step."""
        if ltp <= 0:
            return 0
        
        # Round to nearest strike step
        atm = round(ltp / self.strike_step) * self.strike_step
        return atm

    def check_smart_money(self, tick, ltq_threshold=1000):
        """Flag unusual last traded quantity in a single tick."""
        ltq = tick.get('last_traded_quantity', 0)
        
        if ltq >= ltq_threshold:
            return True, f"High LTQ: {ltq}"
        return False, None

    def calculate_iv(self, option_price, spot_price, strike, dte, option_type):
        """
        Calculate Implied Volatility using Black-Scholes.
        dte: Days to expiry
        option_type: 'c' or 'p'
        """
        if option_price <= 0 or spot_price <= 0 or dte <= 0:
            return 0.0
            
        time_to_expiry_years = dte / 365.0
        try:
            iv = implied_volatility(option_price, spot_price, strike, time_to_expiry_years, self.risk_free_rate, option_type)
            return round(iv * 100, 2) # Return as percentage
        except Exception as e:
            logging.debug(f"IV calc error: {e}")
            return 0.0

    def evaluate(self, tick, spot_price=None, strike=None, dte=None, option_type=None):
        """
        Evaluates a tick for signals.
        Returns a dictionary with signal information.
        """
        signals = {}
        ltp = tick.get('last_price', 0)
        
        # 1. ATM Logic
        atm = self.get_atm_strike(ltp)
        signals['atm_strike'] = atm
        
        # 2. Smart Money
        is_smart_money, reason = self.check_smart_money(tick)
        signals['smart_money_flag'] = is_smart_money
        if is_smart_money:
            signals['smart_money_reason'] = reason
            
        # 3. IV Calculation (only valid for options)
        if spot_price and strike and dte and option_type:
            signals['iv'] = self.calculate_iv(ltp, spot_price, strike, dte, option_type)
            
        return signals
