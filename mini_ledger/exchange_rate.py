class HardcodedRateProvider:
    
    RATES = {
        ("USD", "2026-04-28"): 0.90,
        ("EUR", "2026-04-29"): 0.98,
    }
    
    def get_rate(self, currency: str, date: str = None) -> float | None:
        if currency == "CHF":
            return 1.00
        
        # No entry means no rate for that day. The pipeline dead-letters those
        # rather than guessing at a number.
        return self.RATES.get((currency, date))