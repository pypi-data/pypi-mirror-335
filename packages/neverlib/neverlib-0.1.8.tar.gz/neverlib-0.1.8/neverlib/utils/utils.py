# -*- coding:utf-8 -*-
# Author:凌逆战 | Never
# Date: 2023/9/25
"""
folder处理
"""
import os
import random
import shutil
import fnmatch
import subprocess
from tqdm import tqdm
import multiprocessing
from datetime import datetime
from joblib import Parallel, delayed


def get_path_list(source_path, end="*.wav", shuffle=False):
    wav_list = []
    for root, dirnames, filenames in os.walk(source_path):
        # 实现列表特殊字符的过滤或筛选,返回符合匹配“.wav”字符列表
        for filename in fnmatch.filter(filenames, end):
            wav_list.append(os.path.join(root, filename))
    print(source_path, len(wav_list))
    if shuffle:
        random.shuffle(wav_list)
    return wav_list


def rename_files_and_folders(directory, replace='_-', replacement='_'):
    # 将路径的指定字符替换为指定字符
    for root, dirs, files in os.walk(directory):
        for filename in files:
            if replace in filename:
                new_filename = filename.replace(replace, replacement)
                old_path = os.path.join(root, filename)
                new_path = os.path.join(root, new_filename)
                os.rename(old_path, new_path)
                print(f'Renamed file: {old_path} -> {new_path}')

        for folder in dirs:
            if replace in folder:
                new_folder = folder.replace(replace, replacement)
                old_path = os.path.join(root, folder)
                new_path = os.path.join(root, new_folder)
                os.rename(old_path, new_path)
                print(f'Renamed folder: {old_path} -> {new_path}')


def audio_split_ffmpeg(source_path, target_path, sr, channel_num, duration, endwith="*.pcm"):
    """
    使用ffmpeg分割音频, 分割为短音频(单位:秒), 似乎无法非常准确的分割到指定长度
    :param source_path: 源音频路径
    :param target_path: 目标音频路径
    :param sr: 源音频采样率
    :param channel_num: 源音频声道数
    :param duration: 分割为时长(短音频)(单位:秒)
    :param endwith: 音频格式(支持pcm和wav)
    """
    wav_path_list = get_path_list(source_path, end=endwith)
    print("待分割的音频数: ", len(wav_path_list))
    for wav_path in wav_path_list:
        wav_folder = wav_path[:-4].replace(source_path, target_path)
        if not os.path.exists(wav_folder):
            os.makedirs(wav_folder)

        if endwith == "*.pcm":
            # 将pcm文件切割成30s的语音, 有括号会报错
            # ffmpeg -f s16le -ar 16000 -ac 6 -i ./NO.1_A3035_2.pcm -f segment -segment_time 30 -c copy NO.1_A3035_2/%03d.wav
            command = ["ffmpeg", "-f", "s16le", "-ar", f"{sr}", "-ac", str(channel_num),
                       "-i", wav_path, "-f", "segment", "-segment_time",
                       f"{duration}", "-c", "copy", f"{wav_folder}/%03d.wav"]
            subprocess.run(command, check=True)
        elif endwith == "*.wav":
            # ffmpeg -i ./NO.1_A3035_2.wav -f segment -segment_time 30 -c copy NO.1_A3035_2/%03d.wav
            command = ["ffmpeg", "-i", wav_path, "-f", "segment", "-segment_time",
                       f"{duration}", "-c", "copy", f"{wav_folder}/%03d.wav"]
            subprocess.run(command, check=True)
        else:
            assert False, "不支持的音频格式"
    print("分割完毕: done!")


def audio_split_sox(source_path, target_path, duration, endwith="*.wav"):
    """
    使用sox分割音频, 分割为短音频(单位:秒), 可以非常准确的分割到指定长度
    :param source_path: 源音频路径
    :param target_path: 目标音频路径
    :param duration: 分割为时长(短音频)(单位:秒)
    :param endwith: 音频格式(只支持wav)
    """
    wav_path_list = get_path_list(source_path, end=endwith)

    for wav_path in wav_path_list:
        wav_folder = wav_path[:-4].replace(source_path, target_path)
        if not os.path.exists(wav_folder):
            os.makedirs(wav_folder)

        output_pattern = f"{wav_folder}/%.wav"

        if endwith == "*.wav":
            # 对 WAV 文件直接进行分割
            os.system(f"sox {wav_path} {output_pattern} trim 0 {str(duration)} : newfile : restart")
        else:
            assert False, "不支持的音频格式"

    print("分割完毕: done!")


def audio_split_worker(wav_path, target_path, sr, channel_num, duration, endwith="*.pcm"):
    wav_name = os.path.basename(wav_path)[:-4]
    wav_folder = os.path.join(target_path, wav_name)
    if not os.path.exists(wav_folder):
        os.makedirs(wav_folder)

    if endwith == "*.pcm":
        # 将pcm文件切割成30s的语音, 有括号会报错
        # os.system(r"ffmpeg -f s16le -ar {} -ac {} -i {} -f segment -segment_time {} -c copy {}/%03d.wav".format(
        #           sr, channel_num, wav_path, duration, wav_folder))
        command = ["ffmpeg", "-f", "s16le", "-ar", f"{sr}", "-ac", str(channel_num),
                   "-i", wav_path, "-f", "segment", "-segment_time",
                   f"{duration}", "-c", "copy", f"{wav_folder}/%03d.wav"]
        subprocess.run(command, check=True)
        # 调用库
        # input_audio = ffmpeg.input(wav_path, format='s16le', ar=16000, ac=5)
        # output_audio = ffmpeg.output(input_audio, f='segment', segment_time=30, c='copy', path=f'{wav_folder}/%03d.wav')
        # ffmpeg.run(output_audio)
    elif endwith == "*.wav":
        # ffmpeg -i ./NO.1_A3035_2.wav -f segment -segment_time 30 -c copy NO.1_A3035_2/%03d.wav
        command = ["ffmpeg", "-i", wav_path, "-f", "segment", "-segment_time",
                   f"{duration}", "-c", "copy", f"{wav_folder}/%03d.wav"]
        subprocess.run(command, check=True)
    else:
        assert False, "不支持的音频格式"


def audio_split_multiprocessing(source_path, target_path, sr, channel_num, duration, endwith="*.pcm"):
    wav_path_list = get_path_list(source_path, end=endwith)
    print("待分割的音频数: ", len(wav_path_list))

    # 创建进程池
    pool = multiprocessing.Pool(processes=5)

    # 使用进程池处理音频文件分割任务
    for wav_path in wav_path_list:
        pool.apply_async(audio_split_worker, args=(wav_path, target_path, sr, channel_num, duration, endwith))

    # 关闭进程池，等待所有进程完成
    pool.close()
    pool.join()

    print("分割完毕: done!")


def get_file_time(file_path):
    # 获取最后修改时间
    mod_time = os.path.getmtime(file_path)
    # 转为data_time格式：年-月-日-时-分-秒
    datetime_dt = datetime.fromtimestamp(mod_time)

    # 如果时间早于2024-09-04 02:00:00，则删除
    # if datetime_dt < datetime(2024, 9, 4, 2, 0, 0):
    #     print(file_path)
    return datetime_dt


def TrainValSplit(dataset_dir, train_dir, val_dir, percentage=0.9):
    """ 分割数据集为训练集和验证集
    :param dataset_dir: 源数据集地址
    :param train_dir: 训练集地址
    :param val_dir: 验证集地址
    :param percentage: 分割百分比
    """
    wav_path_list = sorted(get_path_list(dataset_dir))
    random.seed(10086)
    random.shuffle(wav_path_list)  # 打乱列表的顺序
    total_wav_num = len(wav_path_list)
    # 计算训练集和验证集的分割点
    split_idx = int(total_wav_num * percentage)
    train_path_list, val_path_list = wav_path_list[:split_idx], wav_path_list[split_idx:]

    for train_wavpath in tqdm(train_path_list, desc="Copying train wav"):
        target_path = train_wavpath.replace(dataset_dir, train_dir)
        if not os.path.exists(os.path.split(target_path)[0]):
            os.makedirs(os.path.split(target_path)[0])
        shutil.copy(train_wavpath, target_path)

    for val_wavpath in tqdm(val_path_list, desc="Copying val wav"):
        target_path = val_wavpath.replace(dataset_dir, val_dir)
        if not os.path.exists(os.path.split(target_path)[0]):
            os.makedirs(os.path.split(target_path)[0])
        shutil.copy(val_wavpath, target_path)

    print("Done!")
