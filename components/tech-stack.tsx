"use client";

import { motion } from "framer-motion";

const technologies = [
  {
    category: "深度学习框架",
    items: [
      { name: "PyTorch", description: "深度学习基础框架" },
      { name: "Transformers", description: "Hugging Face模型库" },
      { name: "Qwen3-VL 1.7B", description: "多模态大语言模型" },
    ],
  },
  {
    category: "医学影像处理",
    items: [
      { name: "pydicom", description: "DICOM文件解析" },
      { name: "nibabel", description: "NIfTI格式处理" },
      { name: "SimpleITK", description: "医学图像处理" },
    ],
  },
  {
    category: "数据处理",
    items: [
      { name: "OpenCV", description: "图像与视频处理" },
      { name: "NumPy", description: "数值计算" },
      { name: "Pandas", description: "数据分析" },
    ],
  },
  {
    category: "架构设计",
    items: [
      { name: "Pipeline Filter", description: "管道过滤器模式" },
      { name: "Dataclass Config", description: "类型安全配置" },
      { name: "Modular Stages", description: "模块化处理阶段" },
    ],
  },
];

const metrics = [
  { label: "处理速度", value: "~30s/样本", description: "端到端处理" },
  { label: "标签准确率", value: ">85%", description: "与专家标注对比" },
  { label: "模型大小", value: "1.7B", description: "参数量" },
  { label: "显存需求", value: "<8GB", description: "推理模式" },
];

export function TechStack() {
  return (
    <section id="tech" className="py-24 px-6 bg-muted/30">
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
            技术实现
          </span>
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            技术栈与性能指标
          </h2>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            基于成熟的开源技术栈构建，注重可维护性和可扩展性
          </p>
        </motion.div>

        {/* Performance metrics */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-12"
        >
          {metrics.map((metric, index) => (
            <motion.div
              key={metric.label}
              initial={{ opacity: 0, scale: 0.95 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 0.3, delay: index * 0.1 }}
              className="p-6 rounded-2xl bg-card border border-border text-center"
            >
              <div className="text-2xl md:text-3xl font-bold gradient-text mb-1">
                {metric.value}
              </div>
              <div className="text-sm font-medium text-foreground mb-1">
                {metric.label}
              </div>
              <div className="text-xs text-muted-foreground">
                {metric.description}
              </div>
            </motion.div>
          ))}
        </motion.div>

        {/* Technology grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {technologies.map((tech, index) => (
            <motion.div
              key={tech.category}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.4, delay: index * 0.1 }}
              className="p-6 rounded-2xl bg-card border border-border"
            >
              <h3 className="font-semibold text-primary mb-4">
                {tech.category}
              </h3>
              <div className="space-y-3">
                {tech.items.map((item) => (
                  <div key={item.name} className="flex flex-col">
                    <span className="font-medium text-sm">{item.name}</span>
                    <span className="text-xs text-muted-foreground">
                      {item.description}
                    </span>
                  </div>
                ))}
              </div>
            </motion.div>
          ))}
        </div>

        {/* Code architecture */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.4 }}
          className="mt-12 p-6 rounded-2xl bg-card border border-border"
        >
          <h3 className="text-lg font-semibold mb-4">项目结构</h3>
          <pre className="p-4 rounded-xl bg-muted overflow-x-auto text-sm font-mono">
            <code className="text-muted-foreground">{`01/
├── main.py              # 主入口
├── pipeline.py          # 流水线调度
├── config.py            # 统一配置
├── stages/              # 处理阶段
│   ├── base.py          # 基类定义
│   ├── report_extraction.py
│   ├── dicom_conversion.py
│   ├── video_conversion.py
│   ├── json_cleaning.py
│   ├── copy_to_test.py
│   ├── path_update.py
│   └── label_generation.py
└── utils/               # 工具函数
    ├── file_utils.py
    ├── json_utils.py
    └── logger.py`}</code>
          </pre>
        </motion.div>
      </div>
    </section>
  );
}
