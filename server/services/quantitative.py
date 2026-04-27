"""
量化财务分析函数

参考 ai-hedge-fund 的 WarrenBuffett 分析逻辑，实现巴菲特风格的量化分析：
- 基本面分析 (ROE, debt, margins, current ratio)
- 盈利一致性分析
- 护城河分析
- DCF 内在价值计算
- 定价权分析
- 安全边际计算
"""

from typing import Optional, List, Dict, Union, Any


class FinancialMetrics:
    """财务指标数据结构"""
    def __init__(
        self,
        return_on_equity: float = None,
        debt_to_equity: float = None,
        operating_margin: float = None,
        current_ratio: float = None,
        gross_margin: float = None,
        net_margin: float = None,
        return_on_invested_capital: float = None,
        asset_turnover: float = None,
        market_cap: float = None,
        revenue: float = None,
        net_income: float = None,
    ):
        self.return_on_equity = return_on_equity
        self.debt_to_equity = debt_to_equity
        self.operating_margin = operating_margin
        self.current_ratio = current_ratio
        self.gross_margin = gross_margin
        self.net_margin = net_margin
        self.return_on_invested_capital = return_on_invested_capital
        self.asset_turnover = asset_turnover
        self.market_cap = market_cap
        self.revenue = revenue
        self.net_income = net_income


class LineItem:
    """财务明细数据结构"""
    def __init__(
        self,
        capital_expenditure: float = None,
        depreciation_and_amortization: float = None,
        net_income: float = None,
        outstanding_shares: float = None,
        total_assets: float = None,
        total_liabilities: float = None,
        shareholders_equity: float = None,
        dividends_and_other_cash_distributions: float = None,
        issuance_or_purchase_of_equity_shares: float = None,
        gross_profit: float = None,
        revenue: float = None,
        free_cash_flow: float = None,
        gross_margin: float = None,
        current_assets: float = None,
        current_liabilities: float = None,
    ):
        self.capital_expenditure = capital_expenditure
        self.depreciation_and_amortization = depreciation_and_amortization
        self.net_income = net_income
        self.outstanding_shares = outstanding_shares
        self.total_assets = total_assets
        self.total_liabilities = total_liabilities
        self.shareholders_equity = shareholders_equity
        self.dividends_and_other_cash_distributions = dividends_and_other_cash_distributions
        self.issuance_or_purchase_of_equity_shares = issuance_or_purchase_of_equity_shares
        self.gross_profit = gross_profit
        self.revenue = revenue
        self.free_cash_flow = free_cash_flow
        self.gross_margin = gross_margin
        self.current_assets = current_assets
        self.current_liabilities = current_liabilities


def analyze_fundamentals(metrics: List[Union[FinancialMetrics, dict]]) -> dict:
    """
    分析公司基本面 - 巴菲特选股标准
    
    评估维度:
    - ROE (股东权益回报率): >15% 为强
    - Debt to Equity (负债权益比): <0.5 为保守
    - Operating Margin (营业利润率): >15% 为强
    - Current Ratio (流动比率): >1.5 为良好
    
    Returns:
        {"score": int, "details": str, "metrics": dict}
    """
    if not metrics:
        return {"score": 0, "details": "Insufficient fundamental data", "metrics": {}}

    # 支持字典或对象
    if isinstance(metrics[0], dict):
        latest = metrics[0]
        m = FinancialMetrics(**latest)
    else:
        latest = metrics[0]
        m = latest

    score = 0
    reasoning = []

    # Check ROE (Return on Equity)
    roe = getattr(m, 'return_on_equity', None) or (m.__dict__.get('return_on_equity') if hasattr(m, '__dict__') else None)
    if roe and roe > 0.15:  # 15% ROE threshold
        score += 2
        reasoning.append(f"Strong ROE of {roe:.1%}")
    elif roe:
        reasoning.append(f"Weak ROE of {roe:.1%}")
    else:
        reasoning.append("ROE data not available")

    # Check Debt to Equity
    de = getattr(m, 'debt_to_equity', None)
    if de and de < 0.5:
        score += 2
        reasoning.append("Conservative debt levels")
    elif de:
        reasoning.append(f"High debt to equity ratio of {de:.1f}")
    else:
        reasoning.append("Debt to equity data not available")

    # Check Operating Margin
    om = getattr(m, 'operating_margin', None)
    if om and om > 0.15:
        score += 2
        reasoning.append("Strong operating margins")
    elif om:
        reasoning.append(f"Weak operating margin of {om:.1%}")
    else:
        reasoning.append("Operating margin data not available")

    # Check Current Ratio
    cr = getattr(m, 'current_ratio', None)
    if cr and cr > 1.5:
        score += 1
        reasoning.append("Good liquidity position")
    elif cr:
        reasoning.append(f"Weak liquidity with current ratio of {cr:.1f}")
    else:
        reasoning.append("Current ratio data not available")

    # Prepare metrics dict
    if isinstance(latest, dict):
        metrics_dict = latest
    else:
        metrics_dict = {
            "return_on_equity": roe,
            "debt_to_equity": de,
            "operating_margin": om,
            "current_ratio": cr,
        }

    return {
        "score": score,
        "details": "; ".join(reasoning),
        "metrics": metrics_dict
    }


def analyze_consistency(financial_line_items: List[Union[LineItem, dict]]) -> dict:
    """
    分析盈利一致性 - 验证盈利是否稳定增长
    
    Returns:
        {"score": int, "details": str}
    """
    if not financial_line_items or len(financial_line_items) < 4:
        return {"score": 0, "details": "Insufficient historical data", "consistency_score": 0}

    # 支持字典或对象
    def get_net_income(item):
        if isinstance(item, dict):
            return item.get('net_income')
        return getattr(item, 'net_income', None)

    earnings_values = [get_net_income(item) for item in financial_line_items[:5]]
    earnings_values = [v for v in earnings_values if v is not None]

    if len(earnings_values) < 4:
        return {"score": 0, "details": "Insufficient earnings data for trend analysis", "consistency_score": 0}

    score = 0
    reasoning = []

    # Check earnings growth trend
    # Simple check: is each period's earnings bigger than the next?
    earnings_growth = all(
        earnings_values[i] > earnings_values[i + 1]
        for i in range(len(earnings_values) - 1)
    )

    if earnings_growth:
        score += 3
        reasoning.append("Consistent earnings growth over past periods")
    else:
        reasoning.append("Inconsistent earnings growth pattern")

    # Calculate total growth rate from oldest to latest
    if len(earnings_values) >= 2 and earnings_values[-1] != 0:
        growth_rate = (earnings_values[0] - earnings_values[-1]) / abs(earnings_values[-1])
        reasoning.append(f"Total earnings growth of {growth_rate:.1%} over past {len(earnings_values)} periods")

    # Calculate consistency score (0-1)
    if len(earnings_values) >= 2:
        increases = sum(
            1 for i in range(len(earnings_values) - 1)
            if earnings_values[i] > earnings_values[i + 1]
        )
        consistency_score = increases / (len(earnings_values) - 1)
    else:
        consistency_score = 0

    return {
        "score": score,
        "details": "; ".join(reasoning),
        "consistency_score": consistency_score,
    }


def analyze_moat(metrics: List[Union[FinancialMetrics, dict]]) -> dict:
    """
    评估公司是否具有持久竞争优势（护城河）
    
    护城河指标:
    1. Return on Capital Consistency - 持续高ROE
    2. Pricing Power - 稳定/改善的利润率
    3. Scale Advantages - 资产效率提升
    4. Competitive Position Strength - 表现稳定性
    
    Returns:
        {"score": int, "max_score": int, "details": str}
    """
    if not metrics or len(metrics) < 2:
        return {"score": 0, "max_score": 5, "details": "Insufficient data for comprehensive moat analysis"}

    def get_field(item, field_name):
        if isinstance(item, dict):
            return item.get(field_name)
        return getattr(item, field_name, None)

    reasoning = []
    moat_score = 0
    max_score = 5

    # 1. Return on Capital Consistency
    historical_roes = [get_field(m, 'return_on_equity') for m in metrics]
    historical_roes = [r for r in historical_roes if r is not None]

    if len(historical_roes) >= 3:
        high_roe_periods = sum(1 for roe in historical_roes if roe > 0.15)
        roe_consistency = high_roe_periods / len(historical_roes)

        if roe_consistency >= 0.8:
            moat_score += 2
            avg_roe = sum(historical_roes) / len(historical_roes)
            reasoning.append(
                f"Excellent ROE consistency: {high_roe_periods}/{len(historical_roes)} periods >15% (avg: {avg_roe:.1%})"
            )
        elif roe_consistency >= 0.6:
            moat_score += 1
            reasoning.append(f"Good ROE performance: {high_roe_periods}/{len(historical_roes)} periods >15%")
        else:
            reasoning.append(f"Inconsistent ROE: only {high_roe_periods}/{len(historical_roes)} periods >15%")

    # 2. Operating Margin Stability (Pricing Power Indicator)
    historical_margins = [get_field(m, 'operating_margin') for m in metrics]
    historical_margins = [m for m in historical_margins if m is not None]

    if len(historical_margins) >= 3:
        avg_margin = sum(historical_margins) / len(historical_margins)
        recent_margins = historical_margins[:min(3, len(historical_margins))]
        older_margins = historical_margins[-min(3, len(historical_margins)):]

        recent_avg = sum(recent_margins) / len(recent_margins)
        older_avg = sum(older_margins) / len(older_margins) if older_margins else 0

        if avg_margin > 0.2 and recent_avg >= older_avg:
            moat_score += 1
            reasoning.append(f"Strong and stable operating margins (avg: {avg_margin:.1%}) indicate pricing power moat")
        elif avg_margin > 0.15:
            reasoning.append(f"Decent operating margins (avg: {avg_margin:.1%}) suggest some competitive advantage")
        else:
            reasoning.append(f"Low operating margins (avg: {avg_margin:.1%}) suggest limited pricing power")

    # 3. Asset Efficiency
    asset_turnovers = [get_field(m, 'asset_turnover') for m in metrics]
    asset_turnovers = [a for a in asset_turnovers if a is not None]

    if len(asset_turnovers) >= 3:
        if any(turnover > 1.0 for turnover in asset_turnovers):
            moat_score += 1
            reasoning.append("Efficient asset utilization suggests operational moat")

    # 4. Competitive Position Strength (stability measure)
    if len(historical_roes) >= 3 and len(historical_margins) >= 3:
        roe_avg = sum(historical_roes) / len(historical_roes)
        roe_variance = sum((roe - roe_avg) ** 2 for roe in historical_roes) / len(historical_roes)
        roe_stability = 1 - (roe_variance ** 0.5) / roe_avg if roe_avg > 0 else 0

        margin_avg = sum(historical_margins) / len(historical_margins)
        margin_variance = sum((margin - margin_avg) ** 2 for margin in historical_margins) / len(historical_margins)
        margin_stability = 1 - (margin_variance ** 0.5) / margin_avg if margin_avg > 0 else 0

        overall_stability = (roe_stability + margin_stability) / 2

        if overall_stability > 0.7:
            moat_score += 1
            reasoning.append(f"High performance stability ({overall_stability:.1%}) suggests strong competitive moat")

    # Cap the score at max_score
    moat_score = min(moat_score, max_score)

    return {
        "score": moat_score,
        "max_score": max_score,
        "details": "; ".join(reasoning) if reasoning else "Limited moat analysis available",
    }


def calculate_intrinsic_value(
    financial_line_items: List[Union[LineItem, dict]],
    current_price: float = None,
    shares_outstanding: float = None,
    discount_rate: float = 0.10,
    stage1_growth: float = 0.08,
    stage2_growth: float = 0.04,
    terminal_growth: float = 0.025,
) -> dict:
    """
    使用 DCF 模型计算内在价值（三阶段模型）
    
    Args:
        financial_line_items: 财务明细数据
        current_price: 当前股价（可选）
        shares_outstanding: 流通股数（可选）
        discount_rate: 折现率 (default: 10%)
        stage1_growth: 第一阶段增长率 (default: 8%)
        stage2_growth: 第二阶段增长率 (default: 4%)
        terminal_growth: 永续增长率 (default: 2.5%)
    
    Returns:
        {"intrinsic_value": float, "raw_intrinsic_value": float, "per_share_value": float, "details": list}
    """
    if not financial_line_items or len(financial_line_items) < 2:
        return {
            "intrinsic_value": None,
            "raw_intrinsic_value": None,
            "per_share_value": None,
            "details": ["Insufficient data for reliable valuation"]
        }

    def get_field(item, field_name):
        if isinstance(item, dict):
            return item.get(field_name)
        return getattr(item, field_name, None)

    # 获取最新数据
    latest = financial_line_items[0]

    # 计算所有者收益 (Owner Earnings)
    net_income = get_field(latest, 'net_income')
    depreciation = get_field(latest, 'depreciation_and_amortization')
    capex = get_field(latest, 'capital_expenditure')

    if net_income is None or depreciation is None or capex is None:
        return {
            "intrinsic_value": None,
            "raw_intrinsic_value": None,
            "per_share_value": None,
            "details": ["Missing components for owner earnings calculation"]
        }

    # 保守估计：假设 85% 的 capex 是维护性 capex
    maintenance_capex = abs(capex) * 0.85 if capex else 0

    # 所有者收益 = 净利润 + 折旧摊销 - 维护性资本支出
    owner_earnings = net_income + (depreciation or 0) - maintenance_capex

    if owner_earnings <= 0:
        return {
            "intrinsic_value": None,
            "raw_intrinsic_value": None,
            "per_share_value": None,
            "details": ["Negative or zero owner earnings - not suitable for DCF"]
        }

    # 如果没有提供流通股数，尝试从数据中获取
    if not shares_outstanding:
        shares_outstanding = get_field(latest, 'outstanding_shares')

    details = []

    # 三阶段 DCF 模型
    stage1_years = 5  # 高增长阶段
    stage2_years = 5  # 过渡阶段

    # Stage 1: Higher growth
    stage1_pv = 0
    for year in range(1, stage1_years + 1):
        future_earnings = owner_earnings * (1 + stage1_growth) ** year
        pv = future_earnings / (1 + discount_rate) ** year
        stage1_pv += pv

    # Stage 2: Transition growth
    stage2_pv = 0
    stage1_final_earnings = owner_earnings * (1 + stage1_growth) ** stage1_years
    for year in range(1, stage2_years + 1):
        future_earnings = stage1_final_earnings * (1 + stage2_growth) ** year
        pv = future_earnings / (1 + discount_rate) ** (stage1_years + year)
        stage2_pv += pv

    # Terminal value using Gordon Growth Model
    final_earnings = stage1_final_earnings * (1 + stage2_growth) ** stage2_years
    terminal_earnings = final_earnings * (1 + terminal_growth)
    terminal_value = terminal_earnings / (discount_rate - terminal_growth)
    terminal_pv = terminal_value / (1 + discount_rate) ** (stage1_years + stage2_years)

    # 总内在价值
    intrinsic_value = stage1_pv + stage2_pv + terminal_pv

    # 保守内在价值（额外 15% 安全边际）
    conservative_intrinsic_value = intrinsic_value * 0.85

    # 每股价值
    per_share_value = None
    if shares_outstanding and shares_outstanding > 0:
        per_share_value = conservative_intrinsic_value / shares_outstanding

    details.extend([
        f"Stage 1 PV: ${stage1_pv:,.0f}",
        f"Stage 2 PV: ${stage2_pv:,.0f}",
        f"Terminal PV: ${terminal_pv:,.0f}",
        f"Total IV: ${intrinsic_value:,.0f}",
        f"Conservative IV (15% haircut): ${conservative_intrinsic_value:,.0f}",
        f"Owner earnings: ${owner_earnings:,.0f}",
        f"Discount rate: {discount_rate:.1%}",
        f"Stage 1 growth: {stage1_growth:.1%}",
        f"Stage 2 growth: {stage2_growth:.1%}",
        f"Terminal growth: {terminal_growth:.1%}",
    ])

    if current_price and per_share_value:
        margin_of_safety = (per_share_value - current_price) / current_price
        details.append(f"Margin of Safety: {margin_of_safety:.1%} (current price: ${current_price:.2f})")

    return {
        "intrinsic_value": conservative_intrinsic_value,
        "raw_intrinsic_value": intrinsic_value,
        "per_share_value": per_share_value,
        "owner_earnings": owner_earnings,
        "assumptions": {
            "discount_rate": discount_rate,
            "stage1_growth": stage1_growth,
            "stage2_growth": stage2_growth,
            "terminal_growth": terminal_growth,
            "stage1_years": stage1_years,
            "stage2_years": stage2_years,
        },
        "details": details,
    }


def analyze_pricing_power(
    financial_line_items: List[Union[LineItem, dict]],
    metrics: List[Union[FinancialMetrics, dict]] = None
) -> dict:
    """
    分析定价权 - 巴菲特的关键护城河指标
    
    评估公司是否能够在不失去客户的情况下提价
    （通过_margin扩张判断）
    
    Returns:
        {"score": int, "details": str}
    """
    if not financial_line_items:
        return {"score": 0, "details": "Insufficient data for pricing power analysis"}

    def get_field(item, field_name):
        if isinstance(item, dict):
            return item.get(field_name)
        return getattr(item, field_name, None)

    score = 0
    reasoning = []

    # Check gross margin trends
    gross_margins = []
    for item in financial_line_items:
        gm = get_field(item, 'gross_margin')
        if gm is not None:
            gross_margins.append(gm)

    if len(gross_margins) >= 3:
        recent_avg = sum(gross_margins[:2]) / 2 if len(gross_margins) >= 2 else gross_margins[0]
        older_avg = sum(gross_margins[-2:]) / 2 if len(gross_margins) >= 2 else gross_margins[-1]

        if recent_avg > older_avg + 0.02:  # 2%+ improvement
            score += 3
            reasoning.append("Expanding gross margins indicate strong pricing power")
        elif recent_avg > older_avg:
            score += 2
            reasoning.append("Improving gross margins suggest good pricing power")
        elif abs(recent_avg - older_avg) < 0.01:  # Stable within 1%
            score += 1
            reasoning.append("Stable gross margins during economic uncertainty")
        else:
            reasoning.append("Declining gross margins may indicate pricing pressure")

    # Check if company has been able to maintain high margins consistently
    if gross_margins:
        avg_margin = sum(gross_margins) / len(gross_margins)
        if avg_margin > 0.5:  # 50%+ gross margins
            score += 2
            reasoning.append(f"Consistently high gross margins ({avg_margin:.1%}) indicate strong pricing power")
        elif avg_margin > 0.3:  # 30%+ gross margins
            score += 1
            reasoning.append(f"Good gross margins ({avg_margin:.1%}) suggest decent pricing power")

    return {
        "score": min(score, 5),  # Cap at 5
        "details": "; ".join(reasoning) if reasoning else "Limited pricing power analysis available"
    }


def calculate_margin_of_safety(
    intrinsic_value: float,
    current_price: float,
    market_cap: float = None,
    shares_outstanding: float = None
) -> dict:
    """
    计算安全边际
    
    安全边际 = (内在价值 - 当前价格) / 内在价值
    
    Returns:
        {"margin_of_safety": float, "is_attractive": bool, "details": str}
    """
    if not intrinsic_value or intrinsic_value <= 0:
        return {
            "margin_of_safety": None,
            "is_attractive": False,
            "details": "Invalid intrinsic value"
        }

    if not current_price or current_price <= 0:
        return {
            "margin_of_safety": None,
            "is_attractive": False,
            "details": "Invalid current price"
        }

    # 基于每股价值计算
    if shares_outstanding and shares_outstanding > 0:
        per_share_intrinsic = intrinsic_value / shares_outstanding
        margin_of_safety = (per_share_intrinsic - current_price) / per_share_intrinsic
    else:
        # 基于总市值计算
        margin_of_safety = (intrinsic_value - market_cap) / intrinsic_value if market_cap else None

    if margin_of_safety is None:
        return {
            "margin_of_safety": None,
            "is_attractive": False,
            "details": "Insufficient data for margin of safety calculation"
        }

    # 吸引人的投资：安全边际 > 20%
    is_attractive = margin_of_safety > 0.20

    if margin_of_safety > 0.40:
        details = f"Excellent margin of safety: {margin_of_safety:.1%} - 极具吸引力的买入机会"
    elif margin_of_safety > 0.20:
        details = f"Good margin of safety: {margin_of_safety:.1%} - 合理的买入机会"
    elif margin_of_safety > 0:
        details = f"Limited margin of safety: {margin_of_safety:.1%} - 估值偏高"
    else:
        details = f"Negative margin of safety: {margin_of_safety:.1%} - 估值偏高，不建议买入"

    return {
        "margin_of_safety": margin_of_safety,
        "is_attractive": is_attractive,
        "details": details,
        "per_share_intrinsic": intrinsic_value / shares_outstanding if shares_outstanding else None,
        "current_price": current_price,
    }


def analyze_management_quality(financial_line_items: List[Union[LineItem, dict]]) -> dict:
    """
    分析管理层质量
    
    检查：
    - 股票回购（对股东友好）
    - 股票发行（稀释）
    - 分红记录
    
    Returns:
        {"score": int, "max_score": int, "details": str}
    """
    if not financial_line_items:
        return {"score": 0, "max_score": 2, "details": "Insufficient data for management analysis"}

    def get_field(item, field_name):
        if isinstance(item, dict):
            return item.get(field_name)
        return getattr(item, field_name, None)

    reasoning = []
    mgmt_score = 0

    latest = financial_line_items[0]

    # Check for share repurchases (negative = buyback)
    issuance = get_field(latest, 'issuance_or_purchase_of_equity_shares')
    if issuance is not None:
        if issuance < 0:
            mgmt_score += 1
            reasoning.append("Company has been repurchasing shares (shareholder-friendly)")
        elif issuance > 0:
            reasoning.append("Recent common stock issuance (potential dilution)")
        else:
            reasoning.append("No significant new stock issuance detected")

    # Check for dividends
    dividends = get_field(latest, 'dividends_and_other_cash_distributions')
    if dividends is not None and dividends < 0:
        mgmt_score += 1
        reasoning.append("Company has a track record of paying dividends")
    else:
        reasoning.append("No or minimal dividends paid")

    return {
        "score": mgmt_score,
        "max_score": 2,
        "details": "; ".join(reasoning),
    }


def calculate_owner_earnings(financial_line_items: List[Union[LineItem, dict]]) -> dict:
    """
    计算所有者收益（巴菲特的真实收益衡量标准）
    
    所有者收益 = 净利润 + 折旧摊销 - 维护性资本支出
    
    Returns:
        {"owner_earnings": float, "components": dict, "details": list}
    """
    if not financial_line_items or len(financial_line_items) < 2:
        return {
            "owner_earnings": None,
            "components": {},
            "details": ["Insufficient data for owner earnings calculation"]
        }

    def get_field(item, field_name):
        if isinstance(item, dict):
            return item.get(field_name)
        return getattr(item, field_name, None)

    latest = financial_line_items[0]
    details = []

    # Core components
    net_income = get_field(latest, 'net_income')
    depreciation = get_field(latest, 'depreciation_and_amortization')
    capex = get_field(latest, 'capital_expenditure')

    if net_income is None:
        return {
            "owner_earnings": None,
            "components": {},
            "details": ["Missing net income data"]
        }

    # 估算维护性 capex（假设 85% 是维护性的）
    depreciation = depreciation or 0
    capex = capex or 0
    maintenance_capex = abs(capex) * 0.85

    # 计算所有者收益
    owner_earnings = net_income + depreciation - maintenance_capex

    # 合理性检查
    if owner_earnings < net_income * 0.3:
        details.append("Warning: Owner earnings significantly below net income - high capex intensity")

    details.extend([
        f"Net income: ${net_income:,.0f}",
        f"Depreciation: ${depreciation:,.0f}",
        f"Estimated maintenance capex: ${maintenance_capex:,.0f}",
        f"Owner earnings: ${owner_earnings:,.0f}"
    ])

    return {
        "owner_earnings": owner_earnings,
        "components": {
            "net_income": net_income,
            "depreciation": depreciation,
            "maintenance_capex": maintenance_capex,
            "total_capex": abs(capex) if capex else 0
        },
        "details": details,
    }


def comprehensive_analysis(
    metrics: List[Union[FinancialMetrics, dict]],
    financial_line_items: List[Union[LineItem, dict]],
    current_price: float = None,
    market_cap: float = None
) -> dict:
    """
    综合分析 - 整合所有量化指标
    
    Returns:
        综合评分和详细分析结果
    """
    if not metrics and not financial_line_items:
        return {
            "score": 0,
            "max_score": 0,
            "details": "Insufficient data for comprehensive analysis",
            "signal": "neutral",
            "confidence": 50
        }

    results = {}

    # 基本面分析
    if metrics:
        results["fundamentals"] = analyze_fundamentals(metrics)
        
        if isinstance(metrics[0], dict):
            metrics_dict = metrics[0]
        else:
            metrics_dict = metrics[0]
        results["moat"] = analyze_moat(metrics)

    # 一致性分析
    if financial_line_items:
        results["consistency"] = analyze_consistency(financial_line_items)
        results["management"] = analyze_management_quality(financial_line_items)
        results["pricing_power"] = analyze_pricing_power(financial_line_items, metrics)
        results["intrinsic_value"] = calculate_intrinsic_value(
            financial_line_items,
            current_price=current_price
        )

    # 计算总分
    total_score = 0
    max_score = 0

    score_breakdown = {}
    
    if "fundamentals" in results:
        total_score += results["fundamentals"]["score"]
        max_score += 10  # 2+2+2+1+3
        score_breakdown["fundamentals"] = results["fundamentals"]["score"]

    if "moat" in results:
        total_score += results["moat"]["score"]
        max_score += results["moat"].get("max_score", 5)
        score_breakdown["moat"] = results["moat"]["score"]

    if "consistency" in results:
        total_score += results["consistency"]["score"]
        max_score += 5
        score_breakdown["consistency"] = results["consistency"]["score"]

    if "management" in results:
        total_score += results["management"]["score"]
        max_score += results["management"].get("max_score", 2)
        score_breakdown["management"] = results["management"]["score"]

    if "pricing_power" in results:
        total_score += results["pricing_power"]["score"]
        max_score += 5
        score_breakdown["pricing_power"] = results["pricing_power"]["score"]

    # 安全边际
    margin_of_safety = None
    if "intrinsic_value" in results and current_price:
        iv = results["intrinsic_value"]
        if iv.get("per_share_value"):
            margin_data = calculate_margin_of_safety(
                intrinsic_value=iv["per_share_value"] * (financial_line_items[0].get("outstanding_shares") if isinstance(financial_line_items[0], dict) else getattr(financial_line_items[0], 'outstanding_shares', None)) if isinstance(financial_line_items[0], dict) else iv.get("intrinsic_value", 0),
                current_price=current_price,
                market_cap=market_cap
            )
            margin_of_safety = margin_data.get("margin_of_safety")

    # 生成信号
    if max_score > 0:
        score_ratio = total_score / max_score
        
        if score_ratio >= 0.7 and margin_of_safety and margin_of_safety > 0:
            signal = "bullish"
            confidence = int(70 + score_ratio * 30)
        elif score_ratio >= 0.5:
            signal = "neutral"
            confidence = int(50 + score_ratio * 30)
        elif score_ratio >= 0.3:
            signal = "neutral"
            confidence = int(40 + score_ratio * 20)
        else:
            signal = "bearish"
            confidence = int(30 + score_ratio * 40)
    else:
        signal = "neutral"
        confidence = 50
        score_ratio = 0

    return {
        "score": total_score,
        "max_score": max_score,
        "score_ratio": score_ratio,
        "score_breakdown": score_breakdown,
        "margin_of_safety": margin_of_safety,
        "signal": signal,
        "confidence": min(95, max(20, confidence)),
        "analysis_results": results,
        "details": {
            "fundamentals": results.get("fundamentals", {}).get("details", ""),
            "moat": results.get("moat", {}).get("details", ""),
            "consistency": results.get("consistency", {}).get("details", ""),
            "pricing_power": results.get("pricing_power", {}).get("details", ""),
            "intrinsic_value": results.get("intrinsic_value", {}).get("details", []),
        }
    }
