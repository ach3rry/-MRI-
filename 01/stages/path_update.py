#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
阶段4: 更新JSON路径
更新测试集中JSON文件的文件路径字段
"""

import os
from typing import Dict, Any, List
from pathlib import Path

from .base import BaseStage, StageResult, StageStatus
from ..utils.json_utils import load_json, save_json
from ..utils.logger import ProgressLogger


class PathUpdateStage(BaseStage):
    """路径更新阶段"""
    
    @property
    def stage_name(self) -> str:
        return "更新JSON路径"
    
    def _update_single_file(self, json_path: str) -> bool:
        """更新单个JSON文件的路径"""
        try:
            # 加载JSON
            data = load_json(json_path)
            if data is None:
                return False
            
            # 检查是否有文件路径字段
            if "文件路径" not in data:
                return False
            
            # 获取JSON文件所在目录的绝对路径
            json_dir = os.path.dirname(json_path)
            abs_path = os.path.abspath(json_dir)
            
            # 更新路径
            old_path = data["文件路径"]
            data["文件路径"] = abs_path
            
            # 保存
            if save_json(data, json_path):
                self.logger.debug(f"更新路径: {old_path} -> {abs_path}")
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"更新路径失败 {json_path}: {e}")
            return False
    
    def process(self, context: Dict[str, Any]) -> StageResult:
        """执行路径更新"""
        test_set_dir = self.config.data.test_set_dir
        
        if not os.path.exists(test_set_dir):
            return StageResult(
                stage_name=self.stage_name,
                status=StageStatus.FAILED,
                message=f"测试集目录不存在: {test_set_dir}"
            )
        
        # 查找所有JSON文件
        json_files = []
        for root, dirs, files in os.walk(test_set_dir):
            for file in files:
                if file.endswith(".json"):
                    json_files.append(os.path.join(root, file))
        
        if not json_files:
            return StageResult(
                stage_name=self.stage_name,
                status=StageStatus.WARNING,
                message=f"测试集中未找到JSON文件"
            )
        
        self.logger.info(f"找到 {len(json_files)} 个JSON文件")
        
        # 更新每个文件
        updated_count = 0
        progress = ProgressLogger(self.logger, len(json_files), "路径更新")
        
        for json_path in json_files:
            if self._update_single_file(json_path):
                updated_count += 1
                progress.update("success")
            else:
                progress.update("error")
        
        progress.summary()
        
        return StageResult(
            stage_name=self.stage_name,
            status=StageStatus.SUCCESS,
            message=f"成功更新 {updated_count}/{len(json_files)} 个文件",
            data={
                'total': len(json_files),
                'updated': updated_count
            }
        )
