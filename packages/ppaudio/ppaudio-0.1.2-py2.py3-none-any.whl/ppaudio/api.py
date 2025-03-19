"""
ppaudio API模块

本模块提供了ppaudio库的主要接口，包括模型训练、测试、单文件预测和音频比较功能。
用户可以通过这些接口轻松地进行声音分类任务。
"""

import os
import logging
import warnings
import paddle
from .core.trainer import Trainer
from .core.dataset import AudioDataset
from .core.features import FeatureExtractor
from .models.model_factory import create_model
from .utils.logger import setup_logger, get_logger

# 设置日志级别和警告过滤
os.environ['GLOG_v'] = '0'
os.environ['GLOG_logtostderr'] = '0'
logging.getLogger("paddle").setLevel(logging.ERROR)
warnings.filterwarnings('ignore')

# 初始化默认日志记录器（如果还没有创建）
default_logger = get_logger('ppaudio') or setup_logger('ppaudio', log_file='default')


def train(config_path):
    """
    训练声音分类模型

    Args:
        config_path (str): 配置文件的路径，通常是一个YAML文件

    该函数会根据配置文件设置训练参数，加载数据集，并开始训练过程。
    训练完成后，模型会被保存到配置文件中指定的位置。
    """
    trainer = Trainer(config_path)
    trainer.train()


import logging
import os
import paddle
from .config.config_parser import ConfigParser
from .models.model_factory import create_model
from .core.dataset import AudioDataset
from .core.features import FeatureExtractor
from .utils.logger import setup_logger, get_logger

def test(config_path, model_path=None, test_csv=None):
    """
    测试已训练的声音分类模型

    Args:
        config_path (str): 配置文件的路径
        model_path (str, optional): 已训练模型的路径。如果为None，会从配置文件中读取
        test_csv (str, optional): 测试数据集的CSV文件路径。如果为None，会从配置文件中读取

    Returns:
        dict: 包含测试结果的字典，包括总样本数、正确预测数和准确率

    该函数会加载指定的模型和测试数据集，然后在测试集上评估模型的性能。
    """
    logger = get_logger('ppaudio.test') or setup_logger('ppaudio.test', log_file='default')
    
    if not config_path:
        raise ValueError("配置文件路径不能为空")
    
    # 加载配置
    config = ConfigParser(config_path)
    
    # 获取系统配置和数据集配置
    sys_config = config.get_system_config()
    dataset_config = config.get_dataset_config()
    
    # 处理模型路径
    if model_path is None:
        model_path = sys_config.get('model_path')
        if not model_path:
            raise ValueError("未提供model_path，且配置文件中也未指定")
    
    # 处理测试数据CSV路径
    if test_csv is None:
        test_csv = dataset_config.get('test_data')
        if not test_csv:
            raise ValueError("未提供test_csv，且配置文件中也未指定")
    
    # 处理路径
    is_full_path = dataset_config.get('dataset', {}).get('is_full_path', False)
    test_data_root = dataset_config.get('test_data_root', './dataset/test_data')
    
    if not is_full_path:
        model_path = os.path.normpath(model_path)
        test_csv = os.path.normpath(test_csv)
    
    # 确保文件存在
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"模型文件不存在: {model_path}")
    if not os.path.exists(test_csv):
        raise FileNotFoundError(f"测试数据CSV文件不存在: {test_csv}")
    
    # 加载数据集
    try:
        dataset = AudioDataset(
            root_dir=test_data_root,
            csv_file=test_csv,
            is_full_path=is_full_path,
            adjust_audio_length=dataset_config.get('dataset', {}).get('adjust_audio_length', False)
        )
    except Exception as e:
        logger.error(f"加载数据集时出错: {str(e)}")
        raise
    
    # 创建模型
    model = create_model(sys_config.get('model_type', 'cnn14'), num_classes=2)
    
    # 加载模型参数
    try:
        state_dict = paddle.load(model_path)
        model_info = state_dict.pop('model_info', None)
        model.set_state_dict(state_dict)
    except Exception as e:
        logger.error(f"加载模型参数时出错: {str(e)}")
        raise
    
    if model_info:
        logger.info(f"加载的模型信息: {model_info}")
    else:
        logger.warning("模型中没有保存模型信息")
    
    # 创建特征提取器
    preprocess_config = config.get_preprocess_config()
    feature_method = preprocess_config.get('feature_method', 'LogMelSpectrogram')
    method_args = preprocess_config.get('method_args', {})
    feature_extractor = FeatureExtractor(feature_method=feature_method, **method_args)
    
    # 进行预测
    correct = 0
    total = 0
    model.eval()
    
    with paddle.no_grad():
        for waveform, label in dataset:
            try:
                feats = feature_extractor.extract_features(waveform.reshape(1, -1))
                logits = model(feats)
                pred = paddle.argmax(logits, axis=1).item()
                
                total += 1
                if pred == label:
                    correct += 1
            except Exception as e:
                logger.warning(f"处理样本时出错: {str(e)}")
                continue
    
    if total == 0:
        logger.error("没有成功处理任何样本")
        return {'total': 0, 'correct': 0, 'accuracy': 0.0}
    
    accuracy = correct / total
    logger.info(f"测试完成: 准确率 = {accuracy:.4f} (正确: {correct}, 总数: {total})")
    
    return {
        'total': total,
        'correct': correct,
        'accuracy': accuracy
    }


def test_single(model_path, wav_path, save_vis=False, config_path=None):
    """
    使用已训练的模型预测单个音频文件的类别

    Args:
        model_path (str): 已训练模型的路径
        wav_path (str): 要预测的音频文件路径
        save_vis (bool, optional): 是否保存可视化结果
        config_path (str, optional): 配置文件的路径。如果为None，会尝试在模型目录下查找

    Returns:
        dict: 包含预测结果的字典，包括预测的类别和置信度

    该函数会加载指定的模型，然后对给定的音频文件进行分类预测。
    如果save_vis为True，还会生成并保存音频的波形图和频谱图。
    """
    logger = get_logger('ppaudio.test_single') or setup_logger('ppaudio.test_single', log_file='default')
    
    # 如果没有提供配置文件，尝试在模型目录下找
    if config_path is None:
        model_dir = os.path.dirname(model_path)
        for file in os.listdir(model_dir):
            if file.endswith('.yaml') or file.endswith('.yml'):
                config_path = os.path.join(model_dir, file)
                break
    
    if not config_path:
        logger.warning("未找到配置文件，使用默认配置")
        
    # 加载配置
    if config_path:
        from .config.config_parser import ConfigParser
        config = ConfigParser(config_path)
        preprocess_config = config.get_preprocess_config()
        feature_method = preprocess_config.get('feature_method', 'LogMelSpectrogram')
        method_args = preprocess_config.get('method_args', {})
        model_config = config.get_system_config()
    else:
        feature_method = 'LogMelSpectrogram'
        method_args = {}
        model_config = {'model_type': 'cnn14'}
    
    # 创建模型
    from .models.model_factory import create_model
    model = create_model(model_config.get('model_type', 'cnn14'), num_classes=2)
    
    # 加载模型参数
    model.set_state_dict(paddle.load(model_path))
    
    # 创建特征提取器
    feature_extractor = FeatureExtractor(feature_method=feature_method, **method_args)
    
    # 加载音频
    from paddleaudio import load
    waveform, sr = load(wav_path, mono=True, dtype='float32')
    
    # 提取特征
    feats = feature_extractor.extract_features(waveform.reshape(1, -1))
    
    # 预测
    model.eval()
    with paddle.no_grad():
        logits = model(feats)
        probs = paddle.nn.functional.softmax(logits, axis=1)
        pred = paddle.argmax(logits, axis=1).item()
        prob = probs[0][pred].item()
    
    logger.info(f"预测结果: 类别 = {pred}, 置信度 = {prob:.4f}")
    
    # 如果需要保存可视化结果
    if save_vis:
        from .utils.visualization import plot_waveform, plot_spectrogram
        import matplotlib.pyplot as plt
        
        # 绘制波形图
        plt.figure(figsize=(12, 6))
        plt.subplot(2, 1, 1)
        plt.plot(waveform)
        plt.title('波形图')
        
        # 绘制频谱图
        plt.subplot(2, 1, 2)
        plt.imshow(feats.numpy()[0].T, aspect='auto', origin='lower')
        plt.colorbar(format='%+2.0f dB')
        plt.title('特征图')
        
        # 保存图像到log目录
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        log_dir = os.path.join(project_root, 'log')
        os.makedirs(log_dir, exist_ok=True)
        vis_path = os.path.join(log_dir, f"{os.path.splitext(os.path.basename(wav_path))[0]}_analysis.png")
        plt.tight_layout()
        plt.savefig(vis_path)
        plt.close()
        logger.info(f"可视化结果已保存到: {vis_path}")
    
    return {
        'prediction': pred,
        'probability': prob
    }


def compare(model_path, wav1, wav2, show_pic=True, config_path=None):
    """
    比较两个音频文件的分类结果

    Args:
        model_path (str): 已训练模型的路径
        wav1 (str): 第一个音频文件的路径
        wav2 (str): 第二个音频文件的路径
        show_pic (bool, optional): 是否显示比较的可视化结果
        config_path (str, optional): 配置文件的路径。如果为None，会尝试在模型目录下查找

    Returns:
        dict: 包含比较结果的字典，包括两个文件的预测类别、概率分布和是否属于同一类别

    该函数会加载指定的模型，然后对两个给定的音频文件进行分类预测并比较结果。
    如果show_pic为True，还会生成并保存两个音频的波形图和频谱图的对比图。
    """
    logger = get_logger('ppaudio.compare') or setup_logger('ppaudio.compare', log_file='default')
    
    # 如果没有提供配置文件，尝试在模型目录下找
    if config_path is None:
        model_dir = os.path.dirname(model_path)
        for file in os.listdir(model_dir):
            if file.endswith('.yaml') or file.endswith('.yml'):
                config_path = os.path.join(model_dir, file)
                break
    
    if not config_path:
        logger.warning("未找到配置文件，使用默认配置")
        
    # 加载配置
    if config_path:
        from .config.config_parser import ConfigParser
        config = ConfigParser(config_path)
        preprocess_config = config.get_preprocess_config()
        feature_method = preprocess_config.get('feature_method', 'LogMelSpectrogram')
        method_args = preprocess_config.get('method_args', {})
        model_config = config.get_system_config()
    else:
        feature_method = 'LogMelSpectrogram'
        method_args = {}
        model_config = {'model_type': 'cnn14'}
    
    # 创建模型
    from .models.model_factory import create_model
    model = create_model(model_config.get('model_type', 'cnn14'), num_classes=2)
    
    # 加载模型参数
    model.set_state_dict(paddle.load(model_path))
    
    # 创建特征提取器
    feature_extractor = FeatureExtractor(feature_method=feature_method, **method_args)
    
    # 加载音频
    from paddleaudio import load
    waveform1, sr1 = load(wav1, mono=True, dtype='float32')
    waveform2, sr2 = load(wav2, mono=True, dtype='float32')
    
    # 提取特征
    feats1 = feature_extractor.extract_features(waveform1.reshape(1, -1))
    feats2 = feature_extractor.extract_features(waveform2.reshape(1, -1))
    
    # 预测
    model.eval()
    with paddle.no_grad():
        logits1 = model(feats1)
        logits2 = model(feats2)
        probs1 = paddle.nn.functional.softmax(logits1, axis=1)
        probs2 = paddle.nn.functional.softmax(logits2, axis=1)
        pred1 = paddle.argmax(logits1, axis=1).item()
        pred2 = paddle.argmax(logits2, axis=1).item()
    
    logger.info(f"文件1预测结果: 类别 = {pred1}, 置信度 = {probs1[0][pred1].item():.4f}")
    logger.info(f"文件2预测结果: 类别 = {pred2}, 置信度 = {probs2[0][pred2].item():.4f}")
    
    # 可视化比较
    if show_pic:
        from .utils.visualization import compare_spectrograms
        import matplotlib.pyplot as plt
        
        plt.figure(figsize=(12, 8))
        
        # 绘制波形图
        plt.subplot(2, 2, 1)
        plt.plot(waveform1)
        plt.title(f'波形图1 - 类别: {pred1}')
        
        plt.subplot(2, 2, 2)
        plt.plot(waveform2)
        plt.title(f'波形图2 - 类别: {pred2}')
        
        # 绘制频谱图
        plt.subplot(2, 2, 3)
        plt.imshow(feats1.numpy()[0].T, aspect='auto', origin='lower')
        plt.colorbar(format='%+2.0f dB')
        plt.title('特征图1')
        
        plt.subplot(2, 2, 4)
        plt.imshow(feats2.numpy()[0].T, aspect='auto', origin='lower')
        plt.colorbar(format='%+2.0f dB')
        plt.title('特征图2')
        
        # 保存或显示图像到log目录
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        log_dir = os.path.join(project_root, 'log')
        os.makedirs(log_dir, exist_ok=True)
        save_path = os.path.join(log_dir, f"compare_{os.path.basename(wav1)}_{os.path.basename(wav2)}.png")
        plt.tight_layout()
        plt.savefig(save_path)
        if show_pic:
            plt.show()
        plt.close()
        logger.info(f"比较结果已保存到: {save_path}")
    
    return {
        'prediction1': pred1,
        'prediction2': pred2,
        'probabilities1': probs1.numpy()[0],
        'probabilities2': probs2.numpy()[0],
        'are_same_class': pred1 == pred2
    }