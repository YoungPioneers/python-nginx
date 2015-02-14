#!/usr/bin/env python
# encoding: utf-8
#
#  Author:   huangjunwei@youmi.net
#  Time:     Fri 16 Jan 2015 05:23:13 PM HKT
#  File:     nginx/parser.py
#  Desc:
#


class Parser(object):
    # block -> dict{ "name": "upstream", "param": "http", "value": [ block or items ], "type": "block" }
    # item  -> dict{ "name": "server", "valie": [ blocks or items ], "type": "item" }

    """
    Attributes:
        _i(int): current parser position
        _config(str): configuration str
        _length(str): length of file
        _data(list): structured configuration data
        _off_char(str): indent char
    """
    def __init__(self, offset_char=' '):
	"""initializer
        Args:
            offset_char(str): indent char
        Returns:
            None
        Raises:
            None
        """
        self._i = 0
        self._config = ''
        self._length = 0
        self._data = []
        # tab or whitespace ~
        self._off_char = offset_char

    def __call__(self):
        return self.gen_config()

    def load(self, config):
	"""str configuration loader
        Args:
            config(str): configuration str
        Returns:
            list: structured configuration data
        Raises:
            None
        """
        self._config = config
        self._length = len(config) - 1
        self._i = 0
        return self.parse_block()

    def loadf(self, filename):
        conf = ''
        with open(filename, 'r') as f:
            conf = f.read()
        return self.load(conf)

    # 块解析器
    def parse_block(self):
	"""block parser
        Args:
            None
        Returns:
            list: structured configuration data
        Raises:
            None
        """
        data = []
        param_name = None
        param_value = None
        buf = ''
        while self._i < self._length:
            # 换行符可能block换行或item之间的换行
            if '\n' == self._config[self._i]:
                if buf and param_name:
                    if param_value is None:
                        param_value = []
                    param_value.append(buf.strip())
                    buf = ''
            elif ' ' == self._config[self._i]:
                if not param_name and len(buf.strip()) > 0:
                    param_name = buf.strip()
                    buf = ''
                else:
                    buf += self._config[self._i]
            elif ';' == self._config[self._i]:
                if isinstance(param_value, list):
                    # tag value
                    param_value.append(buf.strip())
                else:
                    # tag value
                    param_value = buf.strip()
                # tag
                data.append({'name': param_name, 'value': param_value.split(' '), 'type': 'item'})
                param_name = None
                param_value = None
                buf = ''
            elif '{' == self._config[self._i]:
                self._i += 1
                block = self.parse_block()
                data.append({'name': param_name, 'param': buf.strip(), 'value': block, 'type': 'block'})
                param_name = None
                param_value = None
                buf = ''
            elif '}' == self._config[self._i]:
                self._i += 1
                return data
            elif '#' == self._config[self._i]:  # skip comments
                # 遇到#时，忽略下一字符为空格的注释
                if ' ' == self._config[self._i + 1]:
                    while self._i < self._length and '\n' != self._config[self._i]:
                        self._i += 1
                else:
                    buf += self._config[self._i]
            else:
                buf += self._config[self._i]
            self._i += 1
        return data
