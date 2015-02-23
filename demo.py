#!/usr/bin/env python
# encoding: utf-8

from parser import Parser
from config import Config

# just 4 test
if "__main__" == __name__:
    # 配置文件路径
    path = r'./default'

    # 结构化后的配置内容
    data = Parser().loadf(path)
    # print data

    # 对配置内容的操作通过 config 实例
    config = Config(path)

    # 一些操作示例
    # print config.find(('upstream', 'http')).toggle('server', '8000').gen_config()
    # print config.find('http', 'server').append("addtional", "string").remove("additional", "string").gen_config()

    # 保存配置内容至制定文件
    # config.savef(r'./default.result')
