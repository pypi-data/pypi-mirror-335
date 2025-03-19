# -*- coding:utf-8 -*-
# Author:凌逆战 | Never
# Date: 2024/9/19
"""

"""
import numpy as np


def find_active_segments(vad_array):
    # 计算活动段的起始点和结束点
    # vad_array = np.array([0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1])
    # 返回 [(2320, 8079), (8400, 8719), (8880, 10959), (11600, 25039), (25840, 27439), (29040, 29359), (29520, 31759), (32240, 32399)]
    starts = np.where((vad_array[:-1] == 0) & (vad_array[1:] == 1))[0] + 1
    ends = np.where((vad_array[:-1] == 1) & (vad_array[1:] == 0))[0]

    # 如果活动段以1开始但没有以0结束，则需要手动添加结束点
    if vad_array[-1] == 1: ends = np.append(ends, len(vad_array) - 1)
    # 如果活动段以0开始但没有以1结束，则需要手动添加起始点
    if vad_array[0] == 1: starts = np.insert(starts, 0, 0)

    # 处理可能存在的错位情况
    if len(starts) > len(ends): starts = starts[:-1]

    Timestamps = [{"start": int(start), "end": int(end)} for start, end in zip(starts, ends)]

    return Timestamps