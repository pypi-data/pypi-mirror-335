# sdk/interfaces.py
from typing import List
from global_pb2 import Envelope, OrdSideEnum, OrdTypeEnum, ReqStkOrderField, ReqStkCancelOrderField, ReqStkQryExpendableFundExField, ReqStkQryExpendableSharesExField
from market_data_pb2 import MessageTypeEnum, DirectionEnum, TrdTypeEnum, OrdActionTypeEnum, TransFlagEnum, Envelope
from google.protobuf.timestamp_pb2 import Timestamp

class ClientInterface:
    def __init__(self, logger):
        self.logger = logger

    def initialize(self):
        """
        初始化 SDK 连接和资源。
        """
        pass

    def subscribe(self, symbols):
        """
        对策略端的行情推送进行过滤。可以随时、多次调用。不影响服务器的行情订阅。
        """
        pass
        
    def send_order(self, symbol: str, ord_price: float, ord_qty: int, ord_side: OrdSideEnum, ord_type: OrdTypeEnum):
        """
        发送委托。
        
        返回值：
            该委托的biz_index。发送失败时，返回-1。
        """
        pass
            
    def cancel_order(self, biz_index: int):
        """
        发送委托撤单请求。

        参数:
            biz_index : 委托撤单对象的编号。
        返回值：
            该委托的biz_index。发送失败时，返回-1。
        """
        pass
