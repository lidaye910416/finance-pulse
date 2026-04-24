"""
LangGraph 工作流定义

定义多智能体分析的工作流图结构:

                    ┌─────────────────┐
                    │   collect_data  │
                    └────────┬────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────┐
│                                                          │
│   ┌─────────────┐    ┌─────────────┐                   │
│   │ analyst_1   │    │ analyst_2   │    并行分析       │
│   └──────┬──────┘    └──────┬──────┘                   │
│          │                   │                           │
│   ┌──────┴──────┐    ┌──────┴──────┐                   │
│   │ analyst_3   │    │ analyst_N   │                   │
│   └──────┬──────┘    └──────┬──────┘                   │
│          │                   │                           │
│          └────────┬──────────┘                           │
│                   │                                      │
│                   ▼                                      │
│          ┌───────────────┐                              │
│          │ gather_signals │ 收集所有信号                 │
│          └───────┬───────┘                              │
│                  │                                       │
│                  ▼                                      │
│   ◄─────────────────────────────────────►                │
│   │                                              │       │
│   │  ┌─────────┐    ┌───────────┐    ┌───────▼───┐   │
│   │  │ debate  │───→│ evaluate  │───→│ continue? │   │
│   │  │ (多头/空头│    │  (评估置信度│    │           │   │
│   │  │  辩论)   │    │  差距)    │    └─────┬─────┘   │
│   │  └─────────┘    └───────────┘          │         │
│   │                                         │         │
│   │                          ┌──────────────┘         │
│   │                          │ (收敛/达到最大迭代)      │
│   │                          ▼                        │
│   └──► synthesizer ◄─────────────────────────────────►┘
│            │
│            ▼
│      ┌───────────┐
│      │  decision │ 最终决策
│      └─────┬─────┘
│            │
│            ▼
│      [输出结果]
│
"""

from typing import Literal

from langgraph.graph import StateGraph, END

from .state import AgentState, should_continue
from agents.analyst import run_analysts_parallel
from agents.debate import run_debate_round
from agents.synthesizer import synthesize_results
from agents.decision import make_decision
from services.llm import LLMService


def create_workflow(llm_service: LLMService) -> StateGraph:
    """
    创建 LangGraph 工作流
    
    Args:
        llm_service: LLM 服务实例
        
    Returns:
        StateGraph: 编译后的工作流图
    """
    
    # 创建状态图
    workflow = StateGraph(AgentState)
    
    # ========== 添加节点 ==========
    
    # 1. 数据收集节点
    workflow.add_node(
        "collect_data",
        lambda state: _collect_data(state, llm_service)
    )
    
    # 2. 并行分析师节点
    workflow.add_node(
        "run_analysts",
        lambda state: run_analysts_parallel(state, llm_service)
    )
    
    # 3. 辩论节点
    workflow.add_node(
        "debate",
        lambda state: run_debate_round(state, llm_service)
    )
    
    # 4. 综合分析节点
    workflow.add_node(
        "synthesize",
        lambda state: synthesize_results(state, llm_service)
    )
    
    # 5. 决策节点
    workflow.add_node(
        "decision",
        lambda state: make_decision(state, llm_service)
    )
    
    # ========== 设置入口和边 ==========
    
    # 入口点
    workflow.set_entry_point("collect_data")
    
    # 主工作流
    workflow.add_edge("collect_data", "run_analysts")
    workflow.add_edge("run_analysts", "debate")
    
    # 条件路由：辩论后决定是继续辩论还是进入综合
    workflow.add_conditional_edges(
        "debate",
        should_continue,
        {
            "debate": "debate",      # 继续辩论（循环）
            "synthesize": "synthesize",  # 进入综合分析
        }
    )
    
    # 完成综合后进入决策
    workflow.add_edge("synthesize", "decision")
    
    # 决策节点是终点
    workflow.add_edge("decision", END)
    
    return workflow


def _collect_data(state: AgentState, llm_service: LLMService) -> AgentState:
    """
    数据收集节点
    
    准备分析所需的股票数据
    """
    from services.data import DataService
    
    data_service = DataService()
    code = state["code"]
    
    try:
        stock_data = data_service.get_stock_data_sync(code)
        state["stock_data"] = stock_data
        print(f"[collect_data] 获取 {code} 数据完成")
    except Exception as e:
        state["error"] = f"数据获取失败: {str(e)}"
        print(f"[collect_data] 错误: {e}")
    
    return state


# 类型别名，用于类型提示
CompiledGraph = any  # 实际是 langgraph.graph.StateGraph
