from typing import NamedTuple

class MarketIndices(NamedTuple):
    """
    주요 시장 지수를 나타내는 NamedTuple입니다.

    속성:
        WTI (str): 서부 텍사스 중질유(WTI) 선물 지수 (심볼: "CL=F").
        GOLD (str): 금 선물 지수 (심볼: "GC=F").
        SILVER (str): 은 선물 지수 (심볼: "SI=F").
        USD_IDX (str): 미국 달러 인덱스 (심볼: "DX-Y.NYB").
        USD_KRW (str): 달러-원 환율 (심볼: "KRW=X").
        SP500 (str): S&P 500 주가지수 (심볼: "^GSPC").
        KOSPI (str): 코스피 지수 (심볼: "^KS11").
        NIKKEI (str): 닛케이 225 지수 (일본) (심볼: "^N225").
        CHINA (str): 항셍 지수 (홍콩) (심볼: "^HSI").
        IRX (str): 미국 단기 국채 금리 지수 (13주 T-빌 금리) (심볼: "^IRX").
    """
    WTI: str = "CL=F"
    GOLD: str = "GC=F"
    SILVER: str = "SI=F"
    USD_IDX: str = "DX-Y.NYB"
    USD_KRW: str = "KRW=X"
    SP500: str = "^GSPC"
    KOSPI: str = "^KS11"
    NIKKEI: str = "^N225"
    CHINA: str = "^HSI"
    IRX: str = "^IRX"

MIs = MarketIndices()