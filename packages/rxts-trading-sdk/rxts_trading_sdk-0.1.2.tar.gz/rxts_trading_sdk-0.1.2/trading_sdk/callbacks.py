# sdk/callbacks.py
from .global_pb2 import Envelope, RtnStkOrderField, RspStkQryExpendableFundExField, RspStkQryExpendableSharesExField
from .market_data_pb2 import SecuDepthMarketData, TransactionTradeData, TransactionEntrustData, RtnMarketCloseField, RtnMarketOpenField, RtnSubscriptionSuccessField  # 导入生成的 Protobuf 类
from .interfaces import ClientInterface
from dataclasses import dataclass
from typing import Optional, Tuple
from typing import Dict, List, Optional, Tuple, Union
import json
import os
from .config import load_config, save_config
from wrappers import (
    RtnStkOrderFieldWrapper,
    RtnStkOrderFillFieldWrapper,
    RtnStkOrderConfirmFieldWrapper,
    ReqStkCancelOrderFieldWrapper,
    RspStkCancelOrderFieldWrapper,
    RspStkOrderFieldWrapper,
    ReqStkOrderFieldWrapper,
)

@dataclass
class Snapshot:
    Symbol: str
    Tick: Optional[SecuDepthMarketData]
    Orders: List[TransactionEntrustData]
    Transactions: List[TransactionTradeData]

@dataclass
class Slice:
    Ticks: Dict[str, Snapshot]

class BaseCallback:
    def __init__(self, logger, config):
        self.logger = logger
        self.sdk = None
        self.config = config
        self.subscribed_stocks = set()  # 用于存储订阅的股票代码
        # 从文件中恢复订阅，这样策略不需要自行在初始化时订阅合约
        self.load_subscribed_stocks_from_config(config)  # 从配置文件中加载订阅的合约

    def attach(self, sdk: ClientInterface):
        self.sdk = sdk

    def on_symbol(self, symbol: str):
        """
        订阅成功通知。
        """
        if symbol in self.subscribed_stocks:
            self.logger.info(f"BaseCallback 行情标的{symbol}订阅成功.")

    def on_data(self, slice: Slice):
        """
        收到行情slice数据
        """
        self.logger.debug(f"222 收到行情slice数据.")

        for symbol, snapshot in slice.Ticks.items():
            self.log_market_data(symbol, snapshot)

    def handle_message(self, envelope: Envelope):
        """
        默认的消息处理器，根据消息类型调用相应的处理方法。
        """
        if envelope.HasField("rsp_stk_order"):
            pass
        elif envelope.HasField("rsp_stk_cancel_order"):
            pass
        elif envelope.HasField("rtn_stk_order"):
            self.on_order(RtnStkOrderFieldWrapper(envelope.rtn_stk_order))
        elif envelope.HasField("rsp_stk_qry_expendable_fund_ex"):
            self.handle_rsp_stk_qry_expendable_fund_ex(envelope.rsp_stk_qry_expendable_fund_ex)
        elif envelope.HasField("rsp_stk_qry_expendable_shares_ex"):
            self.handle_rsp_stk_qry_expendable_shares_ex(envelope.rsp_stk_qry_expendable_shares_ex)
        elif envelope.HasField("rtn_market_close"):
            self.handle_rtn_market_close(envelope.rtn_market_close)
        elif envelope.HasField("rtn_market_open"):
            self.handle_rtn_market_open(envelope.rtn_market_open)
        else:
            self.logger.warning(f"BaseCallback 收到未知类型的 Envelope: {envelope}")

    def on_order(self, rtn: RtnStkOrderField):
        """
        处理委托回报。
        """
        self.logger.info(f"BaseCallback 回报: 委托编号={rtn.biz_index}, 订单编号={rtn.order_id}, 状态={rtn.order_status}")
        
    def subscribe_stocks(self, stocks: Union[str, List[str]], replace: bool = False):
        """订阅股票代码，可以是单个字符串或字符串数组"""
        if replace:
            self.subscribed_stocks.clear()
        
        if isinstance(stocks, str):
            self.subscribed_stocks.add(stocks)
        elif isinstance(stocks, list):
            self.subscribed_stocks.update(stocks)
        else:
            raise ValueError("BaseCallback 参数必须是字符串或字符串数组")
        
        save_config(self.config.get_path(), self.config)
        self.logger.info(f"BaseCallback 已订阅的股票代码: {self.subscribed_stocks}")
        
    def load_subscribed_stocks_from_config(self, config):
        """从配置文件中加载订阅的股票代码列表"""
        if hasattr(config, 'subscriptions') and config.subscriptions:
            self.subscribed_stocks = set(config.subscriptions)
            self.logger.info(f"BaseCallback 从配置文件中加载订阅的股票代码: {self.subscribed_stocks}")
        else:
            self.logger.warning("BaseCallback 配置文件中未找到订阅的股票代码列表")

    def is_subscribed(self, symbol: str):
        return True if symbol in self.subscribed_stocks else False

    def log_market_data(self, symbol: str, snapshot: Snapshot):
        """
        打印行情数据
        """
        self.logger.debug(f"\n{'*'*30} Symbol: {symbol} {'*'*30}")
        
        if snapshot.Tick:
            tick = snapshot.Tick
            self.logger.debug(f"""
    Market Data:
        Is Warmup: {tick.is_warmup}
        Symbol: {tick.symbol}
        Last Price: {tick.last_price}
        Pre Close Price: {tick.pre_close_price}
        Open Price: {tick.open_price}
        High Price: {tick.high_price}
        Low Price: {tick.low_price}
        Close Price: {tick.close_price}
        Upper Limit Price: {tick.upper_limit_price}
        Lower Limit Price: {tick.lower_limit_price}
        Trade Date: {tick.trade_date}
        Update Time: {tick.update_time}
        Trade Volume: {tick.trade_volume}
        Trade Balance: {tick.trade_balance}
        Average Price: {tick.average_price}
        Trades Number: {tick.trades_num}
        Instrument Status: {tick.instrument_trade_status}
        Total Bid Volume: {tick.total_bid_volume}
        Total Ask Volume: {tick.total_ask_volume}
        MA Bid Price: {tick.ma_bid_price}
        MA Ask Price: {tick.ma_ask_price}
        MA Bond Bid/Ask: {tick.ma_bond_bid_price}/{tick.ma_bond_ask_price}
        YTM: {tick.yield_to_maturity}
        IOPV: {tick.iopv}
        Market Depth:""")
            
            # 打印十档行情
            for i in range(len(tick.bid_price)):
                if tick.bid_price[i] != 0 or tick.bid_volume[i] != 0:
                    self.logger.debug(f"        Bid Level {i+1}: Price={tick.bid_price[i]}, Volume={tick.bid_volume[i]}")
            for i in range(len(tick.ask_price)):
                if tick.ask_price[i] != 0 or tick.ask_volume[i] != 0:
                    self.logger.debug(f"        Ask Level {i+1}: Price={tick.ask_price[i]}, Volume={tick.ask_volume[i]}")

        if snapshot.Orders:
            self.logger.debug(f"\n{'#'*20} Orders ({len(snapshot.Orders)}) {'#'*20}")
            for order in snapshot.Orders:
                self.logger.debug(f"""
    Order:
        Is Warmup: {order.is_warmup}
        Symbol: {order.symbol}
        Trans Flag: {order.trans_flag}
        Sequence No: {order.seq_no}
        Channel No: {order.channel_no}
        Trade Date: {order.trade_date}
        Transact Time: {order.transact_time}
        Order Price: {order.order_price}
        Order Volume: {order.order_volume}
        Order Side: {order.order_side}
        Order Action: {order.order_action}
        Tick Status: {order.tick_status}
        Order ID: {order.order_id}
        Biz Index: {order.biz_index}
        Trade Volume: {order.trade_volume}""")

        if snapshot.Transactions:
            self.logger.debug(f"\n{'#'*20} Transactions ({len(snapshot.Transactions)}) {'#'*20}")
            for trade in snapshot.Transactions:
                self.logger.debug(f"""
    Transaction:
        Is Warmup: {trade.is_warmup}
        Symbol: {trade.symbol}
        Trans Flag: {trade.trans_flag}
        Sequence No: {trade.seq_no}
        Channel No: {trade.channel_no}
        Trade Date: {trade.trade_date}
        Transact Time: {trade.transact_time}
        Trade Price: {trade.trade_price}
        Trade Volume: {trade.trade_volume}
        Trade Money: {trade.trade_money}
        Buy Order No: {trade.trade_buy_no}
        Sell Order No: {trade.trade_sell_no}
        BS Flag: {trade.trade_bs_flag}
        Biz Index: {trade.biz_index}""")

        self.logger.debug(f"\n{'-'*100}")
