#!/bin/bash

# SpinGenius 测试脚本
# 测试两篇样例文章的改写功能

echo "======================================"
echo "SpinGenius 伪原创测试"
echo "======================================"
echo ""

# 激活虚拟环境
source venv/bin/activate

# 测试1: 技术博客
echo "📝 测试1: 技术博客改写"
echo "--------------------------------------"
python cli.py rewrite examples/tech_sample.html \
  -o output/tech_rewrite.html \
  --mode local \
  --type tech \
  --check-similarity \
  --show-diff

echo ""
echo ""

# 测试2: 保险文章
echo "📝 测试2: 保险文章改写"
echo "--------------------------------------"
python cli.py rewrite examples/insurance_sample.html \
  -o output/insurance_rewrite.html \
  --mode local \
  --type insurance \
  --check-similarity \
  --show-diff

echo ""
echo "======================================"
echo "✅ 测试完成！"
echo "======================================"
echo ""
echo "输出文件："
echo "  - output/tech_rewrite.html"
echo "  - output/insurance_rewrite.html"
echo ""
