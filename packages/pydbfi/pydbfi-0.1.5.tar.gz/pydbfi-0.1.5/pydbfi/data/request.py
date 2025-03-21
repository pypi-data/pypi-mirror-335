from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class OrderRequest:
    stock_code: str
    quantity: int
    price: float
    order_type: str  # "1": 매도, "2": 매수

    def to_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in self.__dict__.items() if v is not None}


@dataclass
class TransactionHistoryRequest:
    pass


@dataclass
class BalanceRequest:
    pass


@dataclass
class AbleOrderQuantityRequest:
    pass


@dataclass
class QuoteRequest:
    pass


@dataclass
class ChartRequest:
    pass
