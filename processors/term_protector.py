"""
专业术语保护器
在改写前后保护专业术语不被修改
"""

import re
from typing import List, Dict, Tuple


class TermProtector:
    """专业术语保护器"""
    
    def __init__(self, protected_terms: List[str]):
        """
        初始化术语保护器
        
        Args:
            protected_terms: 需要保护的术语列表
        """
        self.protected_terms = protected_terms
        self.term_map = {}
        self.placeholder_prefix = "___TERM_"
        
    def protect(self, text: str) -> str:
        """
        保护文本中的专业术语
        
        Args:
            text: 原始文本
            
        Returns:
            替换后的文本
        """
        self.term_map = {}
        protected_text = text
        
        for idx, term in enumerate(self.protected_terms):
            # 使用正则表达式进行全词匹配
            pattern = r'\b' + re.escape(term) + r'\b'
            placeholder = f"{self.placeholder_prefix}{idx}___"
            
            # 记录替换
            if re.search(pattern, protected_text):
                self.term_map[placeholder] = term
                protected_text = re.sub(pattern, placeholder, protected_text)
        
        return protected_text
    
    def restore(self, text: str) -> str:
        """
        还原文本中的专业术语
        
        Args:
            text: 保护后的文本
            
        Returns:
            还原后的文本
        """
        restored_text = text
        
        for placeholder, term in self.term_map.items():
            restored_text = restored_text.replace(placeholder, term)
        
        return restored_text
    
    def verify(self, original: str, rewritten: str) -> Dict[str, any]:
        """
        验证术语是否被正确保护
        
        Args:
            original: 原始文本
            rewritten: 改写后文本
            
        Returns:
            验证结果
        """
        original_terms = self._extract_terms(original)
        rewritten_terms = self._extract_terms(rewritten)
        
        missing_terms = original_terms - rewritten_terms
        extra_terms = rewritten_terms - original_terms
        
        return {
            'original_count': len(original_terms),
            'rewritten_count': len(rewritten_terms),
            'missing_terms': list(missing_terms),
            'extra_terms': list(extra_terms),
            'protected': len(missing_terms) == 0
        }
    
    def _extract_terms(self, text: str) -> set:
        """提取文本中出现的保护术语"""
        found_terms = set()
        
        for term in self.protected_terms:
            pattern = r'\b' + re.escape(term) + r'\b'
            if re.search(pattern, text):
                found_terms.add(term)
        
        return found_terms
