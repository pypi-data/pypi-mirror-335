from dataclasses import dataclass
from typing import Optional

@dataclass
class WebSearchConfig:
    """网络搜索配置"""
    max_results: int = 3  # 最大搜索结果数
    timeout: int = 10  # 超时时间(秒)
    fetch_content: bool = True  # 是否获取详细内容
    min_sleep: float = 1.0  # 最小随机等待时间
    max_sleep: float = 3.0  # 最大随机等待时间 