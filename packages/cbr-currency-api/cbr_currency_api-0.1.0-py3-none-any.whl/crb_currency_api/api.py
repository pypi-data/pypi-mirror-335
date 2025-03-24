from decimal import Decimal, getcontext
from xml.etree import ElementTree

from .baseAPI import BaseAPI


class CrbCurrencyAPI(BaseAPI):
    url = "http://www.cbr.ru/scripts/XML_daily.asp"

    async def get_currency_rate(self, currency_code: str) -> Decimal:
        """
        Получает курс валюты по её коду
        :param currency_code: Код валюты
        :return: Курс валюты
        """
        # Проверяем, есть ли запрос в кеше
        if currency_code in self.cache:
            return Decimal(self.cache[currency_code])

        getcontext().prec = 5  # Устанавливаем точность decimal = 5
        response = await self._make_request(self.url)  # Делаем запрос к API центробанка
        # Обработка XML
        root = ElementTree.fromstring(response.text)
        rates = {}
        for currency in root.findall("Valute"):
            code = currency.find("CharCode").text
            rate = currency.find("VunitRate").text.replace(",", ".")
            rates[code] = rate
            self.cache[code] = rate
        if currency_code in rates:
            return Decimal(rates[currency_code])
        raise ValueError(f"Валюта {currency_code} не найдена")

    async def exchange(self, from_currency: str, to_currency: str, amount: Decimal):
        from_rate = await self.get_currency_rate(from_currency)
        to_rate = await self.get_currency_rate(to_currency)
        return from_rate / to_rate * amount
