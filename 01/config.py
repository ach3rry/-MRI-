#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据处理系统配置模块
统一管理所有配置参数
"""

import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Tuple, Optional


@dataclass
class DataConfig:
    """数据路径配置"""
    # 输入数据根目录
    input_dir: str = "./202505-202506"
    # 测试集输出目录
    test_set_dir: str = "./测试集"
    # 模型路径
    model_path: str = "./model"
    # 标签生成模型路径
    label_model_path: str = "./qwen3-1.7B"
    # 输出目录
    output_dir: str = "./output"
    # 日志目录
    log_dir: str = "./logs"


@dataclass
class ReportConfig:
    """报告提取配置"""
    # 报告单图片文件名
    report_filename: str = "报告单.jpg"
    # CSV输出文件名
    csv_filename: str = "medical_reports.csv"
    # 需要提取的字段
    required_fields: List[str] = field(default_factory=lambda: [
        '姓名', '性别', '年龄', '影像号', '科室', '床位', '床号',
        '检查时间', '报告时间', '审核时间', '复查时间',
        '检查方法', 'MR表现', '诊断意见',
        '检查者', '报告医师', '实习医师', '审核医师', '复审医师'
    ])
    # 保留的核心字段（清洗后）
    keep_fields: List[str] = field(default_factory=lambda: [
        "检查方法", "MR表现", "诊断意见", "顺序编号", "文件路径"
    ])


@dataclass
class DicomConfig:
    """DICOM转换配置"""
    # DICOM文件扩展名
    dicom_extensions: List[str] = field(default_factory=lambda: ['.dcm', '.dicom'])
    # NIfTI输出扩展名
    nifti_extension: str = ".nii"
    # 序列命名格式
    sequence_pattern: str = "{gjb_id}_{sequence_num:02d}.nii"


@dataclass
class VideoConfig:
    """视频转换配置"""
    # 输出帧率
    fps: int = 24
    # 输出分辨率 (width, height)
    resolution: Tuple[int, int] = (512, 512)
    # 切片轴 (0=X, 1=Y, 2=Z)
    axis: int = 2
    # 视频编码器
    video_codec: str = "mp4v"


@dataclass
class LabelConfig:
    """标签生成配置"""
    # 调试模式
    debug_mode: bool = True
    # 温度参数
    temperature: float = 0.01
    # 最大生成token数
    max_new_tokens: int = 1024
    # 是否跳过已处理
    skip_processed: bool = False
    # 主要病变类型选项
    valid_lesion_types: List[str] = field(default_factory=lambda: [
        "正常", "退行性疾病", "半月板疾病", "韧带疾病", 
        "骨软骨疾病", "炎症性疾病", "术后状态", "混合型"
    ])


@dataclass
class SystemConfig:
    """系统整体配置"""
    # 数据处理流水线阶段
    stages: List[str] = field(default_factory=lambda: [
        "extract_reports",      # 1. 提取医疗报告
        "convert_dicom",        # 2.1 DICOM转NIfTI
        "convert_video",        # 2.2 NIfTI转MP4
        "clean_json",           # 3.1 清洗JSON
        "copy_to_test",         # 3.2 复制到测试集
        "update_paths",         # 4. 更新路径
        "generate_labels",      # 5. 生成标签
    ])
    # 是否启用各阶段
    enable_report_extraction: bool = True
    enable_dicom_conversion: bool = True
    enable_video_conversion: bool = True
    enable_json_cleaning: bool = True
    enable_copy_to_test: bool = True
    enable_path_update: bool = True
    enable_label_generation: bool = True
    # 日志级别
    log_level: str = "INFO"
    # 日志格式
    log_format: str = "%(asctime)s - %(levelname)s - [%(name)s] - %(message)s"


class Config:
    """全局配置类"""
    
    def __init__(self):
        self.data = DataConfig()
        self.report = ReportConfig()
        self.dicom = DicomConfig()
        self.video = VideoConfig()
        self.label = LabelConfig()
        self.system = SystemConfig()
    
    def ensure_directories(self):
        """确保所有必要的目录存在"""
        dirs_to_create = [
            self.data.input_dir,
            self.data.test_set_dir,
            self.data.output_dir,
            self.data.log_dir,
        ]
        for dir_path in dirs_to_create:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    def validate(self) -> Tuple[bool, List[str]]:
        """验证配置有效性"""
        errors = []
        
        # 检查输入目录
        if not os.path.exists(self.data.input_dir):
            errors.append(f"输入目录不存在: {self.data.input_dir}")
        
        # 检查模型路径（如果启用了相关阶段）
        if self.system.enable_report_extraction and not os.path.exists(self.data.model_path):
            errors.append(f"报告提取模型路径不存在: {self.data.model_path}")
        
        if self.system.enable_label_generation and not os.path.exists(self.data.label_model_path):
            errors.append(f"标签生成模型路径不存在: {self.data.label_model_path}")
        
        return len(errors) == 0, errors


# 全局配置实例
config = Config()
