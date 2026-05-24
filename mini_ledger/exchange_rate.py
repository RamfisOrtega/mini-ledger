class HardcodedRateProvider:
    
    RATES = {
        ("USD", "2026-04-28"): 0.90,
        ("EUR", "2026-04-29"): 0.98,
    }
    
    def get_rate(self, currency: str, date: str = None) -> float | None:
        if currency == "CHF":
            return 1.00
        
        # returns None when the key doesn't exist
        return self.RATES.get((currency, date))