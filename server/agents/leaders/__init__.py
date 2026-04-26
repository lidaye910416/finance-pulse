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
from .bill_ackman import (
    BillAckmanLeader,
    create_bill_ackman_leader,
    run_bill_ackman_analysis,
)
from .stanley_druckenmiller import (
    StanleyDruckenmillerLeader,
    create_stanley_druckenmiller_leader,
    run_stanley_druckenmiller_analysis,
)
from .aswath_damodaran import (
    AswathDamodaranLeader,
    create_aswath_damodaran_leader,
    run_aswath_damodaran_analysis,
)
from .mohnish_pabrai import (
    MohnishPabraiLeader,
    create_mohnish_pabrai_leader,
    run_mohnish_pabrai_analysis,
)
from .phil_fisher import (
    PhilFisherLeader,
    create_phil_fisher_leader,
    run_phil_fisher_analysis,
)
from .rakesh_jhunjhunwala import (
    RakeshJhunjhunwalaLeader,
    create_rakesh_jhunjhunwala_leader,
    run_rakesh_jhunjhunwala_analysis,
)
from .george_soros import (
    GeorgeSorosLeader,
    create_george_soros_leader,
    run_george_soros_analysis,
)
from .ray_dalio import (
    RayDalioLeader,
    create_ray_dalio_leader,
    run_ray_dalio_analysis,
)
from .paul_tudor_jones import (
    PaulTudorJonesLeader,
    create_paul_tudor_jones_leader,
    run_paul_tudor_jones_analysis,
)
from .jim_simons import (
    JimSimonsLeader,
    create_jim_simons_leader,
    run_jim_simons_analysis,
)
from .ed_thorp import (
    EdThorpLeader,
    create_ed_thorp_leader,
    run_ed_thorp_analysis,
)
from .john_bogle import (
    JohnBogleLeader,
    create_john_bogle_leader,
    run_john_bogle_analysis,
)
from .howard_marks import (
    HowardMarksLeader,
    create_howard_marks_leader,
    run_howard_marks_analysis,
)
from .seth_klarman import (
    SethKlarmanLeader,
    create_seth_klarman_leader,
    run_seth_klarman_analysis,
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
    # Bill Ackman
    "BillAckmanLeader",
    "create_bill_ackman_leader",
    "run_bill_ackman_analysis",
    # Stanley Druckenmiller
    "StanleyDruckenmillerLeader",
    "create_stanley_druckenmiller_leader",
    "run_stanley_druckenmiller_analysis",
    # Aswath Damodaran
    "AswathDamodaranLeader",
    "create_aswath_damodaran_leader",
    "run_aswath_damodaran_analysis",
    # Mohnish Pabrai
    "MohnishPabraiLeader",
    "create_mohnish_pabrai_leader",
    "run_mohnish_pabrai_analysis",
    # Phil Fisher
    "PhilFisherLeader",
    "create_phil_fisher_leader",
    "run_phil_fisher_analysis",
    # Rakesh Jhunjhunwala
    "RakeshJhunjhunwalaLeader",
    "create_rakesh_jhunjhunwala_leader",
    "run_rakesh_jhunjhunwala_analysis",
    # George Soros
    "GeorgeSorosLeader",
    "create_george_soros_leader",
    "run_george_soros_analysis",
    # Ray Dalio
    "RayDalioLeader",
    "create_ray_dalio_leader",
    "run_ray_dalio_analysis",
    # Paul Tudor Jones
    "PaulTudorJonesLeader",
    "create_paul_tudor_jones_leader",
    "run_paul_tudor_jones_analysis",
    # Jim Simons
    "JimSimonsLeader",
    "create_jim_simons_leader",
    "run_jim_simons_analysis",
    # Ed Thorp
    "EdThorpLeader",
    "create_ed_thorp_leader",
    "run_ed_thorp_analysis",
    # John Bogle
    "JohnBogleLeader",
    "create_john_bogle_leader",
    "run_john_bogle_analysis",
    # Howard Marks
    "HowardMarksLeader",
    "create_howard_marks_leader",
    "run_howard_marks_analysis",
    # Seth Klarman
    "SethKlarmanLeader",
    "create_seth_klarman_leader",
    "run_seth_klarman_analysis",
]
