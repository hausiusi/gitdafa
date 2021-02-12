#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import abc


class TableInterface(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'get_table_row') and
                callable(subclass.get_table_row) and
                hasattr(subclass, 'get_table_headers') and
                callable(subclass.get_table_headers) or
                NotImplemented)

    @abc.abstractmethod
    def get_table_row(self) -> []:
        """Gets one row of the table related to this object"""
        raise NotImplementedError

    @abc.abstractmethod
    def get_table_headers(self) -> []:
        """Gets table header names list suitable to all this type of objects"""
        raise NotImplementedError
