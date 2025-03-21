from collections import OrderedDict
from dataclasses import dataclass
from typing import Tuple, Dict, List
import math

from utils_hj3415 import tools, setup_logger
from db_hj3415 import myredis

from analyser_hj3415.analyser.eval.common import Tools

mylogger = setup_logger(__name__,'INFO')


@dataclass
class RedData:
    """
    재무 데이터를 표현하고 계산하기 위한 데이터 구조.

    이 클래스는 기업의 재무 데이터를 관리하며, 사업가치, 재산가치, 부채평가 등 다양한 재무
    지표를 포함합니다. 초기화 시 특정 속성 값을 검증하며, 재무 데이터 분석에 유용하게 활용됩니다.

    속성:
        code (str): 기업의 6자리 숫자 코드.
        name (str): 기업명.
        사업가치 (float): 지배주주 당기순이익 / 기대수익률로 계산된 사업가치.
        지배주주당기순이익 (float): 지배주주에게 귀속된 당기순이익.
        expect_earn (float): 기대수익률.
        재산가치 (float): 유동자산 - (유동부채 * 1.2) + 고정자산(투자자산, 투자부동산)으로 계산된 재산가치.
        유동자산 (float): 기업의 유동자산.
        유동부채 (float): 기업의 유동부채.
        투자자산 (float): 투자자산.
        투자부동산 (float): 투자부동산.
        부채평가 (float): 비유동부채를 평가한 값.
        발행주식수 (int): 발행된 주식 수.
        date (list): 재무 데이터와 관련된 날짜 목록.
        주가 (float): 최근 주가.
        red_price (float): 계산된 레드 가격.
        score (int): 최근 주가와 레드 가격 간 괴리율로 산출된 점수.

    예외:
        ValueError: 'code'가 6자리 숫자 문자열이 아닌 경우 발생.
    """
    code: str
    name: str

    # 사업가치 계산 - 지배주주지분 당기순이익 / 기대수익률
    사업가치: float
    지배주주당기순이익: float
    expect_earn: float

    # 재산가치 계산 - 유동자산 - (유동부채*1.2) + 고정자산중 투자자산
    재산가치: float
    유동자산: float
    유동부채: float
    투자자산: float
    투자부동산: float

    # 부채평가 - 비유동부채
    부채평가: float

    # 발행주식수
    발행주식수: int

    date: list
    주가: float
    red_price: float
    score: int

    def __post_init__(self):
        if not tools.is_6digit(self.code):
            raise ValueError(f"code는 6자리 숫자형 문자열이어야합니다. (입력값: {self.code})")


class Red:
    """
    특정 기업의 재무 데이터를 계산하고 분석하기 위한 클래스.

    이 클래스는 주어진 종목 코드에 대해 데이터를 가져오고, 사업가치, 재산가치, 부채평가 등 다양한
    재무 지표를 계산하며, Redis 캐시를 활용하여 데이터 저장 및 재사용을 관리합니다.

    속성:
        c101 (myredis.C101): 기업 정보 및 데이터 접근을 위한 객체.
        c103 (myredis.C103): 재무 상태표 데이터 접근을 위한 객체.
        name (str): 기업명.
        recent_price (float): 최근 주가.
        expect_earn (float): 기대수익률. 기본값은 0.06 (6%).
    """
    REDIS_RED_DATA_SUFFIX = "red_data"

    def __init__(self, code: str, expect_earn: float = 0.06):
        assert tools.is_6digit(code), f'Invalid value : {code}'
        mylogger.debug(f"Red : 초기화 ({code})")
        self.c101 = myredis.C101(code)
        self.c103 = myredis.C103(code, 'c103재무상태표q')

        self.name = self.c101.get_name()
        self.recent_price = tools.to_float(self.c101.get_recent()['주가'])
        self._code = code

        self.expect_earn = expect_earn

    def __str__(self):
        return f"Red({self.code}/{self.name})"

    @property
    def code(self) -> str:
        return self._code

    @code.setter
    def code(self, code: str):
        assert tools.is_6digit(code), f'Invalid value : {code}'
        mylogger.debug(f"Red : 종목코드 변경({self.code} -> {code})")
        self.c101.code = code
        self.c103.code = code

        self.name = self.c101.get_name()
        self.recent_price = tools.to_float(self.c101.get_recent()['주가'])
        self._code = code

    def _calc비유동부채(self, refresh: bool) -> Tuple[str, float]:
        """
        비유동부채를 계산합니다.

        기본적으로 재무 상태표에서 비유동부채 데이터를 가져오며, 만약 데이터가 누락되었거나 NaN인 경우
        직접 계산하여 반환합니다.

        매개변수:
            refresh (bool): 데이터 새로고침 여부. True일 경우 최신 데이터를 가져옵니다.

        반환값:
            Tuple[str, float]: 가장 최근 날짜와 계산된 비유동부채 값.

        예외:
            ValueError: 필요한 데이터가 누락된 경우 발생.

        로그:
            - 비유동부채 데이터가 없을 경우 경고 메시지를 출력합니다.
        """
        mylogger.debug(f'In the calc비유동부채... refresh : {refresh}')
        self.c103.page = 'c103재무상태표q'

        d, 비유동부채 = self.c103.sum_recent_4q('비유동부채', refresh)
        if math.isnan(비유동부채):
            mylogger.warning(f"{self} - 비유동부채가 없는 종목. 수동으로 계산합니다.")
            # 보험관련업종은 예수부채가 없는대신 보험계약부채가 있다...
            d1, v1 = self.c103.latest_value_pop2('예수부채', refresh)
            d2, v2 = self.c103.latest_value_pop2('보험계약부채(책임준비금)', refresh)
            d3, v3 = self.c103.latest_value_pop2('차입부채', refresh)
            d4, v4 = self.c103.latest_value_pop2('기타부채', refresh)
            mylogger.debug(f'예수부채 : {d1}, {v1}')
            mylogger.debug(f'보험계약부채(책임준비금) : {d2}, {v2}')
            mylogger.debug(f'차입부채 : {d3}, {v3}')
            mylogger.debug(f'기타부채 : {d4}, {v4}')

            try:
                date, *_ = Tools.date_set(d1, d2, d3, d4)
            except ValueError:
                # 날짜 데이터가 없는경우
                date = ''
            계산된비유동부채value = round(tools.nan_to_zero(v1) + tools.nan_to_zero(v2) + tools.nan_to_zero(v3) + tools.nan_to_zero(v4),1)
            mylogger.debug(f"{self} - 계산된 비유동부채 : {계산된비유동부채value}")
            return date, 계산된비유동부채value
        else:
            return d, 비유동부채

    def _score(self, red_price: int) -> int:
        """
        최근 주가와 레드 가격 간 괴리율을 계산하여 점수를 반환합니다.

        매개변수:
            red_price (int): 계산된 레드 가격.

        반환값:
            int: 괴리율 기반 점수. 양수는 저평가, 음수는 과대평가를 나타냅니다.

        로그:
            - 최근 주가와 레드 가격, 괴리율, 계산된 점수를 출력합니다.
        """
        if math.isnan(self.recent_price):
            return 0

        deviation = Tools.cal_deviation(self.recent_price, red_price)

        score = tools.to_int(Tools.sigmoid_score(deviation))
        #score = tools.to_int(Tools.log_score(deviation))
        if self.recent_price >= red_price:
            score = -score

        mylogger.debug(f"최근주가 : {self.recent_price} red가격 : {red_price} 괴리율 : {tools.to_int(deviation)} score : {score}")

        return score

    def _generate_data(self, refresh: bool) -> RedData:
        """
        RedData 객체를 생성하기 위해 재무 데이터를 계산합니다.

        내부적으로 사업가치, 재산가치, 비유동부채 등을 계산하며, 계산된 결과를 RedData 객체로 반환합니다.

        매개변수:
            refresh (bool): 데이터 새로고침 여부. True일 경우 최신 데이터를 가져옵니다.

        반환값:
            RedData: 계산된 재무 데이터를 포함하는 RedData 객체.

        예외:
            ZeroDivisionError: 발행 주식 수가 0인 경우 발생.
            ValueError: 필요한 날짜 데이터가 없는 경우 발생.

        로그:
            - 각 단계의 계산 결과와 주요 값을 출력합니다.
        """
        d1, 지배주주당기순이익 = Tools.calc당기순이익(self.c103, refresh)
        mylogger.debug(f"{self} 지배주주당기순이익: {지배주주당기순이익}")
        d2, 유동자산 = Tools.calc유동자산(self.c103, refresh)
        d3, 유동부채 = Tools.calc유동부채(self.c103, refresh)
        d4, 부채평가 = self._calc비유동부채(refresh)

        self.c103.page = 'c103재무상태표q'
        d5, 투자자산 = self.c103.latest_value_pop2('투자자산', refresh)
        d6, 투자부동산 = self.c103.latest_value_pop2('투자부동산', refresh)

        # 사업가치 계산 - 지배주주지분 당기순이익 / 기대수익률
        사업가치 = round(지배주주당기순이익 / self.expect_earn, 2)

        # 재산가치 계산 - 유동자산 - (유동부채*1.2) + 고정자산중 투자자산
        재산가치 = round(유동자산 - (유동부채 * 1.2) + tools.nan_to_zero(투자자산) + tools.nan_to_zero(투자부동산), 2)

        _, 발행주식수 = self.c103.latest_value_pop2('발행주식수', refresh)
        if math.isnan(발행주식수):
            발행주식수 = tools.to_int(self.c101.get_recent(refresh).get('발행주식'))
        else:
            발행주식수 = 발행주식수 * 1000

        try:
            red_price = round(((사업가치 + 재산가치 - 부채평가) * 100000000) / 발행주식수)
        except (ZeroDivisionError, ValueError):
            red_price = math.nan

        score = self._score(red_price)

        try:
            date_list = Tools.date_set(d1, d2, d3, d4)
        except ValueError:
            # 날짜 데이터가 없는경우
            date_list = ['',]

        return RedData(
            code = self.code,
            name = self.name,
            사업가치 = 사업가치,
            지배주주당기순이익 = 지배주주당기순이익,
            expect_earn = self.expect_earn,
            재산가치 = 재산가치,
            유동자산 = 유동자산,
            유동부채 = 유동부채,
            투자자산 = 투자자산,
            투자부동산 = 투자부동산,
            부채평가 = 부채평가,
            발행주식수 = 발행주식수,
            date = date_list,
            red_price = red_price,
            주가 = self.recent_price,
            score = score,
        )

    def get(self, refresh = False) -> RedData:
        mylogger.debug(f"*** Get red data ***")
        redis_name = f"{self.code}_{self.REDIS_RED_DATA_SUFFIX}_{self.expect_earn}"
        mylogger.debug(f"{self} redisname: '{redis_name}' / refresh : {refresh}")

        def fetch_generate_data(refresh_in: bool) -> RedData:
            return self._generate_data(refresh_in) # type: ignore

        return myredis.Base.fetch_and_cache_data(redis_name, refresh, fetch_generate_data, refresh)

    @classmethod
    def bulk_get_data(cls, codes: List[str], expect_earn: float, refresh: bool) -> Dict[str, RedData]:
        return myredis.Corps.bulk_get_or_compute(
            [f"{code}_{cls.REDIS_RED_DATA_SUFFIX}_{expect_earn}" for code in codes],
            lambda key: cls(key[:6], expect_earn)._generate_data(refresh=True),
            refresh=refresh
        )


    @staticmethod
    def ranking(expect_earn: float = 0.06, refresh=False) -> OrderedDict:
        mylogger.info("**** Start red ranking ... ****")

        data = Red.bulk_get_data(myredis.Corps.list_all_codes(), expect_earn, refresh)
        mylogger.debug(data)
        return  OrderedDict(sorted(data.items(), key=lambda x: x[1].score, reverse=True))


