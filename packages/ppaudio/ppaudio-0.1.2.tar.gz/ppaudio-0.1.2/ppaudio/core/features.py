"""
特征提取模块

本模块提供了音频特征提取的功能，支持多种特征提取方法：
1. 对数梅尔频谱图 (LogMelSpectrogram)
2. 短时傅里叶变换 (STFT)
3. 带通滤波器处理

主要用于将音频波形转换为适合机器学习模型输入的特征表示。
"""

import os
import sys
import paddle
import numpy as np
import logging
from paddleaudio.features import LogMelSpectrogram, Spectrogram
from scipy.signal import butter, lfilter

# 设置paddle日志级别
logging.getLogger("paddle").setLevel(logging.ERROR)

# 禁用特定的paddle日志
for logger_name in ["paddle", "paddle.distributed.fleet.launch.launch_utils", "paddle.distributed.fleet.base.fleet_base"]:
    paddle_logger = logging.getLogger(logger_name)
    paddle_logger.setLevel(logging.ERROR)
    paddle_logger.propagate = False


class FeatureExtractor:
    """
    音频特征提取器

    该类提供了多种音频特征提取方法，可以将音频波形转换为频谱特征。
    支持对数梅尔频谱图和STFT特征，并可以应用频率滤波器。
    """
    def __init__(self, sr=48000, n_fft=1024, hop_length=512, win_length=1024,
                 window='hann', f_min=50, f_max=14000, n_mels=64, feature_method='log_mel'):
        """
        初始化特征提取器

        Args:
            sr (int): 采样率（Hz）
            n_fft (int): FFT窗口大小
            hop_length (int): 帧移（相邻窗口之间的样本数）
            win_length (int): 窗口长度
            window (str): 窗口类型（如'hann'）
            f_min (float): 最低频率（Hz）
            f_max (float): 最高频率（Hz）
            n_mels (int): 梅尔滤波器组的数量
            feature_method (str): 特征提取方法（'log_mel'或'stft'）
        """
        self.sr = sr
        self.n_fft = n_fft
        self.hop_length = hop_length
        self.win_length = win_length
        self.window = window
        self.f_min = f_min
        self.f_max = f_max
        self.n_mels = n_mels
        self.feature_method = feature_method
        
        self.log_mel_spectrogram = LogMelSpectrogram(
            sr=sr, n_fft=n_fft, hop_length=hop_length, win_length=win_length,
            window=window, f_min=f_min, f_max=f_max, n_mels=n_mels
        )
        
        self.stft = Spectrogram(
            n_fft=n_fft, hop_length=hop_length, win_length=win_length,
            window=window
        )
    
    def apply_filter(self, data, filter_type="band", freq_range="50,14000"):
        """
        对音频数据应用滤波器

        Args:
            data (numpy.ndarray): 输入音频数据
            filter_type (str): 滤波器类型（'band'表示带通滤波器）
            freq_range (str): 频率范围，格式为"最低频率,最高频率"

        Returns:
            numpy.ndarray: 滤波后的音频数据
        """
        nyquist = 0.5 * self.sr
        lowcut, highcut = None, None
        
        if ',' in freq_range:
            lowcut, highcut = map(float, freq_range.split(','))
        
        # 归一化截止频率
        if lowcut is not None:
            lowcut = lowcut / nyquist
        if highcut is not None:
            highcut = highcut / nyquist
        
        # 设计滤波器
        b, a = butter(N=5, Wn=[lowcut, highcut], btype=filter_type, analog=False)
        
        # 应用滤波器
        y = lfilter(b, a, data)
        return y
    
    def extract_features(self, waveforms, filter_type=None, freq_range=None):
        """
        从音频波形中提取特征

        Args:
            waveforms (numpy.ndarray | paddle.Tensor): 输入音频波形
            filter_type (str, optional): 滤波器类型
            freq_range (str, optional): 频率范围

        Returns:
            paddle.Tensor: 提取的特征，形状为[batch_size, time_steps, feature_dim]

        该方法首先可以对音频进行可选的滤波处理，然后根据配置的特征提取方法
        （LogMelSpectrogram或STFT）提取特征。最后返回适合模型输入的特征张量。
        """
        if filter_type:
            if waveforms.ndim == 1:
                waveforms = self.apply_filter(waveforms, filter_type, freq_range)
                waveforms = np.expand_dims(waveforms, axis=0)
            else:
                waveforms = np.array([self.apply_filter(wf, filter_type, freq_range) for wf in waveforms])
        
        if isinstance(waveforms, np.ndarray):
            waveforms = paddle.to_tensor(waveforms, dtype='float32')
        
        if self.feature_method == "log_mel" or self.feature_method == "LogMelSpectrogram":
            feats = self.log_mel_spectrogram(waveforms)
        elif self.feature_method == "stft":
            feats = self.stft(waveforms)
        else:
            raise ValueError(f"不支持的特征类型: {self.feature_method}。使用 'log_mel' 或 'stft'。")
        
        return paddle.transpose(feats, [0, 2, 1])