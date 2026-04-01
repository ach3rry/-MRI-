"use client";

import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

const labelCategories = [
  {
    name: "病变类型",
    color: "primary",
    labels: [
      "正常", "退行性疾病", "半月板疾病", "韧带疾病",
      "骨软骨疾病", "炎症性疾病", "术后状态", "混合型"
    ],
  },
  {
    name: "解剖位置",
    color: "accent",
    labels: [
      "前交叉韧带", "后交叉韧带", "内侧半月板", "外侧半月板",
      "内侧副韧带", "外侧副韧带", "髌骨", "股骨髁",
      "胫骨平台", "腘窝", "髌上囊", "关节软骨"
    ],
  },
  {
    name: "严重程度",
    color: "warning",
    labels: [
      "轻度", "中度", "重度", "完全撕裂", "部分撕裂"
    ],
  },
  {
    name: "MR信号特征",
    color: "success",
    labels: [
      "T1高信号", "T1低信号", "T2高信号", "T2低信号",
      "信号不均", "增强明显", "水肿信号"
    ],
  },
  {
    name: "伴随征象",
    color: "destructive",
    labels: [
      "积液", "囊肿", "骨髓水肿", "滑膜增厚",
      "游离体", "骨赘形成", "软骨下骨硬化"
    ],
  },
];

const colorMap = {
  primary: {
    bg: "bg-primary/10",
    border: "border-primary/30",
    text: "text-primary",
    dot: "bg-primary",
  },
  accent: {
    bg: "bg-accent/10",
    border: "border-accent/30",
    text: "text-accent",
    dot: "bg-accent",
  },
  warning: {
    bg: "bg-warning/10",
    border: "border-warning/30",
    text: "text-warning",
    dot: "bg-warning",
  },
  success: {
    bg: "bg-success/10",
    border: "border-success/30",
    text: "text-success",
    dot: "bg-success",
  },
  destructive: {
    bg: "bg-destructive/10",
    border: "border-destructive/30",
    text: "text-destructive",
    dot: "bg-destructive",
  },
};

export function Labels() {
  const totalLabels = labelCategories.reduce(
    (sum, cat) => sum + cat.labels.length,
    0
  );

  return (
    <section id="labels" className="py-24 px-6">
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
            标签体系
          </span>
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            {totalLabels}+ 结构化医学标签
          </h2>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            基于医学知识图谱构建的多维度标签体系，覆盖膝关节MRI诊断的关键维度
          </p>
        </motion.div>

        {/* Label categories */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {labelCategories.map((category, index) => {
            const colors = colorMap[category.color as keyof typeof colorMap];
            return (
              <motion.div
                key={category.name}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.4, delay: index * 0.1 }}
                className="p-6 rounded-2xl bg-card border border-border"
              >
                {/* Category header */}
                <div className="flex items-center gap-3 mb-4">
                  <div className={cn("w-3 h-3 rounded-full", colors.dot)} />
                  <h3 className="font-semibold">{category.name}</h3>
                  <span className="ml-auto text-sm text-muted-foreground">
                    {category.labels.length}项
                  </span>
                </div>

                {/* Labels */}
                <div className="flex flex-wrap gap-2">
                  {category.labels.map((label) => (
                    <span
                      key={label}
                      className={cn(
                        "px-3 py-1 rounded-full text-sm border",
                        colors.bg,
                        colors.border,
                        colors.text
                      )}
                    >
                      {label}
                    </span>
                  ))}
                </div>
              </motion.div>
            );
          })}
        </div>

        {/* JSON example */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.5 }}
          className="mt-12 p-6 rounded-2xl bg-card border border-border"
        >
          <h3 className="text-lg font-semibold mb-4">输出示例 (JSON)</h3>
          <pre className="p-4 rounded-xl bg-muted overflow-x-auto text-sm font-mono">
            <code className="text-muted-foreground">{`{
  "patient_id": "GJB_001",
  "scan_date": "2025-05-15",
  "primary_lesion_type": "半月板疾病",
  "anatomical_locations": ["内侧半月板", "后角"],
  "severity": "中度",
  "mr_signals": ["T2高信号", "信号不均"],
  "associated_findings": ["积液", "骨髓水肿"],
  "diagnosis_confidence": 0.92,
  "recommendations": ["建议进一步关节镜检查"]
}`}</code>
          </pre>
        </motion.div>
      </div>
    </section>
  );
}
