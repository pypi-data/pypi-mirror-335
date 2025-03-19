import os
import pandas as pd
from typing import Optional, Union, List
from pathlib import Path


def label_dataset(
    root_dir: Union[str, Path],
    output_path: Union[str, Path],
    ok_pattern: str = 'OK',
    ng_pattern: str = 'NG',
    ok_label: int = 1,
    ng_label: int = 0,
    audio_extensions: Optional[List[str]] = None,
    encoding: str = 'utf-8-sig'
) -> pd.DataFrame:
    """标注音频数据集，根据文件名中的特定模式（如'OK'/'NG'）自动生成标签。

    Args:
        root_dir (Union[str, Path]): 音频文件所在的根目录
        output_path (Union[str, Path]): 输出CSV文件的路径
        ok_pattern (str, optional): OK样本的文件名模式. Defaults to 'OK'.
        ng_pattern (str, optional): NG样本的文件名模式. Defaults to 'NG'.
        ok_label (int, optional): OK样本的标签值. Defaults to 1.
        ng_label (int, optional): NG样本的标签值. Defaults to 0.
        audio_extensions (Optional[List[str]], optional): 要处理的音频文件扩展名列表.
            默认为 ['.wav', '.mp3', '.flac', '.ogg'].
        encoding (str, optional): CSV文件的编码方式. Defaults to 'utf-8-sig'.

    Returns:
        pd.DataFrame: 包含文件路径和标签的DataFrame
    """
    if audio_extensions is None:
        audio_extensions = ['.wav', '.mp3', '.flac', '.ogg']
    
    # 确保路径是Path对象
    root_dir = Path(root_dir)
    output_path = Path(output_path)
    
    # 初始化数据列表
    data_list = []
    
    # 遍历根目录下的所有文件和子目录
    for root, _, files in os.walk(root_dir):
        for file in files:
            # 检查文件扩展名
            if not any(file.lower().endswith(ext) for ext in audio_extensions):
                continue
                
            # 构建完整的文件路径
            file_path = os.path.join(root, file)
            
            # 初始化标签为None（既不含OK也不含NG）
            label = None
            
            # 检查文件名是否包含OK或NG
            if ok_pattern in file:
                label = ok_label
            elif ng_pattern in file:
                label = ng_label
            
            # 如果找到有效标签，将数据添加到列表中
            if label is not None:
                data_list.append({
                    'index': len(data_list),
                    'file_path': file_path,
                    'label': label
                })
    
    # 创建DataFrame
    df = pd.DataFrame(data_list)
    
    # 如果没有找到任何有效数据
    if df.empty:
        print(f"警告：在目录 '{root_dir}' 中没有找到包含 '{ok_pattern}' 或 '{ng_pattern}' 的音频文件。")
        return df
    
    # 将相对路径转换为绝对路径
    df['file_path'] = df['file_path'].apply(lambda x: os.path.abspath(x))
    
    # 将DataFrame写入CSV文件
    if output_path:
        # 确保输出目录存在
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False, encoding=encoding)
        print(f"数据已写入 '{output_path}' 文件。")
        print(f"总共处理了 {len(df)} 个文件：")
        print(f"- {ok_pattern} 样本数量：{len(df[df['label'] == ok_label])}")
        print(f"- {ng_pattern} 样本数量：{len(df[df['label'] == ng_label])}")
    
    return df