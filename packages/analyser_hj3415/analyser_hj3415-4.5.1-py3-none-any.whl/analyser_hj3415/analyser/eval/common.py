import math
from typing import Tuple

from db_hj3415 import myredis
from utils_hj3415.tools import nan_to_zero
from utils_hj3415 import setup_logger

mylogger = setup_logger(__name__,'WARNING')


class Tools:
    """
    재무 데이터 분석 및 계산에 필요한 유틸리티 메서드를 제공하는 클래스.

    이 클래스는 주어진 재무 데이터를 기반으로 다양한 계산을 수행하며,
    로그를 통해 계산 과정 및 결과를 디버깅할 수 있도록 지원합니다.

    주요 기능:
        - Sigmoid 및 로그 점수 계산.
        - 두 값 간의 괴리율(Deviation) 계산.
        - 유효하지 않은 값(NaN, None 등) 필터링.
        - 당기순이익, 유동자산, 유동부채 계산 등.
    """
    @staticmethod
    def sigmoid_score(deviation, a=1.0, b=2.0):
        """"
        주어진 괴리율(Deviation)에 대해 Sigmoid 함수를 적용하여 점수를 계산합니다.

        이 함수는 Sigmoid 함수에 로그 변환된 괴리율을 입력으로 사용하며,
        결과를 0에서 100 사이의 점수로 변환합니다. `a`와 `b` 매개변수를 사용하여
        Sigmoid 곡선의 기울기와 x-축 오프셋을 조정할 수 있습니다.

        매개변수:
            deviation (float): 계산할 괴리율 값 (0 이상의 값이어야 함).
            a (float): Sigmoid 곡선의 기울기 조정값. 기본값은 1.0.
            b (float): Sigmoid 곡선의 x-축 오프셋. 기본값은 2.0.

        반환값:
            float: Sigmoid 함수로 변환된 0~100 사이의 점수.
        """
        # 예: x = log10(deviation + 1)
        x = math.log10(deviation + 1)
        s = 1 / (1 + math.exp(-a * (x - b)))  # 0~1 범위
        return s * 100  # 0~100 범위

    @staticmethod
    def log_score(deviation):
        """
        주어진 괴리율(Deviation)에 대해 로그 점수를 계산합니다.

        괴리율 값에 1을 더한 뒤, 로그 변환(Base-10)을 수행하고
        결과를 상수(33)로 곱하여 점수를 계산합니다.

        매개변수:
            deviation (float): 계산할 괴리율 값.

        반환값:
            float: 계산된 로그 점수.
        """
        return math.log10(deviation + 1) * 33

    @staticmethod
    def cal_deviation(v1: float, v2: float) -> float:
        """
        두 값 간의 퍼센트 괴리율(Deviation)을 계산합니다.

        주어진 두 값 간의 상대적 차이를 백분율로 반환합니다.
        기준값(v1)이 0인 경우, 계산은 NaN을 반환합니다.

        매개변수:
            v1 (float): 기준값.
            v2 (float): 비교할 값.

        반환값:
            float: 두 값 간의 퍼센트 괴리율. 기준값이 0인 경우 NaN.
        """
        try:
            deviation = abs((v1 - v2) / v1) * 100
        except ZeroDivisionError:
            deviation = math.nan
        return deviation

    @staticmethod
    def date_set(*args) -> list:
        """
        주어진 값들에서 유효하지 않은 값을 제거하고 중복 없이 리스트로 반환합니다.

        NaN, None, 빈 문자열 등 유효하지 않은 값을 필터링한 뒤,
        고유한 값만 포함하는 리스트를 생성합니다.

        매개변수:
            *args: 필터링할 값들.

        반환값:
            list: 유효한 값만 포함하는 고유 리스트.
        """
        return [i for i in {*args} if i != "" and i is not math.nan and i is not None]

    @staticmethod
    def calc당기순이익(c103: myredis.C103, refresh: bool) -> Tuple[str, float]:
        """
        지배주주지분 당기순이익을 계산하여 반환합니다.

        기본적으로 재무 데이터에서 지배주주지분 당기순이익을 검색하며,
        데이터가 없거나 유효하지 않은 경우 간접적으로 계산합니다.

        매개변수:
            c103 (myredis.C103): 재무 데이터에 접근하기 위한 객체.
            refresh (bool): 데이터를 새로고침할지 여부.

        반환값:
            Tuple[str, float]: 날짜와 계산된 지배주주지분 당기순이익.
        """
        name = myredis.Corps(c103.code, 'c101').get_name(refresh=refresh)

        mylogger.info(f'{c103.code} / {name} Tools : 당기순이익 계산.. refresh : {refresh}')
        c103.page = 'c103재무상태표q'

        d1, 지배당기순이익 = c103.latest_value_pop2('*(지배)당기순이익', refresh)
        mylogger.debug(f"*(지배)당기순이익: {지배당기순이익}")

        if math.isnan(지배당기순이익):
            mylogger.warning(f"{c103.code} / {name} - (지배)당기순이익이 없는 종목. 수동으로 계산합니다.")
            c103.page = 'c103손익계산서q'
            d2, 최근4분기당기순이익 = c103.sum_recent_4q('당기순이익', refresh)
            mylogger.debug(f"{c103.code} / {name} - 최근4분기당기순이익 : {최근4분기당기순이익}")
            c103.page = 'c103재무상태표y'
            d3, 비지배당기순이익 = c103.latest_value_pop2('*(비지배)당기순이익', refresh)
            mylogger.debug(f"{c103.code} / {name} - 비지배당기순이익y : {비지배당기순이익}")
            # 가변리스트 언패킹으로 하나의 날짜만 사용하고 나머지는 버린다.
            # 여기서 *_는 “나머지 값을 다 무시하겠다”는 의미
            mylogger.debug(f"d2:{d2}, d3: {d3}")
            try:
                date, *_ = Tools.date_set(d2, d3)
            except ValueError:
                # 날짜 데이터가 없는경우
                date = ''
            계산된지배당기순이익 = round(최근4분기당기순이익 - nan_to_zero(비지배당기순이익), 1)
            mylogger.debug(f"{c103.code} / {name} - 계산된 지배당기순이익 : {계산된지배당기순이익}")
            return date, 계산된지배당기순이익
        else:
            return d1, 지배당기순이익

    @staticmethod
    def calc유동자산(c103: myredis.C103, refresh: bool) -> Tuple[str, float]:
        """
        기업의 유동자산을 계산하여 반환합니다.

        최근 4분기의 데이터를 기반으로 유동자산을 계산하며,
        데이터가 없거나 유효하지 않을 경우 간접적으로 계산합니다.

        매개변수:
            c103 (myredis.C103): 재무 데이터에 접근하기 위한 객체.
            refresh (bool): 데이터를 새로고침할지 여부.

        반환값:
            Tuple[str, float]: 날짜와 계산된 유동자산.
        """

        name = myredis.Corps(c103.code, 'c101').get_name(refresh=refresh)

        mylogger.info(f'{c103.code} / {name} Tools : 유동자산계산... refresh : {refresh}')
        c103.page = 'c103재무상태표q'

        d, 유동자산 = c103.sum_recent_4q('유동자산', refresh)
        if math.isnan(유동자산):
            mylogger.warning(f"{c103.code} / {name} - 유동자산이 없는 종목. 수동으로 계산합니다(금융관련업종일 가능성있음).")
            d1, v1 = c103.latest_value_pop2('현금및예치금', refresh)
            d2, v2 = c103.latest_value_pop2('단기매매금융자산', refresh)
            d3, v3 = c103.latest_value_pop2('매도가능금융자산', refresh)
            d4, v4 = c103.latest_value_pop2('만기보유금융자산', refresh)
            mylogger.debug(f'{c103.code} / {name} 현금및예치금 : {d1}, {v1}')
            mylogger.debug(f'{c103.code} / {name} 단기매매금융자산 : {d2}, {v2}')
            mylogger.debug(f'{c103.code} / {name} 매도가능금융자산 : {d3}, {v3}')
            mylogger.debug(f'{c103.code} / {name} 만기보유금융자산 : {d4}, {v4}')

            try:
                date, *_ = Tools.date_set(d1, d2, d3, d4)
            except ValueError:
                # 날짜 데이터가 없는경우
                date = ''
            계산된유동자산value = round(
                nan_to_zero(v1) + nan_to_zero(v2) + nan_to_zero(v3) + nan_to_zero(v4), 1)

            mylogger.info(f"{c103.code} / {name} - 계산된 유동자산 : {계산된유동자산value}")
            return date, 계산된유동자산value
        else:
            return d, 유동자산

    @staticmethod
    def calc유동부채(c103: myredis.C103, refresh: bool) -> Tuple[str, float]:
        """
        기업의 유동부채를 계산하여 반환합니다.

        최근 4분기의 데이터를 기반으로 유동부채를 계산하며,
        데이터가 없거나 유효하지 않을 경우 간접적으로 계산합니다.

        매개변수:
            c103 (myredis.C103): 재무 데이터에 접근하기 위한 객체.
            refresh (bool): 데이터를 새로고침할지 여부.

        반환값:
            Tuple[str, float]: 날짜와 계산된 유동부채.
        """

        name = myredis.Corps(c103.code, 'c101').get_name(refresh=refresh)

        mylogger.info(f'{c103.code} / {name} Tools : 유동부채계산... refresh : {refresh}')
        c103.page = 'c103재무상태표q'

        d, 유동부채 = c103.sum_recent_4q('유동부채', refresh)
        if math.isnan(유동부채):
            mylogger.warning(f"{c103.code} / {name} - 유동부채가 없는 종목. 수동으로 계산합니다.")
            d1, v1 = c103.latest_value_pop2('당기손익인식(지정)금융부채', refresh)
            d2, v2 = c103.latest_value_pop2('당기손익-공정가치측정금융부채', refresh)
            d3, v3 = c103.latest_value_pop2('매도파생결합증권', refresh)
            d4, v4 = c103.latest_value_pop2('단기매매금융부채', refresh)
            mylogger.debug(f'{c103.code} / {name} 당기손익인식(지정)금융부채 : {d1}, {v1}')
            mylogger.debug(f'{c103.code} / {name} 당기손익-공정가치측정금융부채 : {d2}, {v2}')
            mylogger.debug(f'{c103.code} / {name} 매도파생결합증권 : {d3}, {v3}')
            mylogger.debug(f'{c103.code} / {name} 단기매매금융부채 : {d4}, {v4}')

            try:
                date, *_ = Tools.date_set(d1, d2, d3, d4)
            except ValueError:
                # 날짜 데이터가 없는경우
                date = ''
            계산된유동부채value = round(
                nan_to_zero(v1) + nan_to_zero(v2) + nan_to_zero(v3) + nan_to_zero(v4), 1)

            mylogger.info(f"{c103.code} / {name} - 계산된 유동부채 : {계산된유동부채value}")
            return date, 계산된유동부채value
        else:
            return d, 유동부채


"""
- 각분기의 합이 연이 아닌 타이틀(즉 sum_4q를 사용하면 안됨)
'*(지배)당기순이익'
'*(비지배)당기순이익'
'장기차입금'
'현금및예치금'
'매도가능금융자산'
'매도파생결합증권'
'만기보유금융자산'
'당기손익-공정가치측정금융부채'
'당기손익인식(지정)금융부채'
'단기매매금융자산'
'단기매매금융부채'
'예수부채'
'차입부채'
'기타부채'
'보험계약부채(책임준비금)'
'*CAPEX'
'ROE'
"""

"""
- sum_4q를 사용해도 되는 타이틀
'자산총계'
'당기순이익'
'유동자산'
'유동부채'
'비유동부채'

'영업활동으로인한현금흐름'
'재무활동으로인한현금흐름'
'ROIC'
"""
