
from abc import ABC, abstractmethod

class ExchangeRateProvider(ABC):
    
    @abstractmethod
    def get_rate(self, currency: str, date: str = None) -> float | None:
        ...

class HardcodedRateProvider(ExchangeRateProvider):
    
    RATES = {
        ("USD", "2026-04-28"): 0.90,
        ("EUR", "2026-04-29"): 0.98,
    }
    
    def get_rate(self, currency: str, date: str = None) -> float | None:
        if currency == "CHF":
            return 1.00
        
        # returns None when the key doesn't exist
        return self.RATES.get((currency, date))

class LiveApiRateProvider(ExchangeRateProvider):

    def get_rate(self, currency: str, date: str = None) -> float | None:
        # call a real API here
        # return the rate or None
        ...