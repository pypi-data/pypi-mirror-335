"""
Trainer for audio classification models
"""

import os
import time
import paddle
from paddle.io import DataLoader
from .config.config_parser import ConfigParser
from .dataset.audio_dataset import AudioDataset
from .features.feature_extractor import FeatureExtractor
from .models.model_factory import create_model, create_optimizer, create_scheduler, create_loss_function
from .utils.visualization import plot_training_progress
from .utils.logger import setup_logger, get_logger, format_time
from typing import Dict, Any, Optional


class Trainer:
    def __init__(self, config_path: str):
        """
        Initialize trainer
        
        Args:
            config_path: Path to configuration file
        """
        self.config = ConfigParser(config_path)
        self.setup_environment()
        self.setup_data()
        self.setup_model()
        self.setup_training()
    
    def setup_environment(self):
        """Set up training environment"""
        self.use_gpu = self.config.get_use_gpu()
        if self.use_gpu and not paddle.is_compiled_with_cuda():
            print("⚠️ GPU is not available, switching to CPU mode")
            self.use_gpu = False
        paddle.device.set_device('gpu' if self.use_gpu else 'cpu')
    
    def setup_data(self):
        """Set up datasets and data loaders"""
        # Create datasets
        train_dataset = AudioDataset(
            root_dir=os.path.dirname(self.config.get_train_data_path()),
            csv_file=self.config.get_train_data_path(),
            is_full_path=self.config.get_is_full_path(),
            adjust_audio_length=self.config.get_adjust_audio_length()
        )
        val_dataset = AudioDataset(
            root_dir=os.path.dirname(self.config.get_val_data_path()),
            csv_file=self.config.get_val_data_path(),
            is_full_path=self.config.get_is_full_path(),
            adjust_audio_length=self.config.get_adjust_audio_length()
        )
        
        # Create data loaders
        self.train_loader = DataLoader(
            train_dataset,
            batch_size=self.config.get_batch_size(),
            shuffle=self.config.get_shuffle(),
            drop_last=self.config.get_drop_last()
        )
        self.val_loader = DataLoader(
            val_dataset,
            batch_size=self.config.get_batch_size(),
            shuffle=False
        )
        
        # Create feature extractor
        self.feature_extractor = FeatureExtractor(
            feature_type=self.config.get_feature_method(),
            **self.config.get_feature_args()
        )
    
    def setup_model(self):
        """Set up model, optimizer, scheduler, and loss function"""
        num_classes = self.train_loader.dataset.num_classes
        model_config = {
            'num_classes': num_classes,
            **self.config.get_system_config()
        }
        self.model = create_model(self.config.get_feature_method(), model_config)
        
        self.optimizer = create_optimizer(self.model, self.config.get_optimizer_config())
        self.scheduler = create_scheduler(self.optimizer, self.config.get_optimizer_config())
        self.criterion = create_loss_function(self.config.get_loss_config())
    
    def setup_training(self):
        """Set up training parameters"""
        self.epochs = self.config.get_max_epochs()
        self.log_freq = 10
        self.eval_freq = 1
        
        # 设置模型保存目录为项目根目录下的models文件夹
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.save_dir = os.path.join(project_root, 'models')
        os.makedirs(self.save_dir, exist_ok=True)
        
        # 设置日志保存目录为项目根目录下的log文件夹
        self.log_dir = os.path.join(project_root, 'log')
        os.makedirs(self.log_dir, exist_ok=True)
        
        self.model_save_name = self.config.get_model_save_name()
        
        # Setup logger
        log_file = os.path.join(self.log_dir, f"{self.model_save_name}_training.log")
        self.logger = get_logger('ppaudio.trainer') or setup_logger('ppaudio.trainer', log_file=log_file)
    
    def train(self):
        """Train the model"""
        best_val_acc = 0
        train_losses, train_accs, val_accs = [], [], []
        start_time = time.time()
        
        self.logger.info(f"Starting training with {self.epochs} epochs")
        self.logger.info(f"Training on {'GPU' if self.use_gpu else 'CPU'}")
        self.logger.info(f"Training dataset size: {len(self.train_loader.dataset)}")
        self.logger.info(f"Validation dataset size: {len(self.val_loader.dataset)}")
        
        for epoch in range(1, self.epochs + 1):
            self.logger.set_epoch(epoch, self.epochs)
            epoch_start_time = time.time()
            
            train_loss, train_acc = self.train_epoch(epoch)
            val_acc = self.validate(epoch)
            
            epoch_time = time.time() - epoch_start_time
            
            train_losses.append(train_loss)
            train_accs.append(train_acc)
            val_accs.append(val_acc)
            
            self.logger.info(f"Epoch {epoch} completed in {format_time(epoch_time)}")
            self.logger.info(f"Train loss: {train_loss:.4f}, Train acc: {train_acc:.4f}, Val acc: {val_acc:.4f}")
            
            if val_acc > best_val_acc:
                best_val_acc = val_acc
                self.save_model(f"{self.model_save_name}_best.pdparams")
                self.logger.info(f"New best model saved with validation accuracy: {val_acc:.4f}")
            
            if self.config.get_show_train_process():
                progress_plot_path = os.path.join(self.log_dir, "training_progress.png")
                plot_training_progress(train_losses, train_accs, val_accs, save_path=progress_plot_path)
                self.logger.info(f"Training progress plot saved to {progress_plot_path}")
            
            if isinstance(self.scheduler, paddle.optimizer.lr.LRScheduler):
                self.scheduler.step()
        
        total_time = time.time() - start_time
        self.logger.info(f"Training completed in {format_time(total_time)}")
        self.save_model(f"{self.model_save_name}_final.pdparams")
    
    def train_epoch(self, epoch: int) -> tuple:
        """Train for one epoch"""
        self.model.train()
        total_loss, total_correct, total_samples = 0, 0, 0
        epoch_loss, epoch_correct, epoch_samples = 0, 0, 0
        
        for batch_idx, (waveforms, labels) in enumerate(self.train_loader):
            self.logger.set_step(batch_idx + 1, len(self.train_loader))
            
            feats = self.feature_extractor(waveforms)
            logits = self.model(feats)
            loss = self.criterion(logits, labels)
            
            loss.backward()
            self.optimizer.step()
            self.optimizer.clear_grad()
            
            batch_loss = loss.item()
            total_loss += batch_loss
            epoch_loss += batch_loss
            
            preds = paddle.argmax(logits, axis=1)
            batch_correct = (preds == labels).sum().item()
            total_correct += batch_correct
            epoch_correct += batch_correct
            
            total_samples += labels.shape[0]
            epoch_samples += labels.shape[0]
            
            if (batch_idx + 1) % self.log_freq == 0:
                avg_loss = total_loss / self.log_freq
                avg_acc = total_correct / total_samples
                lr = self.optimizer.get_lr()
                
                self.logger.train(f"loss={avg_loss:.4f}, acc={avg_acc:.4f}, lr={lr:.6f}")
                
                total_loss, total_correct, total_samples = 0, 0, 0
        
        # Calculate epoch metrics
        epoch_avg_loss = epoch_loss / len(self.train_loader)
        epoch_avg_acc = epoch_correct / epoch_samples
        
        return epoch_avg_loss, epoch_avg_acc
    
    @paddle.no_grad()
    def validate(self, epoch: int) -> float:
        """Validate the model"""
        self.model.eval()
        total_correct, total_samples = 0, 0
        
        self.logger.info("Starting validation...")
        
        for waveforms, labels in self.val_loader:
            feats = self.feature_extractor(waveforms)
            logits = self.model(feats)
            preds = paddle.argmax(logits, axis=1)
            total_correct += (preds == labels).sum().item()
            total_samples += labels.shape[0]
        
        val_acc = total_correct / total_samples
        self.logger.eval(f"Validation accuracy: {val_acc:.4f}")
        return val_acc
    
    def save_model(self, filename: str):
        """Save the model"""
        save_path = os.path.join(self.save_dir, filename)
        paddle.save(self.model.state_dict(), save_path)
        self.logger.info(f"Model saved to {save_path}")


def train(config_path: str, log_file: Optional[str] = None):
    """
    Train a model using the specified configuration
    
    Args:
        config_path: Path to configuration file
        log_file: Optional path to log file. If not specified, logs will be saved in the same directory as the config file
    """
    trainer = Trainer(config_path)
    trainer.train()