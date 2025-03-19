"""
模型工厂模块

本模块提供了创建模型、优化器和损失函数的工厂函数。
它集中管理了不同类型的模型、优化器和损失函数的创建逻辑，
使得主程序可以更灵活地根据配置选择不同的组件。
"""

import paddle
from .cnn import create_cnn_model
from .lstm import LSTMClassifier


def create_model(model_type, num_classes, **kwargs):
    """
    创建模型实例
    
    Args:
        model_type (str): 模型类型，支持 'cnn14', 'cnn10', 'lstm'
        num_classes (int): 分类的类别数
        **kwargs: 额外的模型参数
    
    Returns:
        paddle.nn.Layer: 创建的模型实例
    
    Raises:
        ValueError: 如果指定了不支持的模型类型
    """
    if model_type in ['cnn14', 'cnn10']:
        return create_cnn_model(model_type, num_classes)
    elif model_type == 'lstm':
        return LSTMClassifier(num_classes=num_classes, **kwargs)
    else:
        raise ValueError(f"不支持的模型类型: {model_type}")


def create_optimizer(model, optimizer_config):
    """
    创建优化器实例
    
    Args:
        model (paddle.nn.Layer): 需要优化的模型
        optimizer_config (dict): 优化器配置，包含类型和学习率等参数
    
    Returns:
        paddle.optimizer.Optimizer: 创建的优化器实例
    
    Raises:
        ValueError: 如果指定了不支持的优化器类型
    """
    optimizer_type = optimizer_config.get('optimizer', 'Adam')
    learning_rate = optimizer_config.get('learning_rate', 0.001)
    
    if optimizer_type == 'Adam':
        return paddle.optimizer.Adam(learning_rate=learning_rate, parameters=model.parameters())
    elif optimizer_type == 'SGD':
        return paddle.optimizer.SGD(learning_rate=learning_rate, parameters=model.parameters())
    else:
        raise ValueError(f"不支持的优化器类型: {optimizer_type}")


def create_loss_function(loss_config):
    """
    创建损失函数实例
    
    Args:
        loss_config (dict): 损失函数配置，包含损失函数类型等参数
    
    Returns:
        paddle.nn.Layer: 创建的损失函数实例
    
    Raises:
        ValueError: 如果指定了不支持的损失函数类型
    """
    loss_type = loss_config.get('criterion', 'CrossEntropyLoss')
    
    if loss_type == 'CrossEntropyLoss':
        return paddle.nn.CrossEntropyLoss()
    elif loss_type == 'BCEWithLogitsLoss':
        return paddle.nn.BCEWithLogitsLoss()
    else:
        raise ValueError(f"不支持的损失函数类型: {loss_type}")