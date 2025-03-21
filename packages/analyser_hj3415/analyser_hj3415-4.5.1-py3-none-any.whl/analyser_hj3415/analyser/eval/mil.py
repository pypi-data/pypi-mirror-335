from dataclasses import dataclass
from typing import Tuple, List, Dict
import math

from utils_hj3415 import tools, setup_logger
from db_hj3415 import myredis, mymongo

from analyser_hj3415.analyser.eval.common import Tools

mylogger = setup_logger(__name__,'WARNING')

@dataclass
class MilData:
    """
    기업의 주요 재무 데이터를 나타내는 데이터 클래스.

    이 클래스는 기업의 다양한 재무 데이터를 포함하며,
    이를 통해 투자 수익률, 가치 지표, 현금 흐름 등을 분석할 수 있습니다.

    속성:
        code (str): 기업의 종목 코드 (6자리 숫자 문자열).
        name (str): 기업명.
        시가총액억 (float): 기업의 시가총액 (억 단위).
        주주수익률 (float): 재무활동 현금흐름을 기반으로 계산된 주주 수익률.
        재무활동현금흐름 (float): 재무활동으로 인한 현금흐름.
        이익지표 (float): 기업의 이익지표.
        영업활동현금흐름 (float): 영업활동으로 인한 현금흐름.
        지배주주당기순이익 (float): 지배주주에게 귀속된 당기순이익.
        roic_r (float): ROIC(투하자본이익률).
        roic_dict (dict): ROIC와 관련된 데이터.
        roe_r (float): ROE(자기자본이익률).
        roe_106 (dict): ROE와 관련된 상세 데이터.
        roa_r (float): ROA(총자산이익률).
        fcf_dict (dict): FCF(자유 현금 흐름) 관련 데이터.
        pfcf_dict (dict): PFCF(주가 대비 자유 현금 흐름 비율) 관련 데이터.
        pcr_dict (dict): PCR(주가 대비 현금 흐름 비율) 관련 데이터.
        score (list): 계산된 평가 점수.
        date (list): 재무 데이터와 관련된 날짜 목록.
    """
    code: str
    name: str

    시가총액억: float

    주주수익률: float
    재무활동현금흐름: float

    이익지표: float
    영업활동현금흐름: float
    지배주주당기순이익: float

    #투자수익률
    roic_r: float
    roic_dict: dict
    roe_r: float
    roe_106: dict
    roa_r: float

    #가치지표
    fcf_dict: dict
    pfcf_dict: dict
    pcr_dict: dict

    score: list
    date: list


class Mil:
    """
    기업의 재무 데이터를 분석하고 계산하는 클래스.

    이 클래스는 주어진 종목 코드에 대해 다양한 재무 데이터를 수집하고,
    이를 기반으로 주요 재무 지표(예: ROIC, ROE, 이익지표 등)를 계산합니다.
    또한 Redis 캐시를 활용하여 계산된 데이터를 저장하고 재사용할 수 있습니다.

    속성:
        c101 (myredis.C101): 기업 정보 및 최근 데이터 접근 객체.
        c103 (myredis.C103): 재무 상태표 데이터 접근 객체.
        c104 (myredis.C104): 투자 지표 데이터 접근 객체.
        c106 (myredis.C106): ROE 관련 데이터 접근 객체.
        name (str): 기업명.
        _code (str): 기업 종목 코드.
    """

    REDIS_MIL_DATA_SUFFIX = "mil_data"

    def __init__(self, code: str):
        assert tools.is_6digit(code), f'Invalid value : {code}'
        mylogger.debug(f"Mil : 종목코드 ({code})")

        self.c101 = myredis.C101(code)
        self.c103 = myredis.C103(code, 'c103현금흐름표q')
        self.c104 = myredis.C104(code, 'c104q')
        self.c106 = myredis.C106(code, 'c106q')

        self.name = self.c101.get_name()
        self._code = code

    def __str__(self):
        return f"Mil({self.code}/{self.name})"

    @property
    def code(self) -> str:
        return self._code

    @code.setter
    def code(self, code: str):
        assert tools.is_6digit(code), f'Invalid value : {code}'
        mylogger.debug(f"Mil : 종목코드 변경({self.code} -> {code})")

        self.c101.code = code
        self.c103.code = code
        self.c104.code = code
        self.c106.code = code

        self.name = self.c101.get_name()
        self._code = code

    def get_marketcap억(self, refresh: bool) -> float:
        """
        기업의 시가총액(억 단위)을 반환합니다.

        매개변수:
            refresh (bool): 데이터를 새로고침할지 여부.

        반환값:
            float: 기업의 시가총액 (억 단위).

        로그:
            - 계산된 시가총액 정보를 출력합니다.
        """
        c101r = self.c101.get_recent(refresh)
        시가총액 = tools.to_int(tools.to_float(c101r.get('시가총액', math.nan)) / 100000000)
        mylogger.debug(f"시가총액: {시가총액}억원")
        return 시가총액

    def _calc주주수익률(self, 시가총액_억: float, refresh: bool) -> Tuple[str, float, float]:
        """
        주주수익률을 계산합니다.

        매개변수:
            시가총액_억 (float): 기업의 시가총액 (억 단위).
            refresh (bool): 데이터를 새로고침할지 여부.

        반환값:
            Tuple[str, float, float]: 최근 날짜, 주주수익률, 재무활동 현금흐름.

        예외:
            ZeroDivisionError: 시가총액이 0일 경우 주주수익률을 계산하지 못합니다.
        """
        self.c103.page = 'c103현금흐름표q'
        d, 재무활동현금흐름 = self.c103.sum_recent_4q('재무활동으로인한현금흐름', refresh)
        try:
            주주수익률 = round((재무활동현금흐름 / 시가총액_억 * -100), 2)
        except ZeroDivisionError:
            주주수익률 = math.nan
            mylogger.warning(f'{self} 주주수익률: {주주수익률} 재무활동현금흐름: {재무활동현금흐름}')
        return d, 주주수익률, 재무활동현금흐름

    def _calc이익지표(self, 시가총액_억: float, refresh: bool) -> Tuple[str, float, float, float]:
        """
        이익지표를 계산합니다.

        매개변수:
            시가총액_억 (float): 기업의 시가총액 (억 단위).
            refresh (bool): 데이터를 새로고침할지 여부.

        반환값:
            Tuple[str, float, float, float]: 최근 날짜, 이익지표, 영업활동 현금흐름, 지배주주 당기순이익.

        예외:
            ZeroDivisionError: 시가총액이 0일 경우 이익지표를 계산하지 못합니다.
        """
        d1, 지배주주당기순이익 = Tools.calc당기순이익(self.c103, refresh)
        self.c103.page = 'c103현금흐름표q'
        d2, 영업활동현금흐름 = self.c103.sum_recent_4q('영업활동으로인한현금흐름', refresh)
        try:
            이익지표 = round(((지배주주당기순이익 - 영업활동현금흐름) / 시가총액_억) * 100, 2)
        except ZeroDivisionError:
            이익지표 = math.nan
            mylogger.warning(f'{self} 이익지표: {이익지표} 영업활동현금흐름: {영업활동현금흐름} 지배주주당기순이익: {지배주주당기순이익}')
        try:
            date, *_ = Tools.date_set(d1, d2)
        except ValueError:
            # 날짜 데이터가 없는경우
            date = ''
        return date , 이익지표, 영업활동현금흐름, 지배주주당기순이익

    def _calc투자수익률(self, refresh: bool) -> tuple:
        """
        ROIC, ROE, ROA 등의 투자 수익률을 계산합니다.

        매개변수:
            refresh (bool): 데이터를 새로고침할지 여부.

        반환값:
            tuple: 계산된 ROIC, ROE, ROA 및 관련 데이터.
        """
        self.c104.page = 'c104q'
        self.c106.page = 'c106q'
        d1, roic_r = self.c104.sum_recent_4q('ROIC', refresh)
        _, roic_dict = self.c104.find('ROIC', remove_yoy=True, del_unnamed_key=True, refresh=refresh)
        d2, roe_r = self.c104.latest_value_pop2('ROE', refresh)
        roe106 = self.c106.find('ROE', refresh)
        d3, roa_r = self.c104.latest_value_pop2('ROA', refresh)

        try:
            date, *_ = Tools.date_set(d1, d2, d3)
        except ValueError:
            # 날짜 데이터가 없는경우
            date = ''

        return date, roic_r, roic_dict, roe_r, roe106, roa_r

    def _calcFCF(self, refresh: bool) -> dict:
        """
        자유 현금 흐름(FCF)을 계산합니다.

        매개변수:
            refresh (bool): 데이터를 새로고침할지 여부.

        반환값:
            dict: 계산된 FCF 딕셔너리. 영업활동 현금흐름 데이터가 없는 경우 빈 딕셔너리를 반환합니다.

        참고:
            - CAPEX가 없는 업종의 경우, 영업활동 현금흐름을 그대로 사용합니다.
        """
        self.c103.page = 'c103현금흐름표y'
        _, 영업활동현금흐름_dict = self.c103.find('영업활동으로인한현금흐름', remove_yoy=True, del_unnamed_key=True, refresh=refresh)

        self.c103.page = 'c103재무상태표y'
        _, capex = self.c103.find('*CAPEX', remove_yoy=True, del_unnamed_key=True, refresh=refresh)

        mylogger.debug(f'영업활동현금흐름 {영업활동현금흐름_dict}')
        mylogger.debug(f'CAPEX {capex}')

        if len(영업활동현금흐름_dict) == 0:
            return {}

        if len(capex) == 0:
            # CAPEX 가 없는 업종은 영업활동현금흐름을 그대로 사용한다.
            mylogger.warning(f"{self} - CAPEX가 없는 업종으로 영업현금흐름을 그대로 사용합니다..")
            return 영업활동현금흐름_dict

        # 영업 활동으로 인한 현금 흐름에서 CAPEX 를 각 연도별로 빼주어 fcf 를 구하고 리턴값으로 fcf 딕셔너리를 반환한다.
        fcf_dict = {}
        for i in range(len(영업활동현금흐름_dict)):
            # 영업활동현금흐름에서 아이템을 하나씩 꺼내서 CAPEX 전체와 비교하여 같으면 차를 구해서 fcf_dict 에 추가한다.
            영업활동현금흐름date, 영업활동현금흐름value = 영업활동현금흐름_dict.popitem()
            # 해당 연도의 capex 가 없는 경우도 있어 일단 capex를 0으로 치고 먼저 추가한다.
            fcf_dict[영업활동현금흐름date] = 영업활동현금흐름value
            for CAPEXdate, CAPEXvalue in capex.items():
                if 영업활동현금흐름date == CAPEXdate:
                    fcf_dict[영업활동현금흐름date] = round(영업활동현금흐름value - CAPEXvalue, 2)

        mylogger.debug(f'fcf_dict {fcf_dict}')
        # 연도순으로 정렬해서 딕셔너리로 반환한다.
        return dict(sorted(fcf_dict.items(), reverse=False))

    def _calcPFCF(self, 시가총액_억: float, fcf_dict: dict) -> dict:
        """
        PFCF(Price to Free Cash Flow Ratio)를 계산합니다.

        매개변수:
            시가총액_억 (float): 기업의 시가총액 (억 단위).
            fcf_dict (dict): 자유 현금 흐름(FCF) 데이터.

        반환값:
            dict: 계산된 PFCF 딕셔너리.
        """
        if math.isnan(시가총액_억):
            mylogger.warning(f"{self} - 시가총액이 nan으로 pFCF를 계산할수 없습니다.")
            return {}

        # pfcf 계산
        pfcf_dict = {}
        for FCFdate, FCFvalue in fcf_dict.items():
            if FCFvalue == 0:
                pfcf_dict[FCFdate] = math.nan
            else:
                pfcf_dict[FCFdate] = round(시가총액_억 / FCFvalue, 2)

        pfcf_dict = mymongo.C1034.del_unnamed_key(pfcf_dict)

        mylogger.debug(f'pfcf_dict : {pfcf_dict}')
        return pfcf_dict

    def _calc가치지표(self, 시가총액_억: float, refresh: bool) -> tuple:
        self.c104.page = 'c104q'

        fcf_dict = self._calcFCF(refresh)
        pfcf_dict = self._calcPFCF(시가총액_억, fcf_dict)

        d, pcr_dict = self.c104.find('PCR', remove_yoy=True, del_unnamed_key=True, refresh=refresh)
        return d, fcf_dict, pfcf_dict, pcr_dict

    def _score(self) -> list:
        return [0,]

    def _generate_data(self, refresh: bool) -> MilData:
        mylogger.debug(f"In generate_data..refresh : {refresh}")
        시가총액_억 = self.get_marketcap억(refresh)
        mylogger.debug(f"{self} 시가총액(억) : {시가총액_억}")

        d1, 주주수익률, 재무활동현금흐름 = self._calc주주수익률(시가총액_억, refresh)
        mylogger.debug(f"{self} 주주수익률 : {주주수익률}, {d1}")

        d2, 이익지표, 영업활동현금흐름, 지배주주당기순이익 = self._calc이익지표(시가총액_억, refresh)
        mylogger.debug(f"{self} 이익지표 : {이익지표}, {d2}")

        d3, roic_r, roic_dict, roe_r, roe106, roa_r = self._calc투자수익률(refresh)
        d4, fcf_dict, pfcf_dict, pcr_dict = self._calc가치지표(시가총액_억, refresh)

        score = self._score()

        try:
            date_list = Tools.date_set(d1, d2, d3, d4)
        except ValueError:
            # 날짜 데이터가 없는경우
            date_list = ['',]

        return MilData(
            code= self.code,
            name= self.name,

            시가총액억= 시가총액_억,

            주주수익률= 주주수익률,
            재무활동현금흐름= 재무활동현금흐름,

            이익지표= 이익지표,
            영업활동현금흐름= 영업활동현금흐름,
            지배주주당기순이익= 지배주주당기순이익,

            roic_r= roic_r,
            roic_dict= roic_dict,
            roe_r= roe_r,
            roe_106= roe106,
            roa_r= roa_r,

            fcf_dict= fcf_dict,
            pfcf_dict= pfcf_dict,
            pcr_dict= pcr_dict,

            score= score,
            date = date_list,
        )

    def get(self, refresh = False) -> MilData:
        """
        MilData 객체를 Redis 캐시에서 가져오거나 새로 생성하여 반환합니다.

        캐시에서 데이터를 검색하고, 없을 경우 `_generate_data`를 호출하여 데이터를 생성합니다.
        생성된 데이터는 Redis 캐시에 저장되어 재사용됩니다.

        매개변수:
            refresh (bool): 캐시를 무시하고 새로 데이터를 계산할지 여부. 기본값은 False.
            verbose (bool): 실행 중 상세 정보를 출력할지 여부. 기본값은 True.

        반환값:
            MilData: Redis 캐시에서 가져오거나 새로 생성된 MilData 객체.

        로그:
            - 캐시 검색 상태와 새로 생성된 데이터를 출력합니다.
        """
        redis_name = f"{self.code}_{self.REDIS_MIL_DATA_SUFFIX}"
        mylogger.debug(f"{self} redisname: '{redis_name}' / refresh : {refresh}")

        def fetch_generate_data(refresh_in: bool) -> dict:
            return self._generate_data(refresh_in) # type: ignore

        return myredis.Base.fetch_and_cache_data(redis_name, refresh, fetch_generate_data, refresh)

    @classmethod
    def bulk_get_data(cls, codes: List[str], refresh: bool) -> Dict[str, MilData]:
        return myredis.Corps.bulk_get_or_compute(
            [f"{code}_{cls.REDIS_MIL_DATA_SUFFIX}" for code in codes],
            lambda key: cls(key[:6])._generate_data(refresh=True),
            refresh=refresh
        )
