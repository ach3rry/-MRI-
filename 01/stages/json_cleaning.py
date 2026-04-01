#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
阶段3.1: JSON数据清洗
清洗JSON文件，仅保留核心字段
"""

import os
from typing import Dict, Any, List
from pathlib import Path

from .base import BaseStage, StageResult, StageStatus
from ..utils.file_utils import find_files_by_pattern, ensure_dir
from ..utils.json_utils import load_json, save_json
from ..utils.logger import ProgressLogger


class JsonCleaningStage(BaseStage):
    """JSON数据清洗阶段"""
    
    @property
    def stage_name(self) -> str:
        return "JSON数据清洗"
    
    def _clean_single_file(self, file_path: str, keep_fields: List[str]) -> bool:
        """清洗单个JSON文件"""
        try:
            # 加载JSON
            data = load_json(file_path)
            if data is None:
                return False
            
            # 清洗数据
            cleaned_data = {field: data.get(field, "") for field in keep_fields}
            
            # 保存（覆盖原文件）
            return save_json(cleaned_data, file_path)
            
        except Exception as e:
            self.logger.error(f"清洗文件失败 {file_path}: {e}")
            return False
    
    def process(self, context: Dict[str, Any]) -> StageResult:
        """执行JSON清洗"""
        data_dir = self.config.data.input_dir
        keep_fields = self.config.report.keep_fields
        
        # 查找所有GJB开头的JSON文件
        json_files = []
        for root, dirs, files in os.walk(data_dir):
            for file in files:
                if file.startswith("GJB") and file.lower().endswith(".json"):
                    json_files.append(os.path.join(root, file))
        
        if not json_files:
            return StageResult(
                stage_name=self.stage_name,
                status=StageStatus.SUCCESS,
                message=f"未找到GJB相关的JSON文件"
            )
        
        self.logger.info(f"找到 {len(json_files)} 个GJB JSON文件")
        
        # 处理每个文件
        success_count = 0
        progress = ProgressLogger(self.logger, len(json_files), "JSON清洗")
        
        for file_path in json_files:
            if self._clean_single_file(file_path, keep_fields):
                success_count += 1
                progress.update("success")
            else:
                progress.update("error")
        
        progress.summary()
        
        return StageResult(
            stage_name=self.stage_name,
            status=StageStatus.SUCCESS,
            message=f"成功清洗 {success_count}/{len(json_files)} 个文件",
            data={
                'total': len(json_files),
                'success': success_count,
                'keep_fields': keep_fields
            }
        )
