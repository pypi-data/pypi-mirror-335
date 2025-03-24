import asyncio
from decimal import Decimal
from crb_currency_api import CrbCurrencyAPI

async def test_get_currency_rate():
    api = CrbCurrencyAPI()
    rate = await api.get_currency_rate("USD")
    assert isinstance(rate, Decimal)
    print(f"Курс USD: {rate}")

async def test_exchange():
    api = CrbCurrencyAPI()
    result = await api.exchange("USD", "EUR", Decimal("100"))
    assert isinstance(result, Decimal)
    print(f"100 USD = {result} EUR")

if __name__ == "__main__":
    asyncio.run(test_get_currency_rate())
    asyncio.run(test_exchange())