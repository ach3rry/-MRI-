#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件操作工具模块
"""

import os
import shutil
from pathlib import Path
from typing import List, Iterator, Optional, Callable


def find_files_by_pattern(
    root_dir: str,
    pattern: str = "*",
    extensions: Optional[List[str]] = None,
    recursive: bool = True
) -> List[str]:
    """
    根据模式查找文件
    
    Args:
        root_dir: 根目录
        pattern: 文件名模式
        extensions: 文件扩展名列表（如 ['.jpg', '.png']）
        recursive: 是否递归查找
        
    Returns:
        匹配的文件路径列表
    """
    root_path = Path(root_dir)
    if not root_path.exists():
        return []
    
    results = []
    
    if recursive:
        files = root_path.rglob(pattern)
    else:
        files = root_path.glob(pattern)
    
    for file_path in files:
        if not file_path.is_file():
            continue
        
        if extensions:
            if file_path.suffix.lower() in [ext.lower() for ext in extensions]:
                results.append(str(file_path))
        else:
            results.append(str(file_path))
    
    return sorted(results)


def find_gjb_folders(root_dir: str, recursive: bool = True) -> List[str]:
    """
    查找所有以GJB开头的文件夹
    
    Args:
        root_dir: 根目录
        recursive: 是否递归查找
        
    Returns:
        GJB文件夹路径列表
    """
    root_path = Path(root_dir)
    if not root_path.exists():
        return []
    
    results = []
    
    if recursive:
        dirs = root_path.rglob("GJB*")
    else:
        dirs = root_path.glob("GJB*")
    
    for dir_path in dirs:
        if dir_path.is_dir():
            results.append(str(dir_path))
    
    return sorted(results)


def find_folders_by_prefix(root_dir: str, prefix: str, recursive: bool = True) -> List[str]:
    """
    查找指定前缀的文件夹
    
    Args:
        root_dir: 根目录
        prefix: 文件夹前缀
        recursive: 是否递归查找
        
    Returns:
        文件夹路径列表
    """
    root_path = Path(root_dir)
    if not root_path.exists():
        return []
    
    results = []
    
    if recursive:
        dirs = root_path.rglob(f"{prefix}*")
    else:
        dirs = root_path.glob(f"{prefix}*")
    
    for dir_path in dirs:
        if dir_path.is_dir():
            results.append(str(dir_path))
    
    return sorted(results)


def ensure_dir(dir_path: str) -> str:
    """
    确保目录存在，不存在则创建
    
    Args:
        dir_path: 目录路径
        
    Returns:
        目录路径
    """
    Path(dir_path).mkdir(parents=True, exist_ok=True)
    return dir_path


def get_gjb_id_from_path(path: str) -> Optional[str]:
    """
    从路径中提取GJB编号
    
    Args:
        path: 文件或目录路径
        
    Returns:
        GJB编号（如GJB0000001）或None
    """
    path_obj = Path(path)
    
    # 先检查当前文件名/文件夹名
    if path_obj.name.startswith("GJB"):
        return path_obj.name
    
    # 检查父目录
    for parent in path_obj.parents:
        if parent.name.startswith("GJB"):
            return parent.name
    
    return None


def copy_directory_tree(src: str, dst: str, overwrite: bool = True) -> bool:
    """
    复制目录树
    
    Args:
        src: 源目录
        dst: 目标目录
        overwrite: 是否覆盖已存在的目标
        
    Returns:
        是否成功
    """
    try:
        if os.path.exists(dst):
            if overwrite:
                shutil.rmtree(dst)
            else:
                return False
        
        shutil.copytree(src, dst)
        return True
    except Exception as e:
        print(f"复制目录失败 {src} -> {dst}: {e}")
        return False


def delete_folders_by_pattern(root_dir: str, pattern: Callable[[str], bool]) -> int:
    """
    删除符合条件的文件夹
    
    Args:
        root_dir: 根目录
        pattern: 判断函数，接收文件夹名返回是否删除
        
    Returns:
        删除的文件夹数量
    """
    deleted_count = 0
    
    for root, dirs, _ in os.walk(root_dir, topdown=False):
        for dir_name in dirs:
            if pattern(dir_name):
                dir_path = os.path.join(root, dir_name)
                try:
                    shutil.rmtree(dir_path)
                    deleted_count += 1
                except Exception as e:
                    print(f"删除失败 {dir_path}: {e}")
    
    return deleted_count


def get_folder_size(folder_path: str) -> int:
    """
    获取文件夹大小（字节）
    
    Args:
        folder_path: 文件夹路径
        
    Returns:
        文件夹大小
    """
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)
    return total_size


def format_size(size_bytes: int) -> str:
    """
    格式化文件大小显示
    
    Args:
        size_bytes: 字节数
        
    Returns:
        格式化后的字符串
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def safe_filename(filename: str) -> str:
    """
    将字符串转换为安全的文件名
    
    Args:
        filename: 原始文件名
        
    Returns:
        安全的文件名
    """
    # 替换不安全的字符
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename.strip()
