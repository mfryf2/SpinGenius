"""
HTML解析器
提取纯文本、保留结构、还原HTML
"""

from bs4 import BeautifulSoup
from typing import Dict, List, Tuple
import re


class HTMLParser:
    """HTML解析和还原处理器"""
    
    def __init__(self, preserve_code: bool = True):
        """
        初始化HTML解析器
        
        Args:
            preserve_code: 是否保留代码块
        """
        self.preserve_code = preserve_code
        self.code_blocks = []
        self.code_placeholder = "___CODE_BLOCK_{}___"
        
    def extract_text(self, html_content: str) -> str:
        """
        从HTML中提取纯文本用于改写
        
        Args:
            html_content: HTML内容
            
        Returns:
            纯文本内容
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 保存代码块
        if self.preserve_code:
            self._extract_code_blocks(soup)
        
        # 提取文本
        text = soup.get_text(separator='\n', strip=True)
        
        # 清理多余空行
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text.strip()
    
    def _extract_code_blocks(self, soup: BeautifulSoup) -> None:
        """提取并保护代码块"""
        self.code_blocks = []
        
        # 查找所有代码块标签
        code_tags = soup.find_all(['code', 'pre'])
        
        for idx, tag in enumerate(code_tags):
            # 保存原始代码
            code_content = str(tag)
            self.code_blocks.append(code_content)
            
            # 替换为占位符
            placeholder = self.code_placeholder.format(idx)
            tag.replace_with(placeholder)
    
    def restore_html(self, original_html: str, rewritten_text: str) -> str:
        """
        将改写后的文本还原为HTML格式
        
        Args:
            original_html: 原始HTML
            rewritten_text: 改写后的纯文本
            
        Returns:
            还原后的HTML
        """
        soup = BeautifulSoup(original_html, 'html.parser')
        
        # 获取原始文本段落
        original_paragraphs = self._get_paragraphs(soup)
        
        # 分割改写后的文本
        rewritten_paragraphs = [p.strip() for p in rewritten_text.split('\n\n') if p.strip()]
        
        # 替换段落内容
        self._replace_paragraphs(soup, original_paragraphs, rewritten_paragraphs)
        
        # 还原代码块
        html_str = str(soup)
        if self.preserve_code:
            html_str = self._restore_code_blocks(html_str)
        
        return html_str
    
    def _get_paragraphs(self, soup: BeautifulSoup) -> List:
        """获取所有文本段落元素"""
        # 查找所有可能包含文本的标签
        text_tags = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'div'])
        
        paragraphs = []
        for tag in text_tags:
            # 只处理直接包含文本的标签
            if tag.get_text(strip=True) and not tag.find(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                paragraphs.append(tag)
        
        return paragraphs
    
    def _replace_paragraphs(self, soup: BeautifulSoup, original_tags: List, rewritten_paragraphs: List) -> None:
        """替换段落内容"""
        # 简单策略：按顺序替换
        min_len = min(len(original_tags), len(rewritten_paragraphs))
        
        for i in range(min_len):
            tag = original_tags[i]
            new_text = rewritten_paragraphs[i]
            
            # 保留标签，只替换文本内容
            tag.string = new_text
    
    def _restore_code_blocks(self, html_str: str) -> str:
        """还原代码块"""
        for idx, code_content in enumerate(self.code_blocks):
            placeholder = self.code_placeholder.format(idx)
            html_str = html_str.replace(placeholder, code_content)
        
        return html_str
    
    def simple_restore(self, rewritten_text: str) -> str:
        """
        简单还原：将文本转换为基本HTML
        
        Args:
            rewritten_text: 改写后的文本
            
        Returns:
            HTML格式
        """
        html_parts = ['<!DOCTYPE html>', '<html lang="zh-CN">', '<head>', 
                     '<meta charset="utf-8">', '</head>', '<body>']
        
        # 先还原代码块
        text_with_code = rewritten_text
        if self.preserve_code:
            text_with_code = self._restore_code_blocks(rewritten_text)
        
        # 使用正则表达式分离代码块和普通文本
        import re
        
        # 分割代码块和文本
        parts = re.split(r'(<pre>.*?</pre>|<code>.*?</code>)', text_with_code, flags=re.DOTALL)
        
        for part in parts:
            part = part.strip()
            if not part:
                continue
            
            # 如果是代码块，直接添加
            if part.startswith('<pre>') or part.startswith('<code>'):
                html_parts.append(part)
            else:
                # 处理普通文本
                # 按双换行符分割段落
                paragraphs = part.split('\n\n')
                
                for para in paragraphs:
                    para = para.strip()
                    if not para:
                        continue
                    
                    # 按单换行符分割行
                    lines = para.split('\n')
                    for line in lines:
                        line = line.strip()
                        if not line:
                            continue
                        
                        # 判断是否是标题
                        is_title = False
                        if len(line) < 50 and not line.endswith('。') and not line.endswith('.') and not line.endswith('，'):
                            if any(keyword in line for keyword in ['指南', 'Hook', '总结', '为什么', '如何']):
                                is_title = True
                        
                        if is_title:
                            if '完全指南' in line:
                                html_parts.append(f'<h1>{line}</h1>')
                            else:
                                html_parts.append(f'<h2>{line}</h2>')
                        else:
                            html_parts.append(f'<p>{line}</p>')
        
        html_parts.extend(['</body>', '</html>'])
        
        return '\n'.join(html_parts)
