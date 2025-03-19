# ppaudio

基于 PaddlePaddle 的简单音频分类库。

## 功能特点

- 简单易用的音频分类 API
- 支持多种音频分类场景：
  - 工业噪声检测
  - 风扇噪声分类
  - 发动机声音分析
  - 动物声音分类
  - 音乐流派分类
- 多种特征提取方法
- 丰富的神经网络架构
- 音频分析可视化工具

## 安装

```bash
pip install ppaudio
```

## 快速开始

1. 准备 CSV 格式的数据：
   - train_data.csv（训练数据）
   - val_data.csv（验证数据）
   - test_data.csv（测试数据）

   每个 CSV 文件应包含两列：音频文件路径和标签（0 或 1）。

2. 创建配置文件（例如 `motor.yaml`）：

```yaml
# 数据集参数
dataset_conf:
  dataset:
    adjust_audio_length: True
    use_dB_normalization: True
    is_full_path: False
  sampler:
    batch_size: 64
    shuffle: True
    drop_last: True
  train_data: 'dataset/train_data.csv'
  val_data: 'dataset/val_data.csv'
  test_data: 'dataset/test_data.csv'

# 预处理参数
preprocess_conf:
  feature_method: 'LogMelSpectrogram'
  method_args:
    sr: 48000
    n_fft: 1024
    hop_length: 512
    win_length: 1024
    window: 'hann'
    f_min: 50
    f_max: 14000
    n_mels: 64

# 损失函数配置
loss_conf:
  criterion: 'CrossEntropyLoss'

# 优化器配置
optimizer_conf:
  optimizer: 'Adam'
  optimizer_args:
    learning_rate: 0.001

# 系统配置
sys_conf:
  use_GPU: True
  max_epoch: 60
  show_train_process: True
  save_train_process: False
  model_save_name: 'model'
```

3. 训练模型：

```python
import ppaudio

# 训练模型
ppaudio.train(config_path='motor.yaml')
```

4. 测试模型：

```python
# 在数据集上测试
ppaudio.test('model', 'dataset/test_data.csv')

# 测试单个音频文件
ppaudio.test_single('model', '123.wav')

# 比较两个音频文件
ppaudio.compare('model', '123.wav', '456.wav', show_pic=True)
```

## 数据标注工具

ppaudio 提供了便捷的数据标注功能，可以根据文件名自动生成标签：

```python
from ppaudio.core import label_dataset

# 标注数据集
label_dataset(
    root_dir='your_audio_folder',    # 音频文件夹路径
    output_path='labels.csv',        # 输出CSV文件路径
    ok_pattern='OK',                 # OK样本的文件名模式
    ng_pattern='NG',                 # NG样本的文件名模式
    ok_label=1,                      # OK样本的标签值
    ng_label=0                       # NG样本的标签值
)
```

## 使用示例

1. 工业噪声检测：

```python
import ppaudio

# 标注数据
ppaudio.core.label_dataset('audio_samples/', 'dataset.csv')

# 训练模型
ppaudio.train(config_path='motor.yaml')

# 测试新样本
ppaudio.test_single('model', 'new_sample.wav')
```

2. 音乐流派分类：

```python
import ppaudio

# 训练模型（使用不同的配置）
ppaudio.train(config_path='music.yaml')

# 比较两个音乐样本
ppaudio.compare('model', 'rock.wav', 'jazz.wav', show_pic=True)
```

## 贡献

欢迎提交 Pull Request 来帮助改进这个项目！

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。