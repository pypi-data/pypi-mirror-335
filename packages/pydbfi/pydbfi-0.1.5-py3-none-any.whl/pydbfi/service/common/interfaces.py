from abc import ABC, abstractmethod
from typing import Any, Dict


class ITradingService(ABC):
    @abstractmethod
    def place_order(self, order_request, **kwargs) -> Dict[str, Any]:
        pass

    @abstractmethod
    def cancel_order(self, cancel_request, **kwargs) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_transaction_history(
        self, request, cont_yn="N", cont_key=None, **kwargs
    ) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_able_order_quantity(
        self, request, cont_yn="N", cont_key=None, **kwargs
    ) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_balance(
        self, request, cont_yn="N", cont_key=None, **kwargs
    ) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_deposit(self, cont_yn="N", cont_key=None, **kwargs) -> Dict[str, Any]:
        pass


class IQuoteService(ABC):
    @abstractmethod
    def get_stock_tickers(
        self, request, cont_yn="N", cont_key=None, **kwargs
    ) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_stock_price(
        self, request, cont_yn="N", cont_key=None, **kwargs
    ) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_order_book(
        self, request, cont_yn="N", cont_key=None, **kwargs
    ) -> Dict[str, Any]:
        pass


class IChartService(ABC):
    @abstractmethod
    def get_minute_chart(
        self, chart_request, cont_yn="N", cont_key=None, **kwargs
    ) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_daily_chart(
        self, chart_request, cont_yn="N", cont_key=None, **kwargs
    ) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_weekly_chart(
        self, chart_request, cont_yn="N", cont_key=None, **kwargs
    ) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_monthly_chart(self, cont_yn="N", cont_key=None, **kwargs) -> Dict[str, Any]:
        pass
