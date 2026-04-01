"use client";

import { motion } from "framer-motion";
import { 
  Workflow, 
  Tags, 
  TrendingDown, 
  Brain,
  FileVideo,
  FileJson,
  Layers
} from "lucide-react";

const features = [
  {
    icon: Workflow,
    title: "端到端自动化流水线",
    description: "7阶段管道过滤器架构，从DICOM原始数据到结构化标签，全流程无人工干预",
    highlight: "Pipeline Filter Pattern",
    color: "primary",
  },
  {
    icon: Tags,
    title: "40+结构化医学标签",
    description: "覆盖病变类型、解剖位置、严重程度、MR信号特征等多维度标签体系",
    highlight: "知识图谱驱动",
    color: "accent",
  },
  {
    icon: TrendingDown,
    title: "90%成本降低",
    description: "相比传统人工标注，大幅降低时间和人力成本，提升标注一致性",
    highlight: "ROI显著",
    color: "success",
  },
  {
    icon: Brain,
    title: "Qwen3-VL 1.7B模型",
    description: "轻量级多模态大模型，支持视觉理解与结构化输出，本地化部署",
    highlight: "边缘计算友好",
    color: "primary",
  },
  {
    icon: FileVideo,
    title: "DICOM转多模态",
    description: "支持DICOM到NIfTI、MP4视频等多种格式转换，便于模型训练",
    highlight: "多格式输出",
    color: "accent",
  },
  {
    icon: FileJson,
    title: "结构化JSON输出",
    description: "标准化数据格式，便于下游任务集成和数据分析",
    highlight: "标准接口",
    color: "primary",
  },
];

const colorMap = {
  primary: "bg-primary/10 text-primary border-primary/20",
  accent: "bg-accent/10 text-accent border-accent/20",
  success: "bg-success/10 text-success border-success/20",
};

const iconColorMap = {
  primary: "text-primary",
  accent: "text-accent",
  success: "text-success",
};

export function Features() {
  return (
    <section id="features" className="py-24 px-6">
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
            核心特性
          </span>
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            创新技术亮点
          </h2>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            结合深度学习与医学影像处理领域的最新技术，打造高效、精准的自动化标注系统
          </p>
        </motion.div>

        {/* Features grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature, index) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.4, delay: index * 0.1 }}
              className="group relative p-6 rounded-2xl bg-card border border-border hover:border-primary/30 transition-all duration-300"
            >
              {/* Icon */}
              <div className={`inline-flex p-3 rounded-xl bg-muted mb-4`}>
                <feature.icon className={`w-6 h-6 ${iconColorMap[feature.color as keyof typeof iconColorMap]}`} />
              </div>

              {/* Content */}
              <h3 className="text-lg font-semibold mb-2 group-hover:text-primary transition-colors">
                {feature.title}
              </h3>
              <p className="text-muted-foreground text-sm mb-4 leading-relaxed">
                {feature.description}
              </p>

              {/* Highlight badge */}
              <span className={`inline-block px-3 py-1 rounded-full text-xs font-medium border ${colorMap[feature.color as keyof typeof colorMap]}`}>
                {feature.highlight}
              </span>

              {/* Hover effect */}
              <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-primary/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none" />
            </motion.div>
          ))}
        </div>

        {/* Additional highlight */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.4 }}
          className="mt-12 p-8 rounded-2xl bg-gradient-to-r from-primary/10 via-accent/5 to-primary/10 border border-primary/20"
        >
          <div className="flex flex-col md:flex-row items-center justify-between gap-6">
            <div className="flex items-center gap-4">
              <div className="p-4 rounded-xl bg-primary/20">
                <Layers className="w-8 h-8 text-primary" />
              </div>
              <div>
                <h3 className="text-xl font-semibold mb-1">模块化可扩展架构</h3>
                <p className="text-muted-foreground">
                  基于管道过滤器设计模式，各处理阶段可独立配置、替换和扩展
                </p>
              </div>
            </div>
            <a
              href="#pipeline"
              className="shrink-0 px-6 py-3 bg-primary text-primary-foreground rounded-xl font-medium hover:bg-primary/90 transition-colors"
            >
              查看架构详情
            </a>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
