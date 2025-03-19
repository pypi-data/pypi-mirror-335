"""
可视化工具模块

本模块提供了一系列用于音频数据可视化的工具函数，包括：
- 波形图绘制
- 频谱图绘制
- 多音频比较可视化

这些工具可以帮助用户直观地分析和比较音频数据的特征。
"""

import matplotlib.pyplot as plt
import numpy as np


def plot_waveform(waveform, sr=48000, title="波形图"):
    """
    绘制音频波形图
    
    Args:
        waveform (numpy.ndarray): 音频波形数据
        sr (int): 采样率（Hz）
        title (str): 图表标题
    
    Returns:
        matplotlib.figure.Figure: 生成的图表对象
    
    绘制音频波形的时域表示，x轴为时间（秒），y轴为振幅。
    """
    """绘制波形图"""
    plt.figure(figsize=(10, 4))
    plt.plot(np.arange(len(waveform)) / sr, waveform)
    plt.title(title)
    plt.xlabel("时间 (秒)")
    plt.ylabel("振幅")
    plt.grid(True)
    plt.tight_layout()
    return plt.gcf()


def plot_spectrogram(spectrogram, title="频谱图"):
    """
    绘制频谱图
    
    Args:
        spectrogram (numpy.ndarray): 频谱图数据
        title (str): 图表标题
    
    Returns:
        matplotlib.figure.Figure: 生成的图表对象
    
    绘制音频的频谱表示，x轴为时间，y轴为频率，颜色表示能量强度。
    """
    """绘制频谱图"""
    plt.figure(figsize=(10, 4))
    plt.imshow(spectrogram, aspect='auto', origin='lower')
    plt.title(title)
    plt.xlabel("时间帧")
    plt.ylabel("频率")
    plt.colorbar(format='%+2.0f dB')
    plt.tight_layout()
    return plt.gcf()


def compare_spectrograms(spec1, spec2, title1="频谱图1", title2="频谱图2"):
    """
    比较两个频谱图
    
    Args:
        spec1 (numpy.ndarray): 第一个频谱图数据
        spec2 (numpy.ndarray): 第二个频谱图数据
        title1 (str): 第一个频谱图的标题
        title2 (str): 第二个频谱图的标题
    
    Returns:
        matplotlib.figure.Figure: 包含两个频谱图对比的图表对象
    
    将两个频谱图并排显示，方便直观比较它们的差异。
    常用于比较正常音频和异常音频的特征差异。
    """
    """比较两个频谱图"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
    
    im1 = ax1.imshow(spec1, aspect='auto', origin='lower')
    ax1.set_title(title1)
    ax1.set_xlabel("时间帧")
    ax1.set_ylabel("频率")
    plt.colorbar(im1, ax=ax1, format='%+2.0f dB')
    
    im2 = ax2.imshow(spec2, aspect='auto', origin='lower')
    ax2.set_title(title2)
    ax2.set_xlabel("时间帧")
    ax2.set_ylabel("频率")
    plt.colorbar(im2, ax=ax2, format='%+2.0f dB')
    
    plt.tight_layout()
    return fig