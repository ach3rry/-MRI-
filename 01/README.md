# 膝关节MRI数据处理系统

端到端的数据处理流水线，用于膝关节MRI医学影像数据的自动化处理。

## 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                     数据处理流水线                              │
├─────────────────────────────────────────────────────────────────┤
│  阶段1: 医疗报告提取 → 从报告单图片提取结构化信息                │
│  阶段2: DICOM转换    → DICOM序列转NIfTI格式                      │
│  阶段3: 视频转换     → NIfTI转MP4视频                            │
│  阶段4: JSON清洗     → 清洗数据保留核心字段                      │
│  阶段5: 复制到测试集 → 复制GJB文件夹到测试集                     │
│  阶段6: 路径更新     → 更新JSON文件路径                          │
│  阶段7: 标签生成     → 基于报告生成结构化标签                    │
└─────────────────────────────────────────────────────────────────┘
```

## 目录结构

```
01/
├── main.py              # 主入口脚本
├── pipeline.py          # 流水线核心模块
├── config.py            # 配置管理
├── requirements.txt     # 依赖列表
├── README.md            # 说明文档
├── stages/              # 处理阶段模块
│   ├── __init__.py
│   ├── base.py          # 阶段基类
│   ├── report_extraction.py    # 报告提取
│   ├── dicom_conversion.py     # DICOM转换
│   ├── video_conversion.py     # 视频转换
│   ├── json_cleaning.py        # JSON清洗
│   ├── copy_to_test.py         # 复制到测试集
│   ├── path_update.py          # 路径更新
│   └── label_generation.py     # 标签生成
└── utils/               # 工具模块
    ├── __init__.py
    ├── logger.py        # 日志管理
    ├── file_utils.py    # 文件操作
    └── json_utils.py    # JSON操作
```

## 安装

```bash
# 安装依赖
pip install -r requirements.txt
```

## 使用方法

### 1. 运行完整流水线

```bash
cd 01
python main.py
```

### 2. 运行指定阶段

```bash
# 只运行DICOM转换到视频转换
python main.py --start-stage "DICOM转NIfTI" --end-stage "NIfTI转MP4视频"

# 跳过某些阶段
python main.py --skip-stages "标签生成" "视频转换"

# 只执行指定阶段
python main.py --only-stages "医疗报告提取" "JSON数据清洗"
```

### 3. 指定数据目录

```bash
python main.py --input-dir ./data --test-set-dir ./test --output-dir ./output
```

### 4. 查看可用阶段

```bash
python main.py --list-stages
```

### 5. 验证配置

```bash
python main.py --validate-only
```

## 配置说明

在 `config.py` 中可以修改以下配置：

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `input_dir` | 输入数据目录 | `./202505-202506` |
| `test_set_dir` | 测试集目录 | `./测试集` |
| `output_dir` | 输出目录 | `./output` |
| `model_path` | 报告提取模型路径 | `./model` |
| `label_model_path` | 标签生成模型路径 | `./qwen3-1.7B` |

## 阶段说明

### 阶段1: 医疗报告提取
- **输入**: 报告单图片 (`报告单.jpg`)
- **输出**: CSV文件 + JSON文件
- **功能**: 使用Qwen3-VL模型从报告单提取结构化信息

### 阶段2: DICOM转NIfTI
- **输入**: DICOM序列文件
- **输出**: NIfTI格式文件 (`.nii`)
- **功能**: 将DICOM医学影像转换为标准NIfTI格式

### 阶段3: NIfTI转MP4
- **输入**: NIfTI文件
- **输出**: MP4视频文件
- **功能**: 将3D医学影像转换为视频以便查看

### 阶段4: JSON数据清洗
- **输入**: GJB开头的JSON文件
- **输出**: 清洗后的JSON文件
- **功能**: 仅保留核心字段（检查方法、MR表现、诊断意见、顺序编号、文件路径）

### 阶段5: 复制到测试集
- **输入**: GJB文件夹
- **输出**: 测试集目录
- **功能**: 将处理好的数据复制到测试集目录

### 阶段6: 更新JSON路径
- **输入**: 测试集中的JSON文件
- **输出**: 更新后的JSON文件
- **功能**: 更新文件路径字段为绝对路径

### 阶段7: 膝关节MRI标签生成
- **输入**: 包含报告信息的JSON文件
- **输出**: 添加标签字段的JSON文件
- **功能**: 使用大语言模型生成结构化医学标签

## 标签结构

生成的标签包含以下字段：

```json
{
  "半月板": {
    "是否异常": false,
    "损伤分级": [],
    "是否撕裂": false,
    "类型": []
  },
  "韧带": {
    "前交叉韧带": "正常",
    "后交叉韧带": "正常",
    "内侧副韧带": "正常",
    "外侧副韧带": "正常",
    "髌韧带": "正常",
    "股四头肌腱": "正常"
  },
  "骨软骨单元": {
    "软骨损伤": false,
    "软骨变薄": false,
    "软骨缺损": false,
    "骨髓水肿": false,
    "骨挫伤": false,
    "骨质增生": false,
    "骨折": false,
    "骨囊变": false,
    "软骨下骨硬化": false
  },
  "髌股关节": {
    "髌骨软化": false,
    "髌骨高位": false,
    "髌骨低位": false,
    "髌骨不稳": false,
    "髌骨倾斜": false,
    "髌股关节紊乱": false
  },
  "滑膜关节腔": {
    "关节积液": "无",
    "滑膜炎": false,
    "滑膜增生": false
  },
  "囊性病变": {
    "是否存在": false,
    "类型": []
  },
  "其他结构": {
    "髂胫束异常": false,
    "腘肌腱异常": false,
    "关节游离体": false
  },
  "病理机制": {
    "退行性改变": false,
    "创伤性改变": false,
    "炎症性改变": false,
    "术后改变": false
  },
  "任务标签": {
    "半月板损伤": false,
    "韧带损伤": false,
    "骨软骨病变": false,
    "髌股关节病变": false,
    "关节积液": false,
    "囊性病变": false,
    "退行性疾病": false,
    "创伤性疾病": false,
    "炎症性疾病": false,
    "术后状态": false
  },
  "主要病变类型": "正常"
}
```

## 日志

- 日志文件保存在 `./logs/` 目录
- 文件名格式: `Pipeline_YYYYMMDD_HHMMSS.log`
- 执行报告保存在: `pipeline_report_YYYYMMDD_HHMMSS.json`

## 依赖说明

- **numpy**: 数值计算
- **pydicom**: DICOM文件读取
- **nibabel**: NIfTI文件处理
- **opencv-python**: 视频编码
- **torch/transformers/modelscope**: AI模型推理

## 注意事项

1. 确保模型文件已下载并放置在正确位置
2. DICOM转换需要较大的内存空间
3. 标签生成需要GPU加速以获得更好性能
4. 建议在处理大量数据前先用小样本测试

## 许可证

MIT License
