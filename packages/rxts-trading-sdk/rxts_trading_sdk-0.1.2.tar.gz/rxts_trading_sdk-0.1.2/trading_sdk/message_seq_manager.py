# RXTSCOPYRIGHT_START
# copyright Brent Jiang, 2024-12-29.
# all rights reserved.
# RXTSCOPYRIGHT_END

# encoding: utf-8
import os
import json
from datetime import datetime

class MessageSeqManager:
    def __init__(self, persist_dir):
        """
        初始化函数，用于设置保存消息序号的目录

        :param persist_dir: 磁盘上保存消息序号文件的目录路径
        """
        self.persist_dir = persist_dir
        if not os.path.exists(self.persist_dir):
            os.makedirs(self.persist_dir)

    def _get_seq_file_path(self, date, seq_type):
        """
        根据日期和消息序号类型获取对应的序号保存文件路径

        :param date: 日期，格式为datetime.date类型
        :param seq_type: 消息序号类型，字符串类型
        :return: 对应序号保存文件的完整路径
        """
        date_str = date.strftime('%Y-%m-%d')
        file_name = f"{seq_type}_{date_str}.json"
        return os.path.join(self.persist_dir, file_name)

    def _load_seq(self, date, seq_type):
        """
        从本地文件加载指定日期和消息序号类型的消息序号

        :param date: 日期，格式为datetime.date类型
        :param seq_type: 消息序号类型，字符串类型
        :return: 返回加载的消息序号，如果文件不存在则返回0
        """
        file_path = self._get_seq_file_path(date, seq_type)
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                data = json.load(file)
                return data.get('seq', 0)
        return 0

    def _save_seq(self, date, seq_type, seq):
        """
        将指定日期和消息序号类型的消息序号保存到本地文件

        :param date: 日期，格式为datetime.date类型
        :param seq_type: 消息序号类型，字符串类型
        :param seq: 要保存的消息序号
        """
        file_path = self._get_seq_file_path(date, seq_type)
        data = {'seq': seq}
        with open(file_path, 'w') as file:
            json.dump(data, file)

    def get_next_seq(self, seq_type):
        """
        获取指定消息序号类型的下一个消息序号，考虑程序重启情况

        :param seq_type: 消息序号类型，字符串类型
        :return: 下一个消息序号
        """
        today = datetime.now().date()
        current_seq = self._load_seq(today, seq_type)
        next_seq = current_seq + 1
        self._save_seq(today, seq_type, next_seq)
        return next_seq