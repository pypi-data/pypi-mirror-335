'''
Author: 凌逆战 | Never
Date: 2025-03-19 21:25:39
LastEditTime: 2025-03-19 21:29:30
FilePath: \neverlib\neverlib\utils\waveform_analyzer.py
Description: 
'''
# -*- coding:utf-8 -*-
# Author:凌逆战 | Never
# Date: 2024/12/2
"""
https://github.com/endolith/waveform-analysis
https://github.com/aishoot/Speech_Feature_Extraction
"""
import numpy as np
import librosa


def dB(level):
    return 20 * np.log10(level + 1e-6)


def peak_amplitude(wav):
    """ 计算峰值幅度
    :param wav: (*, ch)
    :return:
    """
    peak_amp = np.max(np.abs(wav))
    return dB(peak_amp)


def rms_amplitude(wav):
    """ 总计RMS振幅
    :param wav: (*, ch)
    :return:
    """
    # 分帧
    frame = librosa.util.frame(wav.flatten(), frame_length=512, hop_length=256)  # (frame_length, frame_num)
    rms_amp = np.sqrt(np.mean(np.square(frame), axis=0))  # (frame_num,)
    return dB(rms_amp)


def rms_amplitude(wav):
    """ 总计RMS振幅
    :param wav: (*, ch)
    :return:
    """
    # 分帧
    frame = librosa.util.frame(wav.flatten(), frame_length=512, hop_length=256)  # (frame_length, frame_num)
    rms_amp = np.sqrt(np.mean(np.square(frame), axis=0))  # (frame_num,)
    return dB(rms_amp)
