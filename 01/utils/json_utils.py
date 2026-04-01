#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JSON操作工具模块
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, Tuple


def load_json(file_path: str, encoding: str = 'utf-8') -> Optional[Dict[str, Any]]:
    """
    安全加载JSON文件
    
    Args:
        file_path: JSON文件路径
        encoding: 文件编码
        
    Returns:
        JSON数据字典，失败返回None
    """
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"文件不存在: {file_path}")
        return None
    except json.JSONDecodeError as e:
        print(f"JSON解析错误 {file_path}: {e}")
        return None
    except Exception as e:
        print(f"读取文件错误 {file_path}: {e}")
        return None


def save_json(
    data: Dict[str, Any],
    file_path: str,
    encoding: str = 'utf-8',
    indent: int = 2,
    ensure_ascii: bool = False
) -> bool:
    """
    安全保存JSON文件
    
    Args:
        data: 要保存的数据
        file_path: 目标文件路径
        encoding: 文件编码
        indent: 缩进空格数
        ensure_ascii: 是否确保ASCII编码
        
    Returns:
        是否成功
    """
    try:
        # 确保目录存在
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding=encoding) as f:
            json.dump(data, f, ensure_ascii=ensure_ascii, indent=indent)
        return True
    except Exception as e:
        print(f"保存JSON失败 {file_path}: {e}")
        return False


def clean_json_fields(
    data: Dict[str, Any],
    keep_fields: List[str],
    default_value: Any = ""
) -> Dict[str, Any]:
    """
    清洗JSON数据，仅保留指定字段
    
    Args:
        data: 原始数据
        keep_fields: 要保留的字段列表
        default_value: 缺失字段的默认值
        
    Returns:
        清洗后的数据
    """
    return {field: data.get(field, default_value) for field in keep_fields}


def merge_json_data(
    base_data: Dict[str, Any],
    override_data: Dict[str, Any],
    deep_merge: bool = True
) -> Dict[str, Any]:
    """
    合并两个JSON数据
    
    Args:
        base_data: 基础数据
        override_data: 覆盖数据
        deep_merge: 是否深度合并
        
    Returns:
        合并后的数据
    """
    result = base_data.copy()
    
    for key, value in override_data.items():
        if deep_merge and isinstance(value, dict) and key in result and isinstance(result[key], dict):
            result[key] = merge_json_data(result[key], value, deep_merge)
        else:
            result[key] = value
    
    return result


def validate_json_schema(
    data: Dict[str, Any],
    required_keys: List[str]
) -> Tuple[bool, List[str]]:
    """
    验证JSON数据是否包含必需的字段
    
    Args:
        data: 要验证的数据
        required_keys: 必需的字段列表
        
    Returns:
        (是否有效, 缺失的字段列表)
    """
    missing = [key for key in required_keys if key not in data]
    return len(missing) == 0, missing


def extract_json_from_text(text: str) -> Optional[Dict[str, Any]]:
    """
    从文本中提取JSON数据
    
    Args:
        text: 包含JSON的文本
        
    Returns:
        提取的JSON数据或None
    """
    import re
    
    try:
        # 尝试提取代码块 ```json ... ```
        match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
        if match:
            return json.loads(match.group(1))
        
        # 尝试提取最外层 {}
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        
        return None
    except json.JSONDecodeError:
        return None


def compare_json_data(
    data1: Dict[str, Any],
    data2: Dict[str, Any],
    ignore_keys: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    比较两个JSON数据的差异
    
    Args:
        data1: 第一个数据
        data2: 第二个数据
        ignore_keys: 忽略的字段
        
    Returns:
        差异信息
    """
    if ignore_keys is None:
        ignore_keys = []
    
    differences = {
        'only_in_1': {},
        'only_in_2': {},
        'different': {}
    }
    
    all_keys = set(data1.keys()) | set(data2.keys())
    
    for key in all_keys:
        if key in ignore_keys:
            continue
        
        if key in data1 and key not in data2:
            differences['only_in_1'][key] = data1[key]
        elif key in data2 and key not in data1:
            differences['only_in_2'][key] = data2[key]
        elif data1.get(key) != data2.get(key):
            differences['different'][key] = {
                'value1': data1[key],
                'value2': data2[key]
            }
    
    return differences


def batch_update_json_files(
    folder_path: str,
    update_func: callable,
    pattern: str = "*.json",
    recursive: bool = True
) -> Dict[str, int]:
    """
    批量更新JSON文件
    
    Args:
        folder_path: 文件夹路径
        update_func: 更新函数，接收并返回字典
        pattern: 文件匹配模式
        recursive: 是否递归
        
    Returns:
        统计信息
    """
    stats = {'total': 0, 'success': 0, 'error': 0}
    
    path_obj = Path(folder_path)
    if not path_obj.exists():
        return stats
    
    if recursive:
        files = list(path_obj.rglob(pattern))
    else:
        files = list(path_obj.glob(pattern))
    
    for file_path in files:
        stats['total'] += 1
        
        data = load_json(str(file_path))
        if data is None:
            stats['error'] += 1
            continue
        
        try:
            updated_data = update_func(data)
            if save_json(updated_data, str(file_path)):
                stats['success'] += 1
            else:
                stats['error'] += 1
        except Exception as e:
            print(f"更新失败 {file_path}: {e}")
            stats['error'] += 1
    
    return stats
