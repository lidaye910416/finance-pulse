"""
Valuation Analyst Implementation

估值分析师的具体实现
- DCF 估值模型
- PE/PB 相对估值

This module provides the ValuationAnalyst class for stock valuation.
"""

import json
import math
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from graph.state import AgentState
    from services.llm import LLMService
    from services.data import DataService

import pandas as pd


class ValuationAnalyst:
    """估值分析师
    
    提供估值分析功能：
    - DCF 现金流折现模型
    - PE/PB 相对估值
    - PEG 估值
    - 行业比较
    """
    
    # 类级别的配置
    ANALYST_ID = "valuation_analyst"
    ANALYST_NAME = "估值分析师"
    
    def __init__(self):
        """初始化 Valuation Analyst"""
        self.id = self.ANALYST_ID
        self.name = self.ANALYST_NAME
    
    def analyze(
        self,
        state: 'AgentState',
        data_service: 'DataService'
    ) -> dict:
        """运行估值分析
        
        Args:
            state: 当前工作流状态
            data_service: 数据服务实例
            
        Returns:
            估值分析结果
        """
        code = state.get("code", "")
        
        print(f"[analyst:{self.id}] {self.name} 正在分析 {code}...")
        
        try:
            # 获取实时行情
            stock_data = data_service.get_stock_data(code)
            
            # 获取财务指标
            financial_metrics = data_service.get_financial_metrics(code, "annual", 8)
            
            # 计算各估值方法
            dcf_valuation = self._calculate_dcf_valuation(stock_data, financial_metrics)
            pe_valuation = self._calculate_pe_valuation(stock_data, financial_metrics)
            pb_valuation = self._calculate_pb_valuation(stock_data, financial_metrics)
            peg_valuation = self._calculate_peg_valuation(stock_data, financial_metrics)
            
            # 综合估值
            combined = self._combine_valuations(
                dcf_valuation,
                pe_valuation,
                pb_valuation,
                peg_valuation
            )
            
            result = {
                "signal": combined["signal"],
                "confidence": combined["confidence"],
                "valuation": {
                    "dcf": dcf_valuation,
                    "pe": pe_valuation,
                    "pb": pb_valuation,
                    "peg": peg_valuation,
                    "综合估值": combined,
                },
                "analyst_id": self.id,
                "analyst_name": self.name,
            }
            
            print(f"[analyst:{self.id}] 完成: signal={result['signal']}, "
                  f"综合估值={combined['intrinsic_value']}")
            
            return result
            
        except Exception as e:
            print(f"[analyst:{self.id}] 错误: {e}")
            return self._get_empty_result(f"分析失败: {str(e)}")
    
    def _calculate_dcf_valuation(
        self,
        stock_data: dict,
        financial_metrics: list
    ) -> dict:
        """计算 DCF 估值"""
        price = stock_data.get("price", 0)
        
        if not financial_metrics or price <= 0:
            return {
                "signal": "neutral",
                "confidence": 0.3,
                "metrics": {
                    "dcf_value": None,
                    "current_price": price,
                    "discount": None,
                    "upside": None,
                }
            }
        
        # 获取净利润用于估算 FCF
        latest = financial_metrics[0] if financial_metrics else {}
        net_income = latest.get("profit_growth", 0) * 1000  # 简化估算
        
        # 假设净利润作为 FCF 的近似
        base_fcf = net_income if net_income > 0 else price * 0.1  # 默认 10% 作为 FCF
        
        # DCF 参数
        growth_rate = 0.05  # 默认 5% 增长率
        discount_rate = 0.10  # 10% 折现率
        terminal_growth = 0.03  # 3% 永续增长率
        projection_years = 5
        
        # 计算 DCF
        pv = 0.0
        for year in range(1, projection_years + 1):
            fcf = base_fcf * (1 + growth_rate) ** year
            pv += fcf / (1 + discount_rate) ** year
        
        # 永续价值
        terminal_fcf = base_fcf * (1 + growth_rate) ** projection_years * (1 + terminal_growth)
        terminal_value = terminal_fcf / (discount_rate - terminal_growth)
        pv_terminal = terminal_value / (1 + discount_rate) ** projection_years
        
        dcf_value = pv + pv_terminal
        
        # 计算折价
        if dcf_value > 0:
            discount = (dcf_value - price) / dcf_value * 100
            upside = (dcf_value - price) / price * 100
        else:
            discount = 0
            upside = 0
        
        # 信号判断
        if discount > 30:
            signal = "bullish"
            confidence = 0.75
        elif discount > 15:
            signal = "bullish"
            confidence = 0.65
        elif discount < -30:
            signal = "bearish"
            confidence = 0.75
        elif discount < -15:
            signal = "bearish"
            confidence = 0.65
        else:
            signal = "neutral"
            confidence = 0.5
        
        return {
            "signal": signal,
            "confidence": confidence,
            "metrics": {
                "dcf_value": round(dcf_value, 2),
                "current_price": round(price, 2),
                "discount_pct": round(discount, 1),
                "upside_pct": round(upside, 1),
                "growth_rate": round(growth_rate * 100, 1),
                "discount_rate": round(discount_rate * 100, 1),
            }
        }
    
    def _calculate_pe_valuation(
        self,
        stock_data: dict,
        financial_metrics: list
    ) -> dict:
        """计算 PE 估值"""
        price = stock_data.get("price", 0)
        pe = stock_data.get("pe")
        
        if not pe or pe <= 0:
            # 尝试从财务指标估算
            if financial_metrics:
                pe = 20.0  # 默认 PE
            else:
                return {
                    "signal": "neutral",
                    "confidence": 0.3,
                    "metrics": {"pe": None, "fair_pe": None, "valuation": "unknown"}
                }
        
        # 合理 PE 范围（基于不同市场环境）
        fair_pe_low = 15
        fair_pe_high = 25
        fair_pe = (fair_pe_low + fair_pe_high) / 2
        
        # 判断估值水平
        if pe < fair_pe_low * 0.7:
            valuation = "严重低估"
            signal = "bullish"
            confidence = 0.7
        elif pe < fair_pe_low:
            valuation = "低估"
            signal = "bullish"
            confidence = 0.6
        elif pe > fair_pe_high * 1.3:
            valuation = "严重高估"
            signal = "bearish"
            confidence = 0.7
        elif pe > fair_pe_high:
            valuation = "高估"
            signal = "bearish"
            confidence = 0.6
        else:
            valuation = "合理"
            signal = "neutral"
            confidence = 0.5
        
        return {
            "signal": signal,
            "confidence": confidence,
            "metrics": {
                "pe": round(pe, 1),
                "fair_pe_low": fair_pe_low,
                "fair_pe_high": fair_pe_high,
                "fair_pe": fair_pe,
                "valuation": valuation,
            }
        }
    
    def _calculate_pb_valuation(
        self,
        stock_data: dict,
        financial_metrics: list
    ) -> dict:
        """计算 PB 估值"""
        price = stock_data.get("price", 0)
        pb = stock_data.get("pb")
        
        if not pb or pb <= 0:
            if financial_metrics:
                pb = 3.0  # 默认 PB
            else:
                return {
                    "signal": "neutral",
                    "confidence": 0.3,
                    "metrics": {"pb": None, "fair_pb": None, "valuation": "unknown"}
                }
        
        # 合理 PB 范围
        fair_pb_low = 2.0
        fair_pb_high = 5.0
        
        # 判断估值水平
        if pb < fair_pb_low * 0.7:
            valuation = "严重低估"
            signal = "bullish"
            confidence = 0.7
        elif pb < fair_pb_low:
            valuation = "低估"
            signal = "bullish"
            confidence = 0.6
        elif pb > fair_pb_high * 1.3:
            valuation = "严重高估"
            signal = "bearish"
            confidence = 0.7
        elif pb > fair_pb_high:
            valuation = "高估"
            signal = "bearish"
            confidence = 0.6
        else:
            valuation = "合理"
            signal = "neutral"
            confidence = 0.5
        
        return {
            "signal": signal,
            "confidence": confidence,
            "metrics": {
                "pb": round(pb, 2),
                "fair_pb_low": fair_pb_low,
                "fair_pb_high": fair_pb_high,
                "valuation": valuation,
            }
        }
    
    def _calculate_peg_valuation(
        self,
        stock_data: dict,
        financial_metrics: list
    ) -> dict:
        """计算 PEG 估值"""
        price = stock_data.get("price", 0)
        pe = stock_data.get("pe")
        
        if not pe or pe <= 0:
            return {
                "signal": "neutral",
                "confidence": 0.3,
                "metrics": {"peg": None, "growth_rate": None, "valuation": "unknown"}
            }
        
        # 获取增长率
        growth_rate = 0.0
        if financial_metrics:
            latest = financial_metrics[0]
            growth_rate = latest.get("profit_growth", 0) / 100  # 转换为小数
        
        if growth_rate <= 0:
            growth_rate = 0.10  # 默认 10%
        
        # 计算 PEG
        peg = pe / (growth_rate * 100) if growth_rate > 0 else 999
        
        # 判断估值水平
        if peg < 0.5:
            valuation = "严重低估"
            signal = "bullish"
            confidence = 0.75
        elif peg < 1.0:
            valuation = "低估（成长合理）"
            signal = "bullish"
            confidence = 0.65
        elif peg < 1.5:
            valuation = "合理"
            signal = "neutral"
            confidence = 0.5
        elif peg < 2.0:
            valuation = "略高估"
            signal = "bearish"
            confidence = 0.55
        else:
            valuation = "严重高估"
            signal = "bearish"
            confidence = 0.65
        
        return {
            "signal": signal,
            "confidence": confidence,
            "metrics": {
                "peg": round(peg, 2),
                "pe": round(pe, 1),
                "growth_rate": round(growth_rate * 100, 1),
                "valuation": valuation,
            }
        }
    
    def _combine_valuations(
        self,
        dcf: dict,
        pe: dict,
        pb: dict,
        peg: dict
    ) -> dict:
        """综合估值"""
        # 权重
        weights = {
            "dcf": 0.40,
            "pe": 0.25,
            "pb": 0.15,
            "peg": 0.20,
        }
        
        # 计算综合信号
        signals = {
            "dcf": dcf["signal"],
            "pe": pe["signal"],
            "pb": pb["signal"],
            "peg": peg["signal"],
        }
        
        confidences = {
            "dcf": dcf["confidence"],
            "pe": pe["confidence"],
            "pb": pb["confidence"],
            "peg": peg["confidence"],
        }
        
        signal_values = {"bullish": 1, "neutral": 0, "bearish": -1}
        
        weighted_sum = sum(
            signal_values[s] * weights[k] * confidences[k]
            for k, s in signals.items()
        )
        total_weight = sum(weights[k] * confidences[k] for k in weights)
        
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
        
        # 计算综合内在价值
        dcf_value = dcf["metrics"].get("dcf_value")
        intrinsic_value = dcf_value if dcf_value else 0
        
        return {
            "signal": signal,
            "confidence": confidence,
            "intrinsic_value": round(intrinsic_value, 2) if intrinsic_value else None,
            "overall_score": round(final_score * 100, 1),
        }
    
    def _get_empty_result(self, reason: str) -> dict:
        """获取空结果"""
        return {
            "signal": "neutral",
            "confidence": 0,
            "valuation": {
                "dcf": {"metrics": {}},
                "pe": {"metrics": {}},
                "pb": {"metrics": {}},
                "peg": {"metrics": {}},
                "综合估值": {"signal": "neutral", "overall_score": 0},
            },
            "analyst_id": self.id,
            "analyst_name": self.name,
            "error": reason,
        }


# 便捷函数

def run_valuation_analyst(
    state: 'AgentState',
    llm_service: Optional['LLMService'] = None
) -> dict:
    """运行估值分析的便捷函数
    
    Args:
        state: 当前工作流状态
        llm_service: LLM 服务实例（可选）
        
    Returns:
        估值分析结果
    """
    from services.data import get_data_service
    
    analyst = ValuationAnalyst()
    data_service = get_data_service()
    
    return analyst.analyze(state, data_service)
