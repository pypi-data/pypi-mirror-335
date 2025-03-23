from global_pb2 import (
    RtnStkOrderField,
    RtnStkOrderFillField,
    RtnStkOrderConfirmField,
    ReqStkCancelOrderField,
    RspStkCancelOrderField,
    RspStkOrderField,
    ReqStkOrderField,
)

class RtnStkOrderFieldWrapper:
    def __init__(self, rtn_stk_order: RtnStkOrderField):
        self._rtn_stk_order = rtn_stk_order

    @property
    def biz_index(self):
        return self._rtn_stk_order.biz_index

    @property
    def symbol(self):
        return self._rtn_stk_order.symbol

    @property
    def order_id(self):
        #return self._rtn_stk_order.order_id
        return self._rtn_stk_order.biz_index

    @property
    def order_frz_amt(self):
        return self._rtn_stk_order.order_frz_amt

    @property
    def fund_avl(self):
        return self._rtn_stk_order.fund_avl

    @property
    def stk_avl(self):
        return self._rtn_stk_order.stk_avl

    @property
    def order_status(self):
        return self._rtn_stk_order.order_status

    @property
    def side(self):
        return self._rtn_stk_order.side

    @property
    def order_type(self):
        return self._rtn_stk_order.order_type

    @property
    def offer_ret_msg(self):
        return self._rtn_stk_order.offer_ret_msg

    @property
    def order_qty(self):
        return self._rtn_stk_order.order_qty

    @property
    def withdrawn_qty(self):
        return self._rtn_stk_order.withdrawn_qty

    @property
    def total_matched_qty(self):
        return self._rtn_stk_order.total_matched_qty

    @property
    def total_matched_amt(self):
        return self._rtn_stk_order.total_matched_amt

    @property
    def stk_qty(self):
        return self._rtn_stk_order.stk_qty

    @property
    def matched_amt(self):
        return self._rtn_stk_order.matched_amt

    # CamelCase properties (首字母大写)
    @property
    def BizIndex(self):
        return self.biz_index

    @property
    def Symbol(self):
        return self._rtn_stk_order.symbol

    @property
    def Ticker(self):
        return self._rtn_stk_order.symbol

    @property
    def OrderId(self):
        return self.order_id

    @property
    def OrderFrzAmt(self):
        return self.order_frz_amt

    @property
    def FundAvl(self):
        return self.fund_avl

    @property
    def StkAvl(self):
        return self.stk_avl

    @property
    def OrderStatus(self):
        return self.order_status

    @property
    def Status(self):
        return self.order_status

    @property
    def OrderType(self):
        return self.order_type

    @property
    def OfferRetMsg(self):
        return self.offer_ret_msg

    @property
    def OrderQty(self):
        return self.order_qty

    @property
    def WithdrawnQty(self):
        return self.withdrawn_qty

    @property
    def TotalMatchedQty(self):
        return self.total_matched_qty

    @property
    def FillQuantity(self):
        return self.total_matched_qty

    @property
    def TotalMatchedAmt(self):
        return self.total_matched_amt

    @property
    def StkQty(self):
        return self.stk_qty

    @property
    def MatchedAmt(self):
        return self.matched_amt


class RtnStkOrderFillFieldWrapper:
    def __init__(self, rtn_stk_order_fill_field: RtnStkOrderFillField):
        self._rtn_stk_order_fill_field = rtn_stk_order_fill_field

    @property
    def biz_index(self):
        return self._rtn_stk_order_fill_field.biz_index

    @property
    def symbol(self):
        return self._rtn_stk_order_fill_field.symbol

    @property
    def matched_sn(self):
        return self._rtn_stk_order_fill_field.matched_sn

    @property
    def order_id(self):
        #return self._rtn_stk_order_fill_field.order_id
        return self._rtn_stk_order_fill_field.biz_index

    @property
    def matched_qty(self):
        return self._rtn_stk_order_fill_field.matched_qty

    @property
    def matched_price(self):
        return self._rtn_stk_order_fill_field.matched_price

    @property
    def order_frz_amt(self):
        return self._rtn_stk_order_fill_field.order_frz_amt

    @property
    def fund_avl(self):
        return self._rtn_stk_order_fill_field.fund_avl

    @property
    def stk_avl(self):
        return self._rtn_stk_order_fill_field.stk_avl

    @property
    def matched_date(self):
        return self._rtn_stk_order_fill_field.matched_date

    @property
    def matched_time(self):
        return self._rtn_stk_order_fill_field.matched_time

    @property
    def is_withdraw(self):
        return self._rtn_stk_order_fill_field.is_withdraw

    @property
    def matched_type(self):
        return self._rtn_stk_order_fill_field.matched_type

    @property
    def order_status(self):
        return self._rtn_stk_order_fill_field.order_status

    @property
    def side(self):
        return self._rtn_stk_order_fill_field.side

    @property
    def order_type(self):
        return self._rtn_stk_order_fill_field.order_type

    @property
    def offer_ret_msg(self):
        return self._rtn_stk_order_fill_field.offer_ret_msg

    @property
    def order_qty(self):
        return self._rtn_stk_order_fill_field.order_qty

    @property
    def withdrawn_qty(self):
        return self._rtn_stk_order_fill_field.withdrawn_qty

    @property
    def total_matched_qty(self):
        return self._rtn_stk_order_fill_field.total_matched_qty

    @property
    def total_matched_amt(self):
        return self._rtn_stk_order_fill_field.total_matched_amt

    @property
    def stk_qty(self):
        return self._rtn_stk_order_fill_field.stk_qty

    @property
    def matched_amt(self):
        return self._rtn_stk_order_fill_field.matched_amt

    @property
    def ex_order_sn(self):
        return self._rtn_stk_order_fill_field.ex_order_sn

    # CamelCase properties (首字母大写)
    @property
    def BizIndex(self):
        return self.biz_index

    @property
    def Symbol(self):
        return self._rtn_stk_order_fill_field.symbol

    @property
    def Ticker(self):
        return self._rtn_stk_order_fill_field.symbol

    @property
    def MatchedSn(self):
        return self.matched_sn

    @property
    def OrderId(self):
        #return self.order_id
        return self.biz_index

    @property
    def MatchedQty(self):
        return self.matched_qty

    @property
    def MatchedPrice(self):
        return self.matched_price

    @property
    def OrderFrzAmt(self):
        return self.order_frz_amt

    @property
    def FundAvl(self):
        return self.fund_avl

    @property
    def StkAvl(self):
        return self.stk_avl

    @property
    def MatchedDate(self):
        return self.matched_date

    @property
    def MatchedTime(self):
        return self.matched_time

    @property
    def IsWithdraw(self):
        return self.is_withdraw

    @property
    def MatchedType(self):
        return self.matched_type

    @property
    def OrderStatus(self):
        return self.order_status

    @property
    def OrderType(self):
        return self.order_type

    @property
    def OfferRetMsg(self):
        return self.offer_ret_msg

    @property
    def OrderQty(self):
        return self.order_qty

    @property
    def WithdrawnQty(self):
        return self.withdrawn_qty

    @property
    def TotalMatchedQty(self):
        return self.total_matched_qty

    @property
    def TotalMatchedAmt(self):
        return self.total_matched_amt

    @property
    def StkQty(self):
        return self.stk_qty

    @property
    def MatchedAmt(self):
        return self.matched_amt

    @property
    def ExOrderSn(self):
        return self.ex_order_sn


class RtnStkOrderConfirmFieldWrapper:
    def __init__(self, rtn_stk_order_confirm_field: RtnStkOrderConfirmField):
        self._rtn_stk_order_confirm_field = rtn_stk_order_confirm_field

    @property
    def biz_index(self):
        return self._rtn_stk_order_confirm_field.biz_index

    @property
    def symbol(self):
        return self._rtn_stk_order_confirm_field.symbol

    @property
    def order_id(self):
        return self._rtn_stk_order_confirm_field.order_id

    @property
    def trdacct(self):
        return self._rtn_stk_order_confirm_field.trdacct

    @property
    def cust_code(self):
        return self._rtn_stk_order_confirm_field.cust_code

    @property
    def cuacct_code(self):
        return self._rtn_stk_order_confirm_field.cuacct_code

    @property
    def cuacct_sn(self):
        return self._rtn_stk_order_confirm_field.cuacct_sn

    @property
    def order_status(self):
        return self._rtn_stk_order_confirm_field.order_status

    @property
    def side(self):
        return self._rtn_stk_order_confirm_field.side

    @property
    def order_type(self):
        return self._rtn_stk_order_confirm_field.order_type

    @property
    def order_date(self):
        return self._rtn_stk_order_confirm_field.order_date

    @property
    def order_price(self):
        return self._rtn_stk_order_confirm_field.order_price

    @property
    def order_qty(self):
        return self._rtn_stk_order_confirm_field.order_qty

    # CamelCase properties (首字母大写)
    @property
    def BizIndex(self):
        return self.biz_index

    @property
    def Symbol(self):
        return self._rtn_stk_order_confirm_field.symbol

    @property
    def Ticker(self):
        return self._rtn_stk_order_confirm_field.symbol

    @property
    def OrderId(self):
        return self.order_id

    @property
    def TrdAcct(self):
        return self.trdacct

    @property
    def CustCode(self):
        return self.cust_code

    @property
    def CuacctCode(self):
        return self.cuacct_code

    @property
    def CuacctSn(self):
        return self.cuacct_sn

    @property
    def OrderStatus(self):
        return self.order_status

    @property
    def OrderType(self):
        return self.order_type

    @property
    def OrderDate(self):
        return self.order_date

    @property
    def OrderPrice(self):
        return self.order_price

    @property
    def OrderQty(self):
        return self.order_qty


class ReqStkCancelOrderFieldWrapper:
    def __init__(self, req_stk_cancel_order_field: ReqStkCancelOrderField):
        self._req_stk_cancel_order_field = req_stk_cancel_order_field

    @property
    def biz_index(self):
        return self._req_stk_cancel_order_field.biz_index

    @property
    def order_id(self):
        return self._req_stk_cancel_order_field.order_id

    # CamelCase properties (首字母大写)
    @property
    def BizIndex(self):
        return self.biz_index

    @property
    def OrderId(self):
        return self.order_id


class RspStkCancelOrderFieldWrapper:
    def __init__(self, rsp_stk_cancel_order_field: RspStkCancelOrderField):
        self._rsp_stk_cancel_order_field = rsp_stk_cancel_order_field

    @property
    def biz_index(self):
        return self._rsp_stk_cancel_order_field.biz_index

    @property
    def order_id(self):
        return self._rsp_stk_cancel_order_field.order_id

    @property
    def order_price(self):
        return self._rsp_stk_cancel_order_field.order_price

    @property
    def order_qty(self):
        return self._rsp_stk_cancel_order_field.order_qty

    @property
    def order_amt(self):
        return self._rsp_stk_cancel_order_field.order_amt

    @property
    def order_frz_amt(self):
        return self._rsp_stk_cancel_order_field.order_frz_amt

    @property
    def symbol(self):
        return self._rsp_stk_cancel_order_field.symbol

    @property
    def wt_order_id(self):
        return self._rsp_stk_cancel_order_field.wt_order_id

    # CamelCase properties (首字母大写)
    @property
    def BizIndex(self):
        return self.biz_index

    @property
    def OrderId(self):
        return self.order_id

    @property
    def OrderPrice(self):
        return self.order_price

    @property
    def OrderQty(self):
        return self.order_qty

    @property
    def OrderAmt(self):
        return self.order_amt

    @property
    def OrderFrzAmt(self):
        return self.order_frz_amt

    @property
    def Symbol(self):
        return self._rtn_stk_order_confirm_field.symbol

    @property
    def Ticker(self):
        return self._rtn_stk_order_confirm_field.symbol

    @property
    def WtOrderId(self):
        return self.wt_order_id


class RspStkOrderFieldWrapper:
    def __init__(self, rsp_stk_order_field: RspStkOrderField):
        self._rsp_stk_order_field = rsp_stk_order_field

    @property
    def biz_index(self):
        return self._rsp_stk_order_field.biz_index

    @property
    def order_id(self):
        return self._rsp_stk_order_field.order_id

    @property
    def order_price(self):
        return self._rsp_stk_order_field.order_price

    @property
    def order_qty(self):
        return self._rsp_stk_order_field.order_qty

    @property
    def order_amt(self):
        return self._rsp_stk_order_field.order_amt

    @property
    def order_frz_amt(self):
        return self._rsp_stk_order_field.order_frz_amt

    @property
    def symbol(self):
        return self._rsp_stk_order_field.symbol

    @property
    def side(self):
        return self._rsp_stk_order_field.side

    @property
    def order_type(self):
        return self._rsp_stk_order_field.order_type

    @property
    def ex_order_sn(self):
        return self._rsp_stk_order_field.ex_order_sn

    @property
    def order_status(self):
        return self._rsp_stk_order_field.order_status

    # CamelCase properties (首字母大写)
    @property
    def BizIndex(self):
        return self.biz_index

    @property
    def OrderId(self):
        return self.order_id

    @property
    def OrderPrice(self):
        return self.order_price

    @property
    def OrderQty(self):
        return self.order_qty

    @property
    def OrderAmt(self):
        return self.order_amt

    @property
    def OrderFrzAmt(self):
        return self.order_frz_amt

    @property
    def Symbol(self):
        return self._rsp_stk_order_field.symbol

    @property
    def Ticker(self):
        return self._rsp_stk_order_field.symbol

    @property
    def ExOrderSn(self):
        return self.ex_order_sn

    @property
    def OrderStatus(self):
        return self.order_status


class ReqStkOrderFieldWrapper:
    def __init__(self, req_stk_order_field: ReqStkOrderField):
        self._req_stk_order_field = req_stk_order_field

    @property
    def biz_index(self):
        return self._req_stk_order_field.biz_index

    @property
    def symbol(self):
        return self._req_stk_order_field.symbol

    @property
    def order_price(self):
        return self._req_stk_order_field.order_price

    @property
    def order_qty(self):
        return self._req_stk_order_field.order_qty

    @property
    def side(self):
        return self._req_stk_order_field.side

    @property
    def position_effect(self):
        return self._req_stk_order_field.position_effect

    @property
    def order_type(self):
        return self._req_stk_order_field.order_type

    # CamelCase properties (首字母大写)
    @property
    def BizIndex(self):
        return self.biz_index

    @property
    def Symbol(self):
        return self._req_stk_order_field.symbol

    @property
    def Ticker(self):
        return self._req_stk_order_field.symbol

    @property
    def OrderPrice(self):
        return self.order_price

    @property
    def OrderQty(self):
        return self.order_qty

    @property
    def PositionEffect(self):
        return self.position_effect

    @property
    def OrderType(self):
        return self.order_type
    
from google.protobuf.timestamp_pb2 import Timestamp
from typing import List

class SecuDepthMarketDataWrapper:
    def __init__(self, secu_depth_market_data):
        self._data = secu_depth_market_data

    # 保留原始的 snake_case 字段访问
    @property
    def symbol(self):
        return self._data.symbol

    @property
    def last_price(self):
        return self._data.last_price

    @property
    def pre_close_price(self):
        return self._data.pre_close_price

    @property
    def open_price(self):
        return self._data.open_price

    @property
    def high_price(self):
        return self._data.high_price

    @property
    def low_price(self):
        return self._data.low_price

    @property
    def close_price(self):
        return self._data.close_price

    @property
    def upper_limit_price(self):
        return self._data.upper_limit_price

    @property
    def lower_limit_price(self):
        return self._data.lower_limit_price

    @property
    def trade_date(self):
        return self._data.trade_date

    @property
    def update_time(self):
        return self._data.update_time

    @property
    def trade_volume(self):
        return self._data.trade_volume

    @property
    def trade_balance(self):
        return self._data.trade_balance

    @property
    def average_price(self):
        return self._data.average_price

    @property
    def bid_price(self) -> List[float]:
        return self._data.bid_price

    @property
    def ask_price(self) -> List[float]:
        return self._data.ask_price

    @property
    def bid_volume(self) -> List[int]:
        return self._data.bid_volume

    @property
    def ask_volume(self) -> List[int]:
        return self._data.ask_volume

    @property
    def trades_num(self):
        return self._data.trades_num

    @property
    def instrument_trade_status(self):
        return self._data.instrument_trade_status

    @property
    def total_bid_volume(self):
        return self._data.total_bid_volume

    @property
    def total_ask_volume(self):
        return self._data.total_ask_volume

    @property
    def ma_bid_price(self):
        return self._data.ma_bid_price

    @property
    def ma_ask_price(self):
        return self._data.ma_ask_price

    @property
    def ma_bond_bid_price(self):
        return self._data.ma_bond_bid_price

    @property
    def ma_bond_ask_price(self):
        return self._data.ma_bond_ask_price

    @property
    def yield_to_maturity(self):
        return self._data.yield_to_maturity

    @property
    def iopv(self):
        return self._data.iopv

    @property
    def etf_buy_count(self):
        return self._data.etf_buy_count

    @property
    def etf_sell_count(self):
        return self._data.etf_sell_count

    @property
    def etf_buy_volume(self):
        return self._data.etf_buy_volume

    @property
    def etf_buy_balance(self):
        return self._data.etf_buy_balance

    @property
    def etf_sell_volume(self):
        return self._data.etf_sell_volume

    @property
    def etf_sell_balance(self):
        return self._data.etf_sell_balance

    @property
    def total_warrant_exec_volume(self):
        return self._data.total_warrant_exec_volume

    @property
    def warrant_lower_price(self):
        return self._data.warrant_lower_price

    @property
    def warrant_upper_price(self):
        return self._data.warrant_upper_price

    @property
    def cancel_buy_num(self):
        return self._data.cancel_buy_num

    @property
    def cancel_sell_num(self):
        return self._data.cancel_sell_num

    @property
    def cancel_buy_volume(self):
        return self._data.cancel_buy_volume

    @property
    def cancel_sell_volume(self):
        return self._data.cancel_sell_volume

    @property
    def cancel_buy_value(self):
        return self._data.cancel_buy_value

    @property
    def cancel_sell_value(self):
        return self._data.cancel_sell_value

    @property
    def total_buy_num(self):
        return self._data.total_buy_num

    @property
    def total_sell_num(self):
        return self._data.total_sell_num

    @property
    def duration_after_buy(self):
        return self._data.duration_after_buy

    @property
    def duration_after_sell(self):
        return self._data.duration_after_sell

    @property
    def bid_orders_num(self):
        return self._data.bid_orders_num

    @property
    def ask_orders_num(self):
        return self._data.ask_orders_num

    @property
    def pre_iopv(self):
        return self._data.pre_iopv

    @property
    def channel_no(self):
        return self._data.channel_no

    @property
    def bond_last_auction_price(self):
        return self._data.bond_last_auction_price

    @property
    def bond_auction_volume(self):
        return self._data.bond_auction_volume

    @property
    def bond_auction_balance(self):
        return self._data.bond_auction_balance

    @property
    def bond_last_trade_type(self):
        return self._data.bond_last_trade_type

    @property
    def bond_trade_status(self) -> List[str]:
        return self._data.bond_trade_status

    @property
    def r1(self):
        return self._data.r1

    @property
    def local_recv_time(self) -> Timestamp:
        return self._data.local_recv_time

    @property
    def sequence_no(self):
        return self._data.sequence_no

    @property
    def is_warmup(self):
        return self._data.is_warmup

    # 添加 camelCase 属性访问器
    @property
    def Symbol(self):
        return self.symbol

    @property
    def LastPrice(self):
        return self.last_price

    @property
    def PreClosePrice(self):
        return self.pre_close_price

    @property
    def OpenPrice(self):
        return self.open_price

    @property
    def HighPrice(self):
        return self.high_price

    @property
    def LowPrice(self):
        return self.low_price

    @property
    def ClosePrice(self):
        return self.close_price

    @property
    def UpperLimitPrice(self):
        return self.upper_limit_price

    @property
    def LowerLimitPrice(self):
        return self.lower_limit_price

    @property
    def TradeDate(self):
        return self.trade_date

    @property
    def UpdateTime(self):
        return self.update_time

    @property
    def TradeVolume(self):
        return self.trade_volume

    @property
    def TradeBalance(self):
        return self.trade_balance

    @property
    def AveragePrice(self):
        return self.average_price

    @property
    def BidPrice(self) -> List[float]:
        return self.bid_price

    @property
    def AskPrice(self) -> List[float]:
        return self.ask_price

    @property
    def BidVolume(self) -> List[int]:
        return self.bid_volume

    @property
    def AskVolume(self) -> List[int]:
        return self.ask_volume

    @property
    def TradesNum(self):
        return self.trades_num

    @property
    def InstrumentTradeStatus(self):
        return self.instrument_trade_status

    @property
    def TotalBidVolume(self):
        return self.total_bid_volume

    @property
    def TotalAskVolume(self):
        return self.total_ask_volume

    @property
    def MaBidPrice(self):
        return self.ma_bid_price

    @property
    def MaAskPrice(self):
        return self.ma_ask_price

    @property
    def MaBondBidPrice(self):
        return self.ma_bond_bid_price

    @property
    def MaBondAskPrice(self):
        return self.ma_bond_ask_price

    @property
    def YieldToMaturity(self):
        return self.yield_to_maturity

    @property
    def Iopv(self):
        return self.iopv

    @property
    def EtfBuyCount(self):
        return self.etf_buy_count

    @property
    def EtfSellCount(self):
        return self.etf_sell_count

    @property
    def EtfBuyVolume(self):
        return self.etf_buy_volume

    @property
    def EtfBuyBalance(self):
        return self.etf_buy_balance

    @property
    def EtfSellVolume(self):
        return self.etf_sell_volume

    @property
    def EtfSellBalance(self):
        return self.etf_sell_balance

    @property
    def TotalWarrantExecVolume(self):
        return self.total_warrant_exec_volume

    @property
    def WarrantLowerPrice(self):
        return self.warrant_lower_price

    @property
    def WarrantUpperPrice(self):
        return self.warrant_upper_price

    @property
    def CancelBuyNum(self):
        return self.cancel_buy_num

    @property
    def CancelSellNum(self):
        return self.cancel_sell_num

    @property
    def CancelBuyVolume(self):
        return self.cancel_buy_volume

    @property
    def CancelSellVolume(self):
        return self.cancel_sell_volume

    @property
    def CancelBuyValue(self):
        return self.cancel_buy_value

    @property
    def CancelSellValue(self):
        return self.cancel_sell_value

    @property
    def TotalBuyNum(self):
        return self.total_buy_num

    @property
    def TotalSellNum(self):
        return self.total_sell_num

    @property
    def DurationAfterBuy(self):
        return self.duration_after_buy

    @property
    def DurationAfterSell(self):
        return self.duration_after_sell

    @property
    def BidOrdersNum(self):
        return self.bid_orders_num

    @property
    def AskOrdersNum(self):
        return self.ask_orders_num

    @property
    def PreIopv(self):
        return self.pre_iopv

    @property
    def ChannelNo(self):
        return self.channel_no

    @property
    def BondLastAuctionPrice(self):
        return self.bond_last_auction_price

    @property
    def BondAuctionVolume(self):
        return self.bond_auction_volume

    @property
    def BondAuctionBalance(self):
        return self.bond_auction_balance

    @property
    def BondLastTradeType(self):
        return self.bond_last_trade_type

    @property
    def BondTradeStatus(self) -> List[str]:
        return self.bond_trade_status

    @property
    def R1(self):
        return self.r1

    @property
    def LocalRecvTime(self) -> Timestamp:
        return self.local_recv_time

    @property
    def SequenceNo(self):
        return self.sequence_no

    @property
    def IsWarmup(self):
        return self.is_warmup