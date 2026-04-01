#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据处理流水线核心模块
管理所有处理阶段的执行
"""

import time
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

from .config import Config
from .utils.logger import setup_logger, get_logger
from .stages.base import BaseStage, StageResult, StageStatus
from .stages import (
    ReportExtractionStage,
    DicomConversionStage,
    VideoConversionStage,
    JsonCleaningStage,
    CopyToTestStage,
    PathUpdateStage,
    LabelGenerationStage,
)


@dataclass
class PipelineStats:
    """流水线统计信息"""
    start_time: float = 0.0
    end_time: float = 0.0
    stage_results: List[StageResult] = field(default_factory=list)
    
    @property
    def total_duration(self) -> float:
        """总耗时"""
        if self.end_time > self.start_time:
            return self.end_time - self.start_time
        return 0.0
    
    @property
    def success_count(self) -> int:
        """成功阶段数"""
        return sum(1 for r in self.stage_results if r.is_success)
    
    @property
    def failed_count(self) -> int:
        """失败阶段数"""
        return sum(1 for r in self.stage_results if r.status == StageStatus.FAILED)
    
    @property
    def skipped_count(self) -> int:
        """跳过阶段数"""
        return sum(1 for r in self.stage_results if r.status == StageStatus.SKIPPED)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'total_duration': self.total_duration,
            'success_count': self.success_count,
            'failed_count': self.failed_count,
            'skipped_count': self.skipped_count,
            'stage_results': [r.to_dict() for r in self.stage_results]
        }


class DataProcessingPipeline:
    """
    数据处理流水线
    协调各个处理阶段的执行
    """
    
    def __init__(self, config: Optional[Config] = None):
        """
        初始化流水线
        
        Args:
            config: 配置对象，如果为None则使用默认配置
        """
        self.config = config or Config()
        self.logger = setup_logger(
            "Pipeline",
            log_dir=self.config.data.log_dir,
            level=self.config.system.log_level
        )
        
        # 确保目录存在
        self.config.ensure_directories()
        
        # 初始化阶段
        self.stages: List[BaseStage] = []
        self._init_stages()
        
        # 流水线上下文
        self.context: Dict[str, Any] = {}
        
        # 统计信息
        self.stats = PipelineStats()
        
        self.logger.info("数据处理流水线初始化完成")
    
    def _init_stages(self):
        """初始化所有处理阶段"""
        # 1. 报告提取
        if self.config.system.enable_report_extraction:
            self.stages.append(ReportExtractionStage(self.config, self.logger))
        
        # 2.1 DICOM转换
        if self.config.system.enable_dicom_conversion:
            self.stages.append(DicomConversionStage(self.config, self.logger))
        
        # 2.2 视频转换
        if self.config.system.enable_video_conversion:
            self.stages.append(VideoConversionStage(self.config, self.logger))
        
        # 3.1 JSON清洗
        if self.config.system.enable_json_cleaning:
            self.stages.append(JsonCleaningStage(self.config, self.logger))
        
        # 3.2 复制到测试集
        if self.config.system.enable_copy_to_test:
            self.stages.append(CopyToTestStage(self.config, self.logger))
        
        # 4. 路径更新
        if self.config.system.enable_path_update:
            self.stages.append(PathUpdateStage(self.config, self.logger))
        
        # 5. 标签生成
        if self.config.system.enable_label_generation:
            self.stages.append(LabelGenerationStage(self.config, self.logger))
        
        self.logger.info(f"已初始化 {len(self.stages)} 个处理阶段")
    
    def validate(self) -> bool:
        """
        验证配置是否有效
        
        Returns:
            是否有效
        """
        is_valid, errors = self.config.validate()
        
        if not is_valid:
            self.logger.error("配置验证失败:")
            for error in errors:
                self.logger.error(f"  - {error}")
            return False
        
        self.logger.info("配置验证通过")
        return True
    
    def run(self, start_stage: Optional[str] = None, end_stage: Optional[str] = None) -> PipelineStats:
        """
        运行流水线
        
        Args:
            start_stage: 起始阶段名称（可选，用于部分执行）
            end_stage: 结束阶段名称（可选，用于部分执行）
            
        Returns:
            流水线统计信息
        """
        self.logger.info("=" * 70)
        self.logger.info("开始执行数据处理流水线")
        self.logger.info("=" * 70)
        
        # 记录开始时间
        self.stats.start_time = time.time()
        
        # 确定执行范围
        stages_to_run = self.stages
        if start_stage or end_stage:
            stage_names = [s.stage_name for s in self.stages]
            start_idx = 0
            end_idx = len(self.stages)
            
            if start_stage and start_stage in stage_names:
                start_idx = stage_names.index(start_stage)
            if end_stage and end_stage in stage_names:
                end_idx = stage_names.index(end_stage) + 1
            
            stages_to_run = self.stages[start_idx:end_idx]
        
        self.logger.info(f"将执行 {len(stages_to_run)} 个阶段")
        
        # 执行每个阶段
        for stage in stages_to_run:
            result = stage.run(self.context)
            self.stats.stage_results.append(result)
            
            # 更新上下文
            self.context[f"{stage.stage_name}_result"] = result
            
            # 如果阶段失败且不是可跳过的，停止执行
            if result.status == StageStatus.FAILED:
                self.logger.error(f"阶段 {stage.stage_name} 失败，停止执行")
                break
        
        # 记录结束时间
        self.stats.end_time = time.time()
        
        # 输出汇总
        self._print_summary()
        
        # 保存报告
        self._save_report()
        
        return self.stats
    
    def _print_summary(self):
        """打印执行汇总"""
        self.logger.info("=" * 70)
        self.logger.info("数据处理流水线执行完成")
        self.logger.info("=" * 70)
        self.logger.info(f"总耗时: {self.stats.total_duration:.2f} 秒")
        self.logger.info(f"成功阶段: {self.stats.success_count}")
        self.logger.info(f"失败阶段: {self.stats.failed_count}")
        self.logger.info(f"跳过阶段: {self.stats.skipped_count}")
        
        self.logger.info("-" * 70)
        self.logger.info("各阶段详情:")
        for result in self.stats.stage_results:
            status_icon = "✓" if result.is_success else "✗" if result.status == StageStatus.FAILED else "⊘"
            self.logger.info(f"  {status_icon} {result.stage_name}: {result.status.value} ({result.duration:.2f}s) - {result.message}")
        self.logger.info("=" * 70)
    
    def _save_report(self):
        """保存执行报告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = f"{self.config.data.log_dir}/pipeline_report_{timestamp}.json"
        
        report = {
            'timestamp': timestamp,
            'config': {
                'input_dir': self.config.data.input_dir,
                'test_set_dir': self.config.data.test_set_dir,
                'output_dir': self.config.data.output_dir,
            },
            'stats': self.stats.to_dict()
        }
        
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            self.logger.info(f"执行报告已保存: {report_path}")
        except Exception as e:
            self.logger.error(f"保存报告失败: {e}")
    
    def get_stage(self, name: str) -> Optional[BaseStage]:
        """
        获取指定名称的阶段
        
        Args:
            name: 阶段名称
            
        Returns:
            阶段实例或None
        """
        for stage in self.stages:
            if stage.stage_name == name:
                return stage
        return None
    
    def enable_stage(self, name: str, enabled: bool = True):
        """
        启用或禁用阶段
        
        Args:
            name: 阶段名称
            enabled: 是否启用
        """
        stage = self.get_stage(name)
        if stage:
            stage.enabled = enabled
            self.logger.info(f"阶段 {name} 已{'启用' if enabled else '禁用'}")
        else:
            self.logger.warning(f"未找到阶段: {name}")
    
    def reset_context(self):
        """重置流水线上下文"""
        self.context = {}
        self.logger.info("流水线上下文已重置")
