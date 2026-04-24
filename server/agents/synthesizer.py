"""
综合分析 Agent

汇总所有分析师和辩论的结果，生成综合分析报告
"""

from graph.state import AgentState
from services.llm import LLMService


SYNTHESIZER_SYSTEM = """你是一位专业的金融分析师，擅长综合多方观点形成客观全面的分析报告。
你的分析应该平衡多方意见，给出有理有据的综合判断。"""


def _build_synthesis_prompt(state: AgentState) -> str:
    """构建综合分析的 prompt"""
    signals = state.get("analyst_signals", [])
    bullish_signal = state.get("bullish_signal", {})
    bearish_signal = state.get("bearish_signal", {})
    debate_history = state.get("debate_history", [])
    stock_data = state.get("stock_data", {})
    
    # 统计信号
    bullish_count = len([s for s in signals if s.get("signal") == "bullish"])
    bearish_count = len([s for s in signals if s.get("signal") == "bearish"])
    neutral_count = len([s for s in signals if s.get("signal") == "neutral"])
    avg_confidence = sum(s.get("confidence", 0) for s in signals) / max(len(signals), 1)
    
    return f"""请综合以下分析结果，生成最终的分析报告：

【股票信息】
{state.get('name', '')}（{state.get('code', '')}）
当前价格: ¥{stock_data.get('price', 0):.2f}
涨跌幅: {stock_data.get('change_percent', 0):+.2f}%

【分析师共识】
- 看多: {bullish_count}位
- 看空: {bearish_count}位
- 中性: {neutral_count}位
- 平均置信度: {avg_confidence:.1f}%

【分析师详情】
{chr(10).join([f"- {s['agent']}: {s['signal']} ({s['confidence']}%) - {s.get('reasoning', '')[:60]}" for s in signals])}

【辩论结果】(共{len(debate_history)}轮)
最新一轮:
- 多头: {bullish_signal.get('agent', '')} {bullish_signal.get('confidence', 0)}% - {bullish_signal.get('reasoning', '')[:60]}
- 空头: {bearish_signal.get('agent', '')} {bearish_signal.get('confidence', 0)}% - {bearish_signal.get('reasoning', '')[:60]}

请生成一段200字以内的综合分析报告，包含：
1. 市场共识总结
2. 主要看多理由
3. 主要看空理由
4. 风险提示

请用JSON格式返回：
{{
    "summary": "综合分析报告（200字以内）",
    "bullish_summary": "看多总结（50字以内）",
    "bearish_summary": "看空总结（50字以内）",
    "risk_warnings": ["风险1", "风险2"]
}}"""


async def synthesize_results(state: AgentState, llm_service: LLMService) -> AgentState:
    """
    综合分析节点
    
    在辩论收敛或达到最大迭代后执行
    """
    print("[synthesizer] 开始综合分析...")
    
    prompt = _build_synthesis_prompt(state)
    
    try:
        response = await llm_service.complete([
            {"role": "system", "content": SYNTHESIZER_SYSTEM},
            {"role": "user", "content": prompt},
        ])
        
        import json
        try:
            import re
            json_match = re.search(r'\{[\s\S]*\}', response["content"])
            if json_match:
                data = json.loads(json_match.group())
            else:
                data = json.loads(response["content"])
            
            state["final_summary"] = data.get("summary", response["content"][:500])
            state["summary_details"] = {
                "bullish_summary": data.get("bullish_summary", ""),
                "bearish_summary": data.get("bearish_summary", ""),
                "risk_warnings": data.get("risk_warnings", []),
            }
        except json.JSONDecodeError:
            state["final_summary"] = response["content"][:500]
            state["summary_details"] = {}
        
        state["total_tokens"] = state.get("total_tokens", 0) + response.get("tokens", 0)
        
        print(f"[synthesizer] 综合分析完成")
        
    except Exception as e:
        print(f"[synthesizer] 综合分析出错: {e}")
        state["error"] = f"综合分析失败: {str(e)}"
        
        # 使用默认总结
        signals = state.get("analyst_signals", [])
        bullish_count = len([s for s in signals if s.get("signal") == "bullish"])
        bearish_count = len([s for s in signals if s.get("signal") == "bearish"])
        
        state["final_summary"] = f"基于{len(signals)}位分析师的分析：{bullish_count}位看多，{bearish_count}位看空。请参考各方意见做出投资决策。"
    
    return state
