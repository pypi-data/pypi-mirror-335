"""
模型训练器模块

本模块提供了模型训练的核心功能，包括数据加载、模型创建、训练循环和验证过程。
它整合了配置解析、数据集处理、特征提取和模型定义等多个组件，实现端到端的模型训练。
"""

import time
import paddle
import os
from paddle.io import DataLoader
from ..config.config_parser import ConfigParser
from .dataset import AudioDataset
from .features import FeatureExtractor
from ..models.model_factory import create_model, create_optimizer, create_loss_function
from ..utils.logger import setup_logger, get_logger, format_time


class Trainer:
    """
    模型训练器类
    
    该类封装了整个模型训练过程，包括环境设置、数据加载、模型创建、训练循环和验证。
    它使用配置文件来设置各种参数，并提供了灵活的训练和验证方法。
    """
    def __init__(self, config_path):
        """
        初始化训练器
        
        Args:
            config_path (str): 配置文件的路径
        
        初始化过程包括加载配置、设置环境、准备数据集、创建模型等步骤。
        """
        self.config = ConfigParser(config_path)
        self.config_path = config_path  # 直接存储配置文件路径
        self.logger = get_logger('ppaudio.core.trainer') or setup_logger('ppaudio.core.trainer', log_file='default')
        self.setup_environment()
        self.setup_data()
        self.setup_model()
        self.setup_training()
    
    def setup_environment(self):
        """
        设置训练环境
        
        根据配置文件设置是否使用GPU，并相应地设置paddle的执行设备。
        同时设置paddle的日志级别，屏蔽不必要的日志信息。
        """
        # 设置paddle的日志级别为ERROR，屏蔽INFO级别的日志
        import os
        import logging
        import warnings
        
        os.environ['GLOG_v'] = '0'
        os.environ['GLOG_logtostderr'] = '0'
        logging.getLogger("paddle").setLevel(logging.ERROR)
        warnings.filterwarnings('ignore')
        
        self.use_gpu = self.config.get_system_config().get('use_GPU', False)
        if self.use_gpu and not paddle.is_compiled_with_cuda():
            self.logger.warning("GPU不可用，切换到CPU模式")
            self.use_gpu = False
        paddle.device.set_device('gpu' if self.use_gpu else 'cpu')
        

    def setup_data(self):
        """
        设置数据集和数据加载器
        
        根据配置创建训练集和验证集，设置数据加载器，并初始化特征提取器。
        """
        dataset_config = self.config.get_dataset_config()
        dataset_settings = dataset_config.get('dataset', {})

        # 设置数据集
        self.train_dataset = AudioDataset(
            root_dir=dataset_config.get('train_data_root', ''),
            csv_file=dataset_config.get('train_data', ''),
            is_full_path=dataset_settings.get('is_full_path', False),
            adjust_audio_length=dataset_settings.get('adjust_audio_length', False)
        )
        
        self.val_dataset = AudioDataset(
            root_dir=dataset_config.get('val_data_root', ''),
            csv_file=dataset_config.get('val_data', ''),
            is_full_path=dataset_settings.get('is_full_path', False),
            adjust_audio_length=dataset_settings.get('adjust_audio_length', False)
        )
        
        # 设置数据加载器
        sampler_config = dataset_config.get('sampler', {})
        batch_size = sampler_config.get('batch_size', 32)
        shuffle = sampler_config.get('shuffle', True)
        drop_last = sampler_config.get('drop_last', True)
        
        self.train_loader = DataLoader(
            self.train_dataset, 
            batch_size=batch_size, 
            shuffle=shuffle,
            drop_last=drop_last
        )
        
        self.val_loader = DataLoader(
            self.val_dataset, 
            batch_size=batch_size, 
            shuffle=False
        )
        
        # 设置特征提取器
        preprocess_config = self.config.get_preprocess_config()
        feature_method = preprocess_config.get('feature_method', 'LogMelSpectrogram')
        method_args = preprocess_config.get('method_args', {})
        
        self.feature_extractor = FeatureExtractor(
            feature_method=feature_method,
            **method_args
        )
    
    def setup_model(self):
        """
        设置模型、优化器和损失函数
        
        根据配置创建模型、优化器和损失函数，为训练做准备。
        """
        model_config = self.config.get_system_config()
        self.model = create_model(model_config.get('model_type', 'cnn14'), num_classes=2)
        self.optimizer = create_optimizer(self.model, self.config.get_optimizer_config())
        self.criterion = create_loss_function(self.config.get_loss_config())
    
    def setup_training(self):
        """
        设置训练参数
        
        从配置文件中读取训练相关的参数，如训练轮数、日志频率等。
        """
        self.epochs = self.config.get_system_config().get('max_epoch', 20)
        self.log_freq = self.config.get_system_config().get('log_freq', 10)
        self.eval_freq = 1
    
    def train(self):
        """
        执行完整的训练过程
        
        包括多个训练轮次，每轮训练后进行验证，并记录训练进度和结果。
        """
        self.logger.info(f"开始训练...总轮次={self.epochs}")
        start_time = time.time()
        
        best_accuracy = 0.0
        for epoch in range(1, self.epochs + 1):
            self.train_epoch(epoch)
            if epoch % self.eval_freq == 0:
                accuracy = self.validate(epoch)
                if accuracy > best_accuracy:
                    best_accuracy = accuracy
                    self.save_model()
        
        total_time = time.time() - start_time
        self.logger.info(f"训练完成! 总用时: {format_time(total_time)}")

    def save_model(self):
        """
        保存当前模型
        如果模型文件已存在，先将其备份，备份文件名包含原始名称和备份时间（精确到分钟）
        同时保存模型信息，包括日期、准确率和轮次
        """
        import datetime
        import shutil
        
        model_path = self.config.get_system_config().get('model_path', 'models/model_best.pdparams')
        
        # 检查模型文件是否已存在
        if os.path.exists(model_path):
            # 生成备份文件名，包含当前时间（精确到分钟）
            current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M")
            model_dir = os.path.dirname(model_path)
            backup_dir = os.path.join(model_dir, 'backups')
            
            # 确保备份目录存在
            os.makedirs(backup_dir, exist_ok=True)
            
            # 构建备份文件名：原始名称+备份时间+扩展名
            original_filename = os.path.basename(model_path)
            name_parts = os.path.splitext(original_filename)
            backup_filename = f"{name_parts[0]}_{current_time}{name_parts[1]}"
            backup_path = os.path.join(backup_dir, backup_filename)
            
            # 备份文件
            shutil.copy2(model_path, backup_path)
            self.logger.info(f"已将原模型备份到 {backup_path}")
        
        # 获取当前日期、准确率和轮次
        current_date = datetime.datetime.now().strftime("%m-%d")
        accuracy = self.validate(self.epochs)  # 使用最后一个epoch的验证准确率
        current_epoch = self.epochs  # 当前轮次
        
        # 创建模型信息
        model_info = f"date:{current_date};acc={accuracy:.2f};epoch={current_epoch}"
        
        # 保存当前模型和模型信息
        state_dict = self.model.state_dict()
        state_dict['model_info'] = model_info  # 将模型信息添加到状态字典中
        
        # 保存模型
        paddle.save(state_dict, model_path)
        self.logger.info(f"模型已保存到 {model_path}，信息: {model_info}")
        
        # 更新配置文件中的模型信息
        import yaml
        config_path = self.config.config_path  # 获取配置文件路径
        
        # 读取当前配置
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
        
        # 更新模型信息
        if 'sys_conf' not in config_data:
            config_data['sys_conf'] = {}
        config_data['sys_conf']['model_info'] = model_info
        
        # 保存更新后的配置
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True)
        
        self.logger.info(f"模型信息已更新到配置文件: {config_path}")
    
    def train_epoch(self, epoch):
        """
        训练一个完整的epoch
        
        Args:
            epoch (int): 当前的epoch数
        
        Returns:
            tuple: (平均损失, 平均准确率)
        
        在一个epoch中遍历整个训练集，更新模型参数，并记录训练指标。
        """
        self.model.train()
        total_loss = 0
        correct = 0
        total = 0
        
        for batch_idx, (waveforms, labels) in enumerate(self.train_loader):
            feats = self.feature_extractor.extract_features(waveforms)
            logits = self.model(feats)
            loss = self.criterion(logits, labels)
            
            loss.backward()
            self.optimizer.step()
            self.optimizer.clear_grad()
            
            total_loss += loss.item()
            # 确保预测结果和标签都是int32类型
            preds = paddle.cast(paddle.argmax(logits, axis=1), dtype='int32')
            labels = paddle.cast(labels, dtype='int32')
            correct += (preds == labels).sum().item()
            total += labels.shape[0]
            
            if (batch_idx + 1) % self.log_freq == 0:
                self.logger.info(f"Epoch {epoch} [{batch_idx+1}/{len(self.train_loader)}] "
                                 f"Loss: {total_loss/self.log_freq:.4f} "
                                 f"Acc: {correct/total:.4f}")
                total_loss = 0
                correct = 0
                total = 0
    
    def validate(self, epoch):
        """
        在验证集上评估模型
        
        Args:
            epoch (int): 当前的epoch数
        
        Returns:
            float: 验证集上的准确率
        
        在验证集上运行模型，计算准确率，用于监控模型的泛化能力。
        """
        self.model.eval()
        total_loss = 0
        correct = 0
        total = 0
        
        with paddle.no_grad():
            for waveforms, labels in self.val_loader:
                feats = self.feature_extractor.extract_features(waveforms)
                logits = self.model(feats)
                loss = self.criterion(logits, labels)
                
                total_loss += loss.item()
                # 确保预测结果和标签都是int32类型
                preds = paddle.cast(paddle.argmax(logits, axis=1), dtype='int32')
                labels = paddle.cast(labels, dtype='int32')
                correct += (preds == labels).sum().item()
                total += labels.shape[0]
        
        avg_loss = total_loss / len(self.val_loader)
        accuracy = correct / total
        self.logger.info(f"Validation Epoch: {epoch} "
                         f"Loss: {avg_loss:.4f} "
                         f"Acc: {accuracy:.4f}")
        
        return accuracy