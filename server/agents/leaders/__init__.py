"""
Leader 模块

实现不同投资大师的分析风格，用于 Fusion 模式下的最终决策。
"""

from .base import LeaderBase, create_leader, get_available_leaders

__all__ = [
    "LeaderBase",
    "create_leader",
    "get_available_leaders",
]
