#!/usr/bin/python3
# -*-coding: utf-8 -*-

from enum import IntEnum
from PyQt5.QAxContainer import QAxWidget


ON_EVENT_CONNECT_SIGNAL = 'OnEventConnect(int)'
ON_RECEIVE_MSG_SIGNAL = 'OnReceiveMsg(QString, QString, QString, QString)'
ON_RECEIVE_TR_DATA_SIGNAL = 'OnReceiveTrData(QString, QString, QString, ' \
                            'QString, QString, int, QString, QString, QString)'
ON_RECEIVE_REAL_DATA_SIGNAL = 'OnReceiveRealData(QString, QString, QString)'


class Market(IntEnum):
    KOSPI = 0
    ELW = 3
    # = 4 # 뮤추얼펀드
    # = 5 # 신주인수권
    # = 6 # 리츠
    ETF = 8
    # = 9 # 하이일드펀드
    KOSDAQ = 10
    OUTSIDE = 30


class ResponseError(IntEnum):
    NONE = 0  # 정상처리
    SISE_OVERFLOW = -200  # 시세조회 과부화
    RQ_STRUCT_FAIL = -201  # 입력 구조체 생성 실패
    RQ_STRING_FAIL = -202  # 요청전문 작성 실패


class KiwoomOpenAPI(QAxWidget):
    """Open API+ 모듈을 래핑한 클래스."""

    def __init__(self):
        super().__init__()
        assert self.setControl('KHOPENAPI.KHOpenAPICtrl.1')

    def set_connect_handler(self, handler: callable):
        """통신 연결 상태 변경 이벤트 핸들러 연결."""
        self.OnEventConnect.connect(handler)

    def reset_connect_handler(self):
        self.OnEventConnect.disconnect()

    def set_msg_handler(self, handler: callable):
        """수신 메세지 이벤트 핸들러 연결."""
        self.OnReceiveMsg.connect(handler)

    def reset_msg_handler(self):
        self.OnReceiveMsg.disconnect()

    def set_trade_data_handler(self, handler: callable):
        """Tran 요청 수신 이벤트 핸들러 연결."""
        self.OnReceiveTrData.connect(handler)

    def reset_trade_data_handler(self):
        self.OnReceiveTrData.disconnect()

    def set_real_data_handler(self, handler: callable):
        """실시간 시세 이벤트 핸들러 연결."""
        self.OnReceiveRealData.connect(handler)

    def reset_real_data_handler(self):
        self.OnReceiveRealData.disconnect()

    @property
    def connected(self) -> bool:
        """현재 접속 상태를 반환.

        Return:
            True - 연결 완료
            False - 미연결
        """
        return self.dynamicCall('GetConnectState()') == 0

    @property
    def is_real_server(self) -> bool:
        """실제 서버로 접속 했는지 확인."""

        ret: str = self.dynamicCall(
            'KOA_Functions(QString, QString)', 'GetServerGubun', '')
        return ret != '1'  # '1'은 모의투자 서버

    def connect(self):
        """수동 로그인설정인 경우 로그인창을 출력.
        자동로그인 설정인 경우 로그인창에서 자동으로 로그인을 시도합니다.
        """
        self.CommConnect()

    def get_code_list(self, market: Market) -> list[str]:
        """시장구분에 따른 종목코드를 반환.

        Args:
          market: 시장 구분 값

        Return:
            종목코드 리스트.
        """
        ret: str = self.GetCodeListByMarket(f'{market.value}')
        code_list = ret.split(';')
        if code_list[-1] == '':
            return code_list[:-1]
        return code_list[:]

    def get_future_code_list(self) -> list[str]:
        """지수선물 코드 리스트를 반환.

        Return:
            종목코드 리스트
        """
        ret: str = self.GetFutureList()
        code_list = ret.split(';')
        if code_list[-1] == '':
            return code_list[:-1]
        return code_list[:]

    def get_master_code_name(self, code: str) -> str:
        """종목코드의 한글명을 반환.

        Args:
            code: 종목코드
        Return:
            종목 한글명
        """
        return self.GetMasterCodeName(code)

    def set_input_value(self, id: str, value: str):
        """Tran 입력 값을 서버통신 전에 세팅

        조회요청시 TR의 Input값을 지정하는 함수입니다.
        CommRqData 호출 전에 입력값들을 셋팅합니다.
        각 TR마다 Input 항목이 다릅니다. 순서에 맞게 Input 값들을 셋팅해야 합니다.
        
        Args:
            id - TR에 명시된 Input이름
            value - Input이름으로 지정한 값
        """
        self.SetInputValue(id, value)

    def request_data(
        self,
        req_name: str,
        tran_code: str,
        prev_next: int,
        screen_no: str) -> ResponseError:
        """Tran을 서버로 요청.

        Args:
            req_name - 임의로 지정한 요청명
            tran_code - Tran명 입력
            prev_next
                0 - 조회
                2 - 연속
            screen_no
                4자리의 화면번호

        Returns:
            TrRequestError
        """
        return self.CommRqData(req_name, tran_code, prev_next, screen_no)

    def get_receive_count(self, tran_code: str, req_name: str) -> int:
        """수신된 데이터의 개수 반환.

        예를 들어 차트 조회는 한번에 최대 900개 데이터를 수신할 수 있다.
        이렇게 수신한 데이터 개수를 얻을때 사용한다.
        OnReceiveTRData()이벤트가 발생될 때 그 안에서 사용해야 한다.

        Args:
            req_name - 요청 이름
            tran_code - Tran명 입력

        Returns:
            수신된 데이터의 개수
        """
        return self.GetRepeatCnt(tran_code, req_name)

    def get_request_data(
        self,
        tr_code: str,
        record_name: str,
        index: int,
        item_name: str) -> str:
        """OnReceiveTRData() 이벤트가 발생될때 수신한 데이터를 얻어오는 함수.

        이 함수는 OnReceiveTRData() 이벤트가 발생될때 그 안에서 사용해야 한다.

        Args:
            tr_code - 요청한 TR 이름
            record_name - 레코드 이름 (용도를 잘 모르겠다.)
            index - 요청 index
            item_name - Tr에서 가져오려는 데이터 이름

        Return:
            요청한 데이터 값
        """

        ret: str = self.GetCommData(tr_code, record_name, index, item_name)
        return ret.strip()
