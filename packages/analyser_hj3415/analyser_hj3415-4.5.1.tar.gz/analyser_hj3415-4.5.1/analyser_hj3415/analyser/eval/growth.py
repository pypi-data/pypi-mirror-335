from dataclasses import dataclass

from utils_hj3415 import tools, setup_logger
from db_hj3415 import myredis

from analyser_hj3415.analyser.eval.common import Tools


mylogger = setup_logger(__name__,'WARNING')


@dataclass()
class GrowthData:
    """
    기업의 성장 데이터를 저장하는 데이터 클래스.

    이 클래스는 기업의 성장 데이터를 관리하며, 매출액 증가율 및 영업이익률 데이터를 포함합니다.
    또한, 평가 점수와 관련된 날짜 데이터를 관리합니다.

    속성:
        code (str): 기업의 종목 코드 (6자리 숫자 문자열).
        name (str): 기업명.
        매출액증가율_r (float): 최신 매출액 증가율.
        매출액증가율_dict (dict): 매출액 증가율과 관련된 과거 데이터.
        영업이익률_c106 (dict): c106 데이터를 기반으로 한 영업이익률 데이터.
        score (list): 평가 점수.
        date (list): 성장 데이터와 관련된 날짜 목록.
    """
    code: str
    name: str

    매출액증가율_r: float
    매출액증가율_dict: dict

    영업이익률_c106: dict

    score: list
    date: list


class Growth:
    """
    기업의 성장 데이터를 계산하고 관리하는 클래스.

    이 클래스는 기업의 매출액 증가율, 영업이익률 등과 같은 성장 지표를 계산하며,
    Redis 캐시를 통해 데이터를 저장하고 재사용할 수 있도록 지원합니다.

    속성:
        c101 (myredis.C101): 기업 정보와 데이터를 가져오기 위한 객체.
        c104 (myredis.C104): 매출액 증가율 데이터를 관리하기 위한 객체.
        c106 (myredis.C106): 영업이익률 데이터를 관리하기 위한 객체.
        name (str): 기업명.
        _code (str): 기업 종목 코드.
    """
    def __init__(self, code: str):
        assert tools.is_6digit(code), f'Invalid value : {code}'
        mylogger.debug(f"Growth : 종목코드 ({code})")

        self.c101 = myredis.C101(code)
        self.c104 = myredis.C104(code, 'c104q')
        self.c106 = myredis.C106(code, 'c106q')

        self.name = self.c101.get_name()
        self._code = code

    def __str__(self):
        return f"Growth({self.code}/{self.name})"

    @property
    def code(self) -> str:
        """
        현재 기업의 종목 코드를 반환합니다.

        반환값:
            str: 기업의 종목 코드 (6자리 숫자 문자열).
        """
        return self._code

    @code.setter
    def code(self, code: str):
        """
        기업의 종목 코드를 변경합니다.

        종목 코드 변경 시 관련된 데이터 객체(c101, c104, c106)의 코드도 함께 변경됩니다.

        매개변수:
            code (str): 변경할 종목 코드 (6자리 숫자 문자열).

        예외:
            AssertionError: 종목 코드가 6자리 숫자 문자열이 아닐 경우 발생.
        """
        assert tools.is_6digit(code), f'Invalid value : {code}'
        mylogger.debug(f"Growth : 종목코드 변경({self.code} -> {code})")

        self.c101.code = code
        self.c104.code = code
        self.c106.code = code

        self.name = self.c101.get_name()
        self._code = code

    def _score(self) -> list:
        return [0,]

    def _generate_data(self, refresh=False) -> GrowthData:
        """
        성장 데이터를 계산하여 GrowthData 객체를 생성합니다.

        이 함수는 매출액 증가율, 영업이익률 등의 데이터를 계산하고,
        이를 GrowthData 객체로 정리하여 반환합니다.

        매개변수:
            refresh (bool, optional): 데이터를 새로고침할지 여부. 기본값은 False.

        반환값:
            GrowthData: 계산된 성장 데이터를 포함하는 객체.

        예외:
            ValueError: 날짜 데이터가 없을 경우 기본값으로 빈 날짜 리스트를 설정.
        """
        self.c104.page = 'c104y'
        _, 매출액증가율_dict = self.c104.find('매출액증가율', remove_yoy=True, refresh=refresh)

        self.c104.page = 'c104q'
        d2, 매출액증가율_r = self.c104.latest_value_pop2('매출액증가율')

        mylogger.info(f'매출액증가율 : {매출액증가율_r} {매출액증가율_dict}')

        # c106 에서 타 기업과 영업이익률 비교
        self.c106.page = 'c106y'
        영업이익률_c106 = self.c106.find('영업이익률', refresh)

        score = self._score()

        try:
            date_list = Tools.date_set(d2)
        except ValueError:
            # 날짜 데이터가 없는경우
            date_list = ['', ]

        return GrowthData(
            code= self.code,
            name= self.name,

            매출액증가율_r= 매출액증가율_r,
            매출액증가율_dict= 매출액증가율_dict,

            영업이익률_c106= 영업이익률_c106,

            score= score,
            date= date_list,
        )

    def get(self, refresh = False) -> GrowthData:
        """
        GrowthData 객체를 Redis 캐시에서 가져오거나 새로 생성하여 반환합니다.

        캐시에서 데이터를 검색하고, 없을 경우 `_generate_data`를 호출하여 데이터를 생성합니다.
        생성된 데이터는 Redis 캐시에 저장되어 재사용됩니다.

        매개변수:
            refresh (bool, optional): 캐시 데이터를 무시하고 새로 계산할지 여부. 기본값은 False.
            verbose (bool, optional): 실행 중 상세 정보를 출력할지 여부. 기본값은 True.

        반환값:
            GrowthData: Redis 캐시에서 가져오거나 새로 생성된 GrowthData 객체.

        로그:
            - 캐시 검색 상태와 새로 생성된 데이터를 출력합니다.
        """

        redis_name = f"{self.code}_growth"
        mylogger.debug(f"{self} redisname: '{redis_name}' / refresh : {refresh}")

        def fetch_generate_data(refresh_in: bool) -> dict:
            return self._generate_data(refresh_in) # type: ignore

        return myredis.Base.fetch_and_cache_data(redis_name, refresh, fetch_generate_data, refresh)
