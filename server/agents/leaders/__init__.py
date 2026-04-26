"""
Leader 模块

实现不同投资大师的分析风格，用于 Fusion 模式下的最终决策。
"""

from .base import LeaderBase, create_leader, get_available_leaders

# 导入各 Leader
from .warren_buffett import (
    WarrenBuffettLeader,
    create_warren_buffett_leader,
    run_warren_buffett_analysis,
)
from .ben_graham import (
    BenGrahamLeader,
    create_ben_graham_leader,
    run_ben_graham_analysis,
)
from .peter_lynch import (
    PeterLynchLeader,
    create_peter_lynch_leader,
    run_peter_lynch_analysis,
)
from .charlie_munger import (
    CharlieMungerLeader,
    create_charlie_munger_leader,
    run_charlie_munger_analysis,
)
from .cathie_wood import (
    CathieWoodLeader,
    create_cathie_wood_leader,
    run_cathie_wood_analysis,
)

__all__ = [
    # Base
    "LeaderBase",
    "create_leader",
    "get_available_leaders",
    # Warren Buffett
    "WarrenBuffettLeader",
    "create_warren_buffett_leader",
    "run_warren_buffett_analysis",
    # Ben Graham
    "BenGrahamLeader",
    "create_ben_graham_leader",
    "run_ben_graham_analysis",
    # Peter Lynch
    "PeterLynchLeader",
    "create_peter_lynch_leader",
    "run_peter_lynch_analysis",
    # Charlie Munger
    "CharlieMungerLeader",
    "create_charlie_munger_leader",
    "run_charlie_munger_analysis",
    # Cathie Wood
    "CathieWoodLeader",
    "create_cathie_wood_leader",
    "run_cathie_wood_analysis",
]
