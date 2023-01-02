#!/usr/bin/python3
# -*-coding: utf-8 -*-

from PyQt5.QAxContainer import QAxWidget


ON_EVENT_CONNECT_SIGNAL = 'OnEventConnect(int)'
ON_RECEIVE_MSG_SIGNAL = 'OnReceiveMsg(QString, QString, QString, QString)'
ON_RECEIVE_TR_DATA_SIGNAL = 'OnReceiveTrData(QString, QString, QString, ' \
                            'QString, QString, int, QString, QString, QString)'
ON_RECEIVE_REAL_DATA_SIGNAL = 'OnReceiveRealData(QString, QString, QString)'


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
