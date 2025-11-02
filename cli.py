#!/usr/bin/env python3
"""
SpinGenius CLI
命令行入口
"""

import click
import os
import sys
from pathlib import Path
from colorama import init, Fore, Style
from typing import Optional
import difflib

# 初始化colorama
init(autoreset=True)

# 导入核心模块
from core.local_rewriter import LocalRewriter
from core.api_rewriter import APIRewriter
from processors.html_parser import HTMLParser
from processors.term_protector import TermProtector

# 相似度检测器是可选的
try:
    from processors.similarity import SimilarityChecker
    SIMILARITY_AVAILABLE = True
except ImportError:
    SIMILARITY_AVAILABLE = False


def show_text_diff(original: str, rewritten: str, max_lines: int = 30):
    """显示文本差异对比"""
    original_lines = original.split('\n')
    rewritten_lines = rewritten.split('\n')
    
    diff = difflib.unified_diff(
        original_lines,
        rewritten_lines,
        fromfile='原文',
        tofile='改写后',
        lineterm=''
    )
    
    print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}📝 文本差异对比 (Diff){Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
    
    count = 0
    for line in diff:
        if count >= max_lines:
            print(f"{Fore.YELLOW}... (仅显示前{max_lines}行差异){Style.RESET_ALL}")
            break
        
        if line.startswith('+') and not line.startswith('+++'):
            print(f"{Fore.GREEN}{line}{Style.RESET_ALL}")
        elif line.startswith('-') and not line.startswith('---'):
            print(f"{Fore.RED}{line}{Style.RESET_ALL}")
        elif line.startswith('@@'):
            print(f"{Fore.CYAN}{line}{Style.RESET_ALL}")
        else:
            print(line)
        count += 1
    
    print()


@click.group()
@click.version_option(version='1.0.0', prog_name='SpinGenius')
def cli():
    """
    SpinGenius - 智能文章伪原创工具
    
    支持本地模型和API两种模式，专为技术博客和保险文章设计。
    """
    pass


@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('-o', '--output', 'output_file', type=click.Path(), required=True,
              help='输出文件路径')
@click.option('-m', '--mode', type=click.Choice(['local', 'api']), default='local',
              help='改写模式: local(本地) 或 api(API)')
@click.option('-t', '--type', 'article_type', type=click.Choice(['tech', 'insurance']), 
              default='tech', help='文章类型: tech(技术博客) 或 insurance(保险文章)')
@click.option('-p', '--provider', type=click.Choice(['openai', 'claude', 'qwen']),
              help='API提供商 (仅在api模式下有效)')
@click.option('--check-similarity', is_flag=True, help='检查改写后的相似度')
@click.option('--show-diff', is_flag=True, help='显示文本差异对比')
@click.option('--preserve-html', is_flag=True, default=True, help='保留HTML结构')
def rewrite(input_file: str, output_file: str, mode: str, article_type: str, 
            provider: Optional[str], check_similarity: bool, show_diff: bool, preserve_html: bool):
    """
    改写文章
    
    示例:
    
    \b
    # 技术博客（本地模式）
    python cli.py rewrite input.html -o output.html --mode local --type tech
    
    \b
    # 保险文章（API模式）
    python cli.py rewrite input.html -o output.html --mode api --type insurance --provider openai
    """
    try:
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}SpinGenius - 文章改写工具{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
        
        # 读取输入文件
        print(f"{Fore.YELLOW}📖 读取文件: {input_file}{Style.RESET_ALL}")
        with open(input_file, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        # 解析HTML
        print(f"{Fore.YELLOW}🔍 解析HTML内容...{Style.RESET_ALL}")
        html_parser = HTMLParser(preserve_code=True)
        text_content = html_parser.extract_text(original_content)
        
        print(f"{Fore.GREEN}✓ 提取文本长度: {len(text_content)} 字符{Style.RESET_ALL}\n")
        
        # 初始化改写器
        if mode == 'local':
            print(f"{Fore.CYAN}🤖 使用本地模型改写{Style.RESET_ALL}")
            rewriter = LocalRewriter()
        else:
            provider = provider or 'openai'
            print(f"{Fore.CYAN}🌐 使用 {provider.upper()} API 改写{Style.RESET_ALL}")
            rewriter = APIRewriter(provider=provider)
        
        # 执行改写
        print(f"{Fore.YELLOW}✍️  开始改写 ({article_type} 类型)...{Style.RESET_ALL}")
        rewritten_text = rewriter.rewrite(text_content, article_type=article_type)
        
        # 还原HTML
        if preserve_html and original_content.strip().startswith('<'):
            print(f"{Fore.YELLOW}🔄 还原HTML结构...{Style.RESET_ALL}")
            rewritten_html = html_parser.restore_html(original_content, rewritten_text)
        else:
            print(f"{Fore.YELLOW}🔄 生成HTML格式...{Style.RESET_ALL}")
            rewritten_html = html_parser.simple_restore(rewritten_text)
        
        # 保存结果
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(rewritten_html)
        
        print(f"{Fore.GREEN}✓ 改写完成，已保存到: {output_file}{Style.RESET_ALL}\n")
        
        # 相似度检测
        if check_similarity:
            if not SIMILARITY_AVAILABLE:
                print(f"{Fore.YELLOW}⚠ 相似度检测功能未安装{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}  安装: pip install numpy sentence-transformers{Style.RESET_ALL}\n")
            else:
                print(f"{Fore.YELLOW}📊 检测相似度...{Style.RESET_ALL}")
                checker = SimilarityChecker()
                result = checker.check_quality(text_content, rewritten_text)
                
                status_color = Fore.GREEN if result['passed'] else Fore.RED
                print(f"{status_color}相似度: {result['similarity']:.2%}{Style.RESET_ALL}")
                print(f"{status_color}状态: {result['status']}{Style.RESET_ALL}")
                print(f"{status_color}评价: {result['message']}{Style.RESET_ALL}\n")
        
        # 显示差异对比
        if show_diff:
            show_text_diff(text_content, rewritten_text)
        
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}✨ 任务完成！{Style.RESET_ALL}")
        
    except Exception as e:
        print(f"\n{Fore.RED}❌ 错误: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)


@cli.command()
@click.argument('file1', type=click.Path(exists=True))
@click.argument('file2', type=click.Path(exists=True))
def check(file1: str, file2: str):
    """
    检查两个文件的相似度
    
    示例:
    
    \b
    python cli.py check original.html rewritten.html
    """
    try:
        if not SIMILARITY_AVAILABLE:
            print(f"{Fore.RED}❌ 相似度检测功能未安装{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}安装: pip install numpy sentence-transformers{Style.RESET_ALL}")
            sys.exit(1)
        
        print(f"{Fore.CYAN}📊 相似度检测{Style.RESET_ALL}\n")
        
        # 读取文件
        with open(file1, 'r', encoding='utf-8') as f:
            content1 = f.read()
        with open(file2, 'r', encoding='utf-8') as f:
            content2 = f.read()
        
        # 提取文本
        parser = HTMLParser()
        text1 = parser.extract_text(content1)
        text2 = parser.extract_text(content2)
        
        # 检测相似度
        checker = SimilarityChecker()
        result = checker.check_quality(text1, text2)
        
        # 显示结果
        print(f"文件1: {file1}")
        print(f"文件2: {file2}\n")
        
        status_color = Fore.GREEN if result['passed'] else Fore.RED
        print(f"{status_color}相似度: {result['similarity']:.2%}{Style.RESET_ALL}")
        print(f"{status_color}阈值: {result['threshold']:.2%}{Style.RESET_ALL}")
        print(f"{status_color}状态: {result['status']}{Style.RESET_ALL}")
        print(f"{status_color}评价: {result['message']}{Style.RESET_ALL}")
        
    except Exception as e:
        print(f"\n{Fore.RED}❌ 错误: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)


@cli.command()
@click.argument('input_pattern', type=str)
@click.option('-o', '--output-dir', type=click.Path(), required=True,
              help='输出目录')
@click.option('-m', '--mode', type=click.Choice(['local', 'api']), default='local',
              help='改写模式')
@click.option('-t', '--type', 'article_type', type=click.Choice(['tech', 'insurance']),
              default='tech', help='文章类型')
def batch(input_pattern: str, output_dir: str, mode: str, article_type: str):
    """
    批量处理文件
    
    示例:
    
    \b
    python cli.py batch "./articles/*.html" -o ./output/ --mode local --type tech
    """
    import glob
    from tqdm import tqdm
    
    try:
        # 查找文件
        files = glob.glob(input_pattern)
        if not files:
            print(f"{Fore.RED}未找到匹配的文件: {input_pattern}{Style.RESET_ALL}")
            return
        
        print(f"{Fore.CYAN}找到 {len(files)} 个文件{Style.RESET_ALL}\n")
        
        # 创建输出目录
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # 初始化改写器
        if mode == 'local':
            rewriter = LocalRewriter()
        else:
            rewriter = APIRewriter()
        
        html_parser = HTMLParser()
        
        # 批量处理
        success_count = 0
        for file_path in tqdm(files, desc="处理进度"):
            try:
                # 读取文件
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 改写
                text = html_parser.extract_text(content)
                rewritten = rewriter.rewrite(text, article_type=article_type)
                rewritten_html = html_parser.simple_restore(rewritten)
                
                # 保存
                output_file = Path(output_dir) / Path(file_path).name
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(rewritten_html)
                
                success_count += 1
                
            except Exception as e:
                print(f"\n{Fore.RED}处理失败 {file_path}: {str(e)}{Style.RESET_ALL}")
        
        print(f"\n{Fore.GREEN}✓ 完成! 成功处理 {success_count}/{len(files)} 个文件{Style.RESET_ALL}")
        
    except Exception as e:
        print(f"\n{Fore.RED}❌ 错误: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)


@cli.command()
def info():
    """显示系统信息和配置"""
    try:
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}SpinGenius 系统信息{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
        
        # 检查Ollama
        print(f"{Fore.YELLOW}本地模型 (Ollama):{Style.RESET_ALL}")
        try:
            rewriter = LocalRewriter()
            if rewriter.is_available():
                print(f"  {Fore.GREEN}✓ Ollama服务运行中{Style.RESET_ALL}")
                if rewriter.check_model_exists():
                    print(f"  {Fore.GREEN}✓ 模型 {rewriter.model} 已安装{Style.RESET_ALL}")
                else:
                    print(f"  {Fore.RED}✗ 模型 {rewriter.model} 未安装{Style.RESET_ALL}")
                    print(f"    运行: ollama pull {rewriter.model}")
            else:
                print(f"  {Fore.RED}✗ Ollama服务未运行{Style.RESET_ALL}")
                print(f"    运行: ollama serve")
        except Exception as e:
            print(f"  {Fore.RED}✗ 错误: {str(e)}{Style.RESET_ALL}")
        
        print()
        
        # 检查API配置
        print(f"{Fore.YELLOW}API配置:{Style.RESET_ALL}")
        from dotenv import load_dotenv
        load_dotenv()
        
        api_keys = {
            'OpenAI': os.getenv('OPENAI_API_KEY'),
            'Claude': os.getenv('CLAUDE_API_KEY'),
            'Qwen': os.getenv('QWEN_API_KEY'),
        }
        
        for name, key in api_keys.items():
            if key and not key.startswith('${'):
                print(f"  {Fore.GREEN}✓ {name} API Key 已配置{Style.RESET_ALL}")
            else:
                print(f"  {Fore.YELLOW}○ {name} API Key 未配置{Style.RESET_ALL}")
        
        print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        
    except Exception as e:
        print(f"\n{Fore.RED}❌ 错误: {str(e)}{Style.RESET_ALL}")


if __name__ == '__main__':
    cli()
