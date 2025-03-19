"""
日志工具模块

本模块提供了日志记录功能，支持：
- 同时输出到控制台和文件
- 自定义日志格式
- 时间格式化
- 不同级别的日志记录

主要用于记录训练过程、测试结果和错误信息。
"""

import os
import sys
import logging
from datetime import timedelta


def get_logger(name='ppaudio'):
    """
    获取已存在的日志记录器，如果不存在则返回None
    
    Args:
        name (str): 日志记录器名称
        
    Returns:
        logging.Logger: 已存在的日志记录器，如果不存在则返回None
    """
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    return None


def get_default_log_dir():
    """
    获取默认的日志目录路径
    
    Returns:
        str: 日志目录的绝对路径
    """
    # 获取ppaudio包的根目录
    ppaudio_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    # 日志目录在项目根目录下的log文件夹
    log_dir = os.path.join(ppaudio_root, 'log')
    os.makedirs(log_dir, exist_ok=True)
    return log_dir


def get_default_log_file(name='ppaudio'):
    """
    获取默认的日志文件路径
    
    Args:
        name (str): 日志文件名前缀
        
    Returns:
        str: 日志文件的完整路径
    """
    log_dir = get_default_log_dir()
    return os.path.join(log_dir, f'{name}.log')


def setup_logger(name='ppaudio', log_file='default', level=logging.INFO):
    """
    设置并返回一个配置好的日志记录器
    
    Args:
        name (str): 日志记录器名称
        log_file (str, optional): 日志文件路径，不指定则只输出到控制台
        level (int): 日志级别，默认为INFO
    
    Returns:
        logging.Logger: 配置好的日志记录器
    
    该函数创建一个日志记录器，可以同时输出到控制台和文件（如果指定）。
    日志格式包含时间戳、日志级别和消息内容。
    """
    """设置日志记录器"""
    logger = logging.getLogger(name)
    
    # 清除已有的处理器
    if logger.handlers:
        for handler in logger.handlers:
            logger.removeHandler(handler)
    
    logger.setLevel(level)
    logger.propagate = False
    
    # 创建格式化器
    formatter = logging.Formatter(
        '[%(asctime)s][%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 添加控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)
    logger.addHandler(console_handler)
    
    # 处理日志文件路径
    if log_file:
        if log_file == 'default':
            log_file = get_default_log_file(name)
        
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)
        logger.addHandler(file_handler)
    
    return logger


def format_time(seconds):
    """
    将秒数格式化为时:分:秒格式
    
    Args:
        seconds (int): 秒数
    
    Returns:
        str: 格式化后的时间字符串，格式为 HH:MM:SS
    
    用于将训练时间等数值转换为人类可读的格式。
    """
    """将秒数格式化为时:分:秒格式"""
    return str(timedelta(seconds=int(seconds)))