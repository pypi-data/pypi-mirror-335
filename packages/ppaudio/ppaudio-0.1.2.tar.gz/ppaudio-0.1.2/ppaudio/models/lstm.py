"""
LSTM模型模块

本模块定义了基于LSTM的声音分类模型。LSTM模型特别适合处理时序数据，
可以捕捉音频特征中的时序依赖关系，适用于需要考虑时序信息的声音分类任务。
"""

import paddle
import paddle.nn as nn
import paddle.nn.functional as F


class LSTMClassifier(nn.Layer):
    """
    基于LSTM的声音分类器
    
    该模型使用LSTM层处理时序特征，后接全连接层进行分类。
    支持单向/双向LSTM，多层LSTM，并包含dropout和批归一化层以防止过拟合。
    """
    def __init__(self, input_size=26, hidden_size=128, num_layers=2,
                 num_classes=2, dropout=0.5, bidirectional=True):
        """
        初始化LSTM分类器
        
        Args:
            input_size (int): 输入特征的维度
            hidden_size (int): LSTM隐藏层的大小
            num_layers (int): LSTM的层数
            num_classes (int): 分类的类别数
            dropout (float): Dropout率，用于防止过拟合
            bidirectional (bool): 是否使用双向LSTM
        """
        super().__init__()
        
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            direction='bidirectional' if bidirectional else 'forward',
            dropout=dropout if num_layers > 1 else 0
        )
        
        lstm_out_size = hidden_size * 2 if bidirectional else hidden_size
        self.dropout = nn.Dropout(dropout)
        self.bn = nn.BatchNorm1D(lstm_out_size)
        self.fc1 = nn.Linear(lstm_out_size, 64)
        self.fc2 = nn.Linear(64, num_classes)
    
    def forward(self, x):
        """
        前向传播
        
        Args:
            x (Tensor): 输入张量，形状为 [batch_size, time_steps, input_size]
        
        Returns:
            Tensor: 模型输出的logits，形状为 [batch_size, num_classes]
        
        流程：
        1. 输入经过dropout
        2. 通过LSTM层处理
        3. 提取最后时刻的隐藏状态
        4. 经过批归一化
        5. 通过全连接层得到最终输出
        """
        # LSTM层
        x = self.dropout(x)
        lstm_out, (h, c) = self.lstm(x)
        
        # 获取最后的隐藏状态
        if self.lstm.direction == 'bidirectional':
            last_hidden = paddle.concat([h[-2], h[-1]], axis=1)
        else:
            last_hidden = h[-1]
        
        # 批归一化
        normalized = self.bn(last_hidden)
        
        # 全连接层
        x = F.relu(self.fc1(normalized))
        x = self.dropout(x)
        logits = self.fc2(x)
        
        return logits