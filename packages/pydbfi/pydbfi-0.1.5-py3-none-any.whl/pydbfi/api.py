import logging
from datetime import datetime
from typing import Any, Dict

from .data.domestic.request import *
from .data.overseas.request import *
from .oauth import OAuth
from .service.chart import *
from .service.quote import *
from .service.trading import *


class BaseAPI:
    def __init__(self, app_key: str, app_secret_key: str, log_level=logging.INFO):
        self._setup_logging(log_level)
        self.auth = OAuth(appkey=app_key, appsecretkey=app_secret_key)
        self.logger.info("DB증권 API SDK가 초기화되었습니다.")

        try:
            self.auth.get_token()
            self.logger.info(f"토큰 발급 성공 (만료: {self.auth.expire_in})")
        except Exception as e:
            self.logger.error(f"토큰 발급 실패: {str(e)}")

    def _setup_logging(self, log_level):
        self.logger = logging.getLogger("db-trading-sdk")
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        self.logger.setLevel(log_level)

    def close(self):
        try:
            self.auth.revoke_token()
            self.logger.info("DB증권 API 세션이 종료되었습니다.")
        except Exception as e:
            self.logger.error(f"세션 종료 중 오류 발생: {str(e)}")

    def _execute_service(
        self,
        service_getter,
        method_name: str,
        request=None,
        use_cont: bool = False,
        cont_yn: str = "N",
        cont_key: str = None,
    ):
        service = service_getter()
        method = getattr(service, method_name)
        if request is not None:
            if use_cont:
                return method(request, cont_yn=cont_yn, cont_key=cont_key)
            else:
                return method(request)
        else:
            if use_cont:
                return method(cont_yn=cont_yn, cont_key=cont_key)
            else:
                return method()


class DomesticAPI(BaseAPI):
    def __init__(self, app_key: str, app_secret_key: str, log_level=logging.INFO):
        super().__init__(app_key, app_secret_key, log_level)
        self._trading_service = None
        self._quote_service = None
        self._chart_service = None

    def _get_trading_service(self):
        if self._trading_service is None:
            self._trading_service = DomesticTradingService(auth=self.auth)
        return self._trading_service

    def _get_quote_service(self):
        if self._quote_service is None:
            self._quote_service = DomesticQuoteService(auth=self.auth)
        return self._quote_service

    def _get_chart_service(self):
        if self._chart_service is None:
            self._chart_service = DomesticChartService(auth=self.auth)
        return self._chart_service

    # ===== 매매 관련 =====

    def buy(
        self,
        stock_code: str,
        quantity: int,
        price: float,
        price_type: str = "00",  # 지정가(00)
        credit_type: str = "000",  # 보통
        loan_date: str = "00000000",  # 일반주문
        order_condition: str = "0",  # 없음
    ) -> Dict[str, Any]:
        order_request = DomesticOrderRequest(
            stock_code=stock_code,
            quantity=quantity,
            price=price,
            order_type="2",  # 매수
            price_type=price_type,
            credit_type=credit_type,
            loan_date=loan_date,
            order_condition=order_condition,
        )
        return self._execute_service(
            self._get_trading_service, "place_order", request=order_request
        )

    def sell(
        self,
        stock_code: str,
        quantity: int,
        price: float,
        price_type: str = "00",  # 지정가(00)
        credit_type: str = "000",  # 보통
        loan_date: str = "00000000",  # 일반주문
        order_condition: str = "0",  # 없음
    ) -> Dict[str, Any]:
        order_request = DomesticOrderRequest(
            stock_code=stock_code,
            quantity=quantity,
            price=price,
            order_type="1",  # 매도
            price_type=price_type,
            credit_type=credit_type,
            loan_date=loan_date,
            order_condition=order_condition,
        )
        return self._execute_service(
            self._get_trading_service, "place_order", request=order_request
        )

    def cancel(self, order_no: int, stock_code: str, quantity: int) -> Dict[str, Any]:
        cancel_request = DomesticCancelOrderRequest(
            original_order_no=order_no, stock_code=stock_code, quantity=quantity
        )
        return self._execute_service(
            self._get_trading_service, "cancel_order", request=cancel_request
        )

    def get_transaction_history(
        self,
        execution_status: str = "0",  # 체결여부 (0:전체, 1:체결, 2:미체결)
        order_type: str = "0",  # 매매구분 (0:전체, 1:매도, 2:매수)
        stock_type: str = "0",  # 종목구분 (0:전체)
        query_type: str = "0",  # 조회구분 (0:전체, 1:ELW, 2:ELW제외)
        cont_yn: str = "N",
        cont_key: str = None,
    ) -> Dict[str, Any]:
        request = DomesticTransactionHistoryRequest(
            execution_status=execution_status,
            order_type=order_type,
            stock_type=stock_type,
            query_type=query_type,
        )
        return self._execute_service(
            self._get_trading_service,
            "get_transaction_history",
            request=request,
            use_cont=True,
            cont_yn=cont_yn,
            cont_key=cont_key,
        )

    def get_stock_balance(
        self,
        query_type: str = "0",  # 조회구분코드 (0:전체, 1:비상장제외, 2:비상장,코넥스,kotc 제외)
        cont_yn: str = "N",
        cont_key: str = None,
    ) -> Dict[str, Any]:
        request = DomesticBalanceRequest(query_type=query_type)
        return self._execute_service(
            self._get_trading_service,
            "get_balance",
            request=request,
            use_cont=True,
            cont_yn=cont_yn,
            cont_key=cont_key,
        )

    def get_deposit(self, cont_yn: str = "N", cont_key: str = None):
        return self._execute_service(
            self._get_trading_service,
            "get_deposit",
            request=None,
            use_cont=True,
            cont_yn=cont_yn,
            cont_key=cont_key,
        )

    def get_able_order_quantity(
        self,
        stock_code: str,
        price: float,
        order_type: str = "2",  # 매매구분 (1:매도, 2:매수)
        cont_yn: str = "N",
        cont_key: str = None,
    ) -> Dict[str, Any]:
        stock_code = 'A' + stock_code
        request = DomesticAbleOrderQuantityRequest(
            stock_code=stock_code, price=price, order_type=order_type
        )
        return self._execute_service(
            self._get_trading_service,
            "get_able_order_quantity",
            request=request,
            use_cont=True,
            cont_yn=cont_yn,
            cont_key=cont_key,
        )

    # ===== 시세 관련 =====

    def get_stock_tickers(
        self,
        market_code: str = "J",  # 시장분류코드 (J:주식, E:ETF, EN:ETN)
        cont_yn: str = "N",
        cont_key: str = None,
    ) -> Dict[str, Any]:
        request = DomesticQuoteRequest(market_type=market_code)
        return self._execute_service(
            self._get_quote_service,
            "get_stock_tickers",
            request=request,
            use_cont=True,
            cont_yn=cont_yn,
            cont_key=cont_key,
        )

    def get_stock_price(
        self,
        stock_code: str,
        market_code: str = "J",  # 시장분류코드 (J:주식, E:ETF, EN:ETN)
        cont_yn: str = "N",
        cont_key: str = None,
    ) -> Dict[str, Any]:
        request = DomesticQuoteRequest(market_type=market_code, stock_code=stock_code)
        return self._execute_service(
            self._get_quote_service,
            "get_stock_price",
            request=request,
            use_cont=True,
            cont_yn=cont_yn,
            cont_key=cont_key,
        )

    # ===== 차트 관련 =====

    def get_minute_chart(
        self,
        stock_code: str,
        start_date: str,
        time_interval: str = "60",  # 시간 간격 (60:1분, 300:5분, 600:10분 등)
        market_code: str = "J",  # 시장분류코드 (J:주식)
        adjust_price_yn: str = "0",  # 수정주가 사용 여부 (0:사용, 1:미사용)
        cont_yn: str = "N",
        cont_key: str = None,
    ) -> Dict[str, Any]:
        request = DomesticMinuteChartRequest(
            market_type=market_code,
            adjust_price_yn=adjust_price_yn,
            stock_code=stock_code,
            start_date=start_date,
            time_interval=time_interval,
        )
        return self._execute_service(
            self._get_chart_service,
            "get_minute_chart",
            request=request,
            use_cont=True,
            cont_yn=cont_yn,
            cont_key=cont_key,
        )

    def get_daily_chart(
        self,
        stock_code: str,
        start_date: str,
        end_date: str,
        market_code: str = "J",  # 시장분류코드 (J:주식)
        adjust_price_yn: str = "0",  # 수정주가 사용 여부 (0:사용, 1:미사용)
        cont_yn: str = "N",
        cont_key: str = None,
    ) -> Dict[str, Any]:
        request = DomesticDailyChartRequest(
            market_type=market_code,
            adjust_price_yn=adjust_price_yn,
            stock_code=stock_code,
            start_date=start_date,
            end_date=end_date,
        )
        return self._execute_service(
            self._get_chart_service,
            "get_daily_chart",
            request=request,
            use_cont=True,
            cont_yn=cont_yn,
            cont_key=cont_key,
        )

    def get_weekly_chart(
        self,
        stock_code: str,
        start_date: str,
        end_date: str,
        market_code: str = "J",  # 시장분류코드 (J:주식)
        adjust_price_yn: str = "0",  # 수정주가 사용 여부 (0:사용, 1:미사용)
        cont_yn: str = "N",
        cont_key: str = None,
    ) -> Dict[str, Any]:
        request = DomesticWeeklyChartRequest(
            market_type=market_code,
            adjust_price_yn=adjust_price_yn,
            stock_code=stock_code,
            start_date=start_date,
            end_date=end_date,
            period="W",  # 주봉
        )
        return self._execute_service(
            self._get_chart_service,
            "get_weekly_chart",
            request=request,
            use_cont=True,
            cont_yn=cont_yn,
            cont_key=cont_key,
        )

    def get_monthly_chart(
        self,
        stock_code: str,
        start_date: str,
        end_date: str,
        market_code: str = "J",  # 시장분류코드 (J:주식)
        adjust_price_yn: str = "0",  # 수정주가 사용 여부 (0:사용, 1:미사용)
        cont_yn: str = "N",
        cont_key: str = None,
    ) -> Dict[str, Any]:
        request = DomesticMonthlyChartRequest(
            market_type=market_code,
            adjust_price_yn=adjust_price_yn,
            stock_code=stock_code,
            start_date=start_date,
            end_date=end_date,
            period="M",  # 월봉
        )
        return self._execute_service(
            self._get_chart_service,
            "get_monthly_chart",
            request=request,
            use_cont=True,
            cont_yn=cont_yn,
            cont_key=cont_key,
        )

    def get_yearly_chart(
        self,
        stock_code: str,
        start_date: str,
        end_date: str,
        market_code: str = "J",  # 시장분류코드 (J:주식)
        adjust_price_yn: str = "0",  # 수정주가 사용 여부 (0:사용, 1:미사용)
        cont_yn: str = "N",
        cont_key: str = None,
    ) -> Dict[str, Any]:
        request = DomesticWeeklyChartRequest(
            market_type=market_code,
            adjust_price_yn=adjust_price_yn,
            stock_code=stock_code,
            start_date=start_date,
            end_date=end_date,
            period="Y",  # 년봉
        )
        return self._execute_service(
            self._get_chart_service,
            "get_yearly_chart",
            request=request,
            use_cont=True,
            cont_yn=cont_yn,
            cont_key=cont_key,
        )


class OverseasAPI(BaseAPI):
    def __init__(self, app_key: str, app_secret_key: str, log_level=logging.INFO):
        super().__init__(app_key, app_secret_key, log_level)
        self._trading_service = None
        self._quote_service = None
        self._chart_service = None

    def _get_trading_service(self):
        if self._trading_service is None:
            self._trading_service = OverseasTradingService(auth=self.auth)
        return self._trading_service

    def _get_quote_service(self):
        if self._quote_service is None:
            self._quote_service = OverseasQuoteService(auth=self.auth)
        return self._quote_service

    def _get_chart_service(self):
        if self._chart_service is None:
            self._chart_service = OverseasChartService(auth=self.auth)
        return self._chart_service

    # ===== 매매 관련 =====

    def buy(
        self,
        stock_code: str,
        quantity: int,
        price: float,
        price_type: str = "1",  # 지정가
        order_condition: str = "1",  # 일반
        trade_type: str = "0",  # 주문
        original_order_no: int = 0,  # 신규주문
    ) -> Dict[str, Any]:
        order_request = OverseasOrderRequest(
            stock_code=stock_code,
            quantity=quantity,
            price=price,
            order_type="2",  # 매수
            price_type=price_type,
            order_condition=order_condition,
            trade_type=trade_type,
            original_order_no=original_order_no,
        )
        return self._execute_service(
            self._get_trading_service, "place_order", request=order_request
        )

    def sell(
        self,
        stock_code: str,
        quantity: int,
        price: float,
        price_type: str = "1",  # 지정가
        order_condition: str = "1",  # 일반
        trade_type: str = "0",  # 주문
        original_order_no: int = 0,  # 신규주문
    ) -> Dict[str, Any]:
        order_request = OverseasOrderRequest(
            stock_code=stock_code,
            quantity=quantity,
            price=price,
            order_type="1",  # 매도
            price_type=price_type,
            order_condition=order_condition,
            trade_type=trade_type,
            original_order_no=original_order_no,
        )
        return self._execute_service(
            self._get_trading_service, "place_order", request=order_request
        )

    def cancel(self, order_no: int, stock_code: str, quantity: int) -> Dict[str, Any]:
        cancel_request = OverseasCancelOrderRequest(
            original_order_no=order_no, stock_code=stock_code, quantity=quantity
        )
        return self._execute_service(
            self._get_trading_service, "cancel_order", request=cancel_request
        )

    def get_transaction_history(
        self,
        start_date: str = "",  # 조회시작일자 (YYYYMMDD)
        end_date: str = "",  # 조회종료일자 (YYYYMMDD)
        stock_code: str = "",  # 해외주식종목번호 (빈값은 전체 종목)
        order_type: str = "0",  # 해외주식매매구분코드 (0:전체, 1:매도, 2:매수)
        execution_status: str = "0",  # 주문체결구분코드 (0:전체, 1:체결, 2:미체결)
        sort_type: str = "0",  # 정렬구분코드 (0:역순, 1:정순)
        query_type: str = "0",  # 조회구분코드 (0:합산별, 1:건별)
        online_yn: str = "0",  # 온라인여부 (0:전체, Y:온라인, N:오프라인)
        opposite_order_yn: str = "0",  # 반대매매주문여부 (0:전체, Y:반대매매, N:일반주문)
        won_fcurr_type: str = "1",  # 원화외화구분코드 (1:원화, 2:외화)
        cont_yn: str = "N",
        cont_key: str = None,
    ) -> Dict[str, Any]:
        if not start_date and not end_date:
            today = datetime.now().strftime("%Y%m%d")
            start_date = today
            end_date = today

        request = OverseasTransactionHistoryRequest(
            start_date=start_date,
            end_date=end_date,
            stock_code=stock_code,
            order_type=order_type,
            execution_status=execution_status,
            sort_type=sort_type,
            query_type=query_type,
            online_yn=online_yn,
            opposite_order_yn=opposite_order_yn,
            won_fcurr_type=won_fcurr_type,
        )
        return self._execute_service(
            self._get_trading_service,
            "get_transaction_history",
            request=request,
            use_cont=True,
            cont_yn=cont_yn,
            cont_key=cont_key,
        )

    def get_stock_balance(
        self,
        balance_type: str = "2",  # 처리구분코드 (1:외화잔고, 2:주식잔고상세, 3:주식잔고(국가별), 9:당일실현손익)
        cmsn_type: str = "2",  # 수수료구분코드 (0:전부 미포함, 1:매수제비용만 포함, 2:매수제비용+매도제비용)
        won_fcurr_type: str = "2",  # 원화외화구분코드 (1:원화, 2:외화)
        decimal_balance_type: str = "0",  # 소수점잔고구분코드 (0:전체, 1:일반, 2:소수점)
        cont_yn: str = "N",
        cont_key: str = None,
    ) -> Dict[str, Any]:
        request = OverseasBalanceRequest(
            balance_type=balance_type,
            cmsn_type=cmsn_type,
            won_fcurr_type=won_fcurr_type,
            decimal_balance_type=decimal_balance_type,
        )
        return self._execute_service(
            self._get_trading_service,
            "get_balance",
            request=request,
            use_cont=True,
            cont_yn=cont_yn,
            cont_key=cont_key,
        )

    def get_deposit(self, cont_yn: str = "N", cont_key: str = None):
        return self._execute_service(
            self._get_trading_service,
            "get_deposit",
            request=None,
            use_cont=True,
            cont_yn=cont_yn,
            cont_key=cont_key,
        )

    def get_able_order_quantity(
        self,
        stock_code: str,
        price: float,
        trx_type: str = "2",  # 처리구분코드 (1:매도, 2:매수)
        won_fcurr_type: str = "2",  # 원화외화구분코드 (1:원화, 2:외화)
        cont_yn: str = "N",
        cont_key: str = None,
    ) -> Dict[str, Any]:
        request = OverseasAbleOrderQuantityRequest(
            stock_code=stock_code,
            price=price,
            order_type=trx_type,
            won_fcurr_type=won_fcurr_type,
        )
        return self._execute_service(
            self._get_trading_service,
            "get_able_order_quantity",
            request=request,
            use_cont=True,
            cont_yn=cont_yn,
            cont_key=cont_key,
        )

    # ===== 시세 관련  =====

    def get_stock_tickers(
        self,
        market_code: str = "NY",  # 시장 코드 (NY:뉴욕, NA:나스닥, AM:아멕스)
        cont_yn: str = "N",
        cont_key: str = None,
    ) -> Dict[str, Any]:
        request = OverseasStockTickersRequest(market_code=market_code)
        return self._execute_service(
            self._get_quote_service,
            "get_stock_tickers",
            request=request,
            use_cont=True,
            cont_yn=cont_yn,
            cont_key=cont_key,
        )

    def get_stock_price(
        self,
        stock_code: str,
        market_code: str = "FY",  # 시장 코드 (FY:뉴욕, FN:나스닥, FA:아멕스)
        cont_yn: str = "N",
        cont_key: str = None,
    ) -> Dict[str, Any]:
        request = OverseasQuoteRequest(market_code=market_code, stock_code=stock_code)
        return self._execute_service(
            self._get_quote_service,
            "get_stock_price",
            request=request,
            use_cont=True,
            cont_yn=cont_yn,
            cont_key=cont_key,
        )

    # ===== 차트 관련 =====

    def get_minute_chart(
        self,
        stock_code: str,
        start_date: str,
        end_date: str,
        time_interval: str = "60",  # 시간 간격 (60:1분, 300:5분, 600:10분 등)
        market_code: str = "FY",  # 시장 코드 (FY:뉴욕, FN:나스닥, FA:아멕스)
        adjust_price_yn: str = "1",  # 수정주가 사용 여부 (0:미사용, 1:사용)
        period_specified: str = "Y",  # 기간지정여부코드 (Y:기간지정, N:기간미지정)
        hour_class_code: str = "0",  # 입력시간구분코드 (항상 "0" 입력)
        cont_yn: str = "N",
        cont_key: str = None,
    ) -> Dict[str, Any]:
        request = OverseasMinuteChartRequest(
            market_type=market_code,
            adjust_price_yn=adjust_price_yn,
            period_specified=period_specified,
            hour_class_code=hour_class_code,
            stock_code=stock_code,
            start_date=start_date,
            end_date=end_date,
            chart_interval_code=time_interval,
        )
        return self._execute_service(
            self._get_chart_service,
            "get_minute_chart",
            request=request,
            use_cont=True,
            cont_yn=cont_yn,
            cont_key=cont_key,
        )

    def get_daily_chart(
        self,
        stock_code: str,
        start_date: str,
        end_date: str,
        market_code: str = "FY",  # 시장 코드 (FY:뉴욕, FN:나스닥, FA:아멕스)
        adjust_price_yn: str = "1",  # 수정주가 사용 여부 (0:미사용, 1:사용)
        cont_yn: str = "N",
        cont_key: str = None,
    ) -> Dict[str, Any]:
        request = OverseasDailyChartRequest(
            adjust_price_yn=adjust_price_yn,
            market_type=market_code,
            stock_code=stock_code,
            start_date=start_date,
            end_date=end_date,
        )
        return self._execute_service(
            self._get_chart_service,
            "get_daily_chart",
            request=request,
            use_cont=True,
            cont_yn=cont_yn,
            cont_key=cont_key,
        )

    def get_weekly_chart(
        self,
        stock_code: str,
        start_date: str,
        end_date: str,
        market_code: str = "FY",  # 시장 코드 (FY:뉴욕, FN:나스닥, FA:아멕스)
        use_adjust_price: str = "1",  # 수정주가 사용 여부 (0:미사용, 1:사용)
        cont_yn: str = "N",
        cont_key: str = None,
    ) -> Dict[str, Any]:
        request = OverseasWeeklyChartRequest(
            market_type=market_code,
            use_adjust_price=use_adjust_price,
            stock_code=stock_code,
            start_date=start_date,
            end_date=end_date,
            period_div_code="W",  # 주봉
        )
        return self._execute_service(
            self._get_chart_service,
            "get_weekly_chart",
            request=request,
            use_cont=True,
            cont_yn=cont_yn,
            cont_key=cont_key,
        )

    def get_monthly_chart(
        self,
        stock_code: str,
        start_date: str,
        end_date: str,
        market_code: str = "FY",  # 시장 코드 (FY:뉴욕, FN:나스닥, FA:아멕스)
        use_adjust_price: str = "1",  # 수정주가 사용 여부 (0:미사용, 1:사용)
        cont_yn: str = "N",
        cont_key: str = None,
    ) -> Dict[str, Any]:
        request = OverseasWeeklyChartRequest(
            market_type=market_code,
            use_adjust_price=use_adjust_price,
            stock_code=stock_code,
            start_date=start_date,
            end_date=end_date,
            period_div_code="M",  # 월봉
        )
        return self._execute_service(
            self._get_chart_service,
            "get_monthly_chart",
            request=request,
            use_cont=True,
            cont_yn=cont_yn,
            cont_key=cont_key,
        )

    def get_yearly_chart(
        self,
        stock_code: str,
        start_date: str,
        end_date: str,
        market_code: str = "FY",  # 시장 코드 (FY:뉴욕, FN:나스닥, FA:아멕스)
        use_adjust_price: str = "1",  # 수정주가 사용 여부 (0:미사용, 1:사용)
        cont_yn: str = "N",
        cont_key: str = None,
    ) -> Dict[str, Any]:
        request = OverseasWeeklyChartRequest(
            market_type=market_code,
            use_adjust_price=use_adjust_price,
            stock_code=stock_code,
            start_date=start_date,
            end_date=end_date,
            period_div_code="Y",  # 년봉
        )
        return self._execute_service(
            self._get_chart_service,
            "get_yearly_chart",
            request=request,
            use_cont=True,
            cont_yn=cont_yn,
            cont_key=cont_key,
        )
