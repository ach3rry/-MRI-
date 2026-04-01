#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
流水线阶段基类
定义所有处理阶段的通用接口
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from enum import Enum
import time


class StageStatus(Enum):
    """阶段执行状态"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    WARNING = "warning"


@dataclass
class StageResult:
    """阶段执行结果"""
    stage_name: str
    status: StageStatus
    message: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    start_time: float = 0.0
    end_time: float = 0.0
    error: Optional[Exception] = None
    
    @property
    def duration(self) -> float:
        """执行耗时（秒）"""
        if self.end_time > self.start_time:
            return self.end_time - self.start_time
        return 0.0
    
    @property
    def is_success(self) -> bool:
        """是否成功"""
        return self.status == StageStatus.SUCCESS
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'stage_name': self.stage_name,
            'status': self.status.value,
            'message': self.message,
            'duration': self.duration,
            'data': self.data,
            'error': str(self.error) if self.error else None
        }


class BaseStage(ABC):
    """
    流水线阶段基类
    所有具体处理阶段都应继承此类
    """
    
    def __init__(self, config: Any, logger: Any):
        """
        初始化阶段
        
        Args:
            config: 配置对象
            logger: 日志记录器
        """
        self.config = config
        self.logger = logger
        self.name = self.__class__.__name__
        self._enabled = True
    
    @property
    @abstractmethod
    def stage_name(self) -> str:
        """阶段名称"""
        pass
    
    @property
    def enabled(self) -> bool:
        """是否启用此阶段"""
        return self._enabled
    
    @enabled.setter
    def enabled(self, value: bool):
        self._enabled = value
    
    def pre_process(self, context: Dict[str, Any]) -> bool:
        """
        预处理钩子
        
        Args:
            context: 流水线上下文
            
        Returns:
            是否继续执行
        """
        return True
    
    @abstractmethod
    def process(self, context: Dict[str, Any]) -> StageResult:
        """
        执行阶段处理逻辑
        
        Args:
            context: 流水线上下文，包含之前阶段的数据
            
        Returns:
            阶段执行结果
        """
        pass
    
    def post_process(self, context: Dict[str, Any], result: StageResult) -> StageResult:
        """
        后处理钩子
        
        Args:
            context: 流水线上下文
            result: 阶段执行结果
            
        Returns:
            处理后的结果
        """
        return result
    
    def run(self, context: Dict[str, Any]) -> StageResult:
        """
        运行阶段
        
        Args:
            context: 流水线上下文
            
        Returns:
            阶段执行结果
        """
        if not self.enabled:
            return StageResult(
                stage_name=self.stage_name,
                status=StageStatus.SKIPPED,
                message="阶段已禁用"
            )
        
        # 预处理
        if not self.pre_process(context):
            return StageResult(
                stage_name=self.stage_name,
                status=StageStatus.SKIPPED,
                message="预处理检查未通过"
            )
        
        start_time = time.time()
        self.logger.info(f"开始执行阶段: {self.stage_name}")
        
        try:
            # 执行主处理逻辑
            result = self.process(context)
            result.start_time = start_time
            result.end_time = time.time()
            result.stage_name = self.stage_name
            
            # 后处理
            result = self.post_process(context, result)
            
            # 记录结果
            if result.is_success:
                self.logger.info(f"阶段 {self.stage_name} 执行成功，耗时: {result.duration:.2f}s")
            else:
                self.logger.warning(f"阶段 {self.stage_name} 执行失败: {result.message}")
            
            return result
            
        except Exception as e:
            end_time = time.time()
            self.logger.error(f"阶段 {self.stage_name} 发生异常: {e}", exc_info=True)
            
            return StageResult(
                stage_name=self.stage_name,
                status=StageStatus.FAILED,
                message=f"执行异常: {str(e)}",
                start_time=start_time,
                end_time=end_time,
                error=e
            )
    
    def validate_context(self, context: Dict[str, Any], required_keys: List[str]) -> bool:
        """
        验证上下文是否包含必需的键
        
        Args:
            context: 上下文字典
            required_keys: 必需的键列表
            
        Returns:
            是否有效
        """
        missing = [key for key in required_keys if key not in context]
        if missing:
            self.logger.error(f"上下文缺少必需的键: {missing}")
            return False
        return True
