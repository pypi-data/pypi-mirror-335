# RXTSCOPYRIGHT_START
# copyright Brent Jiang, 2024-10-20.
# all rights reserved.
# RXTSCOPYRIGHT_END

# socket_transport.py
import socket
import struct
import threading
import logging
import time
from google.protobuf.message import Message
from global_pb2 import Envelope

class SocketTransportBase:
    HEADER_LENGTH = 4  # 4字节长度前缀
    HEARTBEAT_INTERVAL = 10  # 心跳间隔(秒)
    HEARTBEAT_TIMEOUT = 30   # 心跳超时(秒)，必须大于HEARTBEAT_INTERVAL。因为代码逻辑是比较最后一次心跳的时间，而不是等待心跳的回复
    RECONNECT_INTERVAL = 5   # 重连间隔(秒)

    def __init__(self, logger, host: str, port: int, is_server: bool):
        self.logger = logger
        self.host = host
        self.port = port
        self.is_server = is_server
        self.socket = None
        self.running = False
        self.message_callback = None
        self.client_sockets = {}  # 服务器模式下的多个客户端 {socket: last_heartbeat_time}
        self.lock = threading.Lock()
        self.last_heartbeat_time = 0
        self.last_heartbeat_sent_time = 0  # 新增：上次发送心跳的时间
        self.reconnecting = False
        
    def initialize(self):
        self._create_socket()
        if self.is_server:
            self.socket.bind((self.host, self.port))
            self.socket.listen()
            self.logger.info(f"SocketTransportBase (Server) listening on {self.host}:{self.port}")
        else:
            self._connect()

    def _create_socket(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)

    def _connect(self):
        try:
            self.socket.connect((self.host, self.port))
            self.logger.info(f"SocketTransportBase (Client) connected to {self.host}:{self.port}")
            self.last_heartbeat_time = time.time()
            self.last_heartbeat_sent_time = time.time()
            return True
        except Exception as e:
            self.logger.error(f"连接失败: {e}, {self.RECONNECT_INTERVAL}秒后重试")
            time.sleep(self.RECONNECT_INTERVAL)
        return False

    def start_receiving(self, callback):
        self.message_callback = callback
        self.running = True
        if self.is_server:
            threading.Thread(target=self.accept_clients, daemon=True).start()
            threading.Thread(target=self.check_client_heartbeats, daemon=True).start()
            threading.Thread(target=self.send_server_heartbeats, daemon=True).start()  # 新增：服务器端心跳
        else:
            threading.Thread(target=self.receive_messages, daemon=True).start()
            threading.Thread(target=self.send_client_heartbeat, daemon=True).start()  # 重命名：客户端心跳
            threading.Thread(target=self.check_connection, daemon=True).start()

    def accept_clients(self):
        self.logger.info("服务器开始接受客户端连接")
        while self.running:
            try:
                client_sock, addr = self.socket.accept()
                self.logger.info(f"接受到来自{addr}的客户端连接")
                with self.lock:
                    self.client_sockets[client_sock] = time.time()
                threading.Thread(target=self.receive_messages, args=(client_sock,), daemon=True).start()
            except Exception as e:
                self.logger.error(f"接受客户端时发生错误: {e}")
                break

    def check_connection(self):
        while self.running:
            if not self.is_server:
                current_time = time.time()
                if current_time - self.last_heartbeat_time > self.HEARTBEAT_TIMEOUT:
                    #self.logger.warning("心跳超时")
                    self.logger.warning("心跳超时，开始重连")
                    self.reconnect()
            time.sleep(5)

    def check_client_heartbeats(self):
        while self.running:
            if self.is_server:
                current_time = time.time()
                with self.lock:
                    dead_clients = []
                    for client_sock, last_heartbeat in self.client_sockets.items():
                        if current_time - last_heartbeat > self.HEARTBEAT_TIMEOUT:
                            dead_clients.append(client_sock)
                    
                    for client_sock in dead_clients:
                        self.logger.warning(f"客户端 {client_sock.getpeername()} 心跳超时，关闭连接")
                        client_sock.close()
                        del self.client_sockets[client_sock]
            time.sleep(1)

    def reconnect(self):
        if self.reconnecting:
            return
        
        self.reconnecting = True
        self.logger.info("开始重连...")
        
        try:
            self.socket.close()
        except:
            pass
            
        while self.running and self.reconnecting:
            try:
                self._create_socket()
                if self._connect():
                    self.reconnecting = False
                    threading.Thread(target=self.receive_messages, daemon=True).start()
                    self.logger.info("重连成功")
                    break
            except Exception as e:
                self.logger.error(f"重连失败: {e}")
                time.sleep(self.RECONNECT_INTERVAL)

    def send(self, envelope: Envelope, client_sock: socket.socket = None):
        if self.socket is None:
            self.logger.error(f"Bus连接状态：未运行")
            return
        
        serialized = envelope.SerializeToString()
        message_length = len(serialized)
        header = struct.pack('>I', message_length)  # 大端
        full_message = header + serialized
        with self.lock:
            try:
                if self.is_server:
                    targets = self.client_sockets.keys() if client_sock is None else [client_sock]
                    for sock in targets:
                        sock.sendall(full_message)
                else:
                    self.socket.sendall(full_message)
                self.logger.debug(f"发送Envelope: {envelope}")
            except Exception as e:
                self.logger.error(f"发送消息时出错: {e}")
                if not self.is_server:
                    self.reconnect()

    def send_server_heartbeats(self):
        """服务器向所有客户端定期发送心跳"""
        while self.running:
            try:
                current_time = time.time()
                if current_time - self.last_heartbeat_sent_time >= self.HEARTBEAT_INTERVAL:
                    envelope = Envelope()
                    envelope.heartbeat.timestamp = int(current_time)
                    self.send(envelope)
                    self.last_heartbeat_sent_time = current_time
            except Exception as e:
                self.logger.error(f"服务器发送心跳失败: {e}")
            time.sleep(1)  # 检查间隔

    def send_client_heartbeat(self):
        """客户端定期发送心跳"""
        while self.running:
            try:
                current_time = time.time()
                if current_time - self.last_heartbeat_sent_time >= self.HEARTBEAT_INTERVAL:
                    envelope = Envelope()
                    envelope.heartbeat.timestamp = int(current_time)
                    self.send(envelope)
                    self.last_heartbeat_sent_time = current_time
            except Exception as e:
                self.logger.error(f"客户端发送心跳失败: {e}")
            time.sleep(1)  # 检查间隔

    def receive_messages(self, sock=None):
        sock = sock or self.socket
        buffer = b''
        while self.running:
            try:
                while len(buffer) < self.HEADER_LENGTH:
                    data = sock.recv(self.HEADER_LENGTH - len(buffer))
                    if not data:
                        self.logger.info("连接关闭")
                        if self.is_server:
                            with self.lock:
                                if sock in self.client_sockets:
                                    del self.client_sockets[sock]
                        else:
                            self.reconnect()
                        return
                    buffer += data

                msg_length = struct.unpack('>I', buffer[:self.HEADER_LENGTH])[0]
                buffer = buffer[self.HEADER_LENGTH:]

                while len(buffer) < msg_length:
                    data = sock.recv(msg_length - len(buffer))
                    if not data:
                        self.logger.info("连接关闭")
                        if self.is_server:
                            with self.lock:
                                if sock in self.client_sockets:
                                    del self.client_sockets[sock]
                        else:
                            self.reconnect()
                        return
                    buffer += data

                message_data = buffer[:msg_length]
                buffer = buffer[msg_length:]
                envelope = Envelope()
                envelope.ParseFromString(message_data)
                
                # 处理心跳消息
                current_time = time.time()
                if envelope.HasField("heartbeat"):
                    if self.is_server:
                        with self.lock:
                            self.client_sockets[sock] = current_time
                    else:
                        self.last_heartbeat_time = current_time
                    self.logger.debug(f"收到心跳消息: timestamp={envelope.heartbeat.timestamp}")
                else:
                    self.logger.debug(f"接收到Envelope: {envelope}")
                    if self.message_callback:
                        self.message_callback(envelope)

            except Exception as e:
                self.logger.error(f"接收消息时出错: {e}")
                if self.is_server:
                    with self.lock:
                        if sock in self.client_sockets:
                            del self.client_sockets[sock]
                else:
                    self.reconnect()
                break

    def shutdown(self):
        self.running = False
        try:
            if self.socket:
                self.socket.close()
            with self.lock:
                for sock in self.client_sockets:
                    sock.close()
                self.client_sockets.clear()
            self.logger.info("SocketTransport已关闭")
        except Exception as e:
            self.logger.error(f"关闭Socket时出错: {e}")
            
    def status(self):
        if self.running:
            return "运行中"
        else:
            return "未运行"