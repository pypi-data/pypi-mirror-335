from dataclasses import dataclass
from typing import Any, Dict, Optional

from ..request import *


@dataclass
class DomesticOrderRequest(OrderRequest):
    price_type: str = "00"  # 기본값: 지정가
    credit_type: str = "000"  # 기본값: 보통
    loan_date: str = "00000000"  # 기본값: 일반주문
    order_condition: str = "0"  # 기본값: 없음

    def to_request_data(self) -> Dict[str, Any]:
        if not self.stock_code.startswith("A") and len(self.stock_code) == 6:
            isu_no = self.stock_code
        else:
            isu_no = self.stock_code

        return {
            "In": {
                "IsuNo": isu_no,  # 종목번호
                "OrdQty": self.quantity,  # 주문수량
                "OrdPrc": self.price,  # 주문가
                "BnsTpCode": self.order_type,  # 매매구분
                "OrdprcPtnCode": self.price_type,  # 호가유형코드
                "MgntrnCode": self.credit_type,  # 신용거래코드
                "LoanDt": self.loan_date,  # 대출일
                "OrdCndiTpCode": self.order_condition,  # 주문조건
            }
        }


@dataclass
class DomesticCancelOrderRequest:
    original_order_no: int
    stock_code: str
    quantity: int

    def to_request_data(self) -> Dict[str, Any]:
        return {
            "In": {
                "OrgOrdNo": self.original_order_no,
                "IsuNo": self.stock_code,
                "OrdQty": self.quantity,
            }
        }


@dataclass
class DomesticTransactionHistoryRequest(TransactionHistoryRequest):
    execution_status: str = "0"  # 체결여부 (0:전체, 1:체결, 2:미체결)
    order_type: str = "0"  # 매매구분 (0:전체, 1:매도, 2:매수)
    stock_type: str = "0"  # 종목구분 (0:전체)
    query_type: str = "0"  # 조회구분 (0:전체, 1:ELW, 2:ELW제외)

    def to_request_data(self) -> Dict[str, Any]:
        return {
            "In": {
                "ExecYn": self.execution_status,
                "BnsTpCode": self.order_type,
                "IsuTpCode": self.stock_type,
                "QryTp": self.query_type,
            }
        }


@dataclass
class DomesticAbleOrderQuantityRequest(AbleOrderQuantityRequest):
    order_type: str = "0"  # 매매구분 (1:매도, 2:매수)
    stock_code: str = "0"  # 종목번호
    price: float = 0  # 주문가

    def to_request_data(self) -> Dict[str, Any]:
        return {
            "In": {
                "BnsTpCode": self.order_type,
                "IsuNo": self.stock_code,
                "OrdPrc": self.price,
            }
        }


@dataclass
class DomesticBalanceRequest(BalanceRequest):
    query_type: str = (
        "0"  # 조회구분코드 (0:전체, 1:비상장제외, 2:비상장,코넥스,kotc 제외)
    )

    def to_request_data(self) -> Dict[str, Any]:
        """API 요청 데이터 형식으로 변환"""
        return {"In": {"QryTpCode": self.query_type}}


@dataclass
class DomesticQuoteRequest(QuoteRequest):
    market_type: str = (
        "J"  # 입력 조건 시장 분류 코드 (J:주식, E:ELW, EN:ETN, U:업종&지수, W:ELW)
    )
    stock_code: Optional[str] = None  # 종목 코드 (업종(U) 선택 시 지수 코드)

    def to_request_data(self) -> Dict[str, Any]:
        return {
            "In": {
                "InputCondMrktDivCode": self.market_type,
                "InputIscd1": self.stock_code,
            }
        }


@dataclass
class DomesticMinuteChartRequest(ChartRequest):
    market_type: str = "J"
    adjust_price_yn: str = "0"  # 수정 주가 사용 여부 (0:사용, 1:미사용)
    stock_code: str = "0"  # 종목 코드
    start_date: str = "0"  # 조회일자 (YYYYMMDD)
    time_interval: Optional[str] = None  # 시간 간격 (60*N: N분)

    def to_request_data(self) -> Dict[str, Any]:
        return {
            "In": {
                "InputCondMrktDivCode": self.market_type,
                "InputOrgAdjPrc": self.adjust_price_yn,
                "InputIscd1": self.stock_code,
                "InputDate1": self.start_date,
                "InputDivXtick": self.time_interval,
            }
        }


@dataclass
class DomesticDailyChartRequest(ChartRequest):
    market_type: str = "J"
    adjust_price_yn: str = "0"  # 수정 주가 사용 여부 (0:사용, 1:미사용)
    stock_code: str = "0"  # 종목 코드
    start_date: str = "0"  # 조회일자 (YYYYMMDD)
    end_date: str = "0"  # 조회일자 (YYYYMMDD)

    def to_request_data(self) -> Dict[str, Any]:
        return {
            "In": {
                "InputCondMrktDivCode": self.market_type,
                "InputOrgAdjPrc": self.adjust_price_yn,
                "InputIscd1": self.stock_code,
                "InputDate1": self.start_date,
                "InputDate2": self.end_date,
            }
        }


@dataclass
class DomesticWeeklyChartRequest(ChartRequest):
    market_type: str = "J"
    adjust_price_yn: str = "0"  # 수정 주가 사용 여부 (0:사용, 1:미사용)
    stock_code: str = "0"  # 종목 코드
    start_date: str = "0"  # 조회일자 (YYYYMMDD)
    end_date: str = "0"  # 조회일자 (YYYYMMDD)
    period: str = "W"  # 주기 (W:주, M:월, Y:년)

    def to_request_data(self) -> Dict[str, Any]:
        return {
            "In": {
                "InputCondMrktDivCode": self.market_type,
                "InputOrgAdjPrc": self.adjust_price_yn,
                "InputIscd1": self.stock_code,
                "InputDate1": self.start_date,
                "InputDate2": self.end_date,
                "InputPeriodDivCode": self.period,
            }
        }


@dataclass
class DomesticMonthlyChartRequest(ChartRequest):
    market_type: str = "J"
    adjust_price_yn: str = "0"  # 수정 주가 사용 여부 (0:사용, 1:미사용)
    stock_code: str = "0"  # 종목 코드
    start_date: str = "0"  # 조회일자 (YYYYMMDD)
    end_date: str = "0"  # 조회일자 (YYYYMMDD)
    period: str = "M"  # 주기 (W:주, M:월, Y:년)

    def to_request_data(self) -> Dict[str, Any]:
        return {
            "In": {
                "InputCondMrktDivCode": self.market_type,
                "InputOrgAdjPrc": self.adjust_price_yn,
                "InputIscd1": self.stock_code,
                "InputDate1": self.start_date,
                "InputDate2": self.end_date,
                "InputPeriodDivCode": self.period,
            }
        }
