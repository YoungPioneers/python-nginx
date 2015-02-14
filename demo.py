#!/usr/bin/env python
# encoding: utf-8

# just 4 test
if "__main__" == __name__:
    path = r'./default'
    data = Parser().loadf(path)
    # print data

    config = Config(path)
    # print config.find(('upstream', 'http')).toggle('server', '8000').gen_config()
    # print config.find('http', 'server').append("addtional", "string").remove("additional", "string").gen_config()
    # config.savef(r'./default.result')
