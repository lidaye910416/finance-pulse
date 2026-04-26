"""
Config Module

配置模块，提供 Leaders 配置和风格映射
"""

from .leaders import (
    LEADERS,
    LEADERS_BY_ID,
    LEADER_IDS,
    STYLES,
    STYLE_ANALYST_MAP,
    get_leaders_by_style,
    get_leader,
)

__all__ = [
    "LEADERS",
    "LEADERS_BY_ID", 
    "LEADER_IDS",
    "STYLES",
    "STYLE_ANALYST_MAP",
    "get_leaders_by_style",
    "get_leader",
]
