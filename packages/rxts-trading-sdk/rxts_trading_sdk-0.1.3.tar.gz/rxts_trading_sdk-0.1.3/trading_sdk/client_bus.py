# RXTSCOPYRIGHT_START
# copyright Brent Jiang, 2024-10-20.
# all rights reserved.
# RXTSCOPYRIGHT_END

# client_bus.py
import threading
from .socket_transport import SocketTransportBase
from .callbacks import BaseCallback
from global_pb2 import Envelope
        
class ClientBus:
    def __init__(self, logger, config, handler):
        self.logger = logger
        self.config = config
        self.transport = SocketTransportBase(logger, self.config.bus.host, self.config.bus.port, is_server=False)
        self.handler = handler
        self.message_id_counter = 1
        self.lock = threading.Lock()

    def on_message_received(self, envelope: Envelope):
        """
        接收到消息后的回调，委托给消息处理器。
        """
        if not envelope.HasField("heartbeat"):  # 不记录心跳日志
            self.logger.info(f"收到 Envelope: {envelope}")
        self.handler.handle_message(envelope)

    def generate_message_id(self) -> int:
        with self.lock:
            msg_id = self.message_id_counter
            self.message_id_counter += 1
            return msg_id

    def initialize(self):
        self.transport.initialize()

    def start(self):
        self.transport.start_receiving(self.on_message_received)
        self.logger.info("ClientBus已启动并开始接收消息")

    def stop(self):
        self.transport.shutdown()
        self.logger.info("ClientBus已停止")

    def publish(self, envelope: Envelope):
        """
        发送Envelope消息。
        """
        self.transport.send(envelope)
        if not envelope.HasField("heartbeat"):  # 不记录心跳日志
            self.logger.debug(f"发送Envelope: {envelope}")

    def status(self):
        return f"{self.transport.status()}"