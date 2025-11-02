"""
API改写器
支持OpenAI、Claude、通义千问等API
"""

from typing import Dict, Any, Optional
from .rewriter import BaseRewriter
from colorama import Fore, Style
import os


class APIRewriter(BaseRewriter):
    """API改写器"""
    
    def __init__(self, config_path: str = "config.yaml", provider: str = None):
        super().__init__(config_path)
        self.api_config = self.config.get('api', {})
        self.provider = provider or self.api_config.get('provider', 'openai')
        self._init_client()
        
    def _init_client(self):
        """初始化API客户端"""
        if self.provider == 'openai':
            self._init_openai()
        elif self.provider == 'claude':
            self._init_claude()
        elif self.provider == 'qwen':
            self._init_qwen()
        else:
            raise ValueError(f"不支持的API提供商: {self.provider}")
    
    def _init_openai(self):
        """初始化OpenAI客户端"""
        try:
            from openai import OpenAI
            config = self.api_config.get('openai', {})
            api_key = config.get('api_key')
            
            if not api_key or api_key.startswith('${'):
                raise ValueError("请在.env文件中设置OPENAI_API_KEY")
            
            self.client = OpenAI(
                api_key=api_key,
                base_url=config.get('base_url')
            )
            self.model = config.get('model', 'gpt-4o')
        except ImportError:
            raise ImportError("请安装openai: pip install openai")
    
    def _init_claude(self):
        """初始化Claude客户端"""
        try:
            from anthropic import Anthropic
            config = self.api_config.get('claude', {})
            api_key = config.get('api_key')
            
            if not api_key or api_key.startswith('${'):
                raise ValueError("请在.env文件中设置CLAUDE_API_KEY")
            
            self.client = Anthropic(api_key=api_key)
            self.model = config.get('model', 'claude-3-5-sonnet-20241022')
        except ImportError:
            raise ImportError("请安装anthropic: pip install anthropic")
    
    def _init_qwen(self):
        """初始化通义千问客户端"""
        try:
            from openai import OpenAI
            config = self.api_config.get('qwen', {})
            api_key = config.get('api_key')
            
            if not api_key or api_key.startswith('${'):
                raise ValueError("请在.env文件中设置QWEN_API_KEY")
            
            self.client = OpenAI(
                api_key=api_key,
                base_url=config.get('base_url', 'https://dashscope.aliyuncs.com/compatible-mode/v1')
            )
            self.model = config.get('model', 'qwen-plus')
        except ImportError:
            raise ImportError("请安装openai: pip install openai")
    
    def is_available(self) -> bool:
        """检查API是否可用"""
        return hasattr(self, 'client') and self.client is not None
    
    def rewrite(self, content: str, article_type: str = 'tech', **kwargs) -> str:
        """
        使用API改写文章
        
        Args:
            content: 原始文章内容
            article_type: 文章类型 (tech/insurance)
            **kwargs: 其他参数
            
        Returns:
            改写后的内容
        """
        if not self.is_available():
            raise RuntimeError(f"API客户端未初始化: {self.provider}")
        
        # 加载提示词
        prompt_template = self.load_prompt(article_type)
        prompt = prompt_template.format(content=content)
        
        print(f"{Fore.CYAN}正在使用 {self.provider.upper()} API 改写...{Style.RESET_ALL}")
        
        try:
            if self.provider == 'claude':
                return self._rewrite_with_claude(prompt)
            else:  # openai 和 qwen 使用相同接口
                return self._rewrite_with_openai(prompt)
        except Exception as e:
            raise RuntimeError(f"API调用失败: {str(e)}")
    
    def _rewrite_with_openai(self, prompt: str) -> str:
        """使用OpenAI API改写"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "你是一位专业的内容改写专家。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=4000
        )
        
        rewritten_content = response.choices[0].message.content.strip()
        
        if not rewritten_content:
            raise RuntimeError("API返回空内容")
        
        print(f"{Fore.GREEN}✓ 改写完成{Style.RESET_ALL}")
        return rewritten_content
    
    def _rewrite_with_claude(self, prompt: str) -> str:
        """使用Claude API改写"""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4000,
            temperature=0.7,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        rewritten_content = response.content[0].text.strip()
        
        if not rewritten_content:
            raise RuntimeError("API返回空内容")
        
        print(f"{Fore.GREEN}✓ 改写完成{Style.RESET_ALL}")
        return rewritten_content
