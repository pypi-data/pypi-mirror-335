import os
import glob
import numpy as np
from scipy.io import wavfile


def count_wav_files(directory):
    """统计WAV文件数量"""
    wav_files = glob.glob(directory + '/**/*.wav', recursive=True)
    return len(wav_files), wav_files


def get_wav_duration(filepath):
    """获取WAV文件时长"""
    samplerate, data = wavfile.read(filepath)
    num_samples = data.shape[0]
    duration = num_samples / float(samplerate)
    return duration


def pad_wav_file(filepath, target_duration, save_path=None):
    """调整WAV文件长度"""
    samplerate, data = wavfile.read(filepath)
    num_samples = data.shape[0]
    current_duration = num_samples / float(samplerate)
    padding_samples = int((target_duration - current_duration) * samplerate)
    
    if padding_samples > 0:
        # 重复数据直到达到目标长度
        padded_data = np.concatenate([data] * ((padding_samples // data.shape[0]) + 1))
        padded_data = padded_data[:padding_samples + num_samples]
        
        if save_path:
            wavfile.write(save_path, samplerate, padded_data.astype(np.int16))
            return True
        return padded_data
    return data


def adjust_dataset_lengths(directory, save_dir=None):
    """调整数据集中所有WAV文件的长度"""
    count, wav_files = count_wav_files(directory)
    
    if count == 0:
        print("未找到WAV文件")
        return 0, 0.0
    
    # 找出最长时长
    durations = [get_wav_duration(file) for file in wav_files]
    longest_duration = max(durations)
    
    # 调整文件
    adjusted_count = 0
    for filepath, duration in zip(wav_files, durations):
        if duration < longest_duration:
            if save_dir:
                filename = os.path.basename(filepath)
                save_path = os.path.join(save_dir, filename)
            else:
                save_path = filepath
                
            if pad_wav_file(filepath, longest_duration, save_path):
                adjusted_count += 1
                print(f"已调整文件：{filepath}")
    
    print(f"总共调整了{adjusted_count}个文件")
    return adjusted_count, longest_duration