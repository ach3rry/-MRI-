"use client";

import { motion } from "framer-motion";
import { 
  FileImage, 
  FileText, 
  RefreshCw, 
  FileVideo,
  FileJson,
  FolderSync,
  Tags,
  ArrowRight,
  CheckCircle2
} from "lucide-react";

const stages = [
  {
    id: 1,
    name: "报告提取",
    code: "extract_reports",
    description: "从报告单图片中提取医疗信息",
    icon: FileText,
    inputs: ["报告单.jpg"],
    outputs: ["medical_reports.csv"],
    details: ["OCR识别", "字段解析", "数据验证"],
  },
  {
    id: 2,
    name: "DICOM转换",
    code: "convert_dicom",
    description: "DICOM格式转NIfTI标准格式",
    icon: RefreshCw,
    inputs: [".dcm文件"],
    outputs: [".nii文件"],
    details: ["序列识别", "格式标准化", "元数据保留"],
  },
  {
    id: 3,
    name: "视频生成",
    code: "convert_video",
    description: "NIfTI切片转MP4视频",
    icon: FileVideo,
    inputs: [".nii文件"],
    outputs: [".mp4视频"],
    details: ["切片提取", "帧合成", "24fps输出"],
  },
  {
    id: 4,
    name: "JSON清洗",
    code: "clean_json",
    description: "数据清洗与格式标准化",
    icon: FileJson,
    inputs: ["原始JSON"],
    outputs: ["清洗后JSON"],
    details: ["字段过滤", "格式统一", "异常处理"],
  },
  {
    id: 5,
    name: "测试集复制",
    code: "copy_to_test",
    description: "构建标准化测试数据集",
    icon: FolderSync,
    inputs: ["处理后数据"],
    outputs: ["测试集目录"],
    details: ["路径重组", "索引生成", "完整性校验"],
  },
  {
    id: 6,
    name: "路径更新",
    code: "update_paths",
    description: "更新数据引用路径",
    icon: FileImage,
    inputs: ["JSON配置"],
    outputs: ["更新后配置"],
    details: ["路径映射", "引用检查", "一致性验证"],
  },
  {
    id: 7,
    name: "标签生成",
    code: "generate_labels",
    description: "基于Qwen3-VL生成医学标签",
    icon: Tags,
    inputs: ["MRI视频", "医疗报告"],
    outputs: ["结构化标签JSON"],
    details: ["多模态理解", "标签推理", "结构化输出"],
    highlight: true,
  },
];

export function Pipeline() {
  return (
    <section id="pipeline" className="py-24 px-6 bg-muted/30">
      <div className="max-w-7xl mx-auto">
        {/* Section header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="text-center mb-16"
        >
          <span className="inline-block px-4 py-1.5 rounded-full bg-primary/10 text-primary text-sm font-medium mb-4">
            系统架构
          </span>
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            7阶段处理流水线
          </h2>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            基于管道过滤器（Pipeline Filter）设计模式，每个阶段独立可配置，支持灵活扩展
          </p>
        </motion.div>

        {/* Pipeline visualization */}
        <div className="relative">
          {/* Connection line */}
          <div className="absolute top-1/2 left-0 right-0 h-0.5 bg-border hidden lg:block" />
          
          {/* Stages */}
          <div className="grid lg:grid-cols-7 gap-4">
            {stages.map((stage, index) => (
              <motion.div
                key={stage.id}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.4, delay: index * 0.08 }}
                className="relative"
              >
                {/* Stage card */}
                <div
                  className={`relative p-4 rounded-xl border transition-all duration-300 hover:scale-105 ${
                    stage.highlight
                      ? "bg-gradient-to-br from-primary/20 to-accent/10 border-primary/40"
                      : "bg-card border-border hover:border-primary/30"
                  }`}
                >
                  {/* Stage number */}
                  <div className={`absolute -top-3 left-4 px-2 py-0.5 rounded-full text-xs font-bold ${
                    stage.highlight
                      ? "bg-primary text-primary-foreground"
                      : "bg-muted text-muted-foreground"
                  }`}>
                    Stage {stage.id}
                  </div>

                  {/* Icon */}
                  <div className={`inline-flex p-2.5 rounded-lg mb-3 ${
                    stage.highlight
                      ? "bg-primary/20"
                      : "bg-muted"
                  }`}>
                    <stage.icon className={`w-5 h-5 ${
                      stage.highlight ? "text-primary" : "text-muted-foreground"
                    }`} />
                  </div>

                  {/* Content */}
                  <h3 className="font-semibold text-sm mb-1">{stage.name}</h3>
                  <p className="text-xs text-muted-foreground mb-3 leading-relaxed">
                    {stage.description}
                  </p>

                  {/* Code badge */}
                  <code className="inline-block px-2 py-1 rounded bg-muted text-xs font-mono text-muted-foreground">
                    {stage.code}
                  </code>

                  {/* Details */}
                  <div className="mt-3 pt-3 border-t border-border/50">
                    <div className="space-y-1">
                      {stage.details.map((detail, i) => (
                        <div key={i} className="flex items-center gap-1.5 text-xs text-muted-foreground">
                          <CheckCircle2 className="w-3 h-3 text-primary shrink-0" />
                          <span>{detail}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Highlight glow */}
                  {stage.highlight && (
                    <div className="absolute inset-0 rounded-xl bg-primary/5 animate-pulse-glow pointer-events-none" />
                  )}
                </div>

                {/* Arrow connector (desktop) */}
                {index < stages.length - 1 && (
                  <div className="hidden lg:flex absolute -right-2 top-1/2 -translate-y-1/2 z-10">
                    <ArrowRight className="w-4 h-4 text-primary" />
                  </div>
                )}
              </motion.div>
            ))}
          </div>
        </div>

        {/* Data flow summary */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.6 }}
          className="mt-16 p-6 rounded-2xl bg-card border border-border"
        >
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <RefreshCw className="w-5 h-5 text-primary" />
            数据流转概览
          </h3>
          <div className="flex flex-wrap items-center gap-3 text-sm">
            <span className="px-3 py-1.5 rounded-lg bg-muted font-mono">
              原始DICOM
            </span>
            <ArrowRight className="w-4 h-4 text-muted-foreground" />
            <span className="px-3 py-1.5 rounded-lg bg-muted font-mono">
              NIfTI + MP4
            </span>
            <ArrowRight className="w-4 h-4 text-muted-foreground" />
            <span className="px-3 py-1.5 rounded-lg bg-muted font-mono">
              清洗后JSON
            </span>
            <ArrowRight className="w-4 h-4 text-muted-foreground" />
            <span className="px-3 py-1.5 rounded-lg bg-primary/20 text-primary font-mono font-semibold">
              40+结构化标签
            </span>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
