"""
TradingAgents agents package

Based on: TradingAgents/tradingagents/agents/

This package contains all TradingAgents-specific agents:
- managers/: Trader, Portfolio Manager
- researchers/: Market Analyst, Social Analyst, News Analyst, Fundamentals Analyst
- risk_debate.py: Risk Debate Node (conservative/moderate/aggressive perspectives)
"""

from .managers.trader import run_trader
from .managers.portfolio_manager import run_portfolio_manager
from .researchers.market import run_market_analyst
from .researchers.social import run_social_analyst
from .researchers.news import run_news_analyst
from .risk_debate import run_risk_debate

__all__ = [
    "run_trader",
    "run_portfolio_manager",
    "run_market_analyst",
    "run_social_analyst",
    "run_news_analyst",
    "run_risk_debate",
]
