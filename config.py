#!/usr/bin/env python
# encoding: utf-8
#
#  Author:   huangjunwei@youmi.net
#  Time:     Fri 16 Jan 2015 05:21:25 PM HKT
#  File:     nginx/config.py
#  Desc:
#

from parser import Parser
import re


class Config(object):
    """
        Attributes:
            _data(list): raw structured data of configuration
            _position(list): current root
    """
    def __init__(self, data):
        """initializer
        Args:
            data(list/str): raw structured data of configuration or just a file path
        Returns:
            None
        Raises:
            None
        """
        if type(data) is str:
            # if data is just a file path
            self._data = Parser().loadf(data)
        else:
            # if data is raw structured data
            self._data = data
        self._position = []

    def _get(self, item_arr, data=[]):
        """get an element
        Args:
            item_arr(list): an element finder, which is a list of tuples or strs
            data(list): data to be search by the element finder
        Returns:
            dict: the element found if existed, None if not
        Raises:
            None
        """
        if [] == item_arr:
            return []

        if [] == data:
            data = self._data

        if type(item_arr) in [str, tuple]:
            item = item_arr
        if isinstance(item_arr, list):
            if 1 == len(item_arr):
                item = item_arr[0]
            else:
                element = item_arr[0]
                if isinstance(element, tuple):
                    # only name, like http { ... }
                    if 1 == len(element):
                        element = (element[0], '')
                    for data_elem in data:
                        if 'block' == data_elem['type']:
                            if (data_elem['name'], data_elem['param']) == element:
                                return self._get(item_arr[1:], self._get_value(data_elem))
        else:
            item = item_arr

        if isinstance(item, str):
            for elem in data:
                if item == elem['name']:
                    return elem

        elif isinstance(item, tuple):
            if 1 == len(item):
                item = (item[0], '')
            for elem in data:
                if 'block' == elem['type'] and (elem['name'], elem['param']) == item:
                    return elem

        return None

    def _get_value(self, data):
        """get an element value
        Args:
            data(list): data to get value
        Returns:
            list: value
        Raises:
            None
        """
        return data['value']

    def _get_name(self, data):
        """get an element name
        Args:
            data(list): data to get name
        Returns:
            str: name
        Raises:
            None
        """
        return data['name']

    def _set(self, item_arr, value=None, param=None, name=None):
        """element setter
        steps:
            1. get its parent
            2. set via its parent's value

        Args:
            item_arr(list): an element finder, which is a list of tuples or strs
            value(list): value to be set
            param(str): param to be set
            name(str): name to be set
        Returns:
            None
        Raises:
            KeyError: no element can be found by the element finder
        """
        # find its parent first
        if 1 == len(item_arr):
            parent = self._data
        else:
            parent = self._get_value(self._get(item_arr[0:-1]))

        elem = item_arr[-1]

        if parent is None:
            raise KeyError('No such block.')

        # set it~
        if isinstance(elem, str):
            for i, child in enumerate(parent):
                if 'item' == child['type']:
                    if value is not None and isinstance(value, str):
                        if isinstance(value, str):
                            child['value'] = [value]
                        else:
                            child['value'] = value
                    if name is not None:
                        child['name'] = name

        elif isinstance(elem, tuple):
            # modifying block
            for i, child in enumerate(parent):
                if 'block' == child['type']:
                    if elem == (child['name'], child['param']):
                        if value is not None and isinstance(value, list):
                            parent[i]['value'] = value
                        if param is not None and isinstance(param, str):
                            parent[i]['param'] = param
                        if name is not None and isinstance(name, str):
                            parent[i]['name'] = name

    def _append(self, item, root=[], position=None):
        """element appender
        Args:
            item(dict): item or block wanted to be added
            root(list): its parent, will be _data if not given
            position(int): index of its parent value to be added
        Returns:
            None
        Raises:
            AttributeError: the root is None
        """
        if [] == root:
            root = self._data
        elif root is None:
            raise AttributeError('Root element is None')
        if position:
            root.insert(position, item)
        else:
            root.append(item)

    def _remove(self, name, reg, root=[]):
        """element remover
        tips:
            just 4 items now
        Args:
            name(str): element name
            reg(str): regular expression to find specific item with value matched it
            root(list): its parent, will be _data if not given
        Returns:
            None
        Raises:
            AttributeError: the root is None
        """
        if [] == root:
            root = self._data
        elif root is None:
            raise AttributeError('Root element is None')

        for i, item in enumerate(root):
            if 'item' == item['type'] and re.search(reg, item['value']):
                for value in item['value']:
                    if re.search(reg, value):
                        del(root[i])
                        break
    def _parent(self, item_arr=[]):
        """parent finder
        Args:
            item_arr(list): an element finder, which is a list of tuples or strs,
                            will be _position if not given
        Returns:
            list: its parent
        Raises:
            None
        """
        if [] == item_arr:
            if [] == self._position:
                return []
            else:
                return self._get(self._position[0:-1])
        else:
            return self._get(item_arr[0:-1])

    def _toggle(self, item_arr, reg):
        """comment or uncomment an item, through its parent
        Args:
            item_arr(list): an element finder, which is a list of tuples or strs
            reg(str): regular expression to find specific item with value matched it
        Returns:
            None
        Raises:
            None
        """
        parent_id = item_arr[0:-1]
        this_name = item_arr[-1]
        parent = self._get(parent_id)
        parent_value = self._get_value(parent)
        new_value = []

        for child in parent_value:
            if 'item' == child['type']:
                n = child['name']
                v = child['value']

                if this_name in n:
                    for value in v:
                        if re.search(reg, value):
                            if '#' == n[0]:
                                # to take effect
                                n = n[1:]
                            else:
                                # to lose effect
                                n = "%s%s" % ('#', n)
                            break
                new_row = {'name': n, 'value': v, 'type': 'item'}
                new_value.append(new_row)
            else:
                new_value.append(child)
        self._set(parent_id, value=new_value)

    def _gen_block(self, blocks, offset):
        """block generator recursion
        Args:
            blocks(list): a list of blocks or items configuration
            offset(str): ident char
        Returns:
            str: configuration str with the given list
        Raises:
            None
        """
        subrez = ''
        block_name = None
        block_param = ''
        for i, block in enumerate(blocks):
            if 'item' == block['type']:
                subrez += self.off_char * offset + '%s %s;\n' % (block['name'], ' '.join(block['value']))

            elif 'block' == block['type']:
                block_value = self._gen_block(block['value'], offset + 4)
                if block['param']:
                    param = block['param'] + ' '
                else:
                    param = ''
                if '' != subrez:
                    subrez += '\n'
                subrez += '%(offset)s%(name)s %(param)s{\n%(data)s%(offset)s}\n' % {
                    'offset': self.off_char * offset, 'name': block['name'], 'data': block_value,
                    'param': param}

            elif isinstance(block, str):
                if 0 == i:
                    subrez += '%s\n' % block
                else:
                    subrez += '%s%s\n' % (self.off_char * offset, block)

        if block_name:
            return '%(offset)s%(name)s %(param)s{\n%(data)s%(offset)s}\n' % {
                'offset': self.off_char * offset, 'name': block_name, 'data': subrez,
                'param': block_param}
        else:
            return subrez

    ########################################################
    #                  可供外部访问的函数                  #
    ########################################################

    # -- just 4 test --
    @property
    def data(self):
        return self._data

    @property
    def position(self):
        return self._position
    # -- just 4 test --

    def gen_config(self, offset_char=' '):
        """change _data to be in readable configuration file form
        Args:
            offset_char(str): indent char
        Returns:
            str: configuration str
        Raises:
            None
        """
        self.off_char = offset_char
        return self._gen_block(self._data, 0)

    def savef(self, filename):
        """save configuration into specific file
        Args:
            filename: dest file
        Returns:
            None
        Raises:
            None
        """
        with open(filename, 'w') as f:
            conf = self.gen_config()
            f.write(conf)

    def find(self, *conditions):
        """find the first element you wanted by conditions and set _position
        Args:
            conditions(list): item_arr, element finder
        Returns:
            self: instance itself
        Raises:
            None
        Usages:
            find(('http',), ('server', ), ('location', 'doc'), 'alias')

        """
        # form item_arr
        item_arr = []
        end = len(conditions) - 1
        for index, condition in enumerate(conditions):
            if type(condition) is tuple:
                item_arr.append(condition)
            elif type(condition) is str and index == end:
                item_arr.append((condition, ))
            else:
                item_arr.append((condition, ))

        self._position = self._position[0:-1] + item_arr

        return self

    def append(self, name, value, index=None):
        """add an new item to the current position
        Args:
            name(str): item name
            value(list): item value
        Returns:
            self: instance itself
        Raises:
            None
        """
        root = self._get_value(self._get(self._position))
        item = (name, value)
        self._append(item, root, index)
        return self

    def remove(self, name, reg='.*'):
        """remove items which values match given regular expression
        Args:
            name(str): item name
            reg(str): a regular expression str
        Retruns:
            None
        Raises:
            None
        """
        root = self._get_value(self._get(self._position))
        self._remove(name, reg, root)
        return self

    def toggle(self, name, reg='.*'):
        """comment or uncomment item with name and regex matched
        Args:
            name(str): item name
            reg(str): regular expression
        Returns:
            self: instance itself
        Raises:
            None
        """
        item_arr = [p for p in self._position]
        item_arr.append(name)
        self._toggle(item_arr, reg)
        return self

    # todo
    def parent(self):
        pass

    def where(self, name, reg):
        pass

    def search(selfi, item_arr):
        pass
