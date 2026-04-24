"""
LangGraph 工作流测试脚本

验证多智能体辩论循环是否正常工作
"""

import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

from graph.workflow import create_workflow
from services.llm import LLMService


async def test_workflow():
    """测试工作流"""
    print("=" * 60)
    print("LangGraph 多智能体工作流测试")
    print("=" * 60)
    
    # 初始化 LLM
    llm_service = LLMService()
    
    if not llm_service.is_configured():
        print("\n⚠️ 警告: LLM 未配置，将使用模拟数据")
        print("请设置 .env 文件中的 LLM_API_KEY")
        print("或设置 USE_MOCK_DATA=true 使用模拟模式")
    
    # 创建工作流
    workflow = create_workflow(llm_service)
    graph = workflow.compile()
    
    print(f"\n✅ 工作流编译成功")
    print(f"   Provider: {llm_service.get_provider()}")
    print(f"   Model: {llm_service.model}")
    
    # 测试状态
    initial_state = {
        "code": "600519",
        "name": "贵州茅台",
        "stock_data": {},
        "iteration": 0,
        "max_iterations": 3,
        "analyst_signals": [],
        "bullish_signal": None,
        "bearish_signal": None,
        "debate_history": [],
        "final_summary": "",
        "recommendation": None,
        "total_tokens": 0,
        "error": None,
    }
    
    print("\n" + "=" * 60)
    print("开始执行工作流...")
    print("=" * 60)
    
    # 运行工作流
    try:
        result = await asyncio.wait_for(
            graph.ainvoke(initial_state),
            timeout=120.0
        )
        
        print("\n" + "=" * 60)
        print("工作流执行完成!")
        print("=" * 60)
        
        print(f"\n📊 执行统计:")
        print(f"   总迭代次数: {result.get('iteration', 0)}")
        print(f"   辩论轮数: {len(result.get('debate_history', []))}")
        print(f"   分析师数量: {len(result.get('analyst_signals', []))}")
        print(f"   总Token消耗: {result.get('total_tokens', 0)}")
        
        # 显示分析师信号
        print(f"\n📈 分析师信号:")
        for signal in result.get('analyst_signals', []):
            emoji = "🟢" if signal.get('signal') == 'bullish' else ("🔴" if signal.get('signal') == 'bearish' else "⚪")
            print(f"   {emoji} {signal.get('agent')}: {signal.get('signal')} ({signal.get('confidence')}%)")
        
        # 显示辩论结果
        debate_history = result.get('debate_history', [])
        if debate_history:
            last_debate = debate_history[-1]
            print(f"\n🔄 辩论结果 (第{last_debate.get('round')}轮):")
            print(f"   多头: {last_debate['bullish'].get('confidence', 0)}%")
            print(f"   空头: {last_debate['bearish'].get('confidence', 0)}%")
            print(f"   收敛: {'是 ✅' if last_debate.get('consensus_reached') else '否'}")
        
        # 显示最终建议
        recommendation = result.get('recommendation')
        if recommendation:
            print(f"\n💡 投资建议:")
            print(f"   操作: {recommendation.get('action', 'N/A').upper()}")
            print(f"   置信度: {recommendation.get('confidence', 0)}%")
            if recommendation.get('entry_price'):
                print(f"   买入价: ¥{recommendation['entry_price']}")
            if recommendation.get('exit_price'):
                print(f"   目标价: ¥{recommendation['exit_price']}")
            if recommendation.get('stop_loss'):
                print(f"   止损价: ¥{recommendation['stop_loss']}")
            print(f"   仓位: {recommendation.get('position_size', 0)}%")
            print(f"   周期: {recommendation.get('timeframe', 'N/A')}")
        
        # 显示综合报告
        if result.get('final_summary'):
            print(f"\n📝 综合报告:")
            print(f"   {result['final_summary'][:200]}...")
        
        return True
        
    except asyncio.TimeoutError:
        print("\n❌ 工作流执行超时 (120秒)")
        return False
    except Exception as e:
        print(f"\n❌ 工作流执行失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_workflow())
    exit(0 if success else 1)
