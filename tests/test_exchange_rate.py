import pytest

from mini_ledger.exchange_rate import HardcodedRateProvider


@pytest.fixture
def rate_provider():
    return HardcodedRateProvider()


def test_CHF(rate_provider:HardcodedRateProvider):
    result = rate_provider.get_rate("CHF")
    assert result == 1.00

def test_GBP_is_None(rate_provider:HardcodedRateProvider):
    result = rate_provider.get_rate("GBP")
    assert result  == None

def test_GBP_date_is_None(rate_provider:HardcodedRateProvider):
    result = rate_provider.get_rate("GBP", "2026-04-28")
    assert result == None

def test_USD_correct(rate_provider:HardcodedRateProvider):
    result = rate_provider.get_rate("USD","2026-04-28")
    assert result == 0.90

def test_EUR_correct(rate_provider:HardcodedRateProvider):
    result = rate_provider.get_rate("EUR","2026-04-29")
    assert result == 0.98

def test_USD_wrong_date_is_None(rate_provider:HardcodedRateProvider):
    result = rate_provider.get_rate("USD","2026-04-29")
    assert result == None

def test_EUR_wrong_date_is_None(rate_provider:HardcodedRateProvider):
    result = rate_provider.get_rate("EUR","2026-04-28")
    assert result == None