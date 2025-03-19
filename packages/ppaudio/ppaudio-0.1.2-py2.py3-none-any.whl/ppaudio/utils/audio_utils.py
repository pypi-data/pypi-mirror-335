"""
Audio utility functions for ppaudio
"""

import os
import numpy as np
from scipy.io import wavfile
from typing import Tuple, List, Optional


def count_wav_files(directory: str) -> Tuple[int, List[str]]:
    """
    Count WAV files in a directory (recursively)
    
    Args:
        directory: Directory to search
        
    Returns:
        Tuple of (count, file_list)
    """
    wav_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.wav'):
                wav_files.append(os.path.join(root, file))
    return len(wav_files), wav_files


def get_wav_duration(filepath: str) -> float:
    """
    Get the duration of a WAV file in seconds
    
    Args:
        filepath: Path to WAV file
        
    Returns:
        Duration in seconds
    """
    samplerate, data = wavfile.read(filepath)
    num_samples = data.shape[0]
    duration = num_samples / float(samplerate)
    return duration


def pad_wav_file(filepath: str, target_duration: float, save_path: Optional[str] = None) -> np.ndarray:
    """
    Pad a WAV file to a target duration by repeating content
    
    Args:
        filepath: Path to WAV file
        target_duration: Target duration in seconds
        save_path: Optional path to save the padded WAV file
        
    Returns:
        Padded audio data as numpy array
    """
    samplerate, data = wavfile.read(filepath)
    num_samples = data.shape[0]
    current_duration = num_samples / float(samplerate)
    
    # Calculate padding
    padding_samples = int((target_duration - current_duration) * samplerate)
    
    if padding_samples <= 0:
        return data
    
    # Repeat data to reach target duration
    repeats = (padding_samples // num_samples) + 1
    padded_data = np.tile(data, (repeats + 1, 1) if len(data.shape) > 1 else repeats + 1)
    padded_data = padded_data[:num_samples + padding_samples]
    
    if save_path:
        wavfile.write(save_path, samplerate, padded_data.astype(np.int16))
    
    return padded_data


def adjust_dataset_lengths(directory: str, save_dir: Optional[str] = None) -> Tuple[int, float]:
    """
    Adjust all WAV files in a directory to the same length
    
    Args:
        directory: Directory containing WAV files
        save_dir: Optional directory to save adjusted files
        
    Returns:
        Tuple of (number of adjusted files, target duration)
    """
    count, wav_files = count_wav_files(directory)
    
    if count == 0:
        print("No WAV files found.")
        return 0, 0.0
    
    # Find the longest duration
    durations = [get_wav_duration(file) for file in wav_files]
    longest_duration = max(durations)
    
    # Adjust files
    adjusted_count = 0
    for filepath, duration in zip(wav_files, durations):
        if duration < longest_duration:
            if save_dir:
                filename = os.path.basename(filepath)
                save_path = os.path.join(save_dir, filename)
            else:
                save_path = filepath
                
            pad_wav_file(filepath, longest_duration, save_path)
            adjusted_count += 1
    
    return adjusted_count, longest_duration