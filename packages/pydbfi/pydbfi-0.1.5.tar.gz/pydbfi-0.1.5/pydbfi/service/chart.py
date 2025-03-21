from typing import Any, Dict

from ..data.domestic.request import *
from ..data.overseas.request import *
from ..service.common.base import BaseService
from ..service.common.interfaces import IChartService


class DomesticChartService(BaseService, IChartService):
    def get_minute_chart(
        self, request: DomesticMinuteChartRequest, cont_yn="N", cont_key=None, **kwargs
    ) -> Dict[str, Any]:
        endpoint = "/api/v1/quote/kr-chart/min"
        data = request.to_request_data()
        return self._request(
            "POST", endpoint, data=data, cont_yn=cont_yn, cont_key=cont_key, **kwargs
        )

    def get_daily_chart(
        self, request: DomesticDailyChartRequest, cont_yn="N", cont_key=None, **kwargs
    ) -> Dict[str, Any]:
        endpoint = "/api/v1/quote/kr-chart/day"
        data = request.to_request_data()
        return self._request(
            "POST", endpoint, data=data, cont_yn=cont_yn, cont_key=cont_key, **kwargs
        )

    def get_weekly_chart(
        self, request: DomesticWeeklyChartRequest, cont_yn="N", cont_key=None, **kwargs
    ) -> Dict[str, Any]:
        endpoint = "/api/v1/quote/kr-chart/week"
        data = request.to_request_data()
        return self._request(
            "POST", endpoint, data=data, cont_yn=cont_yn, cont_key=cont_key, **kwargs
        )

    def get_monthly_chart(
        self, request: DomesticMonthlyChartRequest, cont_yn="N", cont_key=None, **kwargs
    ) -> Dict[str, Any]:
        endpoint = "/api/v1/quote/kr-chart/month"
        data = request.to_request_data()
        return self._request(
            "POST", endpoint, data=data, cont_yn=cont_yn, cont_key=cont_key, **kwargs
        )


class OverseasChartService(BaseService, IChartService):
    def get_minute_chart(
        self, request: OverseasMinuteChartRequest, cont_yn="N", cont_key=None, **kwargs
    ) -> Dict[str, Any]:
        endpoint = "/api/v1/quote/overseas-stock/chart/min"
        data = request.to_request_data()
        return self._request(
            "POST", endpoint, data=data, cont_yn=cont_yn, cont_key=cont_key, **kwargs
        )

    def get_daily_chart(
        self, request: OverseasDailyChartRequest, cont_yn="N", cont_key=None, **kwargs
    ) -> Dict[str, Any]:
        endpoint = "/api/v1/quote/overseas-stock/chart/day"
        data = request.to_request_data()
        return self._request(
            "POST", endpoint, data=data, cont_yn=cont_yn, cont_key=cont_key, **kwargs
        )

    def get_weekly_chart(
        self, request: OverseasWeeklyChartRequest, cont_yn="N", cont_key=None, **kwargs
    ) -> Dict[str, Any]:
        endpoint = "/api/v1/quote/overseas-stock/chart/week"
        data = request.to_request_data()
        return self._request(
            "POST", endpoint, data=data, cont_yn=cont_yn, cont_key=cont_key, **kwargs
        )

    def get_monthly_chart(
        self, request: OverseasMonthlyChartRequest, cont_yn="N", cont_key=None, **kwargs
    ) -> Dict[str, Any]:
        endpoint = "/api/v1/quote/overseas-stock/chart/month"
        data = request.to_request_data()
        return self._request(
            "POST", endpoint, data=data, cont_yn=cont_yn, cont_key=cont_key, **kwargs
        )
