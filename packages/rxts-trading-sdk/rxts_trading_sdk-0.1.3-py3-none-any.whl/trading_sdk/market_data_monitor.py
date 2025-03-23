# market_data_monitor.py
import os
import sys
import time
import struct
import datetime
from dataclasses import dataclass
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import logging
import mmap
import ctypes
import platform
from l2data_reader import (
    MarketDataReader, MarketDataHeader, Envelope, TransactionEntrustData,
    SecuDepthMarketData, TransactionTradeData,
    MessageType, Direction, TrdType, OrdActionType, TransFlag, Envelope,
    time_to_milliseconds
)
from global_pb2 import Envelope
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Union
from collections import defaultdict
from .callbacks import BaseCallback, Slice, Snapshot

# 导入 OrderBook 类
try:
    from level2_order_book import OrderBook
except ImportError as e:
    logging.error(f"无法导入 level2_order_book 模块，请确保已安装该依赖，{e}")
    raise

class MarketDataFileHandler(FileSystemEventHandler):
    def __init__(self, logger, reader: MarketDataReader):
        super().__init__()
        self.logger = logger
        self.reader = reader

    def on_modified(self, event):
        """文件被修改时的处理函数"""
        if not event.is_directory and event.src_path == self.reader.index_file:
            try:
                # 更新文件大小
                self.reader.index_reader.get_size()
                self.logger.info(f"检测到索引文件修改: {event.src_path}")
            except Exception as e:
                self.logger.error(f"处理文件修改事件失败: {e}")

@dataclass
class MarketDataMonitor:
    def __init__(self, logger, data_dir: str,
                 counter_name: str, callback: BaseCallback, data_interval_ms: int = 5000, 
                 bin_market_data_enable: bool = False,
                 bin_market_data_slow_play: bool = False,
                 bin_market_data_files: List[str] = []):
        self.logger = logger
        self.data_dir = data_dir
        self.counter_name = counter_name
        self.callback = callback
        self.data_interval_ms = data_interval_ms
        self.bin_market_data_enable = bin_market_data_enable
        self.bin_market_data_slow_play = bin_market_data_slow_play
        self.bin_market_data_files = bin_market_data_files
        self.reader = None
        self.observer = None
        self.running = False
        self.is_warmup = False
        
        # Slice management
        self.current_slice = defaultdict(lambda: Snapshot(Symbol="", Tick=None, Orders=[], Transactions=[]))
        self.slice_start_time = None  # Will be set when first message arrives
        self.last_msg_time = None
        
        # 添加交易日开始时间配置，默认为9:30:00.500
        self.trading_day_start_time = 93000500  # 9:30:00.500 in HHMMSSfff format
        self.first_slice_created = False  # 标记是否已创建第一个时间片
        
        # 为每个订阅的股票创建并维护 OrderBook 实例
        self.order_books: Dict[str, OrderBook] = {}
        
        # 存储两次 snapshot 间隔之间的所有 orders 和 trades
        self.pending_orders: Dict[str, List[TransactionEntrustData]] = defaultdict(list)
        self.pending_trades: Dict[str, List[TransactionTradeData]] = defaultdict(list)
        
        # 存储上一次 snapshot 的时间
        self.last_snapshot_time: Dict[str, Tuple[int, int]] = {}

    def get_message_time(self, header: MarketDataHeader, market_data: Envelope) -> Optional[Tuple[int, int]]:
        """Extract date and time from market data message"""
        try:
            if header.msg_type == MessageType.SECU_DEPTH_MARKET_DATA:  # Tick data
                return (market_data.secu_depth_market_data.trade_date,
                       market_data.secu_depth_market_data.update_time)
            elif header.msg_type == MessageType.TRANSACTION_ENTRUST:  # Order data
                return (market_data.transaction_entrust_data.trade_date,
                       market_data.transaction_entrust_data.transact_time)
            elif header.msg_type == MessageType.TRANSACTION_TRADE:  # Trade data
                return (market_data.transaction_trade_data.trade_date,
                       market_data.transaction_trade_data.transact_time)
            elif header.msg_type == MessageType.SUBSCRIBE_OK:
                return None
            return None
        except Exception as e:
            self.logger.error(f"提取消息时间失败: {e}")
            return None

    def should_create_new_slice(self, msg_date: int, msg_time: int) -> bool:
        """
        判断是否应该创建新的时间片
        
        Args:
            msg_date: YYYYMMDD格式的日期
            msg_time: HHMMSSfff格式的时间
        
        Returns:
            bool: 是否应该创建新的时间片
        """
        # 如果还没有设置时间片起始时间
        if self.slice_start_time is None:
            return True

        # 如果是第一个时间片且当前消息时间超过了交易日开始时间，创建新的时间片
        if msg_time < self.trading_day_start_time:
            return False
            
        start_date, start_time = self.slice_start_time
        
        # 实盘模式：使用本地时钟
        if not self.is_warmup:
            current_time = int(datetime.datetime.now().strftime('%H%M%S%f')[:9])
        
            # 同一天内的时间差计算
            start_ms = time_to_milliseconds(start_time)
            msg_ms = time_to_milliseconds(current_time)
            time_diff = msg_ms - start_ms
            
            # 处理午夜零点跨天的特殊情况
            if time_diff < 0:
                time_diff += 24 * 3600 * 1000  # 加上一天的毫秒数
                
            return time_diff > self.data_interval_ms
            
        # 如果日期不同
        if msg_date != start_date:
            # 检查是否是连续的交易日
            start_date_obj = datetime.datetime.strptime(str(start_date), '%Y%m%d')
            msg_date_obj = datetime.datetime.strptime(str(msg_date), '%Y%m%d')
            if (msg_date_obj - start_date_obj).days == 1:
                # 如果是下一个交易日
                start_ms = time_to_milliseconds(start_time)
                msg_ms = time_to_milliseconds(msg_time)
                # 计算跨日时间差
                time_diff = (24 * 3600 * 1000 - start_ms) + msg_ms
                return time_diff > self.data_interval_ms
            else:
                # 如果不是连续的交易日，直接创建新片
                return True
        
        # 同一天内的时间差计算
        start_ms = time_to_milliseconds(start_time)
        msg_ms = time_to_milliseconds(msg_time)
        time_diff = msg_ms - start_ms
        
        # 处理午夜零点跨天的特殊情况
        if time_diff < 0:
            time_diff += 24 * 3600 * 1000  # 加上一天的毫秒数
            
        return time_diff > self.data_interval_ms

    def process_message(self, header: MarketDataHeader, market_data: Envelope):
        """Process a single market data message"""
        if header.msg_type == MessageType.SUBSCRIBE_OK:
            # 不论是否warm up, 始终认为后台行情服务是一直在运行的，也要给策略回复on_symbol            
            # 为新订阅的股票创建 OrderBook 实例
            symbol = market_data.rtn_subscription_success.symbol
            if not self.callback.is_subscribed(symbol):
                return

            if symbol not in self.order_books:
                try:
                    self.order_books[symbol] = OrderBook(symbol=symbol)
                    self.logger.info(f"为股票 {symbol} 创建 OrderBook 实例")
                except Exception as e:
                    self.logger.error(f"创建 OrderBook 实例失败: {e}")
            
            self.callback.on_symbol(symbol)
            return
        
        msg_time = self.get_message_time(header, market_data)
        if not msg_time:
            return
            
        msg_date, msg_timestamp = msg_time
        if msg_date == 0 or msg_timestamp == 0:
            msg_time = self.get_message_time(header, market_data)
            if not msg_time:
                return
            msg_date, msg_timestamp = msg_time
            if msg_date == 0 or msg_timestamp == 0:
                return
        
        # Initialize or check slice timing
        if self.should_create_new_slice(msg_date, msg_timestamp):
            if self.current_slice:
                self.push_slice()
                if self.is_warmup and self.bin_market_data_enable and self.bin_market_data_slow_play:   
                    # 等待一段时间，以便回放数据:   
                    self.logger.info(f"等待 {self.data_interval_ms / 1000.0} 秒以慢速回放数据")
                    time.sleep( self.data_interval_ms / 1000.0)
            
            if self.is_warmup:
                # 如果是第一个时间片且消息时间超过了交易日开始时间
                if not self.first_slice_created and msg_timestamp >= self.trading_day_start_time:
                    # 设置时间片起始时间为交易日开始时间
                    self.slice_start_time = (msg_date, self.trading_day_start_time)
                    self.first_slice_created = True
                elif self.first_slice_created:
                    # 计算下一个时间片的起始时间
                    start_date, start_time = self.slice_start_time
                    start_ms = time_to_milliseconds(start_time)
                    new_ms = start_ms + self.data_interval_ms
                    
                    # 处理跨天情况
                    if new_ms >= 24 * 3600 * 1000:
                        new_ms = new_ms % (24 * 3600 * 1000)
                        start_date_obj = datetime.datetime.strptime(str(start_date), '%Y%m%d')
                        new_date_obj = start_date_obj + datetime.timedelta(days=1)
                        new_date = int(new_date_obj.strftime('%Y%m%d'))
                        
                        hours = new_ms // (3600 * 1000)
                        minutes = (new_ms % (3600 * 1000)) // (60 * 1000)
                        seconds = (new_ms % (60 * 1000)) // 1000
                        milliseconds = new_ms % 1000
                        new_time = int(f"{hours:02d}{minutes:02d}{seconds:02d}{milliseconds:03d}")
                        
                        self.slice_start_time = (new_date, new_time)
                    else:
                        hours = new_ms // (3600 * 1000)
                        minutes = (new_ms % (3600 * 1000)) // (60 * 1000)
                        seconds = (new_ms % (60 * 1000)) // 1000
                        milliseconds = new_ms % 1000
                        new_time = int(f"{hours:02d}{minutes:02d}{seconds:02d}{milliseconds:03d}")
                        
                        self.slice_start_time = (start_date, new_time)
                else:
                    # 第一个时间片且消息时间小于交易日开始时间
                    self.slice_start_time = (msg_date, msg_timestamp)
            else:
                pass # push_slice中已经设置了slice_start_time
        
        # 处理消息并更新 OrderBook
        try:
            if header.msg_type == MessageType.SECU_DEPTH_MARKET_DATA:
                # 不处理 Tick 数据，使用自己构建的OrderBook生成的Snapshot作为Tick
                tick_data = market_data.secu_depth_market_data
                symbol = tick_data.symbol
                
                if not self.callback.is_subscribed(symbol):
                    return
                
                # 如果 OrderBook 不存在，创建一个
                if symbol not in self.order_books:
                    try:
                        self.order_books[symbol] = OrderBook(symbol=symbol)
                        self.logger.info(f"为股票 {symbol} 创建 OrderBook 实例")
                    except Exception as e:
                        self.logger.error(f"创建 OrderBook 实例失败: {e}")
                        return
                
                try:
                    # 更新 OrderBook
                    tick = {
                        "upper_limit_price": tick_data.upper_limit_price,
                        "lower_limit_price": tick_data.lower_limit_price,
                    }

                    self.order_books[symbol].update_by_tick([tick])
                except Exception as e:
                    self.logger.error(f"更新 OrderBook 快照数据失败: {e}")

            elif header.msg_type == MessageType.TRANSACTION_ENTRUST:
                # 处理委托数据
                order_data = market_data.transaction_entrust_data
                symbol = order_data.symbol
                
                if not self.callback.is_subscribed(symbol):
                    return
                
                # 设置 is_warmup 标志
                order_data.is_warmup = self.is_warmup and not self.bin_market_data_enable
                
                # 设置 biz_index
                if order_data.biz_index == 0:
                    order_data.biz_index = order_data.seq_no
                
                # 如果 OrderBook 不存在，创建一个
                if symbol not in self.order_books:
                    try:
                        self.order_books[symbol] = OrderBook(symbol=symbol)
                        self.logger.info(f"为股票 {symbol} 创建 OrderBook 实例")
                    except Exception as e:
                        self.logger.error(f"创建 OrderBook 实例失败: {e}")
                        return
                
                # 更新 OrderBook
                try:
                    # 构造委托数据
                    entrust = {
                        "action": "insert",
                        "seq_no": order_data.seq_no,
                        "order_id": order_data.order_id,
                        "symbol": order_data.symbol,
                        "price": order_data.order_price,
                        "volume": order_data.order_volume,
                        "order_side": Direction(order_data.order_side),
                        "order_type": order_data.order_type,
                        "trade_date": order_data.trade_date,
                        "transact_time": order_data.transact_time,
                    }
                    
                    # 更新 OrderBook
                    self.order_books[symbol].update_by_entrusts([entrust])
                    
                    # 将委托数据添加到 pending_orders
                    self.pending_orders[symbol].append(order_data)
                    
                    # 将委托数据添加到当前 slice
                    self.add_order(order_data)
                    
                except Exception as e:
                    self.logger.error(f"更新 OrderBook 委托数据失败: {e}")
                
            elif header.msg_type == MessageType.TRANSACTION_TRADE:
                # 处理成交数据
                trade_data = market_data.transaction_trade_data
                symbol = trade_data.symbol
                
                if not self.callback.is_subscribed(symbol):
                    return
                
                # 设置 is_warmup 标志
                trade_data.is_warmup = self.is_warmup and not self.bin_market_data_enable
                
                # 设置 biz_index
                if trade_data.biz_index == 0:
                    trade_data.biz_index = trade_data.seq_no
                
                # 如果 OrderBook 不存在，创建一个
                if symbol not in self.order_books:
                    try:
                        self.order_books[symbol] = OrderBook(symbol=symbol)
                        self.logger.info(f"为股票 {symbol} 创建 OrderBook 实例")
                    except Exception as e:
                        self.logger.error(f"创建 OrderBook 实例失败: {e}")
                
                # 更新 OrderBook
                try:
                    # 构造成交数据
                    trade = {
                        "trade_type": trade_data.trade_type,  # 66: 主动买, 83: 主动卖
                        "price": trade_data.trade_price,
                        "volume": trade_data.trade_volume,
                        "buy_order_no": trade_data.trade_buy_no,
                        "sell_order_no": trade_data.trade_sell_no,
                        "trans_flag": trade_data.trans_flag,
                        "trade_date": trade_data.trade_date,
                        "transact_time": trade_data.transact_time,
                    }
                    
                    # 更新 OrderBook
                    self.order_books[symbol].update_by_trades([trade])
                    
                    # 将成交数据添加到 pending_trades
                    self.pending_trades[symbol].append(trade_data)
                    
                    # 将成交数据添加到当前 slice
                    self.add_trade(trade_data)
                    
                except Exception as e:
                    self.logger.error(f"更新 OrderBook 成交数据失败: {e}")
        
        except Exception as e:
            self.logger.error(f"处理消息失败: {e}")
            
        self.last_msg_time = (msg_date, msg_timestamp)

    def push_slice(self):
        """Push current slice to callback and wait for processing"""
        if not self.current_slice or len(self.current_slice) == 0:
            return
        
        try:
            # 为每个股票获取 OrderBook 的 snapshot
            for symbol in list(self.current_slice.keys()):
                if symbol in self.order_books:
                    try:
                        # 获取 OrderBook 的 snapshot
                        previous_snapshot, current_snapshot = self.order_books[symbol].snapshot()
                        
                        # 将 snapshot 数据转换为 Tick 格式
                        if current_snapshot:
                            # 创建一个新的 SecuDepthMarketData 对象
                            tick = SecuDepthMarketData()
                            tick.symbol = symbol
                            # 如果启用了文件回放，则不再设定为 warm up
                            tick.is_warmup = self.is_warmup and not self.bin_market_data_enable
                            tick.last_price = current_snapshot.get("last_price", 0)
                            tick.upper_limit_price = current_snapshot.get("upper_limit_price", 0)
                            tick.lower_limit_price = current_snapshot.get("lower_limit_price", 0)
                            if tick.HighPrc == 0:
                                print("HighPrc is 0")
                            
                            # 设置买卖盘数据
                            # 对于repeated字段，需要使用extend方法而不是直接赋值
                            bid_prices = current_snapshot.get("bid_price", [])
                            ask_prices = current_snapshot.get("ask_price", [])
                            bid_volumes = current_snapshot.get("bid_volume", [])
                            ask_volumes = current_snapshot.get("ask_volume", [])
                            
                            # 清空原有数据
                            del tick.bid_price[:]
                            del tick.ask_price[:]
                            del tick.bid_volume[:]
                            del tick.ask_volume[:]
                            
                            # 使用extend方法添加数据
                            tick.bid_price.extend(bid_prices)
                            tick.ask_price.extend(ask_prices)
                            tick.bid_volume.extend(bid_volumes)
                            tick.ask_volume.extend(ask_volumes)
                            
                            # 设置其他必要字段
                            if self.last_msg_time:
                                tick.trade_date = self.last_msg_time[0]
                                tick.update_time = self.last_msg_time[1]
                            
                            # 更新当前 slice 的 Tick 数据
                            self.current_slice[symbol].Tick = tick
                            
                    except Exception as e:
                        self.logger.error(f"获取 OrderBook snapshot 失败: {symbol}, 错误: {e}")
            
            # 创建 Slice 对象
            slice = Slice(Ticks=dict(self.current_slice))
            
            # 调用回调函数
            self.on_data(slice)
            
            # 清空当前 slice
            self.current_slice.clear()
            
            # 清空 pending_orders 和 pending_trades
            self.pending_orders.clear()
            self.pending_trades.clear()
            
            # 根据模式设置新时间片的起始时间
            if not self.is_warmup:
                # 实盘模式：使用系统时间
                current_time = int(datetime.datetime.now().strftime('%H%M%S%f')[:9])
                current_date = int(datetime.datetime.now().strftime('%Y%m%d'))
                self.slice_start_time = (current_date, current_time)
            # 回测模式下，不在这里设置slice_start_time，而是在process_message中设置
            
        except Exception as e:
            self.logger.error(f"推送 Slice 失败: {e}")

    def check_timeout(self):
        """Check if current slice should be pushed due to timeout"""
        if not self.current_slice or not self.last_msg_time or not self.slice_start_time:
            return
            
        try:
            last_date, last_time = self.last_msg_time
            if not self.is_warmup:
                # 实盘模式：使用系统时间
                current_time = int(datetime.datetime.now().strftime('%H%M%S%f')[:9])
                current_date = int(datetime.datetime.now().strftime('%Y%m%d'))
            
                if self.should_create_new_slice(current_date, current_time):
                    self.push_slice()
        except Exception as e:
            self.logger.error(f"检查超时失败: {e}")

    def add_order(self, event: TransactionEntrustData):
        """Add order to current slice"""
        if not self.callback.is_subscribed(event.symbol):
            return
        
        try:
            self.current_slice[event.symbol].Symbol = event.symbol
            self.current_slice[event.symbol].Orders.append(event)
        except Exception as e:
            self.logger.error(f"添加委托数据到 Slice 失败: {e}")

    def add_trade(self, event: TransactionTradeData):
        """Add trade to current slice"""
        if not self.callback.is_subscribed(event.symbol):
            return
        
        try:
            self.current_slice[event.symbol].Symbol = event.symbol
            self.current_slice[event.symbol].Transactions.append(event)
        except Exception as e:
            self.logger.error(f"添加成交数据到 Slice 失败: {e}")

    def on_data(self, slice: Slice):
        """处理时间片数据并打印详细日志"""
        try:
            if slice.Ticks and len(slice.Ticks) > 0:
                # 获取字典中的第一个键
                first_symbol = next(iter(slice.Ticks))
                first_tick = slice.Ticks[first_symbol].Tick
                update_time = first_tick.update_time if first_tick else "无"
                self.logger.debug(f"\n{'='*100}\nTime Slice Data, update_time={update_time}\n{'='*100}")
            else:
                self.logger.debug(f"\n{'='*100}\nTime Slice Data, 无行情数据\n{'='*100}")
            self.callback.on_data(slice)
        except Exception as e:
            self.logger.error(f"处理 Slice 数据失败: {e}")

    def start(self):
        """Start monitoring market data"""
        self.running = True
        
        try:
            # 根据配置决定使用哪种方式读取行情数据
            if self.bin_market_data_enable == True and len(self.bin_market_data_files) > 0:
                # 使用bin_market_data配置的文件
                data_path = self.bin_market_data_files[0]  # 暂时只使用第一个文件
                self.logger.info(f"使用bin_market_data配置的文件: {data_path}")
            else:
                # 使用原有的data_dir逻辑
                data_path = os.path.join(self.data_dir, f"market_data_md_{self.counter_name}_{self.get_current_date()}.bin")
                self.logger.info(f"使用data_dir配置的文件: {data_path}")
            
            if not os.path.exists(data_path):
                self.logger.error(f"Market data files not found: {data_path}")
                return

            self.reader = MarketDataReader(data_path, self.logger)
            processed_msg_count = 0
            current_hist_count = self.reader.get_count()
            self.is_warmup = True if processed_msg_count < current_hist_count else False
            
            # Set up file monitoring
            self.observer = Observer()
            handler = MarketDataFileHandler(self.logger, self.reader)
            self.observer.schedule(handler, self.data_dir, recursive=False)
            self.observer.start()
            
            self.logger.info("Market data monitor started...")
            
            while self.running:
                try:
                    result = self.reader.read_next()
                    if result:
                        header, market_data = result
                        processed_msg_count += 1
                        self.is_warmup = True if processed_msg_count <= current_hist_count else False
                        self.process_message(header, market_data)
                    else:
                        # No new data, check timeout and wait
                        self.check_timeout()
                        time.sleep(0.1)
                except Exception as e:
                    self.logger.error(f"处理行情数据失败: {e}")
                    time.sleep(0.1)
        except Exception as e:
            self.logger.error(f"启动行情监控失败: {e}")
        finally:
            self.stop()

    def get_current_date(self) -> str:
        return datetime.datetime.now().strftime('%Y%m%d')

    def stop(self):
        """停止监控"""
        try:
            self.running = False
            if self.observer:
                self.observer.stop()
                self.observer.join()
            if self.reader:
                self.reader.close()
            
            # 清理资源
            self.order_books.clear()
            self.pending_orders.clear()
            self.pending_trades.clear()
            
            self.logger.info("Market data monitor stopped.")
        except Exception as e:
            self.logger.error(f"停止行情监控失败: {e}")