# Text2PPT

将文字内容转化为精美 PowerPoint 演示文稿的 AI 工具。

## 功能特点

- **智能内容规划**：使用 Seed 2.0 语言模型将输入文字自动转化为结构化的 PPT 内容
- **AI 图像生成**：使用 Seadream 4.5 文生图模型为每一页生成精美的图片（图片内含文字）
- **自动 PPT 组装**：使用 python-pptx 将生成的图片自动组装成 PowerPoint 演示文稿

## 工作流程

```
用户输入文字
    ↓
[Seed 2.0 LLM] 生成 PPT 结构和文生图提示词
    ↓
[Seadream 4.5] 生成每页的图片
    ↓
[python-pptx] 组装成 PPTX 文件
    ↓
输出完整的 PPT 文件
```

## 安装

1. 安装依赖：

```bash
cd text2ppt
pip install -r requirements.txt
```

2. 配置环境变量：

```bash
# 复制示例配置
cp .env.example .env

# 编辑 .env 文件，填入你的 API Key
ARK_API_KEY=your-api-key-here
```

## 使用方法

### 交互式模式

直接运行程序，按提示输入内容：

```bash
python main.py
```

### 命令行模式

从文本文件生成 PPT：

```bash
python main.py --input your_content.txt --output my_presentation --slides 6
```

直接传入文字：

```bash
python main.py --text "人工智能在医疗领域的应用..." --slides 5
```

### 参数说明

| 参数 | 简写 | 说明 |
|------|------|------|
| `--input` | `-i` | 输入文本文件路径 |
| `--text` | `-t` | 直接输入文本内容 |
| `--output` | `-o` | 输出文件名（不含扩展名） |
| `--slides` | `-s` | 生成幻灯片数量（默认5） |
| `--quiet` | `-q` | 减少输出信息 |

## 项目结构

```
text2ppt/
├── main.py              # 主程序入口
├── config.py            # 配置文件
├── llm_client.py        # LLM 客户端（Seed 2.0）
├── image_generator.py   # 图像生成器（Seadream 4.5）
├── ppt_generator.py     # PPT 生成器
├── web_server.py        # Flask Web 服务
├── static/              # 前端静态文件
├── requirements.txt     # Python 依赖
├── .env.example         # 环境变量示例
├── .env                 # 环境变量（需自行创建）
└── output/              # 输出目录
    ├── images/          # 生成的图片
    └── *.pptx           # 生成的 PPT 文件
```

## 模型说明

### Seed 2.0 (语言模型)
- **用途**: 将用户输入的文字内容分析并转化为结构化的 PPT 内容，同时生成适合文生图模型的英文提示词

### Seadream 4.5 (文生图模型)
- **用途**: 根据提示词生成包含文字的高质量 PPT 页面图片
- **输出**: 1920x1080 (16:9) 分辨率的图片

## Web 界面

启动 Web 服务：

```bash
python web_server.py
```

然后访问 http://localhost:5000

## 示例

### 输入

```
人工智能在医疗健康领域的应用：
- 疾病诊断辅助
- 药物研发加速
- 个性化治疗方案
- 医疗影像分析
- 健康监测与预警
```

### 输出

生成一个包含 5 页幻灯片的 PPTX 文件：
1. 封面页：AI in Healthcare 主题
2. 疾病诊断：AI辅助诊断技术
3. 药物研发：加速新药发现
4. 医疗影像：智能影像分析
5. 总结展望：未来医疗的 AI 愿景

## 注意事项

1. 确保已正确配置 `ARK_API_KEY` 环境变量
2. 图片生成可能需要较长时间（每张约 30-60 秒）
3. 生成的图片和 PPT 保存在 `output/` 目录
4. 建议每个 PPT 生成 3-7 页幻灯片效果最佳

## 许可证

MIT License
