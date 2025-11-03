"""
本地模型改写器
使用Ollama进行本地改写
"""

import requests
from typing import Dict, Any, Optional
from .rewriter import BaseRewriter
from colorama import Fore, Style


class LocalRewriter(BaseRewriter):
    """本地模型改写器（基于Ollama）"""
    
    def __init__(self, config_path: str = "config.yaml"):
        super().__init__(config_path)
        self.local_config = self.config.get('local', {})
        self.model = self.local_config.get('model', 'qwen2.5:14b')
        self.base_url = self.local_config.get('base_url', 'http://localhost:11434')
        self.temperature = self.local_config.get('temperature', 0.7)
        self.max_tokens = self.local_config.get('max_tokens', 4000)
        
    def is_available(self) -> bool:
        """检查Ollama服务是否可用"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def check_model_exists(self) -> bool:
        """检查模型是否已下载"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                return any(model['name'] == self.model for model in models)
            return False
        except Exception:
            return False
    
    def rewrite(self, content: str, article_type: str = 'tech', **kwargs) -> str:
        """
        使用本地模型改写文章
        
        Args:
            content: 原始文章内容
            article_type: 文章类型 (tech/insurance)
            **kwargs: 其他参数
            
        Returns:
            改写后的内容
        """
        # 检查服务可用性
        if not self.is_available():
            raise RuntimeError(
                f"{Fore.RED}Ollama服务不可用！{Style.RESET_ALL}\n"
                f"请确保Ollama已启动: ollama serve"
            )
        
        # 检查模型是否存在
        if not self.check_model_exists():
            raise RuntimeError(
                f"{Fore.RED}模型 {self.model} 未找到！{Style.RESET_ALL}\n"
                f"请先下载模型: ollama pull {self.model}"
            )
        
        # 加载提示词
        prompt_template = self.load_prompt(article_type)
        prompt = prompt_template.format(content=content)
        
        # 调用Ollama API
        print(f"{Fore.CYAN}正在使用本地模型 {self.model} 改写...{Style.RESET_ALL}")
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": self.temperature,
                        "num_predict": self.max_tokens,
                    }
                },
                timeout=300  # 5分钟超时
            )
            
            if response.status_code == 200:
                result = response.json()
                rewritten_content = result.get('response', '').strip()
                
                if not rewritten_content:
                    raise RuntimeError("模型返回空内容")
                
                # 处理 deepseek-r1 模型的思考过程标签
                if 'deepseek-r1' in self.model.lower():
                    # 移除 <think>...</think> 标签及其内容
                    import re
                    rewritten_content = re.sub(r'<think>.*?</think>', '', rewritten_content, flags=re.DOTALL)
                    rewritten_content = rewritten_content.strip()
                
                print(f"{Fore.GREEN}✓ 改写完成{Style.RESET_ALL}")
                return rewritten_content
            else:
                raise RuntimeError(f"API调用失败: {response.status_code} - {response.text}")
                
        except requests.exceptions.Timeout:
            raise RuntimeError("请求超时，文章可能过长，请尝试分段处理")
        except Exception as e:
            raise RuntimeError(f"改写失败: {str(e)}")
