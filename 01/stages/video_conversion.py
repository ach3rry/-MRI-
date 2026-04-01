#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
阶段2.2: NIfTI转MP4视频
将NIfTI医学影像转换为MP4视频格式
"""

import os
from pathlib import Path
from typing import Dict, Any, List

try:
    import numpy as np
    import nibabel as nib
    import cv2
    VIDEO_AVAILABLE = True
except ImportError:
    VIDEO_AVAILABLE = False
    np = None
    nib = None
    cv2 = None

from .base import BaseStage, StageResult, StageStatus
from ..utils.file_utils import find_files_by_pattern, ensure_dir
from ..utils.logger import ProgressLogger


class VideoConversionStage(BaseStage):
    """NIfTI转MP4视频阶段"""
    
    @property
    def stage_name(self) -> str:
        return "NIfTI转MP4视频"
    
    def _load_nifti(self, nii_path: str):
        """加载NIfTI文件"""
        if not VIDEO_AVAILABLE:
            return None
        
        try:
            img = nib.load(nii_path)
            return img.get_fdata()
        except Exception as e:
            self.logger.error(f"加载NIfTI失败 {nii_path}: {e}")
            return None
    
    def _apply_window(self, image: np.ndarray, window_width=None, window_center=None) -> np.ndarray:
        """应用窗宽窗位"""
        if not VIDEO_AVAILABLE:
            return image
        
        # 自动窗宽窗位
        if window_width is None or window_center is None:
            lower = np.percentile(image, 1)
            upper = np.percentile(image, 99)
            window_width = upper - lower
            window_center = (upper + lower) / 2
        
        min_intensity = window_center - window_width / 2
        max_intensity = window_center + window_width / 2
        
        windowed = np.clip((image - min_intensity) / (max_intensity - min_intensity), 0, 1)
        return (windowed * 255).astype(np.uint8)
    
    def _convert_to_video(
        self,
        volume: np.ndarray,
        output_path: str,
        fps: int = 24,
        resolution: tuple = (512, 512),
        axis: int = 2
    ) -> bool:
        """将3D体积转换为视频"""
        if not VIDEO_AVAILABLE:
            return False
        
        try:
            ensure_dir(os.path.dirname(output_path))
            
            n_slices = volume.shape[axis]
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, fps, resolution)
            
            if not out.isOpened():
                self.logger.error(f"无法创建视频写入器: {output_path}")
                return False
            
            for i in range(n_slices):
                # 提取切片
                if axis == 0:
                    slice_data = volume[i, :, :].T
                elif axis == 1:
                    slice_data = volume[:, i, :].T
                else:
                    slice_data = volume[:, :, i]
                
                # 归一化
                normalized = self._apply_window(slice_data)
                
                # 调整大小
                resized = cv2.resize(normalized, resolution, interpolation=cv2.INTER_LINEAR)
                
                # 转换为BGR
                frame = cv2.cvtColor(resized, cv2.COLOR_GRAY2BGR)
                
                out.write(frame)
            
            out.release()
            return True
            
        except Exception as e:
            self.logger.error(f"转换视频失败: {e}")
            # 清理部分文件
            if os.path.exists(output_path):
                try:
                    os.remove(output_path)
                except:
                    pass
            return False
    
    def _create_mp4_path(self, nii_path: str) -> str:
        """根据NIfTI路径创建MP4输出路径"""
        base_name = os.path.basename(nii_path)
        if base_name.endswith('.nii.gz'):
            mp4_name = base_name[:-7] + '.mp4'
        elif base_name.endswith('.nii'):
            mp4_name = base_name[:-4] + '.mp4'
        else:
            mp4_name = base_name + '.mp4'
        
        output_dir = os.path.dirname(nii_path)
        return os.path.join(output_dir, mp4_name)
    
    def process(self, context: Dict[str, Any]) -> StageResult:
        """执行视频转换"""
        if not VIDEO_AVAILABLE:
            return StageResult(
                stage_name=self.stage_name,
                status=StageStatus.FAILED,
                message="nibabel或opencv-python未安装，无法进行视频转换"
            )
        
        data_dir = self.config.data.input_dir
        
        # 查找所有GJB相关的NIfTI文件
        nii_files = find_files_by_pattern(
            data_dir,
            pattern="*.nii*",
            extensions=['.nii', '.nii.gz'],
            recursive=True
        )
        
        # 过滤GJB文件
        gjb_nii_files = [f for f in nii_files if 'GJB' in f]
        
        if not gjb_nii_files:
            return StageResult(
                stage_name=self.stage_name,
                status=StageStatus.FAILED,
                message=f"未找到GJB相关的NIfTI文件"
            )
        
        self.logger.info(f"找到 {len(gjb_nii_files)} 个GJB NIfTI文件")
        
        # 转换配置
        fps = self.config.video.fps
        resolution = self.config.video.resolution
        axis = self.config.video.axis
        
        # 处理每个文件
        successful = 0
        failed = 0
        progress = ProgressLogger(self.logger, len(gjb_nii_files), "视频转换")
        
        for nii_path in gjb_nii_files:
            mp4_path = self._create_mp4_path(nii_path)
            
            # 加载NIfTI
            volume = self._load_nifti(nii_path)
            if volume is None:
                failed += 1
                progress.update("error", "加载失败")
                continue
            
            # 转换为视频
            if self._convert_to_video(volume, mp4_path, fps, resolution, axis):
                successful += 1
                progress.update("success")
            else:
                failed += 1
                progress.update("error", "转换失败")
        
        progress.summary()
        
        return StageResult(
            stage_name=self.stage_name,
            status=StageStatus.SUCCESS,
            message=f"成功转换 {successful} 个视频，失败 {failed} 个",
            data={
                'successful': successful,
                'failed': failed,
                'total': len(gjb_nii_files)
            }
        )
