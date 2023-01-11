from dataclasses import dataclass



@dataclass(frozen=True)
class TickDataModel(object):
    code: str  # 종목 코드
    price: str  # 현재가
    volume: str  # 거래량
    datetime: str  # 체결시간
    open: str  # 시가
    high: str  # 고가
    low: str  # 저가
    adjust_stock: str  # 수정주가구분
    adjust_ratio: str  # 수정비율
    large_category: str  # 대업종구분
    small_category: str  # 소업종구분
    stock_info: str # 종목정보
    adjust_stock_event: str  # 수정주가이벤트
    previvous_close: str  # 전일종가


@dataclass(frozen=True)
class InvestorDataModel(object):
    code: str  # 종목 코드
    date: str  # 일자
    value: str  #  현재가
    symbols: str  # 대비기호 (ex, 상/하한,보합 등)
    ratio: str  #  전일대비
    rate: str  #  등락율
    accumulate_volume: str  #  누적거래량
    accumulate_value: str  #  누적거래대금
    personal: str  #  개인투자자
    foreigner: str  #  외국인투자자
    company: str  #  기관계
    financial_investor: str  #  금융투자
    insurance: str  #  보험
    investor_trust: str  #  투신
    etc_financial: str  #  기타금융
    bank: str  #  은행
    pension_fund: str  #  연기금등
    private_fund: str  #  사모펀드
    country: str  #  국가
    other_corp: str  #  기타법인
    fake_foreigner: str  #  내외국
