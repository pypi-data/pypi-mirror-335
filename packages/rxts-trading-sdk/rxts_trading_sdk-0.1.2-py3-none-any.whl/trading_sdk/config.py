# trading_sdk/config.py
import os
import yaml
from typing import List, Optional

class BusConfig:
    def __init__(self, host: str, port: int, subscribe_topics: List[str]):
        self.host = host
        self.port = port
        self.subscribe_topics = subscribe_topics

class TradeConfig:
    def __init__(self, minimum_volume: int, maximum_volume: int, seqnum_persist_dir: str):
        self.minimum_volume = minimum_volume
        self.maximum_volume = maximum_volume
        self.seqnum_persist_dir = seqnum_persist_dir

class MarketConfig:
    def __init__(self, data_interval_ms: int, data_dir: str, 
                 bin_market_data_enable: bool = False,
                 bin_market_data_slow_play: bool = True,
                 bin_market_data_files: List[str] = None):
        self.data_interval_ms = data_interval_ms
        self.data_dir = data_dir
        self.bin_market_data_enable = bin_market_data_enable
        self.bin_market_data_slow_play = bin_market_data_slow_play
        self.bin_market_data_files = bin_market_data_files if bin_market_data_files else []

class LogConfig:
    def __init__(self, path: str, level: str, max_file_size: int, max_files: int):
        self.path = path
        self.level = level
        self.max_file_size = max_file_size
        self.max_files = max_files

class ExtraConfig:
    def __init__(self, local_ip: str, custom_param: str, inmemdb_ip: str, inmemdb_port: int):
        self.local_ip = local_ip
        self.custom_param = custom_param
        self.inmemdb_ip = "127.0.0.1"
        self.inmemdb_port = 13306

class Config:
    def __init__(self,
                 strategy_env: str,
                 bus: BusConfig,
                 trade: TradeConfig,
                 market: MarketConfig,
                 log: LogConfig,
                 extra: ExtraConfig,
                 subscriptions: Optional[List[str]] = None):
        self.strategy_env = strategy_env
        self.bus = bus
        self.trade = trade
        self.market = market
        self.log = log
        self.extra = extra
        self.subscriptions = subscriptions if subscriptions is not None else []

def load_config(file_path: str) -> Config:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"配置文件未找到: {os.path.abspath(file_path)}")

    with open(file_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    strategy_env = data.get('strategy', {}).get('env', 'mock')
    
    bus_data = data.get('bus', {})
    bus = BusConfig(
        host=bus_data.get('host', '127.0.0.1'),
        port=bus_data.get('port', 7710),
        subscribe_topics=bus_data.get('subscribe_topics', [])
    )

    trade_data = data.get('trade', {})
    trade = TradeConfig(
        minimum_volume=trade_data.get('minimum_volume', 1000),
        maximum_volume=trade_data.get('maximum_volume', 10000),
        seqnum_persist_dir=trade_data.get('seqnum_persist_dir', "./data/seqnum")
    )

    market_data = data.get('market', {})
    bin_market_data = market_data.get('bin_market_data', {})
    market = MarketConfig(
        # 表示一个slice的推送间隔时间
        data_interval_ms=market_data.get('data_interval_ms', 5000),
        data_dir=market_data.get('data_dir', "./data/md"),
        bin_market_data_enable=bin_market_data.get('enable', False),
        bin_market_data_slow_play=bin_market_data.get('slow_play', True),
        bin_market_data_files=bin_market_data.get('files', [])
    )

    log_data = data.get('log', {})
    log = LogConfig(
        path=log_data.get('path', './log/'),
        level=log_data.get('level', 'INFO'),
        max_file_size=log_data.get('max_file_size', 104857600),
        max_files=log_data.get('max_files', 10)
    )

    extra_data = data.get('extra', {})
    extra = ExtraConfig(
        local_ip=extra_data.get('local_ip', '192.168.1.100'),
        custom_param=extra_data.get('custom_param', 'value1'),
        inmemdb_ip=extra_data.get('inmemdb_ip', '127.0.0.1'),
        inmemdb_port=extra_data.get('inmemdb_port', '13306')
    )

    subscriptions = data.get('subscriptions', [])  # 加载 subscriptions 字段

    return Config(
        strategy_env=strategy_env,
        bus=bus,
        trade=trade,
        market=market,
        log=log,
        extra=extra,
        subscriptions=subscriptions
    )

def save_config(file_path: str, config: Config):
    """保存配置到 YAML 文件"""
    data = {
        'strategy': {
            'env': config.strategy_env
        },
        'bus': {
            'host': config.bus.host,
            'port': config.bus.port,
            'subscribe_topics': config.bus.subscribe_topics
        },
        'trade': {
            'minimum_volume': config.trade.minimum_volume,
            'maximum_volume': config.trade.maximum_volume,
            'seqnum_persist_dir': config.trade.seqnum_persist_dir
        },
        'market': {
            'data_interval_ms': config.market.data_interval_ms,
            'data_dir': config.market.data_dir,
            'bin_market_data': {
                'enable': config.market.bin_market_data_enable,
                'slow_play': config.market.bin_market_data_slow_play,
                'files': config.market.bin_market_data_files
            }
        },
        'log': {
            'path': config.log.path,
            'level': config.log.level,
            'max_file_size': config.log.max_file_size,
            'max_files': config.log.max_files
        },
        'extra': {
            'local_ip': config.extra.local_ip,
            'custom_param': config.extra.custom_param,
            'inmemdb_ip': config.extra.inmemdb_ip,
            'inmemdb_port': config.extra.inmemdb_port
        },
        'subscriptions': config.subscriptions  # 保存 subscriptions 字段
    }

    with open(file_path, 'w', encoding='utf-8') as f:
        yaml.safe_dump(data, f, default_flow_style=False)