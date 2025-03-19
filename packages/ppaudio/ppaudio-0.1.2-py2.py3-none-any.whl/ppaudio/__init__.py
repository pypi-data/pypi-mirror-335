"""
PPAudio - A PaddlePaddle-based audio classification toolkit
"""

# 在导入paddle之前设置环境变量
import os
import sys
import logging
import warnings

# 设置环境变量，禁用PaddlePaddle的调试日志
os.environ['GLOG_v'] = '0'
os.environ['GLOG_logtostderr'] = '0'
os.environ['GLOG_minloglevel'] = '3'  # 0=INFO, 1=WARNING, 2=ERROR, 3=FATAL
os.environ['FLAGS_eager_delete_tensor_gb'] = '0.0'
os.environ['FLAGS_allocator_strategy'] = 'naive_best_fit'
os.environ['FLAGS_fraction_of_gpu_memory_to_use'] = '0.1'
os.environ['FLAGS_call_stack_level'] = '0'

# 设置所有日志级别为WARNING
logging.getLogger().setLevel(logging.WARNING)

# 现在导入paddle
import paddle
# paddle.set_device('cpu')
paddle.disable_static()

# 尝试设置打印选项，如果失败则忽略
try:
    paddle.set_printoptions(precision=4, suppress=True)
except TypeError:
    # 如果不支持 suppress 参数，则只设置 precision
    paddle.set_printoptions(precision=4)

# 设置paddle日志级别
logging.getLogger("paddle").setLevel(logging.ERROR)

# 禁用特定的paddle日志
for logger_name in ["paddle", "paddle.distributed.fleet.launch.launch_utils", "paddle.distributed.fleet.base.fleet_base"]:
    paddle_logger = logging.getLogger(logger_name)
    paddle_logger.setLevel(logging.ERROR)
    paddle_logger.propagate = False

# 忽略所有警告
warnings.filterwarnings('ignore')

# 导入其他模块
from .api import train, test, test_single, compare
from .utils.logger import setup_logger, get_logger

logger = get_logger('ppaudio') or setup_logger('ppaudio', log_file='default')

__all__ = ['train', 'test', 'test_single', 'compare']
__version__ = '0.1.0'
__all__ = ['train', 'test', 'test_single', 'compare', 'setup_logger']