"""
改写器基类
定义改写器的通用接口
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import yaml
import os


class BaseRewriter(ABC):
    """改写器基类"""
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        初始化改写器
        
        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)
        self.protected_terms = self.config.get('protected_terms', {})
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置文件"""
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"配置文件不存在: {config_path}")
            
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # 处理环境变量
        self._process_env_vars(config)
        return config
    
    def _process_env_vars(self, config: Dict[str, Any]) -> None:
        """处理配置中的环境变量"""
        from dotenv import load_dotenv
        load_dotenv()
        
        def replace_env_vars(obj):
            if isinstance(obj, dict):
                return {k: replace_env_vars(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [replace_env_vars(item) for item in obj]
            elif isinstance(obj, str) and obj.startswith('${') and obj.endswith('}'):
                env_var = obj[2:-1]
                return os.getenv(env_var, obj)
            return obj
        
        for key in config:
            config[key] = replace_env_vars(config[key])
    
    def load_prompt(self, article_type: str) -> str:
        """
        加载提示词模板
        
        Args:
            article_type: 文章类型 (tech/insurance)
            
        Returns:
            提示词模板内容
        """
        prompt_file = f"prompts/{article_type}_blog.txt"
        if not os.path.exists(prompt_file):
            raise FileNotFoundError(f"提示词文件不存在: {prompt_file}")
            
        with open(prompt_file, 'r', encoding='utf-8') as f:
            return f.read()
    
    def get_protected_terms(self, article_type: str) -> list:
        """
        获取需要保护的专业术语
        
        Args:
            article_type: 文章类型
            
        Returns:
            术语列表
        """
        return self.protected_terms.get(article_type, [])
    
    @abstractmethod
    def rewrite(self, content: str, article_type: str = 'tech', **kwargs) -> str:
        """
        改写文章内容
        
        Args:
            content: 原始文章内容
            article_type: 文章类型 (tech/insurance)
            **kwargs: 其他参数
            
        Returns:
            改写后的内容
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        检查改写器是否可用
        
        Returns:
            是否可用
        """
        pass
