# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Website  : https://gitee.com/g1879/TimePinner
@Copyright: (c) 2020 by g1879, Inc. All Rights Reserved.
"""
from typing import Union


class Pinner(object):
    """用于记录时间间隔的工具"""
    times: list
    show_everytime: bool

    def __init__(self, pin: bool = False, show_everytime: bool = True) -> None: ...

    def pin(self, text: str = '', all_time: bool = False, show: bool = None) -> float: ...

    def skip(self) -> None: ...

    def show(self, all_time: bool = False) -> None: ...

    def reset(self, text: str = '', show: bool = None) -> None: ...

    def records(self, all_time: bool = False) -> list: ...

    def winner(self, all_time: bool = False) -> Union[tuple, None]: ...
