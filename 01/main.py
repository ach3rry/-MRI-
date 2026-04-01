#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据处理系统主入口
膝关节MRI数据处理端到端流水线
"""

import os
import sys
import argparse
from typing import Optional

# 确保可以导入本地模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
from pipeline import DataProcessingPipeline
from utils.logger import setup_logger


def create_parser() -> argparse.ArgumentParser:
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        description='膝关节MRI数据处理系统 - 端到端数据处理流水线',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 运行完整流水线
  python main.py
  
  # 只运行指定阶段
  python main.py --start-stage "DICOM转NIfTI" --end-stage "复制到测试集"
  
  # 跳过某些阶段
  python main.py --skip-stages "标签生成" "视频转换"
  
  # 指定数据目录
  python main.py --input-dir ./data --test-set-dir ./test
  
  # 验证配置
  python main.py --validate-only
  
  # 查看可用阶段
  python main.py --list-stages
        """
    )
    
    # 基本选项
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='输出详细日志')
    parser.add_argument('--validate-only', action='store_true',
                       help='仅验证配置，不执行处理')
    parser.add_argument('--list-stages', action='store_true',
                       help='列出所有可用阶段')
    
    # 路径配置
    path_group = parser.add_argument_group('路径配置')
    path_group.add_argument('--input-dir', type=str,
                           help='输入数据目录 (默认: ./202505-202506)')
    path_group.add_argument('--test-set-dir', type=str,
                           help='测试集输出目录 (默认: ./测试集)')
    path_group.add_argument('--output-dir', type=str,
                           help='输出目录 (默认: ./output)')
    path_group.add_argument('--model-path', type=str,
                           help='报告提取模型路径 (默认: ./model)')
    path_group.add_argument('--label-model-path', type=str,
                           help='标签生成模型路径 (默认: ./qwen3-1.7B)')
    
    # 阶段控制
    stage_group = parser.add_argument_group('阶段控制')
    stage_group.add_argument('--start-stage', type=str,
                            help='从指定阶段开始执行')
    stage_group.add_argument('--end-stage', type=str,
                            help='执行到指定阶段结束')
    stage_group.add_argument('--skip-stages', nargs='+',
                            help='跳过的阶段列表')
    stage_group.add_argument('--only-stages', nargs='+',
                            help='仅执行指定的阶段')
    
    # 功能开关
    feature_group = parser.add_argument_group('功能开关')
    feature_group.add_argument('--no-report-extraction', action='store_true',
                              help='禁用报告提取')
    feature_group.add_argument('--no-dicom-conversion', action='store_true',
                              help='禁用DICOM转换')
    feature_group.add_argument('--no-video-conversion', action='store_true',
                              help='禁用视频转换')
    feature_group.add_argument('--no-json-cleaning', action='store_true',
                              help='禁用JSON清洗')
    feature_group.add_argument('--no-copy-to-test', action='store_true',
                              help='禁用复制到测试集')
    feature_group.add_argument('--no-path-update', action='store_true',
                              help='禁用路径更新')
    feature_group.add_argument('--no-label-generation', action='store_true',
                              help='禁用标签生成')
    
    return parser


def apply_args_to_config(config: Config, args) -> Config:
    """将命令行参数应用到配置"""
    # 路径配置
    if args.input_dir:
        config.data.input_dir = args.input_dir
    if args.test_set_dir:
        config.data.test_set_dir = args.test_set_dir
    if args.output_dir:
        config.data.output_dir = args.output_dir
    if args.model_path:
        config.data.model_path = args.model_path
    if args.label_model_path:
        config.data.label_model_path = args.label_model_path
    
    # 功能开关
    if args.no_report_extraction:
        config.system.enable_report_extraction = False
    if args.no_dicom_conversion:
        config.system.enable_dicom_conversion = False
    if args.no_video_conversion:
        config.system.enable_video_conversion = False
    if args.no_json_cleaning:
        config.system.enable_json_cleaning = False
    if args.no_copy_to_test:
        config.system.enable_copy_to_test = False
    if args.no_path_update:
        config.system.enable_path_update = False
    if args.no_label_generation:
        config.system.enable_label_generation = False
    
    # 日志级别
    if args.verbose:
        config.system.log_level = "DEBUG"
    
    return config


def list_stages(pipeline: DataProcessingPipeline):
    """列出所有可用阶段"""
    print("\n可用处理阶段:")
    print("-" * 50)
    for i, stage in enumerate(pipeline.stages, 1):
        status = "启用" if stage.enabled else "禁用"
        print(f"{i}. {stage.stage_name} [{status}]")
    print("-" * 50)
    print(f"总计: {len(pipeline.stages)} 个阶段\n")


def print_banner():
    """打印系统横幅"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║          膝关节MRI数据处理系统 - 端到端流水线               ║
║                                                              ║
║  功能: 医疗报告提取 → DICOM转换 → 视频生成 → 标签生成       ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def main():
    """主函数"""
    # 解析命令行参数
    parser = create_parser()
    args = parser.parse_args()
    
    # 打印横幅
    print_banner()
    
    # 创建配置
    config = Config()
    config = apply_args_to_config(config, args)
    
    # 创建流水线
    pipeline = DataProcessingPipeline(config)
    
    # 列出阶段
    if args.list_stages:
        list_stages(pipeline)
        return 0
    
    # 应用阶段跳过
    if args.skip_stages:
        for stage_name in args.skip_stages:
            pipeline.enable_stage(stage_name, False)
    
    # 如果只执行指定阶段
    if args.only_stages:
        for stage in pipeline.stages:
            stage.enabled = stage.stage_name in args.only_stages
    
    # 验证配置
    if not pipeline.validate():
        print("\n错误: 配置验证失败，请检查配置后重试")
        return 1
    
    if args.validate_only:
        print("\n配置验证通过!")
        return 0
    
    # 执行流水线
    try:
        stats = pipeline.run(
            start_stage=args.start_stage,
            end_stage=args.end_stage
        )
        
        # 返回状态码
        if stats.failed_count > 0:
            print(f"\n警告: 有 {stats.failed_count} 个阶段执行失败")
            return 2
        
        print("\n✓ 所有阶段执行成功!")
        return 0
        
    except KeyboardInterrupt:
        print("\n\n用户中断执行")
        return 130
    except Exception as e:
        print(f"\n\n执行出错: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
