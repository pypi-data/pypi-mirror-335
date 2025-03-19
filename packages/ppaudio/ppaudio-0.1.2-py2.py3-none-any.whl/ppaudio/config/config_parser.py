import yaml
import os


class ConfigParser:
    def __init__(self, config_path):
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self):
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"配置文件未找到: {self.config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        return config

    def get_dataset_config(self):
        return self.config.get('dataset_conf', {})

    def get_preprocess_config(self):
        return self.config.get('preprocess_conf', {})

    def get_loss_config(self):
        return self.config.get('loss_conf', {})

    def get_optimizer_config(self):
        return self.config.get('optimizer_conf', {})

    def get_system_config(self):
        return self.config.get('sys_conf', {})