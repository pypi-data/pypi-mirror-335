"""
CNN模型模块

本模块定义了基于CNN的声音分类模型，包括CNN14和CNN10两种预训练模型的封装。
这些模型适用于各种声音分类任务，如工业异音检测、环境声音分类等。
"""

import paddle
import paddle.nn as nn
from paddlespeech.cls.models import cnn14, cnn10


class SoundClassifier(nn.Layer):
    """
    声音分类器类
    
    该类封装了预训练的CNN模型（如CNN14或CNN10），并添加了一个全连接层用于分类。
    可以用于各种声音分类任务，支持微调预训练模型。
    """
    def __init__(self, backbone, num_class, dropout=0.1):
        """
        初始化声音分类器
        
        Args:
            backbone (nn.Layer): 预训练的CNN主干网络
            num_class (int): 分类的类别数
            dropout (float): Dropout率，用于防止过拟合
        """
        super().__init__()
        self.backbone = backbone
        self.dropout = nn.Dropout(dropout)
        self.fc = nn.Linear(self.backbone.emb_size, num_class)

    def forward(self, x):
        """
        前向传播
        
        Args:
            x (Tensor): 输入张量，形状为 [batch_size, time_steps, feature_dim]
        
        Returns:
            Tensor: 模型输出的logits，形状为 [batch_size, num_class]
        """
        x = x.unsqueeze(1)
        x = self.backbone(x)
        x = self.dropout(x)
        logits = self.fc(x)
        return logits


def create_cnn_model(model_type, num_class):
    """
    创建CNN模型
    
    Args:
        model_type (str): 模型类型，可选 'cnn14' 或 'cnn10'
        num_class (int): 分类的类别数
    
    Returns:
        SoundClassifier: 初始化好的声音分类器模型
    
    根据指定的模型类型创建相应的预训练CNN模型，并封装成SoundClassifier。
    """
    if model_type == 'cnn14':
        backbone = cnn14(pretrained=False, extract_embedding=True)
    elif model_type == 'cnn10':
        backbone = cnn10(pretrained=False, extract_embedding=True)
    else:
        raise ValueError(f"不支持的模型类型: {model_type}")
    
    return SoundClassifier(backbone, num_class)