#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
阶段3.2: 复制到测试集
将GJB文件夹复制到测试集目录
"""

import os
import shutil
from typing import Dict, Any, List
from pathlib import Path

from .base import BaseStage, StageResult, StageStatus
from ..utils.file_utils import find_gjb_folders, ensure_dir
from ..utils.logger import ProgressLogger


class CopyToTestStage(BaseStage):
    """复制到测试集阶段"""
    
    @property
    def stage_name(self) -> str:
        return "复制到测试集"
    
    def _copy_gjb_folder(self, src_path: str, dst_path: str) -> bool:
        """复制单个GJB文件夹"""
        try:
            # 如果目标已存在，先删除
            if os.path.exists(dst_path):
                shutil.rmtree(dst_path)
            
            # 复制文件夹
            shutil.copytree(src_path, dst_path)
            return True
            
        except Exception as e:
            self.logger.error(f"复制失败 {src_path} -> {dst_path}: {e}")
            return False
    
    def process(self, context: Dict[str, Any]) -> StageResult:
        """执行复制操作"""
        source_dir = self.config.data.input_dir
        target_dir = self.config.data.test_set_dir
        
        # 确保目标目录存在
        ensure_dir(target_dir)
        
        # 查找所有GJB文件夹
        gjb_folders = find_gjb_folders(source_dir, recursive=True)
        
        if not gjb_folders:
            return StageResult(
                stage_name=self.stage_name,
                status=StageStatus.FAILED,
                message=f"未找到GJB文件夹"
            )
        
        self.logger.info(f"找到 {len(gjb_folders)} 个GJB文件夹")
        
        # 复制每个文件夹
        success_count = 0
        progress = ProgressLogger(self.logger, len(gjb_folders), "复制到测试集")
        
        for src_path in gjb_folders:
            folder_name = os.path.basename(src_path)
            dst_path = os.path.join(target_dir, folder_name)
            
            if self._copy_gjb_folder(src_path, dst_path):
                success_count += 1
                progress.update("success", f"{folder_name}")
            else:
                progress.update("error", f"{folder_name}")
        
        progress.summary()
        
        return StageResult(
            stage_name=self.stage_name,
            status=StageStatus.SUCCESS,
            message=f"成功复制 {success_count}/{len(gjb_folders)} 个文件夹",
            data={
                'total': len(gjb_folders),
                'success': success_count,
                'target_dir': target_dir
            }
        )
