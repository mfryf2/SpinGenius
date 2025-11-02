# SpinGenius - 智能文章伪原创工具

基于本地大语言模型的文章改写工具，支持技术博客和保险文章的智能改写。

## 功能特性

- ✅ 本地模型改写（Ollama + Qwen2.5:14b）
- ✅ HTML结构保留
- ✅ 相似度检测
- ✅ 文本差异对比
- ✅ 批量处理

## 快速开始

### 1. 环境要求

- Python 3.9+
- Ollama服务
- qwen2.5:14b模型

### 2. 安装依赖

```bash
source venv/bin/activate
pip install -r requirements.txt
```

### 3. 运行测试

```bash
./test.sh
```

## 使用方法

### 单文件改写

```bash
# 技术博客
python cli.py rewrite examples/tech_sample.html \
  -o output/tech_rewrite.html \
  --mode local \
  --type tech \
  --check-similarity \
  --show-diff

# 保险文章
python cli.py rewrite examples/insurance_sample.html \
  -o output/insurance_rewrite.html \
  --mode local \
  --type insurance \
  --check-similarity \
  --show-diff
```

### 相似度检测

```bash
python cli.py check original.html rewritten.html
```

### 批量处理

```bash
python cli.py batch "articles/*.html" -o output/
```

## 项目结构

```
SpinGenius/
├── cli.py                  # 主程序入口
├── config.yaml             # 配置文件
├── requirements.txt        # Python依赖
├── test.sh                 # 测试脚本
├── core/                   # 核心功能模块
│   ├── rewriter.py        # 改写器基类
│   ├── local_rewriter.py  # 本地模型改写
│   └── api_rewriter.py    # API模式改写
├── processors/             # 处理器模块
│   ├── html_parser.py     # HTML解析
│   ├── similarity.py      # 相似度检测
│   └── term_protector.py  # 术语保护
├── prompts/                # 提示词模板
│   ├── tech_blog.txt      # 技术博客提示词
│   └── insurance_blog.txt # 保险文章提示词
├── examples/               # 示例文件
│   ├── tech_sample.html
│   └── insurance_sample.html
└── output/                 # 输出目录
```

## 配置说明

编辑 `config.yaml` 修改模型配置：

```yaml
local:
  model: qwen2.5:14b
  base_url: http://localhost:11434
```

## 测试结果

- ✅ 技术博客改写：2,042字节 → 2,804字节 (+37.3%)
- ✅ 保险文章改写：2,552字节 → 3,439字节 (+34.7%)
- ✅ 所有功能测试通过

## 许可证

MIT License
