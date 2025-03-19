"""
音频数据集模块

本模块提供了音频数据集的加载和处理功能，支持从CSV文件中读取音频文件路径和标签，
并提供音频长度调整等预处理功能。主要用于为模型训练和评估准备数据。
"""


import numpy as np  
import os  
from paddle.io import Dataset  
from paddleaudio import load  
import csv  
from .audio import pad_wav_file


import logging

class AudioDataset(Dataset):
    """
    音频数据集类
    
    该类继承自paddle.io.Dataset，用于加载和处理音频分类任务的数据集。
    支持从CSV文件中读取音频文件路径和标签，并可以自动调整音频长度。
    """
    def __init__(self, root_dir, csv_file, is_full_path=False, adjust_audio_length=True):
        """
        初始化音频数据集
        
        Args:
            root_dir (str): 数据集根目录，用于构建相对路径
            csv_file (str): CSV文件路径，包含音频文件路径和标签
            is_full_path (bool): CSV中的路径是否为完整路径，False表示是相对路径
            adjust_audio_length (bool): 是否调整所有音频到相同长度
        """
        self.root_dir = root_dir
        self.csv_file = csv_file
        self.is_full_path = is_full_path
        self.adjust_audio_length = adjust_audio_length
        
        self.valid_samples = []
        self.logger = logging.getLogger(__name__)
        
        self._load_csv()
        
        if self.adjust_audio_length:
            self.max_length = self._get_max_length()
    
    def _load_csv(self):
        """
        加载CSV文件中的音频路径和标签，只保留存在的音频文件
        
        CSV文件格式应为每行两列：第一列为音频文件路径，第二列为标签（整数）。
        如果is_full_path为False，则会将root_dir与CSV中的路径拼接。
        """
        if not os.path.isfile(self.csv_file):
            raise FileNotFoundError(f"{self.csv_file} 不存在!")
            
        with open(self.csv_file, newline='') as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) != 2:
                    continue
                    
                data_path = row[0]
                if not self.is_full_path:
                    data_path = os.path.join(self.root_dir, row[0])
                
                if os.path.isfile(data_path):
                    label = int(row[1])
                    self.valid_samples.append((data_path, label))
                else:
                    self.logger.warning(f"文件不存在，已跳过: {data_path}")
    
    def _get_max_length(self):
        """
        获取数据集中最长音频的长度
        
        Returns:
            int: 最长音频的样本点数
        
        该方法遍历数据集中的所有有效音频文件，找出最长的一个，用于后续的音频长度调整。
        如果没有找到有效的音频文件，返回默认长度（48000，对应1秒的音频）。
        """
        max_len = 0
        found_valid_file = False
        
        for file_path, _ in self.valid_samples:
            try:
                waveform, sr = load(file_path, mono=True)
                max_len = max(max_len, len(waveform))
                found_valid_file = True
            except Exception as e:
                self.logger.warning(f"无法加载文件 {file_path}: {str(e)}")
                continue
        
        if not found_valid_file:
            self.logger.warning("未找到有效的音频文件，使用默认长度 48000")
            return 48000  # 默认使用1秒的音频长度（采样率48000）
        
        # 确保返回的长度至少为2048（是常用的n_fft值的两倍）
        return max(max_len, 2048)
    
    def __len__(self):
        """
        获取有效数据集大小
        
        Returns:
            int: 数据集中的有效样本数量
        """
        return len(self.valid_samples)
    
    def __getitem__(self, idx):
        """
        获取指定索引的样本
        
        Args:
            idx (int): 样本索引
            
        Returns:
            tuple: (音频波形, 标签)，其中音频波形为numpy数组，标签为整数
            
        如果开启了adjust_audio_length，会将音频调整到与数据集中最长音频相同的长度。
        """
        file_path, label = self.valid_samples[idx]
        
        waveform, sr = load(file=file_path, mono=True, dtype='float32')  # 单通道，float32音频样本点
        
        if self.adjust_audio_length:
            waveform = pad_wav_file(file_path, self.max_length / sr)
        
        return waveform, label