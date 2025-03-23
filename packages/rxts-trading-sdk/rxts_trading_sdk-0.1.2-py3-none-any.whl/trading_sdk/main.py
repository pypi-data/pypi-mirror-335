# trading_sdk/main.py
import threading
import signal
import sys
import time
import os
from typing import List
from decimal import Decimal

from .config import Config, load_config
from .logger import setup_logger
from .callbacks import BaseCallback
from .client_bus import ClientBus
from .interfaces import ClientInterface
from .global_pb2 import Envelope, ReqStkOrderField, ReqStkCancelOrderField, OrdSideEnum, OrdTypeEnum
from .market_data_monitor import MarketDataMonitor
from .message_seq_manager import MessageSeqManager

class SDKMain(ClientInterface):
    def __init__(self, logger, config: Config, callback: BaseCallback):
        self.config = config
        self.logger = logger # setup_logger(self.config.log, self.config.strategy_env)
        self.callback = callback
        self.callback.attach(self)
        self.client_bus = ClientBus(self.logger, self.config, self.callback)
        data_dir = config.market.data_dir
        self.monitor = MarketDataMonitor(self.logger, data_dir, "pazqnsq", self.callback, config.market.data_interval_ms, 
                                         config.market.bin_market_data_enable, config.market.bin_market_data_slow_play, config.market.bin_market_data_files)
        self.running = False
        self.message_seq_manager = MessageSeqManager(config.trade.seqnum_persist_dir)

    def initialize(self):
        self.logger.info("[SDKMain]  初始化 SDK")
        if self.config.market.bin_market_data_enable and self.config.market.bin_market_data_slow_play:
            self.logger.info("[SDKMain]  启用了二进制行情数据，且启用了慢速播放模式，不再连接到bus")
        else:
            self.client_bus.initialize()
            self.subscribe(self.config.bus.subscribe_topics)
            self.logger.info("[SDKMain]  已订阅主题: {self.config.bus.subscribe_topics}")
        self.logger.info("[SDKMain]  SDK 初始化完成")

    def start(self):
        self.logger.info("[SDKMain]  启动 SDK")
        self.running = True
        
        if self.config.market.bin_market_data_enable and self.config.market.bin_market_data_slow_play:
            pass
        else:        
            try:
                self.client_bus.start()
                self.logger.info("[SDKMain]  SDK Trade 已启动并开始接收消息")
            except Exception as e:
                self.logger.error(f"[SDKMain]  SDK Trade 启动错误: {e}")
        
        try:
            self.monitor.start()
            self.logger.info("[SDKMain]  SDK Market 已启动并开始接收消息")
        except Exception as e:
            self.logger.error(f"[SDKMain]  SDK Market 启动错误: {e}")

    def stop(self):
        self.logger.info("[SDKMain]  停止 SDK")
        self.running = False
        if self.config.market.bin_market_data_enable and self.config.market.bin_market_data_slow_play:
            pass
        else:
            self.client_bus.stop()
        self.monitor.stop()
        self.logger.info("[SDKMain]  SDK 已停止")

    def publish(self, envelope):
        """
        发送 Envelope 消息。
        """
        self.client_bus.publish(envelope)
        # self.logger.info(f"[SDKMain]  发送 Envelope: {envelope}")

    def set_config(self, config: Config):
        """
        传入各种配置参数给系统。
        """
        self.config = config
        self.logger.info("[SDKMain]  更新配置参数")

    def on_message_received(self, envelope):
        """
        处理接收到的消息，委托给回调接口。
        """
        self.logger.info(f"[SDKMain]  收到 Envelope: {envelope}")
        if hasattr(self.callback, 'handle_message'):
            self.callback.handle_message(envelope)

    def generate_message_id(self, msg_type: str) -> int:
        msg_id = self.message_seq_manager.get_next_seq(msg_type)
        return msg_id
    
    def current_status(self):
        return f"Bus连接状态：{self.client_bus.status()}";
        pass

    def send_order(self, symbol: str, ord_price: float, ord_qty: int, ord_side: OrdSideEnum, ord_type: OrdTypeEnum):
        """
        发送委托。
        
        返回值：
            该委托的biz_index。发送失败时，返回-1。
        """
        biz_index = int(-1)
        try:
            # 在这里可以直接使用各个展开后的参数进行后续的操作
            self.logger.debug(f"[SDKMain]  证券代码: {symbol}")
            self.logger.debug(f"[SDKMain]  委托价格: {ord_price}")
            self.logger.debug(f"[SDKMain]  委托数量: {ord_qty}")
            self.logger.debug(f"[SDKMain]  买卖方向: {ord_side}")
            self.logger.debug(f"[SDKMain]  订单价格类型: {ord_type}")
            
            symbol_str = symbol
            parts = symbol_str.split('.')
            symbol = parts[0]
            market = parts[1] if len(parts) > 1 else ""
            print(f"拆分后的symbol={symbol}, market={market}")
                
            if market not in ['SH', 'SZ']:
                print("Market must be either 'SZ' or 'SH'")
                return -1
            
            if ord_side not in [OrdSideEnum.BUY, OrdSideEnum.SELL]:
                print("Side must be either 'BUY' or 'SELL'")
                return -1
                
            if ord_type not in [OrdTypeEnum.LIMIT, OrdTypeEnum.MARKET]:
                print("Order type must be either 'LIMIT' or 'MARKET'")
                return -1
            
            # 使用共享的SDK实例发送订单
            order = ReqStkOrderField()
            order.biz_index = self.generate_message_id("biz_index")
            biz_index = order.biz_index
            self.logger.debug(f"[SDKMain]  生成业务层委托序号: {order.biz_index}")
            order.symbol = symbol_str  # todo: 直接放在函数参数中，不要新建对象, 019732.SH, MARKET=FAK
            order.order_price = Decimal(ord_price)
            order.order_qty = ord_qty
            order.side = ord_side
            order.order_type = ord_type
            
            # 封装成envelope
            envelope = Envelope()
            envelope.topic = "order"
            envelope.envelope_message_id = self.generate_message_id("envelop_message_id")
            envelope.req_stk_order.CopyFrom(order)
            self.client_bus.publish(envelope)
            self.logger.info(f"[SDKMain]  发送委托请求: envelope={envelope}")
        except ValueError as e:
            self.logger.error(f"[SDKMain]  [send order failed] Invalid argument value: {e}")
        except Exception as e:
            self.logger.error(f"[SDKMain]  [send order failed] Failed to place order: {e}")
        finally:
            return biz_index
            
    def cancel_order(self, biz_index: int):
        """
        发送委托撤单请求。

        参数:
            biz_index : 委托撤单对象的编号。
        返回值：
            该委托的biz_index。发送失败时，返回-1。
        """
        try:
            self.logger.info(f"[SDKMain]  Cancelling order: {biz_index}")
            # Add actual cancel implementation 
            cancelorder = ReqStkCancelOrderField()
            cancelorder.biz_index = int(biz_index)

            envelope = Envelope()
            envelope.topic = "order"
            envelope.envelope_message_id = self.generate_message_id("envelope_message_id")
            envelope.req_stk_cancel_order.CopyFrom(cancelorder)
            self.client_bus.publish(envelope)
            self.logger.info(f"[SDKMain]  发送撤单请求: envelope={envelope}")
            return cancelorder.biz_index
        except ValueError as e:
            self.logger.error(f"[SDKMain]  [send order failed] Invalid argument value: {e}")
        except Exception as e:
            self.logger.error(f"[SDKMain]  [send order failed] Failed to place order: {e}")
        finally:
            return biz_index

def main(config_path: str):
    config = load_config(config_path)

    # 根据策略环境调整配置
    if config.strategy_env == 'real':
        # 实盘环境的特殊配置
        pass
    else:
        # 模拟或测试环境的特殊配置
        pass

    callback = BaseCallback()  # 用户可以继承 BaseCallback 并实现自定义逻辑
    logger = setup_logger(self.config.log, self.config.strategy_env)
    sdk = SDKMain(logger, config, callback)
    try:
        sdk.initialize()
        sdk.start()
    except KeyboardInterrupt:
        self.logger.info("[SDKMain] Shutting down...")
    finally:
        sdk.stop()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("用法: python main.py <config_file_path>")
        sys.exit(1)
    config_file = sys.argv[1]
    main(config_file)