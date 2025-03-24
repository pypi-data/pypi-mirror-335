from abc import ABC, abstractmethod
from decimal import Decimal
from tenacity import retry, stop_after_attempt, retry_if_exception, wait_fixed
import httpx
from cachetools import TTLCache


class BaseAPI(ABC):
    RETRIES = 3
    RETRY_STATUS_CODES = [
        429,  # TOO_MANY_REQUESTS
        500,  # INTERNAL_SERVER_ERROR
        502,  # BAD_GATEWAY
        503,  # SERVICE_UNAVAILABLE
        504,  # GATEWAY_TIMEOUT
    ]

    def __init__(self):
        self.cache = TTLCache(maxsize=100, ttl=86400)  # Кеш на 24 часа

    @abstractmethod
    async def get_currency_rate(self, currency_code: str) -> Decimal:
        pass

    def _should_retry(self, exc: BaseException) -> bool:
        if isinstance(exc, httpx.HTTPStatusError):
            return exc.response.status_code in self.RETRY_STATUS_CODES
        return False

    @retry(
        stop=stop_after_attempt(RETRIES),  # Максимум 3 попытки
        wait=wait_fixed(2),  # Ждем 2 сек между попытками
        retry=retry_if_exception(_should_retry)
    )
    async def _make_request(self, url: str) -> httpx.Response:
        """
        Выполняет http запрос с повторными попытками
        :param url: Адрес запроса
        :return: Ответ сервера
        :raises httpx.HTTPStatusError: Ошибка HTTP
        """
        async with httpx.AsyncClient() as client:
            # Делаем запрос к API
            response = await client.get(url)
            # Проверяем статус код ответа
            response.raise_for_status()
            return response
