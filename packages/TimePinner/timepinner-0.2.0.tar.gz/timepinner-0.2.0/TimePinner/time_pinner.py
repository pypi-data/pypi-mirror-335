# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Website  : https://gitee.com/g1879/TimePinner
@Copyright: (c) 2020 by g1879, Inc. All Rights Reserved.
"""
from time import perf_counter


class Pinner(object):
    """用于记录时间间隔的工具"""

    def __init__(self, pin=False, show_everytime=True):
        """
        :param pin: 初始化时是否记录一个时间点
        :param show_everytime: 是否每次记录时打印时间差
        """
        self.times = []
        self.show_everytime = show_everytime
        if pin:
            self.pin('起始点')

    def pin(self, text='', all_time=False, show=None):
        """记录一个时间点
        :param text: 记录点说明文本
        :param all_time: 时间点与起始点的时间差，或时间点之间的时间差
        :param show: 是否打印时间差
        :return: 返回时间差
        """
        now = perf_counter()
        num = 0 if all_time else -1
        prev = self.times[num][0] if self.times else now
        self.times.append((now, text))
        gap = now - prev

        if show is True or (self.show_everytime and show is None):
            p_text = f'{text}：' if text else ''
            print(f'{p_text}{gap}')

        return gap

    def skip(self):
        """跳过从上一个时间点到当前的时间"""
        self.times.append((perf_counter(), False))

    def show(self, all_time=False):
        """打印所有时间差
        :param all_time: 每个时间点与起始点的时间差，或时间点之间的时间差
        :return: None
        """
        for k in self.records(all_time):
            print(f'{k[0]}：{k[1]}')

    def reset(self, text='', show=None):
        """清空重新开始记录
        :param text: 记录点说明文本，不传入默认为“起始点”
        :param show: 是否打印信息
        :return: None
        """
        self.times = []
        self.pin(text or '起始点', show)

    def records(self, all_time=False):
        """返回所有时间差组成的列表
        :param all_time: 每个时间点与起始点的时间差，或时间点之间的时间差
        :return: 时间节点列表
        """
        if all_time:
            return [(self.times[k][1] or f't{k}', self.times[k][0] - self.times[0][0])
                    for k in range(1, len(self.times)) if self.times[k][1] is not False]
        else:
            return [(self.times[k][1] or f't{k}', self.times[k][0] - self.times[k - 1][0])
                    for k in range(1, len(self.times)) if self.times[k][1] is not False]

    def winner(self, all_time=False):
        """返回最短的时间差
        :param all_time: 每个时间点与起始点的时间差，或时间点之间的时间差
        :return: 标签与时间组成的tuple
        """
        ts = sorted(self.records(all_time), key=lambda x: x[1])
        return ts[0] if ts else None
