#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
阶段1: 医疗报告提取
从报告单图片中提取结构化信息
"""

import os
import csv
import json
from pathlib import Path
from typing import Dict, Any, List
from PIL import Image

try:
    from modelscope import Qwen3VLForConditionalGeneration, AutoProcessor
    import torch
    MODEL_AVAILABLE = True
except ImportError:
    MODEL_AVAILABLE = False

from .base import BaseStage, StageResult, StageStatus
from ..utils.file_utils import find_files_by_pattern, ensure_dir, get_gjb_id_from_path
from ..utils.json_utils import save_json


class ReportExtractionStage(BaseStage):
    """医疗报告提取阶段"""
    
    def __init__(self, config, logger):
        super().__init__(config, logger)
        self.model = None
        self.processor = None
        self._load_model()
    
    @property
    def stage_name(self) -> str:
        return "医疗报告提取"
    
    def _load_model(self):
        """加载模型"""
        if not MODEL_AVAILABLE:
            self.logger.warning("模型库不可用，报告提取功能将受限")
            return
        
        model_path = self.config.data.model_path
        if not os.path.exists(model_path):
            self.logger.warning(f"模型路径不存在: {model_path}")
            return
        
        try:
            self.logger.info("正在加载报告提取模型...")
            self.model = Qwen3VLForConditionalGeneration.from_pretrained(
                model_path, dtype="auto", device_map="auto"
            )
            self.processor = AutoProcessor.from_pretrained(model_path)
            self.logger.info("模型加载成功")
        except Exception as e:
            self.logger.error(f"模型加载失败: {e}")
    
    def _create_prompt(self) -> str:
        """创建提取提示词"""
        fields = self.config.report.required_fields
        fields_json = '\n'.join([f'  "{field}": ""' for field in fields])
        
        return f"""请从以下医学影像报告中严格按照原文提取以下字段的值：
{', '.join(fields)}

要求：
1. 完全以原文为主，严禁调整，严禁严禁严禁
2. 姓名、检查方法、MR表现、诊断意见四个字段非常重要，不允许为空
3. 如果某个字段在报告中未提及，请返回空字符串""
4. 返回严格的JSON格式数据，不要有任何其他文字

请严格按照以下JSON格式返回结果：
{{
{fields_json}
}}"""
    
    def _extract_from_image(self, image_path: str) -> Dict[str, str]:
        """从图片提取信息"""
        if not MODEL_AVAILABLE or self.model is None:
            # 模拟模式：返回空数据
            self.logger.warning(f"模型不可用，跳过提取: {image_path}")
            return {field: "" for field in self.config.report.required_fields}
        
        try:
            prompt = self._create_prompt()
            messages = [{
                "role": "user",
                "content": [
                    {"type": "image", "image": image_path},
                    {"type": "text", "text": prompt},
                ],
            }]
            
            inputs = self.processor.apply_chat_template(
                messages,
                tokenize=True,
                add_generation_prompt=True,
                return_dict=True,
                return_tensors="pt"
            )
            
            device = next(self.model.parameters()).device
            inputs = {k: v.to(device) for k, v in inputs.items()}
            
            generated_ids = self.model.generate(**inputs, max_new_tokens=2048)
            generated_ids_trimmed = [
                out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs['input_ids'], generated_ids)
            ]
            
            output_text = self.processor.batch_decode(
                generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
            )[0]
            
            # 解析JSON输出
            return self._parse_output(output_text)
            
        except Exception as e:
            self.logger.error(f"提取失败 {image_path}: {e}")
            return {field: "" for field in self.config.report.required_fields}
    
    def _parse_output(self, output_text: str) -> Dict[str, str]:
        """解析模型输出"""
        import re
        
        try:
            # 查找JSON部分
            start_idx = output_text.find('{')
            end_idx = output_text.rfind('}')
            if start_idx != -1 and end_idx != -1:
                json_str = output_text[start_idx:end_idx+1]
                extracted_data = json.loads(json_str)
                
                # 确保所有必需字段都存在
                for field in self.config.report.required_fields:
                    if field not in extracted_data:
                        extracted_data[field] = ""
                
                return extracted_data
        except Exception as e:
            self.logger.warning(f"解析输出失败: {e}")
        
        return {field: "" for field in self.config.report.required_fields}
    
    def process(self, context: Dict[str, Any]) -> StageResult:
        """执行报告提取"""
        data_dir = self.config.data.input_dir
        report_filename = self.config.report.report_filename
        
        # 查找所有报告单图片
        report_images = []
        for root, dirs, files in os.walk(data_dir):
            for file in files:
                if file == report_filename:
                    report_images.append(os.path.join(root, file))
        
        if not report_images:
            return StageResult(
                stage_name=self.stage_name,
                status=StageStatus.FAILED,
                message=f"未找到报告单图片: {report_filename}"
            )
        
        self.logger.info(f"找到 {len(report_images)} 个报告单图片")
        
        # 准备CSV文件
        csv_path = os.path.join(self.config.data.output_dir, self.config.report.csv_filename)
        ensure_dir(os.path.dirname(csv_path))
        
        fieldnames = ['顺序编号'] + self.config.report.required_fields + ['文件路径']
        
        with open(csv_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            processed_count = 0
            
            for idx, img_path in enumerate(report_images):
                self.logger.info(f"处理第 {idx+1}/{len(report_images)} 个报告单")
                
                # 提取信息
                extracted_info = self._extract_from_image(img_path)
                
                # 生成GJB编号
                gjb_number = f"GJB{idx+1:07d}"
                extracted_info['顺序编号'] = gjb_number
                
                # 创建GJB文件夹
                patient_dir = os.path.dirname(img_path)
                gjb_folder = os.path.join(patient_dir, gjb_number)
                ensure_dir(gjb_folder)
                
                extracted_info['文件路径'] = gjb_folder
                
                # 写入CSV
                writer.writerow(extracted_info)
                
                # 保存JSON
                json_path = os.path.join(gjb_folder, f"{gjb_number}.json")
                save_json(extracted_info, json_path)
                
                processed_count += 1
        
        return StageResult(
            stage_name=self.stage_name,
            status=StageStatus.SUCCESS,
            message=f"成功处理 {processed_count} 份报告",
            data={
                'processed_count': processed_count,
                'csv_path': csv_path,
                'report_images': report_images
            }
        )
