#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
阶段5: 膝关节MRI标签生成
基于报告内容生成结构化标签
"""

import os
import re
import json
import traceback
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path

try:
    import torch
    from modelscope import AutoModelForCausalLM, AutoTokenizer
    MODEL_AVAILABLE = True
except ImportError:
    MODEL_AVAILABLE = False
    torch = None

from .base import BaseStage, StageResult, StageStatus
from ..utils.json_utils import load_json, save_json, extract_json_from_text
from ..utils.logger import ProgressLogger


class LabelGenerationStage(BaseStage):
    """标签生成阶段"""
    
    def __init__(self, config, logger):
        super().__init__(config, logger)
        self.model = None
        self.tokenizer = None
        self.device = "cpu"
        self.default_schema = self._create_default_schema()
        self._load_model()
    
    @property
    def stage_name(self) -> str:
        return "膝关节MRI标签生成"
    
    def _create_default_schema(self) -> Dict[str, Any]:
        """创建默认标签模板"""
        return {
            "半月板": {"是否异常": False, "损伤分级": [], "是否撕裂": False, "类型": []},
            "韧带": {
                "前交叉韧带": "正常", "后交叉韧带": "正常", "内侧副韧带": "正常",
                "外侧副韧带": "正常", "髌韧带": "正常", "股四头肌腱": "正常"
            },
            "骨软骨单元": {
                "软骨损伤": False, "软骨变薄": False, "软骨缺损": False, "骨髓水肿": False,
                "骨挫伤": False, "骨质增生": False, "骨折": False, "骨囊变": False, "软骨下骨硬化": False
            },
            "髌股关节": {
                "髌骨软化": False, "髌骨高位": False, "髌骨低位": False,
                "髌骨不稳": False, "髌骨倾斜": False, "髌股关节紊乱": False
            },
            "滑膜关节腔": {"关节积液": "无", "滑膜炎": False, "滑膜增生": False},
            "囊性病变": {"是否存在": False, "类型": []},
            "其他结构": {"髂胫束异常": False, "腘肌腱异常": False, "关节游离体": False},
            "病理机制": {"退行性改变": False, "创伤性改变": False, "炎症性改变": False, "术后改变": False},
            "任务标签": {
                "半月板损伤": False, "韧带损伤": False, "骨软骨病变": False, "髌股关节病变": False,
                "关节积液": False, "囊性病变": False, "退行性疾病": False,
                "创伤性疾病": False, "炎症性疾病": False, "术后状态": False
            },
            "主要病变类型": "正常"
        }
    
    def _load_model(self):
        """加载模型"""
        if not MODEL_AVAILABLE:
            self.logger.warning("模型库不可用，标签生成功能将受限")
            return
        
        model_path = self.config.data.label_model_path
        if not os.path.exists(model_path):
            self.logger.warning(f"标签模型路径不存在: {model_path}")
            return
        
        try:
            self.logger.info("正在加载标签生成模型...")
            
            # 检测设备
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            self.logger.info(f"运行设备: {self.device.upper()}")
            
            self.tokenizer = AutoTokenizer.from_pretrained(
                model_path, trust_remote_code=True
            )
            self.model = AutoModelForCausalLM.from_pretrained(
                model_path,
                torch_dtype="auto",
                device_map="auto",
                trust_remote_code=True
            )
            self.model.eval()
            
            self.logger.info("模型加载成功")
            
        except Exception as e:
            self.logger.error(f"模型加载失败: {e}")
            self.model = None
            self.tokenizer = None
    
    def _create_prompt(self, report_data: Dict[str, Any]) -> str:
        """创建标签生成提示词"""
        check_method = report_data.get('检查方法', '无').strip()
        mr_findings = report_data.get('MR表现', '无').strip()
        diagnosis = report_data.get('诊断意见', '无').strip()
        
        schema_json = json.dumps(self.default_schema, ensure_ascii=False, indent=2)
        
        return f"""你是一个严格的医学数据录入员。请根据膝关节MRI报告内容，将信息填入JSON模板。

### 输入报告
【检查方法】：{check_method}
【MR表现】：{mr_findings}
【诊断意见】：{diagnosis}

### 重要规则（必须严格遵守）
1. **零推断原则**：报告未提及的异常一律填 "正常"、False 或 "无"。
2. **韧带**：只能填 "正常"、"损伤"、"断裂"、"术后重建"。
3. **积液**：只能填 "无"、"少量"、"中量"、"大量"。
4. **半月板**：只有报告明确写了分级（如II度、III度）才填分级字段，否则留空数组。
5. **主要病变类型**：若存在多处严重损伤，必须填 "混合型"。

### 【标注规则 (必须严格遵守)】
**规则1(原则)**：仅基于影像描述填写，禁止推断。未提及的结构一律填"正常"/False/[]。
**规则2(半月板)**：出现损伤/撕裂/变异即为异常=true。分级(I/II/III)仅在报告明确写出时填写。
**规则3(韧带)**：仅限使用 "正常"/"损伤"/"断裂"/"术后重建"。损伤包括拉伤和信号异常。
**规则4(骨软骨)**：多项可同时为true。区分骨挫伤与骨折。
**规则5(髌股)**：髌骨高位与低位互斥。
**规则6(滑膜)**：积液必选其一 ["无", "少量", "中量", "大量"]。
**规则7(囊肿)**：有囊性结构则"是否存在"=true，并记录类型。
**规则8(其他)**：记录髂胫束、腘肌腱、游离体。
**规则9(病理)**：基于结构判断机制(退行/创伤/炎症/术后)，可多选。
**规则10(总结)**：任务标签由各子项决定。主要病变类型若涉及多系统并重，选"混合型"。

### 【取值全集约束】
- **韧带状态**: 正常, 损伤, 断裂, 术后重建
- **关节积液**: 无, 少量, 中量, 大量
- **主要病变类型**: 正常, 退行性疾病, 半月板疾病, 韧带疾病, 骨软骨疾病, 炎症性疾病, 术后状态, 混合型

### 目标JSON模板
请直接输出填好值的JSON，不要输出任何Markdown标记或解释文字：
{schema_json}"""
    
    def _generate_labels(self, report_data: Dict[str, Any], file_name: str = "") -> Tuple[Optional[Dict], Dict]:
        """生成标签"""
        if not MODEL_AVAILABLE or self.model is None:
            return None, {"status": "model_unavailable", "error": "模型未加载"}
        
        prompt = self._create_prompt(report_data)
        
        messages = [
            {"role": "system", "content": "你是一个只输出标准JSON的医学助手。禁止输出任何思考过程。"},
            {"role": "user", "content": prompt}
        ]
        
        try:
            # 构建输入
            text = self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )
            model_inputs = self.tokenizer([text], return_tensors="pt").to(self.device)
            
            # 生成
            generated_ids = self.model.generate(
                **model_inputs,
                max_new_tokens=self.config.label.max_new_tokens,
                temperature=self.config.label.temperature,
                do_sample=False,
                repetition_penalty=1.05
            )
            
            output_ids = generated_ids[0][len(model_inputs.input_ids[0]):]
            response = self.tokenizer.decode(output_ids, skip_special_tokens=True)
            
            # 提取JSON
            labels = extract_json_from_text(response)
            
            if labels is None:
                return None, {
                    "status": "parse_error",
                    "raw_response": response,
                    "error": "无法从响应中提取JSON"
                }
            
            # 验证schema
            is_valid, errors = self._validate_schema(labels)
            if not is_valid:
                return None, {
                    "status": "validation_error",
                    "raw_response": response,
                    "parsed_labels": labels,
                    "errors": errors
                }
            
            return labels, {
                "status": "success",
                "raw_response": response if self.config.label.debug_mode else "(调试模式关闭)"
            }
            
        except Exception as e:
            return None, {
                "status": "generation_error",
                "error": str(e),
                "traceback": traceback.format_exc()
            }
    
    def _validate_schema(self, labels: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """验证标签结构"""
        errors = []
        
        if not isinstance(labels, dict):
            errors.append("标签不是字典类型")
            return False, errors
        
        required_keys = ["半月板", "韧带", "骨软骨单元", "髌股关节", "滑膜关节腔",
                        "囊性病变", "其他结构", "病理机制", "任务标签", "主要病变类型"]
        
        for key in required_keys:
            if key not in labels:
                errors.append(f"缺少必需字段: {key}")
        
        # 验证主要病变类型
        valid_types = self.config.label.valid_lesion_types
        if "主要病变类型" in labels and labels["主要病变类型"] not in valid_types:
            errors.append(f"主要病变类型值无效: {labels.get('主要病变类型')}")
        
        return len(errors) == 0, errors
    
    def _is_default_template(self, labels: Dict[str, Any]) -> bool:
        """检查是否为默认模板（未修改）"""
        # 检查半月板
        if (labels["半月板"]["是否异常"] != False or
            len(labels["半月板"]["损伤分级"]) != 0 or
            labels["半月板"]["是否撕裂"] != False or
            len(labels["半月板"]["类型"]) != 0):
            return False
        
        # 检查韧带
        for ligament_value in labels["韧带"].values():
            if ligament_value != "正常":
                return False
        
        # 检查骨软骨单元
        if any(labels["骨软骨单元"].values()):
            return False
        
        # 检查髌股关节
        if any(labels["髌股关节"].values()):
            return False
        
        # 检查滑膜关节腔
        if (labels["滑膜关节腔"]["关节积液"] != "无" or
            labels["滑膜关节腔"]["滑膜炎"] != False or
            labels["滑膜关节腔"]["滑膜增生"] != False):
            return False
        
        # 检查囊性病变
        if (labels["囊性病变"]["是否存在"] != False or
            len(labels["囊性病变"]["类型"]) != 0):
            return False
        
        # 检查其他结构
        if any(labels["其他结构"].values()):
            return False
        
        # 检查病理机制
        if any(labels["病理机制"].values()):
            return False
        
        # 检查任务标签
        if any(labels["任务标签"].values()):
            return False
        
        # 检查主要病变类型
        if labels["主要病变类型"] != "正常":
            return False
        
        return True
    
    def process(self, context: Dict[str, Any]) -> StageResult:
        """执行标签生成"""
        test_set_dir = self.config.data.test_set_dir
        skip_processed = self.config.label.skip_processed
        
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
        
        # 处理每个文件
        success_count = 0
        skip_count = 0
        error_count = 0
        default_template_count = 0
        
        progress = ProgressLogger(self.logger, len(json_files), "标签生成")
        
        for json_path in json_files:
            try:
                # 加载数据
                data = load_json(json_path)
                if data is None:
                    error_count += 1
                    progress.update("error", "加载失败")
                    continue
                
                # 检查是否已处理
                if skip_processed and "标签" in data and data["标签"]:
                    skip_count += 1
                    progress.update("skip")
                    continue
                
                # 生成标签
                labels, result_info = self._generate_labels(data, os.path.basename(json_path))
                
                if labels and result_info["status"] == "success":
                    # 检查是否为默认模板
                    if self._is_default_template(labels):
                        default_template_count += 1
                        self.logger.warning(f"使用默认模板: {json_path}")
                    
                    # 保存标签
                    data["标签"] = labels
                    if save_json(data, json_path):
                        success_count += 1
                        progress.update("success", f"病变类型: {labels.get('主要病变类型', 'N/A')}")
                    else:
                        error_count += 1
                        progress.update("error", "保存失败")
                else:
                    error_count += 1
                    error_msg = result_info.get('error', '未知错误')
                    progress.update("error", error_msg)
                    
            except Exception as e:
                error_count += 1
                self.logger.error(f"处理异常 {json_path}: {e}")
                progress.update("error", str(e))
        
        progress.summary()
        
        return StageResult(
            stage_name=self.stage_name,
            status=StageStatus.SUCCESS,
            message=f"成功生成 {success_count} 个标签，跳过 {skip_count} 个，失败 {error_count} 个",
            data={
                'total': len(json_files),
                'success': success_count,
                'skip': skip_count,
                'error': error_count,
                'default_template': default_template_count
            }
        )
