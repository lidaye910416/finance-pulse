"""
Sentiment Analyst Implementation

情绪分析师的具体实现
- 市场情绪评分
- 资金流向分析

This module provides the SentimentAnalyst class for market sentiment analysis.
"""

import json
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from graph.state import AgentState
    from services.llm import LLMService
    from services.data import DataService

import pandas as pd


class SentimentAnalyst:
    """情绪分析师
    
    提供市场情绪分析功能：
    - 涨跌家数分析
    - 成交量变化分析
    - 均线情绪判断
    - 趋势一致性分析
    """
    
    # 类级别的配置
    ANALYST_ID = "sentiment_analyst"
    ANALYST_NAME = "情绪分析师"
    
    def __init__(self):
        """初始化 Sentiment Analyst"""
        self.id = self.ANALYST_ID
        self.name = self.ANALYST_NAME
    
    def analyze(
        self,
        state: 'AgentState',
        data_service: 'DataService'
    ) -> dict:
        """运行情绪分析
        
        Args:
            state: 当前工作流状态
            data_service: 数据服务实例
            
        Returns:
            情绪分析结果
        """
        code = state.get("code", "")
        days = state.get("price_history_days", 60)
        
        print(f"[analyst:{self.id}] {self.name} 正在分析 {code}...")
        
        try:
            # 获取历史价格
            prices = data_service.get_price_history(code, days)
            
            if not prices:
                return self._get_empty_result("无法获取价格数据")
            
            # 转换为 DataFrame
            df = pd.DataFrame(prices)
            
            # 计算各情绪指标
            trend_sentiment = self._analyze_trend_sentiment(df)
            volume_sentiment = self._analyze_volume_sentiment(df)
            volatility_sentiment = self._analyze_volatility_sentiment(df)
            
            # 综合情绪
            combined = self._combine_sentiment(
                trend_sentiment,
                volume_sentiment,
                volatility_sentiment
            )
            
            result = {
                "signal": combined["signal"],
                "confidence": combined["confidence"],
                "sentiment": {
                    "trend_sentiment": trend_sentiment,
                    "volume_sentiment": volume_sentiment,
                    "volatility_sentiment": volatility_sentiment,
                    "overall_score": combined["score"],
                    "sentiment_level": combined["level"],
                },
                "analyst_id": self.id,
                "analyst_name": self.name,
            }
            
            print(f"[analyst:{self.id}] 完成: signal={result['signal']}, "
                  f"level={result['sentiment']['sentiment_level']}")
            
            return result
            
        except Exception as e:
            print(f"[analyst:{self.id}] 错误: {e}")
            return self._get_empty_result(f"分析失败: {str(e)}")
    
    def _analyze_trend_sentiment(self, df: pd.DataFrame) -> dict:
        """分析趋势情绪"""
        close = df["close"]
        
        # 计算近期涨跌
        returns = close.pct_change()
        
        # 5日、10日、20日涨跌
        return_5d = returns.tail(5).sum()
        return_10d = returns.tail(10).sum()
        return_20d = returns.tail(20).sum()
        
        # 趋势一致性
        recent_positive = sum(1 for r in returns.tail(5) if r > 0)
        trend_consistency = recent_positive / 5  # 0-1
        
        # 均线系统情绪
        ma5 = close.rolling(5).mean()
        ma20 = close.rolling(20).mean()
        ma60 = close.rolling(60).mean()
        
        ma_bullish = (
            close.iloc[-1] > ma5.iloc[-1] and
            close.iloc[-1] > ma20.iloc[-1] and
            ma5.iloc[-1] > ma20.iloc[-1] and
            ma20.iloc[-1] > ma60.iloc[-1]
        ) if not any(pd.isna([ma5.iloc[-1], ma20.iloc[-1], ma60.iloc[-1]])) else False
        
        # 情绪评分
        score = 0.0
        
        # 近期涨跌贡献
        if return_20d > 0.1:
            score += 0.3
        elif return_20d > 0.05:
            score += 0.2
        elif return_20d > 0:
            score += 0.1
        elif return_20d < -0.1:
            score -= 0.3
        elif return_20d < -0.05:
            score -= 0.2
        else:
            score -= 0.1
        
        # 趋势一致性贡献
        score += (trend_consistency - 0.5) * 0.4
        
        # 均线系统贡献
        if ma_bullish:
            score += 0.2
        
        # 标准化到 0-100
        normalized_score = max(0, min(100, 50 + score * 100))
        
        # 情绪级别
        if normalized_score >= 70:
            level = "极度乐观"
            signal = "bearish"  # 反向指标
            confidence = 0.6
        elif normalized_score >= 55:
            level = "乐观"
            signal = "bullish"
            confidence = 0.65
        elif normalized_score >= 45:
            level = "中性"
            signal = "neutral"
            confidence = 0.5
        elif normalized_score >= 30:
            level = "悲观"
            signal = "bullish"
            confidence = 0.65
        else:
            level = "极度悲观"
            signal = "bullish"  # 反向指标
            confidence = 0.6
        
        return {
            "signal": signal,
            "confidence": confidence,
            "metrics": {
                "return_5d": round(return_5d * 100, 2),
                "return_10d": round(return_10d * 100, 2),
                "return_20d": round(return_20d * 100, 2),
                "trend_consistency": round(trend_consistency, 3),
                "ma_bullish": ma_bullish,
                "score": round(normalized_score, 1),
                "level": level,
            }
        }
    
    def _analyze_volume_sentiment(self, df: pd.DataFrame) -> dict:
        """分析成交量情绪"""
        volume = df["volume"]
        close = df["close"]
        
        # 成交量均线
        volume_ma5 = volume.rolling(5).mean()
        volume_ma20 = volume.rolling(20).mean()
        
        # 今日成交量对比
        current_volume = volume.iloc[-1]
        avg_volume = volume_ma5.iloc[-1] if not pd.isna(volume_ma5.iloc[-1]) else volume.mean()
        
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
        
        # 成交量趋势
        volume_trend = (volume.tail(5) > volume_ma5.tail(5)).sum() / 5
        
        # 量价配合分析
        price_change = (close.iloc[-1] - close.iloc[-5]) / close.iloc[-5] if len(close) >= 5 else 0
        
        # 健康上涨：价涨量增；健康下跌：价跌量缩
        healthy_bull = price_change > 0 and volume_ratio > 1.0
        healthy_bear = price_change < 0 and volume_ratio < 1.0
        
        # 量价背离
        volume_price_divergence = (
            (price_change > 0 and volume_ratio < 0.8) or
            (price_change < 0 and volume_ratio > 1.2)
        )
        
        # 情绪评分
        score = 0.0
        
        if healthy_bull:
            score += 0.2
        elif healthy_bear:
            score += 0.1
        elif volume_price_divergence:
            score -= 0.2
        
        score += (volume_trend - 0.5) * 0.2
        
        # 成交量放大倍数
        if volume_ratio > 2:
            score += 0.2
        elif volume_ratio > 1.5:
            score += 0.1
        elif volume_ratio < 0.5:
            score -= 0.1
        
        # 标准化
        normalized_score = max(0, min(100, 50 + score * 100))
        
        # 情绪级别
        if normalized_score >= 70:
            level = "极度活跃"
        elif normalized_score >= 55:
            level = "活跃"
        elif normalized_score >= 45:
            level = "正常"
        elif normalized_score >= 30:
            level = "低迷"
        else:
            level = "极度低迷"
        
        # 信号判断（成交量大通常是顶部信号）
        if volume_ratio > 2 and price_change > 0:
            signal = "bearish"
            confidence = 0.65
        elif volume_ratio < 0.5:
            signal = "neutral"
            confidence = 0.5
        else:
            signal = "neutral"
            confidence = 0.5
        
        return {
            "signal": signal,
            "confidence": confidence,
            "metrics": {
                "volume_ratio": round(volume_ratio, 2),
                "volume_trend": round(volume_trend, 3),
                "price_change_5d": round(price_change * 100, 2),
                "healthy_pattern": healthy_bull or healthy_bear,
                "divergence": volume_price_divergence,
                "score": round(normalized_score, 1),
                "level": level,
            }
        }
    
    def _analyze_volatility_sentiment(self, df: pd.DataFrame) -> dict:
        """分析波动率情绪"""
        close = df["close"]
        
        # 计算波动率
        returns = close.pct_change()
        volatility_20d = returns.tail(20).std()
        volatility_60d = returns.tail(60).std() if len(returns) >= 60 else returns.std()
        
        volatility_ratio = volatility_20d / volatility_60d if volatility_60d > 0 else 1
        
        # 历史波动率百分位
        all_volatility = returns.rolling(20).std().dropna()
        current_percentile = (all_volatility < volatility_20d).sum() / len(all_volatility) * 100 if len(all_volatility) > 0 else 50
        
        # 波动率变化趋势
        recent_vol = returns.tail(10).std()
        older_vol = returns.iloc[-60:-10].std() if len(returns) >= 60 else returns.std()
        vol_trend = recent_vol / older_vol if older_vol > 0 else 1
        
        # 情绪评分
        score = 0.0
        
        # 波动率百分位
        if current_percentile >= 80:
            score -= 0.2  # 高波动通常意味着顶部/恐慌
        elif current_percentile <= 20:
            score += 0.15  # 低波动可能意味着积累
        elif current_percentile >= 60:
            score -= 0.1
        
        # 波动率变化
        if vol_trend > 1.5:
            score -= 0.15  # 波动率急剧上升
        elif vol_trend < 0.7:
            score += 0.1  # 波动率下降，可能盘整
        
        # 标准化
        normalized_score = max(0, min(100, 50 + score * 100))
        
        # 情绪级别
        if normalized_score >= 70:
            level = "极度波动"
        elif normalized_score >= 55:
            level = "高波动"
        elif normalized_score >= 45:
            level = "正常波动"
        elif normalized_score >= 30:
            level = "低波动"
        else:
            level = "极度低波动"
        
        signal = "neutral"
        confidence = 0.5
        
        return {
            "signal": signal,
            "confidence": confidence,
            "metrics": {
                "volatility_20d": round(volatility_20d * 100, 2),
                "volatility_60d": round(volatility_60d * 100, 2),
                "volatility_ratio": round(volatility_ratio, 3),
                "percentile": round(current_percentile, 1),
                "vol_trend": round(vol_trend, 3),
                "score": round(normalized_score, 1),
                "level": level,
            }
        }
    
    def _combine_sentiment(
        self,
        trend: dict,
        volume: dict,
        volatility: dict
    ) -> dict:
        """综合情绪分析"""
        # 加权平均（趋势情绪权重最高）
        weights = {"trend": 0.5, "volume": 0.3, "volatility": 0.2}
        
        scores = {
            "trend": trend["metrics"]["score"],
            "volume": volume["metrics"]["score"],
            "volatility": volatility["metrics"]["score"],
        }
        
        weighted_score = sum(scores[k] * weights[k] for k in weights)
        
        # 情绪级别
        if weighted_score >= 70:
            level = "极度乐观"
            signal = "bearish" if scores["trend"] > 70 else "bullish"
            confidence = 0.65
        elif weighted_score >= 55:
            level = "乐观"
            signal = "bullish"
            confidence = 0.65
        elif weighted_score >= 45:
            level = "中性"
            signal = "neutral"
            confidence = 0.5
        elif weighted_score >= 30:
            level = "悲观"
            signal = "bullish"
            confidence = 0.65
        else:
            level = "极度悲观"
            signal = "bullish"
            confidence = 0.65
        
        return {
            "signal": signal,
            "confidence": confidence,
            "score": round(weighted_score, 1),
            "level": level,
        }
    
    def _get_empty_result(self, reason: str) -> dict:
        """获取空结果"""
        return {
            "signal": "neutral",
            "confidence": 0,
            "sentiment": {
                "trend_sentiment": {"metrics": {}},
                "volume_sentiment": {"metrics": {}},
                "volatility_sentiment": {"metrics": {}},
                "overall_score": 50,
                "sentiment_level": "未知",
            },
            "analyst_id": self.id,
            "analyst_name": self.name,
            "error": reason,
        }


# 便捷函数

def run_sentiment_analyst(
    state: 'AgentState',
    llm_service: Optional['LLMService'] = None
) -> dict:
    """运行情绪分析的便捷函数
    
    Args:
        state: 当前工作流状态
        llm_service: LLM 服务实例（可选）
        
    Returns:
        情绪分析结果
    """
    from services.data import get_data_service
    
    analyst = SentimentAnalyst()
    data_service = get_data_service()
    
    return analyst.analyze(state, data_service)
