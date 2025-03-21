from dataclasses import dataclass
from typing import Tuple
import math

from utils_hj3415 import tools, setup_logger
from db_hj3415 import myredis

from analyser_hj3415.analyser.eval.common import Tools


mylogger = setup_logger(__name__,'WARNING')

@dataclass()
class BlueData:
    """
    기업의 주요 안정성 지표와 관련된 데이터를 저장하는 데이터 클래스.

    이 클래스는 기업의 유동성, 부채 비율, 자산 회전율 등을 포함하며,
    이를 활용하여 기업의 안정성을 평가할 수 있습니다.

    속성:
        code (str): 기업의 종목 코드 (6자리 숫자 문자열).
        name (str): 기업명.
        유동비율 (float): 유동 자산 대비 유동 부채 비율.
        이자보상배율_r (float): 최근 이자보상배율 값.
        이자보상배율_dict (dict): 이자보상배율 데이터.
        순운전자본회전율_r (float): 최근 순운전자본회전율 값.
        순운전자본회전율_dict (dict): 순운전자본회전율 데이터.
        재고자산회전율_r (float): 최근 재고자산회전율 값.
        재고자산회전율_dict (dict): 재고자산회전율 데이터.
        재고자산회전율_c106 (dict): C106 기준 재고자산회전율 데이터.
        순부채비율_r (float): 최근 순부채비율 값.
        순부채비율_dict (dict): 순부채비율 데이터.
        score (list): 평가 점수.
        date (list): 데이터와 관련된 날짜 목록.
    """
    code: str
    name: str

    유동비율: float

    이자보상배율_r: float
    이자보상배율_dict: dict

    순운전자본회전율_r: float
    순운전자본회전율_dict: dict

    재고자산회전율_r: float
    재고자산회전율_dict: dict
    재고자산회전율_c106: dict

    순부채비율_r: float
    순부채비율_dict: dict

    score: list
    date: list


class Blue:
    """
    기업의 안정성 지표를 분석하고 계산하는 클래스.

    이 클래스는 주어진 기업 코드에 대해 주요 안정성 지표(예: 유동비율, 이자보상배율 등)를 수집하고,
    이를 기반으로 기업의 안정성을 평가합니다. Redis 캐시를 활용하여 계산된 데이터를 저장하고
    재사용할 수 있습니다.

    속성:
        c101 (myredis.C101): 기업 정보 및 최근 데이터 접근 객체.
        c103 (myredis.C103): 재무 상태표 데이터 접근 객체.
        c104 (myredis.C104): 투자 지표 데이터 접근 객체.
        name (str): 기업명.
        _code (str): 기업 종목 코드.
    """
    def __init__(self, code: str):
        assert tools.is_6digit(code), f'Invalid value : {code}'
        mylogger.debug(f"Blue : 종목코드 ({code})")

        self.c101 = myredis.C101(code)
        self.c103 = myredis.C103(code, 'c103재무상태표q')
        self.c104 = myredis.C104(code, 'c104q')

        self.name = self.c101.get_name()
        self._code = code

    def __str__(self):
        return f"Blue({self.code}/{self.name})"

    @property
    def code(self) -> str:
        return self._code

    @code.setter
    def code(self, code: str):
        assert tools.is_6digit(code), f'Invalid value : {code}'
        mylogger.debug(f"Blue : 종목코드 변경({self.code} -> {code})")

        self.c101.code = code
        self.c103.code = code
        self.c104.code = code

        self.name = self.c101.get_name()
        self._code = code

    def _calc유동비율(self, pop_count: int, refresh: bool) -> Tuple[str, float]:
        """
        기업의 유동비율을 계산합니다.

        유동비율 데이터가 유효하지 않거나 100 이하일 경우,
        유동자산과 유동부채를 기반으로 계산을 수행합니다.

        매개변수:
            pop_count (int): 데이터 검색 시 사용할 값의 개수.
            refresh (bool): 데이터를 새로고침할지 여부.

        반환값:
            Tuple[str, float]: 날짜와 계산된 유동비율.

        로그:
            - 유동비율 계산 과정과 결과를 출력합니다.
            - 계산 중 유효하지 않은 데이터가 있으면 경고를 출력합니다.
        """
        mylogger.info(f'In the calc유동비율... refresh : {refresh}')
        self.c104.page = 'c104q'

        유동비율date, 유동비율value = self.c104.latest_value('유동비율', pop_count=pop_count)
        mylogger.info(f'{self} 유동비율 : {유동비율value}/({유동비율date})')

        if math.isnan(유동비율value) or 유동비율value < 100:
            유동자산date, 유동자산value = Tools.calc유동자산(self.c103, refresh)
            유동부채date, 유동부채value = Tools.calc유동부채(self.c103, refresh)

            self.c103.page = 'c103현금흐름표q'
            추정영업현금흐름date, 추정영업현금흐름value = self.c103.sum_recent_4q('영업활동으로인한현금흐름', refresh)
            mylogger.debug(f'{self} 계산전 유동비율 : {유동비율value} / ({유동비율date})')

            계산된유동비율 = 0
            try:
                계산된유동비율 = round(((유동자산value + 추정영업현금흐름value) / 유동부채value) * 100, 2)
            except ZeroDivisionError:
                mylogger.info(f'유동자산: {유동자산value} + 추정영업현금흐름: {추정영업현금흐름value} / 유동부채: {유동부채value}')
                계산된유동비율 = float('inf')
            finally:
                mylogger.debug(f'{self} 계산된 유동비율 : {계산된유동비율}')

                try:
                    date, *_ = Tools.date_set(유동자산date, 유동부채date, 추정영업현금흐름date)
                except ValueError:
                    # 날짜 데이터가 없는경우
                    date = ''
                mylogger.warning(f'{self} 유동비율 이상(100 이하 또는 nan) : {유동비율value} -> 재계산 : {계산된유동비율}')
                return date, 계산된유동비율
        else:
            return 유동비율date, 유동비율value

    def _score(self) -> list:
        return [0 ,]

    def _generate_data(self, refresh: bool) -> BlueData:
        """
        BlueData 형식의 데이터를 생성합니다.

        각종 안정성 지표를 계산하고 데이터를 정리하여 BlueData 객체로 반환합니다.

        매개변수:
            refresh (bool): 데이터를 새로고침할지 여부.

        반환값:
            BlueData: 계산된 안정성 지표 데이터.
        """
        d1, 유동비율 = self._calc유동비율(pop_count=3, refresh=refresh)
        mylogger.info(f'유동비율 {유동비율} / [{d1}]')

        재고자산회전율_c106 = myredis.C106.make_like_c106(self.code, 'c104q', '재고자산회전율', refresh)

        self.c104.page = 'c104y'
        _, 이자보상배율_dict = self.c104.find('이자보상배율', remove_yoy=True, refresh=refresh)
        _, 순운전자본회전율_dict = self.c104.find('순운전자본회전율', remove_yoy=True, refresh=refresh)
        _, 재고자산회전율_dict = self.c104.find('재고자산회전율', remove_yoy=True, refresh=refresh)
        _, 순부채비율_dict = self.c104.find('순부채비율', remove_yoy=True, refresh=refresh)

        self.c104.page = 'c104q'
        d6, 이자보상배율_r = self.c104.latest_value_pop2('이자보상배율', refresh)
        d7, 순운전자본회전율_r = self.c104.latest_value_pop2('순운전자본회전율', refresh)
        d8, 재고자산회전율_r = self.c104.latest_value_pop2('재고자산회전율', refresh)
        d9, 순부채비율_r = self.c104.latest_value_pop2('순부채비율', refresh)

        if len(이자보상배율_dict) == 0:
            mylogger.warning(f'empty dict - 이자보상배율 : {이자보상배율_r} / {이자보상배율_dict}')

        if len(순운전자본회전율_dict) == 0:
            mylogger.warning(f'empty dict - 순운전자본회전율 : {순운전자본회전율_r} / {순운전자본회전율_dict}')

        if len(재고자산회전율_dict) == 0:
            mylogger.warning(f'empty dict - 재고자산회전율 : {재고자산회전율_r} / {재고자산회전율_dict}')

        if len(순부채비율_dict) == 0:
            mylogger.warning(f'empty dict - 순부채비율 : {순부채비율_r} / {순부채비율_dict}')

        score = self._score()

        try:
            date_list = Tools.date_set(d1, d6, d7, d8, d9)
        except ValueError:
            # 날짜 데이터가 없는경우
            date_list = ['' ,]

        return BlueData(
            code= self.code,
            name= self.name,
            유동비율= 유동비율,
            이자보상배율_r= 이자보상배율_r,
            이자보상배율_dict= 이자보상배율_dict,

            순운전자본회전율_r= 순운전자본회전율_r,
            순운전자본회전율_dict= 순운전자본회전율_dict,

            재고자산회전율_r= 재고자산회전율_r,
            재고자산회전율_dict= 재고자산회전율_dict,
            재고자산회전율_c106= 재고자산회전율_c106,

            순부채비율_r= 순부채비율_r,
            순부채비율_dict= 순부채비율_dict,

            score= score,
            date= date_list,
        )

    def get(self, refresh = False) -> BlueData:
        """
        BlueData 객체를 Redis 캐시에서 가져오거나 새로 생성하여 반환합니다.

        캐시에서 데이터를 검색하고, 없을 경우 `_generate_data`를 호출하여 데이터를 생성합니다.
        생성된 데이터는 Redis 캐시에 저장되어 재사용됩니다.

        매개변수:
            refresh (bool): 캐시를 무시하고 새로 데이터를 계산할지 여부. 기본값은 False.
            verbose (bool): 실행 중 상세 정보를 출력할지 여부. 기본값은 True.

        반환값:
            BlueData: Redis 캐시에서 가져오거나 새로 생성된 BlueData 객체.

        로그:
            - 캐시 검색 상태와 새로 생성된 데이터를 출력합니다.
        """
        redis_name = f"{self.code}_blue"
        mylogger.debug(f"{self} redisname: '{redis_name}' / refresh : {refresh}")

        def fetch_generate_data(refresh_in: bool) -> dict:
            return self._generate_data(refresh_in) # type: ignore

        return myredis.Base.fetch_and_cache_data(redis_name, refresh, fetch_generate_data, refresh)
