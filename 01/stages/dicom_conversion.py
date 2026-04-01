#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
阶段2.1: DICOM转NIfTI转换
将DICOM序列转换为NIfTI格式
"""

import os
import sys
import numpy as np
from pathlib import Path
from collections import defaultdict
from typing import Dict, Any, List, Optional, Tuple

try:
    import pydicom
    import nibabel as nib
    DICOM_AVAILABLE = True
except ImportError:
    DICOM_AVAILABLE = False

from .base import BaseStage, StageResult, StageStatus
from ..utils.file_utils import find_gjb_folders, ensure_dir
from ..utils.logger import ProgressLogger


class DicomConversionStage(BaseStage):
    """DICOM转NIfTI阶段"""
    
    @property
    def stage_name(self) -> str:
        return "DICOM转NIfTI"
    
    def _is_dicom_file(self, file_path: Path) -> bool:
        """检查文件是否为DICOM格式"""
        if not DICOM_AVAILABLE:
            return file_path.suffix.upper() in ['.DCM', '.DICOM']
        
        try:
            with open(file_path, 'rb') as f:
                header = f.read(132)
                if len(header) >= 132 and header[128:132] == b'DICM':
                    return True
            pydicom.dcmread(file_path, stop_before_pixels=True)
            return True
        except Exception:
            return False
    
    def _find_dicom_files(self, folder: Path) -> List[Path]:
        """查找文件夹中的DICOM文件"""
        dicom_files = []
        
        for file_path in folder.rglob('*'):
            if file_path.is_file():
                if self._is_dicom_file(file_path):
                    dicom_files.append(file_path)
        
        return dicom_files
    
    def _group_by_series(self, dicom_files: List[Path]) -> Dict[str, List[Path]]:
        """按序列分组DICOM文件"""
        if not DICOM_AVAILABLE:
            return {'default': dicom_files}
        
        series_dict = defaultdict(list)
        
        for dicom_file in dicom_files:
            try:
                ds = pydicom.dcmread(dicom_file, stop_before_pixels=True)
                series_uid = getattr(ds, 'SeriesInstanceUID', 'UNKNOWN')
                series_number = getattr(ds, 'SeriesNumber', '0')
                series_description = getattr(ds, 'SeriesDescription', 'UNKNOWN')
                
                series_key = f"{series_uid}_{series_number}_{series_description}"
                series_dict[series_key].append(dicom_file)
            except Exception as e:
                self.logger.warning(f"读取DICOM头信息失败 {dicom_file}: {e}")
                continue
        
        return series_dict
    
    def _sort_slices(self, dicom_files: List[Path]) -> List[Path]:
        """按切片位置排序"""
        if not DICOM_AVAILABLE:
            return sorted(dicom_files, key=lambda x: x.name)
        
        slice_info = []
        
        for dicom_file in dicom_files:
            try:
                ds = pydicom.dcmread(dicom_file, stop_before_pixels=True)
                
                # 尝试获取切片位置
                slice_location = getattr(ds, 'SliceLocation', None)
                if slice_location is not None:
                    slice_info.append((float(slice_location), dicom_file))
                    continue
                
                # 尝试ImagePositionPatient
                ipp = getattr(ds, 'ImagePositionPatient', None)
                if ipp is not None and len(ipp) >= 3:
                    slice_info.append((float(ipp[2]), dicom_file))
                    continue
                
                # 尝试InstanceNumber
                instance_number = getattr(ds, 'InstanceNumber', None)
                if instance_number is not None:
                    slice_info.append((int(instance_number), dicom_file))
                    continue
                
                slice_info.append((str(dicom_file.name), dicom_file))
                
            except Exception as e:
                self.logger.warning(f"获取切片信息失败 {dicom_file}: {e}")
                slice_info.append((float('inf'), dicom_file))
        
        slice_info.sort(key=lambda x: x[0])
        return [info[1] for info in slice_info]
    
    def _load_series(self, dicom_files: List[Path]) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
        """加载DICOM序列为3D数组"""
        if not DICOM_AVAILABLE:
            return None, None
        
        images = []
        first_ds = None
        pixel_spacing = None
        slice_thickness = None
        
        for dicom_file in dicom_files:
            try:
                ds = pydicom.dcmread(dicom_file)
                if first_ds is None:
                    first_ds = ds
                    pixel_spacing = getattr(ds, 'PixelSpacing', [1.0, 1.0])
                    slice_thickness = getattr(ds, 'SliceThickness', 1.0)
                
                if hasattr(ds, 'pixel_array'):
                    image = ds.pixel_array.astype(np.float32)
                    images.append(image)
            except Exception as e:
                self.logger.warning(f"加载DICOM文件失败 {dicom_file}: {e}")
                continue
        
        if not images:
            return None, None
        
        volume = np.stack(images, axis=-1)
        affine = self._create_affine(first_ds, pixel_spacing, slice_thickness, len(images))
        
        return volume, affine
    
    def _create_affine(self, ds, pixel_spacing, slice_thickness, num_slices) -> np.ndarray:
        """创建仿射矩阵"""
        affine = np.eye(4)
        
        if not DICOM_AVAILABLE or ds is None:
            return affine
        
        try:
            if pixel_spacing and len(pixel_spacing) >= 2:
                affine[0, 0] = float(pixel_spacing[0])
                affine[1, 1] = float(pixel_spacing[1])
            
            if slice_thickness:
                affine[2, 2] = float(slice_thickness)
            
            ipp = getattr(ds, 'ImagePositionPatient', None)
            if ipp and len(ipp) >= 3:
                affine[0, 3] = float(ipp[0])
                affine[1, 3] = float(ipp[1])
                affine[2, 3] = float(ipp[2])
        except Exception as e:
            self.logger.warning(f"创建仿射矩阵失败: {e}")
        
        return affine
    
    def _save_nifti(self, volume: np.ndarray, affine: np.ndarray, output_path: Path) -> bool:
        """保存为NIfTI文件"""
        if not DICOM_AVAILABLE:
            return False
        
        try:
            nii_img = nib.Nifti1Image(volume, affine)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            nib.save(nii_img, str(output_path))
            return True
        except Exception as e:
            self.logger.error(f"保存NIfTI失败 {output_path}: {e}")
            return False
    
    def _process_patient_folder(self, patient_folder: Path, gjb_folders: List[Path]) -> int:
        """处理单个患者文件夹"""
        converted_count = 0
        patient_name = patient_folder.name
        
        # 查找GJB目标文件夹
        gjb_folder = None
        for item in patient_folder.iterdir():
            if item.is_dir() and item.name.startswith('GJB'):
                gjb_folder = item
                break
        
        if gjb_folder is None:
            self.logger.warning(f"未找到GJB文件夹: {patient_folder}")
            return 0
        
        gjb_id = gjb_folder.name
        
        # 查找包含DICOM的乱码文件夹
        for item in patient_folder.iterdir():
            if not item.is_dir():
                continue
            if item.name.startswith('GJB'):
                continue
            if item.name.lower() in ['report', 'reports']:
                continue
            
            # 查找DICOM文件
            dicom_files = self._find_dicom_files(item)
            if not dicom_files:
                continue
            
            self.logger.info(f"找到 {len(dicom_files)} 个DICOM文件在 {item.name}")
            
            # 按序列分组
            series_dict = self._group_by_series(dicom_files)
            if not series_dict:
                continue
            
            # 选择最长的序列
            longest_series = max(series_dict.items(), key=lambda x: len(x[1]))
            series_key, series_files = longest_series
            
            # 排序切片
            sorted_files = self._sort_slices(series_files)
            
            # 加载为3D体积
            volume, affine = self._load_series(sorted_files)
            if volume is None:
                self.logger.error(f"加载DICOM序列失败: {item}")
                continue
            
            # 创建输出文件名
            sequence_num = converted_count + 1
            output_filename = f"{gjb_id}_{sequence_num:02d}.nii"
            output_path = gjb_folder / output_filename
            
            # 保存为NIfTI
            if self._save_nifti(volume, affine, output_path):
                self.logger.info(f"转换成功: {output_path}")
                converted_count += 1
            else:
                self.logger.error(f"转换失败: {output_path}")
        
        return converted_count
    
    def process(self, context: Dict[str, Any]) -> StageResult:
        """执行DICOM转换"""
        if not DICOM_AVAILABLE:
            return StageResult(
                stage_name=self.stage_name,
                status=StageStatus.FAILED,
                message="pydicom或nibabel未安装，无法进行DICOM转换"
            )
        
        data_dir = self.config.data.input_dir
        
        if not os.path.exists(data_dir):
            return StageResult(
                stage_name=self.stage_name,
                status=StageStatus.FAILED,
                message=f"数据目录不存在: {data_dir}"
            )
        
        # 查找所有患者文件夹
        patient_folders = []
        for item in Path(data_dir).iterdir():
            if item.is_dir() and not item.name.startswith('.') and not item.name.startswith('GJB'):
                patient_folders.append(item)
        
        if not patient_folders:
            return StageResult(
                stage_name=self.stage_name,
                status=StageStatus.FAILED,
                message=f"未找到患者文件夹在: {data_dir}"
            )
        
        self.logger.info(f"找到 {len(patient_folders)} 个患者文件夹")
        
        # 处理每个患者
        total_converted = 0
        progress = ProgressLogger(self.logger, len(patient_folders), "DICOM转换")
        
        for patient_folder in patient_folders:
            try:
                count = self._process_patient_folder(patient_folder, [])
                total_converted += count
                progress.update("success" if count > 0 else "skip", f"转换了 {count} 个序列")
            except Exception as e:
                self.logger.error(f"处理患者文件夹失败 {patient_folder}: {e}")
                progress.update("error", str(e))
        
        progress.summary()
        
        return StageResult(
            stage_name=self.stage_name,
            status=StageStatus.SUCCESS,
            message=f"成功转换 {total_converted} 个序列",
            data={'converted_count': total_converted}
        )
