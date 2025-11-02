"""
相似度检测器
使用sentence-transformers计算文本相似度
"""

from typing import Optional


class SimilarityChecker:
    """文本相似度检测器"""
    
    def __init__(self, model_name: str = 'paraphrase-multilingual-MiniLM-L12-v2'):
        """
        初始化相似度检测器
        
        Args:
            model_name: 使用的模型名称
        """
        self.model_name = model_name
        self.model = None
        
    def _load_model(self):
        """延迟加载模型"""
        if self.model is None:
            try:
                import numpy as np
            except ImportError:
                raise ImportError(
                    "相似度检测需要numpy。安装: pip install numpy sentence-transformers"
                )
            try:
                from sentence_transformers import SentenceTransformer
                print("正在加载相似度检测模型...")
                self.model = SentenceTransformer(self.model_name)
                print("✓ 模型加载完成")
            except ImportError:
                raise ImportError(
                    "请安装sentence-transformers: pip install sentence-transformers"
                )
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        计算两段文本的相似度
        
        Args:
            text1: 文本1
            text2: 文本2
            
        Returns:
            相似度分数 (0-1之间，越高越相似)
        """
        self._load_model()
        
        # 生成embeddings
        embeddings = self.model.encode([text1, text2])
        
        # 计算余弦相似度
        similarity = self._cosine_similarity(embeddings[0], embeddings[1])
        
        return float(similarity)
    
    def _cosine_similarity(self, vec1, vec2) -> float:
        """计算余弦相似度"""
        import numpy as np
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def check_quality(self, original: str, rewritten: str, threshold: float = 0.3) -> dict:
        """
        检查改写质量
        
        Args:
            original: 原始文本
            rewritten: 改写后文本
            threshold: 相似度阈值（低于此值为合格）
            
        Returns:
            质量报告字典
        """
        similarity = self.calculate_similarity(original, rewritten)
        
        return {
            'similarity': similarity,
            'threshold': threshold,
            'passed': similarity < threshold,
            'status': 'PASS' if similarity < threshold else 'FAIL',
            'message': self._get_quality_message(similarity, threshold)
        }
    
    def _get_quality_message(self, similarity: float, threshold: float) -> str:
        """生成质量评价消息"""
        if similarity < threshold:
            if similarity < 0.2:
                return "优秀：改写效果很好，相似度很低"
            else:
                return "良好：改写效果不错，相似度较低"
        else:
            if similarity < 0.5:
                return "一般：相似度偏高，建议重新改写"
            else:
                return "较差：相似度过高，需要重新改写"
