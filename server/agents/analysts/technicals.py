"""
Technical Analyst Implementation

技术分析师的具体实现
- 均线分析 (MA5/MA10/MA20/MA60)
- MACD 分析
- KDJ 分析
- 布林带分析

This module provides the TechnicalAnalyst class with technical analysis functions.
"""

import math
import json
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from graph.state import AgentState
    from services.llm import LLMService
    from services.data import DataService

# 使用 pandas 和 numpy（已安装）
import pandas as pd
import numpy as np


class TechnicalAnalyst:
    """技术分析师
    
    提供完整的技术分析功能：
    - 趋势分析（均线、ADX）
    - 动量分析（RSI、MACD）
    - 波动性分析（布林带、ATR）
    - 超买超卖分析（KDJ）
    """
    
    # 类级别的配置
    ANALYST_ID = "technical_analyst"
    ANALYST_NAME = "技术分析师"
    
    def __init__(self):
        """初始化 Technical Analyst"""
        self.id = self.ANALYST_ID
        self.name = self.ANALYST_NAME
    
    def analyze(
        self,
        state: 'AgentState',
        data_service: 'DataService'
    ) -> dict:
        """运行技术分析
        
        Args:
            state: 当前工作流状态
            data_service: 数据服务实例
            
        Returns:
            技术分析结果
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
            
            # 计算各指标
            ma_analysis = self._calculate_moving_averages(df)
            macd_analysis = self._calculate_macd(df)
            kdj_analysis = self._calculate_kdj(df)
            bollinger_analysis = self._calculate_bollinger_bands(df)
            
            # 综合信号
            combined_signal = self._combine_signals(
                ma_analysis,
                macd_analysis,
                kdj_analysis,
                bollinger_analysis
            )
            
            result = {
                "signal": combined_signal["signal"],
                "confidence": combined_signal["confidence"],
                "technicals": {
                    "moving_averages": ma_analysis,
                    "macd": macd_analysis,
                    "kdj": kdj_analysis,
                    "bollinger_bands": bollinger_analysis,
                },
                "analyst_id": self.id,
                "analyst_name": self.name,
            }
            
            print(f"[analyst:{self.id}] 完成: signal={result['signal']}, "
                  f"confidence={result['confidence']}")
            
            return result
            
        except Exception as e:
            print(f"[analyst:{self.id}] 错误: {e}")
            return self._get_empty_result(f"分析失败: {str(e)}")
    
    def _calculate_moving_averages(self, df: pd.DataFrame) -> dict:
        """计算均线分析"""
        close = df["close"]
        
        # 计算各周期均线
        ma5 = close.rolling(window=5).mean()
        ma10 = close.rolling(window=10).mean()
        ma20 = close.rolling(window=20).mean()
        ma60 = close.rolling(window=60).mean()
        
        current_price = close.iloc[-1]
        
        # 金叉死叉判断
        ma5_above_ma10 = ma5.iloc[-1] > ma10.iloc[-1] if not pd.isna(ma10.iloc[-1]) else False
        ma10_above_ma20 = ma10.iloc[-1] > ma20.iloc[-1] if not pd.isna(ma20.iloc[-1]) else False
        ma20_above_ma60 = ma20.iloc[-1] > ma60.iloc[-1] if not pd.isna(ma60.iloc[-1]) else False
        
        # 均线多头排列
        bullish_arrangement = ma5_above_ma10 and ma10_above_ma20 and ma20_above_ma60
        
        # 价格与均线关系
        price_above_ma20 = current_price > ma20.iloc[-1] if not pd.isna(ma20.iloc[-1]) else False
        price_above_ma60 = current_price > ma60.iloc[-1] if not pd.isna(ma60.iloc[-1]) else False
        
        # 计算信号
        if bullish_arrangement and price_above_ma60:
            signal = "bullish"
            confidence = 0.8
        elif not ma5_above_ma10 and not price_above_ma20:
            signal = "bearish"
            confidence = 0.7
        else:
            signal = "neutral"
            confidence = 0.5
        
        return {
            "signal": signal,
            "confidence": confidence,
            "metrics": {
                "ma5": round(ma5.iloc[-1], 2) if not pd.isna(ma5.iloc[-1]) else None,
                "ma10": round(ma10.iloc[-1], 2) if not pd.isna(ma10.iloc[-1]) else None,
                "ma20": round(ma20.iloc[-1], 2) if not pd.isna(ma20.iloc[-1]) else None,
                "ma60": round(ma60.iloc[-1], 2) if not pd.isna(ma60.iloc[-1]) else None,
                "current_price": round(current_price, 2),
                "ma5_above_ma10": ma5_above_ma10,
                "ma10_above_ma20": ma10_above_ma20,
                "ma20_above_ma60": ma20_above_ma60,
                "bullish_arrangement": bullish_arrangement,
                "price_above_ma20": price_above_ma20,
            }
        }
    
    def _calculate_macd(self, df: pd.DataFrame) -> dict:
        """计算 MACD 分析"""
        close = df["close"]
        
        # 计算 EMA
        ema12 = close.ewm(span=12, adjust=False).mean()
        ema26 = close.ewm(span=26, adjust=False).mean()
        
        # MACD 线和信号线
        macd_line = ema12 - ema26
        signal_line = macd_line.ewm(span=9, adjust=False).mean()
        histogram = macd_line - signal_line
        
        # 最新值
        current_macd = macd_line.iloc[-1]
        current_signal = signal_line.iloc[-1]
        current_hist = histogram.iloc[-1]
        
        # MACD 金叉死叉
        macd_bullish_cross = current_macd > current_signal and histogram.iloc[-2] <= 0
        macd_bearish_cross = current_macd < current_signal and histogram.iloc[-2] >= 0
        
        # 柱状图趋势
        hist_positive = current_hist > 0
        hist_increasing = current_hist > histogram.iloc[-2] if len(histogram) > 2 else False
        
        # 计算信号
        if macd_bullish_cross and hist_positive:
            signal = "bullish"
            confidence = 0.75
        elif macd_bearish_cross and not hist_positive:
            signal = "bearish"
            confidence = 0.7
        elif hist_positive and hist_increasing:
            signal = "bullish"
            confidence = 0.6
        elif not hist_positive and not hist_increasing:
            signal = "bearish"
            confidence = 0.6
        else:
            signal = "neutral"
            confidence = 0.5
        
        return {
            "signal": signal,
            "confidence": confidence,
            "metrics": {
                "macd": round(current_macd, 4),
                "signal_line": round(current_signal, 4),
                "histogram": round(current_hist, 4),
                "macd_bullish_cross": macd_bullish_cross,
                "macd_bearish_cross": macd_bearish_cross,
                "histogram_positive": hist_positive,
                "histogram_increasing": hist_increasing,
            }
        }
    
    def _calculate_kdj(self, df: pd.DataFrame) -> dict:
        """计算 KDJ 分析"""
        low = df["low"]
        high = df["high"]
        close = df["close"]
        
        # 计算 KDJ
        period = 9
        k_values = []
        d_values = []
        
        for i in range(len(close)):
            if i < period - 1:
                k_values.append(50)
                d_values.append(50)
                continue
            
            # 找最近 period 天的最低价和最高价
            low_min = low.iloc[i - period + 1:i + 1].min()
            high_max = high.iloc[i - period + 1:i + 1].max()
            
            if high_max == low_min:
                rsv = 50
            else:
                rsv = (close.iloc[i] - low_min) / (high_max - low_min) * 100
            
            # K 和 D 值
            if len(k_values) > 0:
                k = 2 / 3 * k_values[-1] + 1 / 3 * rsv
                d = 2 / 3 * d_values[-1] + 1 / 3 * k
            else:
                k = 50
                d = 50
            
            k_values.append(k)
            d_values.append(d)
        
        # J 值
        j_values = [3 * k - 2 * d for k, d in zip(k_values, d_values)]
        
        # 最新值
        current_k = k_values[-1]
        current_d = d_values[-1]
        current_j = j_values[-1]
        
        # 超买超卖判断
        kdj_overbought = current_k > 80 and current_d > 80
        kdj_oversold = current_k < 20 and current_d < 20
        
        # 金叉死叉
        k_above_d = current_k > current_d
        prev_k_below_d = k_values[-2] < d_values[-2] if len(k_values) > 1 else False
        kdj_golden_cross = k_above_d and prev_k_below_d
        kdj_death_cross = not k_above_d and not prev_k_below_d
        
        # 计算信号
        if kdj_oversold and kdj_golden_cross:
            signal = "bullish"
            confidence = 0.75
        elif kdj_overbought and kdj_death_cross:
            signal = "bearish"
            confidence = 0.7
        elif kdj_oversold:
            signal = "bullish"
            confidence = 0.55
        elif kdj_overbought:
            signal = "bearish"
            confidence = 0.55
        else:
            signal = "neutral"
            confidence = 0.5
        
        return {
            "signal": signal,
            "confidence": confidence,
            "metrics": {
                "k": round(current_k, 2),
                "d": round(current_d, 2),
                "j": round(current_j, 2),
                "overbought": kdj_overbought,
                "oversold": kdj_oversold,
                "golden_cross": kdj_golden_cross,
                "death_cross": kdj_death_cross,
            }
        }
    
    def _calculate_bollinger_bands(self, df: pd.DataFrame) -> dict:
        """计算布林带分析"""
        close = df["close"]
        
        # 计算布林带
        window = 20
        sma = close.rolling(window).mean()
        std = close.rolling(window).std()
        
        upper_band = sma + (std * 2)
        lower_band = sma - (std * 2)
        
        current_price = close.iloc[-1]
        current_upper = upper_band.iloc[-1]
        current_lower = lower_band.iloc[-1]
        current_mid = sma.iloc[-1]
        
        # 布林带位置
        if pd.isna(current_upper) or pd.isna(current_lower):
            bb_position = 0.5
        else:
            bb_range = current_upper - current_lower
            if bb_range > 0:
                bb_position = (current_price - current_lower) / bb_range
            else:
                bb_position = 0.5
        
        # 突破判断
        bb_upper_break = current_price > current_upper if not pd.isna(current_upper) else False
        bb_lower_break = current_price < current_lower if not pd.isna(current_lower) else False
        
        # 收窄判断
        bb_width = (current_upper - current_lower) / current_mid if current_mid and current_mid > 0 else 0
        prev_bb_width = (upper_band.iloc[-2] - lower_band.iloc[-2]) / sma.iloc[-2] if len(upper_band) > 1 and sma.iloc[-2] > 0 else 0
        bb_squeezing = bb_width < prev_bb_width * 0.9
        
        # 计算信号
        if bb_lower_break:
            signal = "bullish"
            confidence = 0.7
        elif bb_upper_break:
            signal = "bearish"
            confidence = 0.7
        elif bb_position < 0.2:
            signal = "bullish"
            confidence = 0.6
        elif bb_position > 0.8:
            signal = "bearish"
            confidence = 0.6
        else:
            signal = "neutral"
            confidence = 0.5
        
        return {
            "signal": signal,
            "confidence": confidence,
            "metrics": {
                "upper_band": round(current_upper, 2) if not pd.isna(current_upper) else None,
                "middle_band": round(current_mid, 2) if not pd.isna(current_mid) else None,
                "lower_band": round(current_lower, 2) if not pd.isna(current_lower) else None,
                "current_price": round(current_price, 2),
                "bb_position": round(bb_position, 3),
                "bb_width": round(bb_width, 4),
                "upper_break": bb_upper_break,
                "lower_break": bb_lower_break,
                "squeezing": bb_squeezing,
            }
        }
    
    def _combine_signals(
        self,
        ma: dict,
        macd: dict,
        kdj: dict,
        bollinger: dict
    ) -> dict:
        """综合所有信号"""
        signals = {
            "ma": ma["signal"],
            "macd": macd["signal"],
            "kdj": kdj["signal"],
            "bollinger": bollinger["signal"],
        }
        confidences = {
            "ma": ma["confidence"],
            "macd": macd["confidence"],
            "kdj": kdj["confidence"],
            "bollinger": bollinger["confidence"],
        }
        
        # 权重
        weights = {
            "ma": 0.30,
            "macd": 0.25,
            "kdj": 0.25,
            "bollinger": 0.20,
        }
        
        # 计算加权得分
        signal_values = {"bullish": 1, "neutral": 0, "bearish": -1}
        
        weighted_sum = sum(
            signal_values[s] * weights[k] * confidences[k]
            for k, s in signals.items()
        )
        total_weight = sum(weights[k] * confidences[k] for k in signals)
        
        if total_weight > 0:
            final_score = weighted_sum / total_weight
        else:
            final_score = 0
        
        # 判断信号
        if final_score > 0.2:
            signal = "bullish"
        elif final_score < -0.2:
            signal = "bearish"
        else:
            signal = "neutral"
        
        confidence = min(abs(final_score) + 0.3, 1.0)
        
        return {"signal": signal, "confidence": confidence}
    
    def _get_empty_result(self, reason: str) -> dict:
        """获取空结果"""
        return {
            "signal": "neutral",
            "confidence": 0,
            "technicals": {
                "moving_averages": {"signal": "neutral", "metrics": {}},
                "macd": {"signal": "neutral", "metrics": {}},
                "kdj": {"signal": "neutral", "metrics": {}},
                "bollinger_bands": {"signal": "neutral", "metrics": {}},
            },
            "analyst_id": self.id,
            "analyst_name": self.name,
            "error": reason,
        }


# 便捷函数

def run_technical_analyst(
    state: 'AgentState',
    llm_service: Optional['LLMService'] = None
) -> dict:
    """运行技术分析的便捷函数
    
    Args:
        state: 当前工作流状态
        llm_service: LLM 服务实例（可选，用于增强分析）
        
    Returns:
        技术分析结果
    """
    # 导入放在函数内避免循环依赖
    from services.data import get_data_service
    
    analyst = TechnicalAnalyst()
    data_service = get_data_service()
    
    return analyst.analyze(state, data_service)
