#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志管理模块
提供统一的日志记录功能
"""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional


class ColoredFormatter(logging.Formatter):
    """带颜色的日志格式化器"""
    
    # ANSI颜色代码
    COLORS = {
        'DEBUG': '\033[36m',      # 青色
        'INFO': '\033[32m',       # 绿色
        'WARNING': '\033[33m',    # 黄色
        'ERROR': '\033[31m',      # 红色
        'CRITICAL': '\033[35m',   # 紫色
        'RESET': '\033[0m'        # 重置
    }
    
    def format(self, record):
        # 保存原始级别名称
        original_levelname = record.levelname
        
        # 添加颜色
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.COLORS['RESET']}"
        
        result = super().format(record)
        
        # 恢复原始级别名称
        record.levelname = original_levelname
        return result


def setup_logger(
    name: str,
    log_dir: str = "./logs",
    level: str = "INFO",
    log_to_file: bool = True,
    log_to_console: bool = True
) -> logging.Logger:
    """
    设置并返回配置好的日志记录器
    
    Args:
        name: 日志记录器名称
        log_dir: 日志文件保存目录
        level: 日志级别
        log_to_file: 是否写入文件
        log_to_console: 是否输出到控制台
        
    Returns:
        配置好的Logger实例
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # 清除已有处理器
    logger.handlers.clear()
    
    # 日志格式
    formatter = ColoredFormatter(
        fmt='%(asctime)s - %(levelname)s - [%(name)s] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 控制台处理器
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # 文件处理器
    if log_to_file:
        # 确保日志目录存在
        Path(log_dir).mkdir(parents=True, exist_ok=True)
        
        # 生成日志文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(log_dir, f"{name}_{timestamp}.log")
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_formatter = logging.Formatter(
            fmt='%(asctime)s - %(levelname)s - [%(name)s] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        logger.info(f"日志文件: {log_file}")
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    获取已存在的日志记录器，如果不存在则创建基础配置
    
    Args:
        name: 日志记录器名称
        
    Returns:
        Logger实例
    """
    return logging.getLogger(name)


class ProgressLogger:
    """进度日志记录器，用于显示处理进度"""
    
    def __init__(self, logger: logging.Logger, total: int, desc: str = "Processing"):
        self.logger = logger
        self.total = total
        self.desc = desc
        self.current = 0
        self.success_count = 0
        self.error_count = 0
        self.skip_count = 0
    
    def update(self, status: str = "success", message: str = ""):
        """更新进度"""
        self.current += 1
        
        if status == "success":
            self.success_count += 1
        elif status == "error":
            self.error_count += 1
        elif status == "skip":
            self.skip_count += 1
        
        # 每10个或最后一条记录日志
        if self.current % 10 == 0 or self.current == self.total:
            self.logger.info(
                f"{self.desc}: [{self.current}/{self.total}] "
                f"成功:{self.success_count} 失败:{self.error_count} 跳过:{self.skip_count}"
            )
    
    def log_item(self, item_name: str, status: str, message: str = ""):
        """记录单个项目"""
        if status == "success":
            self.logger.info(f"✓ {item_name}: {message}")
        elif status == "error":
            self.logger.error(f"✗ {item_name}: {message}")
        elif status == "skip":
            self.logger.warning(f"⊘ {item_name}: {message}")
        elif status == "info":
            self.logger.info(f"ℹ {item_name}: {message}")
    
    def summary(self):
        """输出汇总信息"""
        self.logger.info("=" * 60)
        self.logger.info(f"{self.desc} 完成!")
        self.logger.info(f"总计: {self.total}")
        self.logger.info(f"成功: {self.success_count}")
        self.logger.info(f"失败: {self.error_count}")
        self.logger.info(f"跳过: {self.skip_count}")
        self.logger.info("=" * 60)
