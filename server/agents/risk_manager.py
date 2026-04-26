"""
Risk Manager Agent

基于波动率实现风险管理agent
- 计算波动率指标
- 基于波动率调整仓位限制
- 输出每个ticker的剩余仓位限制
"""

import json
import numpy as np
from typing import Any

from graph.state import AgentState
from services.llm import LLMService


# ========== 波动率计算函数 ==========

def calculate_volatility_metrics(prices: list[dict], lookback_days: int = 60) -> dict:
    """Calculate comprehensive volatility metrics from price data.
    
    Args:
        prices: List of price dicts with 'close' key, sorted by date
        lookback_days: Number of days to use for volatility calculation
        
    Returns:
        dict with daily_volatility, annualized_volatility, volatility_percentile
    """
    if len(prices) < 2:
        return {
            "daily_volatility": 0.05,
            "annualized_volatility": 0.05 * np.sqrt(252),
            "volatility_percentile": 100,
            "data_points": len(prices)
        }
    
    # Extract closing prices
    closes = np.array([p.get('close', 0) for p in prices])
    
    if len(closes) < 2:
        return {
            "daily_volatility": 0.05,
            "annualized_volatility": 0.05 * np.sqrt(252),
            "volatility_percentile": 100,
            "data_points": len(closes)
        }
    
    # Calculate daily returns
    daily_returns = np.diff(closes) / closes[:-1]
    
    if len(daily_returns) < 2:
        return {
            "daily_volatility": 0.05,
            "annualized_volatility": 0.05 * np.sqrt(252),
            "volatility_percentile": 100,
            "data_points": len(daily_returns) + 1
        }
    
    # Use the most recent lookback_days for volatility calculation
    recent_returns = daily_returns[-min(lookback_days, len(daily_returns)):]
    
    # Calculate volatility metrics
    daily_vol = np.std(recent_returns)
    annualized_vol = daily_vol * np.sqrt(252)  # Annualize assuming 252 trading days
    
    # Calculate percentile rank of recent volatility vs historical volatility
    if len(daily_returns) >= 30:
        # Calculate 30-day rolling volatility for the full history
        rolling_vols = []
        for i in range(30, len(daily_returns)):
            rolling_vols.append(np.std(daily_returns[i-30:i]))
        
        if rolling_vols:
            # Compare current volatility against historical rolling volatilities
            current_vol_percentile = (np.array(rolling_vols) <= daily_vol).mean() * 100
        else:
            current_vol_percentile = 50.0
    else:
        current_vol_percentile = 50.0
    
    # Handle NaN values
    daily_vol = daily_vol if not np.isnan(daily_vol) else 0.05
    annualized_vol = annualized_vol if not np.isnan(annualized_vol) else 0.25
    current_vol_percentile = current_vol_percentile if not np.isnan(current_vol_percentile) else 50.0
    
    return {
        "daily_volatility": float(daily_vol),
        "annualized_volatility": float(annualized_vol),
        "volatility_percentile": float(current_vol_percentile),
        "data_points": len(recent_returns)
    }


def calculate_volatility_adjusted_limit(annualized_volatility: float) -> float:
    """
    Calculate position limit as percentage of portfolio based on volatility.
    
    Logic:
    - Low volatility (<15%): Up to 25% allocation
    - Medium volatility (15-30%): 15-20% allocation  
    - High volatility (>30%): 10-15% allocation
    - Very high volatility (>50%): Max 10% allocation
    
    Args:
        annualized_volatility: Annualized volatility (e.g., 0.25 for 25%)
        
    Returns:
        Position limit as a fraction of portfolio (e.g., 0.20 for 20%)
    """
    base_limit = 0.20  # 20% baseline
    
    if annualized_volatility < 0.15:  # Low volatility
        # Allow higher allocation for stable stocks
        vol_multiplier = 1.25  # Up to 25%
    elif annualized_volatility < 0.30:  # Medium volatility  
        # Standard allocation with slight adjustment based on volatility
        vol_multiplier = 1.0 - (annualized_volatility - 0.15) * 0.5  # 20% -> 12.5%
    elif annualized_volatility < 0.50:  # High volatility
        # Reduce allocation significantly
        vol_multiplier = 0.75 - (annualized_volatility - 0.30) * 0.5  # 15% -> 5%
    else:  # Very high volatility (>50%)
        # Minimum allocation for very risky stocks
        vol_multiplier = 0.50  # Max 10%
    
    # Apply bounds to ensure reasonable limits
    vol_multiplier = max(0.25, min(1.25, vol_multiplier))  # 5% to 25% range
    
    return base_limit * vol_multiplier


def calculate_correlation_multiplier(avg_correlation: float) -> float:
    """
    Map average correlation to an adjustment multiplier.
    
    - Very high correlation (>= 0.8): reduce limit sharply (0.7x)
    - High correlation (0.6-0.8): reduce (0.85x)
    - Moderate correlation (0.4-0.6): neutral (1.0x)
    - Low correlation (0.2-0.4): slight increase (1.05x)
    - Very low correlation (< 0.2): increase (1.10x)
    
    Args:
        avg_correlation: Average correlation with other positions (0-1)
        
    Returns:
        Correlation adjustment multiplier
    """
    if avg_correlation >= 0.80:
        return 0.70
    if avg_correlation >= 0.60:
        return 0.85
    if avg_correlation >= 0.40:
        return 1.00
    if avg_correlation >= 0.20:
        return 1.05
    return 1.10


# ========== Risk Manager Agent ==========

async def run_risk_management(
    state: AgentState,
    llm_service: LLMService
) -> AgentState:
    """
    Run risk management analysis for the current portfolio and tickers.
    
    This function calculates:
    1. Volatility metrics for each ticker
    2. Position limits based on volatility
    3. Correlation adjustments for existing positions
    4. Remaining position limits for each ticker
    
    Args:
        state: Current workflow state
        llm_service: LLM service instance
        
    Returns:
        Updated state with risk_analysis results
    """
    print("[risk_manager] Starting risk management analysis...")
    
    # Extract data from state
    portfolio = state.get("portfolio", {"cash": 100000, "positions": {}})
    tickers = state.get("tickers", [])
    
    if not tickers:
        print("[risk_manager] No tickers to analyze")
        state["risk_analysis"] = {}
        return state
    
    cash = portfolio.get("cash", 100000)
    positions = portfolio.get("positions", {})
    
    # Calculate total portfolio value
    # Note: In a real implementation, this would fetch current prices
    total_portfolio_value = cash
    
    # Calculate position limits for each ticker
    risk_analysis = {}
    
    for ticker in tickers:
        print(f"[risk_manager] Analyzing {ticker}...")
        
        # Get historical prices for volatility calculation
        # In a real implementation, this would fetch from a data source
        historical_prices = state.get("historical_prices", {}).get(ticker, [])
        
        if historical_prices:
            volatility_metrics = calculate_volatility_metrics(historical_prices)
        else:
            # Use default volatility if no historical data
            volatility_metrics = {
                "daily_volatility": 0.05,
                "annualized_volatility": 0.25,
                "volatility_percentile": 50.0,
                "data_points": 0
            }
        
        # Calculate volatility-adjusted position limit
        vol_adjusted_limit_pct = calculate_volatility_adjusted_limit(
            volatility_metrics["annualized_volatility"]
        )
        
        # Calculate current position value for this ticker
        current_position = positions.get(ticker, {})
        position_value = current_position.get("value", 0)
        
        # Calculate remaining position limit
        position_limit = total_portfolio_value * vol_adjusted_limit_pct
        remaining_position_limit = max(0, position_limit - position_value)
        
        # Determine risk level
        ann_vol = volatility_metrics["annualized_volatility"]
        if ann_vol < 0.15:
            risk_level = "low"
        elif ann_vol < 0.30:
            risk_level = "medium"
        elif ann_vol < 0.50:
            risk_level = "high"
        else:
            risk_level = "very_high"
        
        risk_analysis[ticker] = {
            "remaining_position_limit": float(remaining_position_limit),
            "position_limit": float(position_limit),
            "current_position_value": float(position_value),
            "volatility_metrics": volatility_metrics,
            "risk_level": risk_level,
            "vol_adjusted_limit_pct": float(vol_adjusted_limit_pct),
            "recommendation": _get_risk_recommendation(
                remaining_position_limit, 
                volatility_metrics, 
                risk_level
            )
        }
        
        print(f"[risk_manager] {ticker}: vol={ann_vol:.1%}, "
              f"limit={vol_adjusted_limit_pct:.1%}, "
              f"remaining=${remaining_position_limit:.2f}")
    
    # Store risk analysis in state
    state["risk_analysis"] = risk_analysis
    
    print(f"[risk_manager] Risk management complete for {len(risk_analysis)} tickers")
    
    return state


def _get_risk_recommendation(
    remaining_limit: float,
    volatility_metrics: dict,
    risk_level: str
) -> str:
    """Generate risk recommendation text based on analysis.
    
    Args:
        remaining_limit: Remaining position limit in dollars
        volatility_metrics: Volatility metrics dict
        risk_level: Risk level string
        
    Returns:
        Recommendation string
    """
    if remaining_limit <= 0:
        return "仓位已满，不建议追加"
    
    if risk_level == "very_high":
        return f"高波动性({volatility_metrics['annualized_volatility']:.1%})，建议谨慎"
    elif risk_level == "high":
        return f"中高波动({volatility_metrics['annualized_volatility']:.1%})，适度配置"
    elif risk_level == "medium":
        return f"中等波动({volatility_metrics['annualized_volatility']:.1%})，可正常配置"
    else:
        return f"低波动({volatility_metrics['annualized_volatility']:.1%})，可增加配置"


async def analyze_portfolio_risk(
    state: AgentState,
    llm_service: LLMService
) -> dict:
    """
    Run LLM-based portfolio risk analysis.
    
    This function uses the LLM to provide additional risk insights
    based on the calculated volatility metrics and position limits.
    
    Args:
        state: Current workflow state
        llm_service: LLM service instance
        
    Returns:
        Risk analysis summary from LLM
    """
    risk_analysis = state.get("risk_analysis", {})
    portfolio = state.get("portfolio", {})
    
    if not risk_analysis:
        return {"error": "No risk analysis data available"}
    
    # Build prompt for risk analysis
    prompt = _build_risk_analysis_prompt(risk_analysis, portfolio)
    
    try:
        response = await llm_service.complete([
            {"role": "system", "content": """你是一位风险管理专家，专注于投资组合风险评估。
你的职责是分析投资组合的风险暴露，提供风险控制建议。
请用专业、谨慎的语气进行分析。"""},
            {"role": "user", "content": prompt}
        ])
        
        return {
            "llm_risk_summary": response.get("content", ""),
            "tokens": response.get("tokens", 0)
        }
    except Exception as e:
        print(f"[risk_manager] LLM analysis error: {e}")
        return {
            "llm_risk_summary": "",
            "error": str(e),
            "tokens": 0
        }


def _build_risk_analysis_prompt(
    risk_analysis: dict,
    portfolio: dict
) -> str:
    """Build prompt for LLM risk analysis."""
    cash = portfolio.get("cash", 0)
    positions = portfolio.get("positions", {})
    
    ticker_summaries = []
    for ticker, data in risk_analysis.items():
        vol = data.get("volatility_metrics", {}).get("annualized_volatility", 0)
        limit_pct = data.get("vol_adjusted_limit_pct", 0) * 100
        remaining = data.get("remaining_position_limit", 0)
        risk_level = data.get("risk_level", "unknown")
        
        ticker_summaries.append(
            f"- {ticker}: 波动率{vol:.1%}, 仓位限制{limit_pct:.1f}%, "
            f"剩余限额${remaining:.2f}, 风险等级{risk_level}"
        )
    
    return f"""请分析以下投资组合的风险状况：

现金: ${cash:.2f}
当前持仓: {len(positions)} 个标的

各标的风险分析：
{chr(10).join(ticker_summaries) if ticker_summaries else '暂无持仓'}

请提供：
1. 整体风险评估
2. 风险集中度分析
3. 建议的风险控制措施
4. 是否需要调整仓位

请用JSON格式返回：
{{
    "overall_risk_level": "低" | "中" | "高" | "极高",
    "risk_concentration": "分散良好" | "略显集中" | "过于集中",
    "key_risks": ["风险1", "风险2"],
    "recommendations": ["建议1", "建议2"],
    "summary": "总结（100字以内）"
}}"""
