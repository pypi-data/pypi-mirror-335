# Initialize the trading_sdk package

# 在导入其他模块前，先处理 market_data_pb2 模块
import sys
import os

# 获取当前包的路径
package_dir = os.path.dirname(__file__)
if package_dir not in sys.path:
    sys.path.insert(0, package_dir)

# 导入所有需要的模块，使它们可以通过包路径访问
from . import global_pb2
from . import market_data_pb2
from . import callbacks
from . import config
from . import logger
from . import main
from . import market_data_monitor

# 可选：导出常用的类和函数，使用户可以直接从包导入
from .callbacks import BaseCallback, Slice, Snapshot
from .config import Config, load_config
from .main import SDKMain
from .logger import setup_logger
from .global_pb2 import (
    RspStkOrderField, 
    RspStkCancelOrderField, 
    RtnStkOrderField,
    RtnStkOrderFillField, 
    RtnStkOrderConfirmField, 
    RspStkQryExpendableFundExField, 
    RspStkQryExpendableSharesExField,
    OrdSideEnum, OrdTypeEnum, 
    ExecTypeEnum, OrdStatusEnum, 
    TimeInForceEnum
)
from .market_data_pb2 import (
    RtnMarketOpenField, 
    RtnMarketCloseField, 
    RtnSubscriptionSuccessField, 
    SecuDepthMarketData, 
    TransactionEntrustData,
    TransactionTradeData,
    MessageTypeEnum, DirectionEnum, 
    TrdTypeEnum, OrdActionTypeEnum, TransFlagEnum
)
from .market_data_monitor import (
    MarketDataMonitor,
    MarketDataFileHandler
)