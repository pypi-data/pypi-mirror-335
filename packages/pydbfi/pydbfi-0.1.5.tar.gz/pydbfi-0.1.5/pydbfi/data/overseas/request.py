from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional

from ..request import *


@dataclass
class OverseasOrderRequest(OrderRequest):
    price_type: str = "1"  # 기본값: 지정가
    order_condition: str = "1"  # 기본값: 일반
    trade_type: str = "0"  # 기본값: 주문
    original_order_no: int = 0  # 기본값: 신규주문

    def to_request_data(self) -> Dict[str, Any]:
        return {
            "In": {
                "AstkIsuNo": self.stock_code,
                "AstkBnsTpCode": self.order_type,
                "AstkOrdprcPtnCode": self.price_type,
                "AstkOrdCndiTpCode": self.order_condition,
                "AstkOrdQty": self.quantity,
                "AstkOrdPrc": self.price,
                "OrdTrdTpCode": self.trade_type,
                "OrgOrdNo": self.original_order_no,
            }
        }


@dataclass
class OverseasCancelOrderRequest:
    original_order_no: int
    stock_code: str
    quantity: int

    def to_request_data(self) -> Dict[str, Any]:
        return {
            "In": {
                "AstkIsuNo": self.stock_code,
                "AstkBnsTpCode": "1",  # 취소주문시에는 원래 매도/매수 구분과 무관
                "AstkOrdprcPtnCode": "1",  # 지정가
                "AstkOrdCndiTpCode": "1",  # 일반
                "AstkOrdQty": self.quantity,
                "AstkOrdPrc": 0,
                "OrdTrdTpCode": "2",  # 취소주문
                "OrgOrdNo": self.original_order_no,
            }
        }


@dataclass
class OverseasTransactionHistoryRequest(TransactionHistoryRequest):
    start_date: str = ""  # 조회시작일자 (YYYYMMDD)
    end_date: str = ""  # 조회종료일자 (YYYYMMDD)
    stock_code: str = ""  # 해외주식종목번호 (빈값은 전체 종목)
    order_type: str = "0"  # 해외주식매매구분코드 (0:전체, 1:매도, 2:매수)
    execution_status: str = "0"  # 주문체결구분코드 (0:전체, 1:체결, 2:미체결)
    sort_type: str = "0"  # 정렬구분코드 (0:역순, 1:정순)s
    query_type: str = "0"  # 조회구분코드 (0:합산별, 1:건별)
    online_yn: str = "0"  # 온라인여부 (0:전체, Y:온라인, N:오프라인)
    opposite_order_yn: str = "0"  # 반대매매주문여부 (0:전체, Y:반대매매, N:일반주문)
    won_fcurr_type: str = "1"  # 원화외화구분코드 (1:원화, 2:외화)

    def to_request_data(self) -> Dict[str, Any]:
        # 시작일자와 종료일자가 없으면 당일 조회
        if not self.start_date and not self.end_date:
            today = datetime.now().strftime("%Y%m%d")
            self.start_date = today
            self.end_date = today

        return {
            "In": {
                "QrySrtDt": self.start_date,
                "QryEndDt": self.end_date,
                "AstkIsuNo": self.stock_code,
                "AstkBnsTpCode": self.order_type,
                "OrdxctTpCode": self.execution_status,
                "StnlnTpCode": self.sort_type,
                "QryTpCode": self.query_type,
                "OnlineYn": self.online_yn,
                "CvrgOrdYn": self.opposite_order_yn,
                "WonFcurrTpCode": self.won_fcurr_type,
            }
        }


@dataclass
class OverseasAbleOrderQuantityRequest(AbleOrderQuantityRequest):
    order_type: str = "1"  # 처리구분코드 ("1:매도, 2:매수")
    stock_code: str = "0"  # 해외주식종목번호
    price: float = 0  # 해외주식주문가
    won_fcurr_type: str = "2"  # 원화외화구분코드 (1:원화, 2:외화)

    def to_request_data(self) -> Dict[str, Any]:
        return {
            "In": {
                "TrxTpCode": self.order_type,
                "AstkIsuNo": self.stock_code,
                "AstkOrdPrc": self.price,
                "WonFcurrTpCode": self.won_fcurr_type,
            }
        }


@dataclass
class OverseasBalanceRequest(BalanceRequest):
    balance_type: str = (
        "2"  # 처리구분코드 (1:외화잔고, 2:주식잔고상세, 3:주식잔고(국가별), 9:당일실현손익)
    )
    cmsn_type: str = (
        "2"  # 수수료구분코드 (0:전부 미포함, 1:매수제비용만 포함, 2:매수제비용+매도제비용)
    )
    won_fcurr_type: str = "2"  # 원화외화구분코드 (1:원화, 2:외화)
    decimal_balance_type: str = "0"  # 소수점잔고구분코드 (0:전체, 1:일반, 2:소수점)

    def to_request_data(self) -> Dict[str, Any]:
        """API 요청 데이터 형식으로 변환"""
        return {
            "In": {
                "TrxTpCode": self.balance_type,
                "CmsnTpCode": self.cmsn_type,
                "WonFcurrTpCode": self.won_fcurr_type,
                "DpntBalTpCode": self.decimal_balance_type,
            }
        }


@dataclass
class OverseasStockTickersRequest(QuoteRequest):
    market_code: str = "NY"  # 시장 코드 (NY:뉴욕, NA:나스닥, AM:아멕스)

    def to_request_data(self) -> Dict[str, Any]:
        return {"In": {"InputDataCode": self.market_code}}


@dataclass
class OverseasQuoteRequest(QuoteRequest):
    market_code: str = "FY"  # 시장 코드 (FY:뉴욕, FN:나스닥, FA:아멕스)
    stock_code: Optional[str] = None  # 종목 코드

    def to_request_data(self) -> Dict[str, Any]:
        return {
            "In": {
                "InputCondMrktDivCode": self.market_code,
                "InputIscd1": self.stock_code,
            }
        }


@dataclass
class OverseasMinuteChartRequest(ChartRequest):
    market_type: str = "FY"  # 입력조건시장분류코드 (FY:뉴욕, FN:나스닥, FA:아멕스)
    adjust_price_yn: str = "1"  # 수정주가 사용 여부 (0:미사용, 1:사용)
    period_specified: str = "Y"  # 기간지정여부코드 (Y:기간지정, N:기간미지정)
    hour_class_code: str = "0"  # 입력시간구분코드 (항상 "0" 입력)
    stock_code: str = ""  # 해외주식 종목코드 (ex. TQQQ)
    start_date: str = ""  # 입력날짜1 (YYYYMMDD)
    end_date: str = ""  # 입력날짜2 (YYYYMMDD)
    chart_interval_code: str = (
        "60"  # 분일별구분코드 (30:30초, 60:1분, 600:10분, 3600:60분)
    )
    period_div_code: Optional[str] = None  # 입력주기 (W:주, M:월, Y:년)

    def to_request_data(self) -> Dict[str, Any]:
        return {
            "In": {
                "InputCondMrktDivCode": self.market_type,
                "InputOrgAdjPrc": self.adjust_price_yn,
                "InputPwDataIncuYn": self.period_specified,
                "InputHourClsCode": self.hour_class_code,
                "InputIscd1": self.stock_code,
                "InputDate1": self.start_date,
                "InputDate2": self.end_date,
                "InputDivXtick": self.chart_interval_code,
                "InputPeriodDivCode": self.period_div_code,
            }
        }


@dataclass
class OverseasDailyChartRequest(ChartRequest):
    market_type: str = "FY"  # 입력조건시장분류코드 (FY:뉴욕, FN:나스닥, FA:아멕스)
    adjust_price_yn: str = "1"  # 수정주가 사용 여부 (0:미사용, 1:사용)
    stock_code: str = ""  # 해외주식 종목코드 (ex. TQQQ)
    start_date: str = ""  # 입력날짜1 (YYYYMMDD)
    end_date: str = ""  # 입력날짜2 (YYYYMMDD)

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
class OverseasWeeklyChartRequest(ChartRequest):
    market_type: str = "FY"  # 입력조건시장분류코드 (FY:뉴욕, FN:나스닥, FA:아멕스)
    use_adjust_price: str = "1"  # 수정주가 사용 여부 (0:미사용, 1:사용)
    stock_code: str = ""  # 해외주식 종목코드 (ex. TQQQ)
    start_date: str = ""  # 입력날짜1 (YYYYMMDD)
    end_date: str = ""  # 입력날짜2 (YYYYMMDD)
    period_div_code: str = "W"  # 입력일/주/월/년 (D:일, W:주, M:월, Y:년)

    def to_request_data(self) -> Dict[str, Any]:
        return {
            "In": {
                "InputCondMrktDivCode": self.market_type,
                "InputOrgAdjPrc": self.use_adjust_price,
                "InputIscd1": self.stock_code,
                "InputDate1": self.start_date,
                "InputDate2": self.end_date,
                "InputPeriodDivCode": self.period_div_code,
            }
        }


@dataclass
class OverseasMonthlyChartRequest(ChartRequest):
    use_adjust_price: str = "1"  # 수정주가 사용 여부 (0:미사용, 1:사용)
    market_type: str = "FY"  # 입력조건시장분류코드 (FY:뉴욕, FN:나스닥, FA:아멕스)
    stock_code: str = ""  # 해외주식 종목코드 (ex. TQQQ)
    start_date: str = ""  # 입력날짜1 (YYYYMMDD)
    end_date: str = ""  # 입력날짜2 (YYYYMMDD)

    def to_request_data(self) -> Dict[str, Any]:
        return {
            "In": {
                "InputOrgAdjPrc": self.use_adjust_price,
                "InputCondMrktDivCode": self.market_type,
                "InputIscd1": self.stock_code,
                "InputDate1": self.start_date,
                "InputDate2": self.end_date,
            }
        }
