"""
FinancePulse AI 分析服务
基于 LangGraph 的多智能体编排

启动方式:
    cd server
    pip install -r requirements.txt
    uvicorn main:app --reload --port 5000

API 文档:
    http://localhost:5000/docs
"""

import os
from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from graph.workflow import create_workflow, CompiledGraph
from graph.tradingagents_workflow import create_tradingagents_workflow
from graph.aihedgefund_workflow import create_aihedgefund_workflow
from graph.fusion_workflow import create_fusion_workflow
from config.leaders import LEADERS
from services.llm import LLMService
from services.data import DataService

load_dotenv()

# ========== 初始化 ==========

app = FastAPI(
    title="FinancePulse AI 服务",
    description="基于 LangGraph 的多智能体股票分析系统",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化服务
llm_service = LLMService()
data_service = DataService()

# 工作流缓存
workflows: dict[str, CompiledGraph] = {}

def get_workflow(mode: str, llm_service: LLMService) -> CompiledGraph:
    """根据mode获取对应的工作流"""
    if mode not in workflows:
        if mode == "tradingagents":
            workflow = create_tradingagents_workflow(llm_service)
        elif mode == "aihedgefund":
            workflow = create_aihedgefund_workflow(llm_service)
        else:  # fusion
            workflow = create_fusion_workflow(llm_service)
        workflows[mode] = workflow.compile()
        print(f"[FinancePulse] 已加载 {mode} 工作流")
    return workflows[mode]

print("[FinancePulse] LangGraph 服务已初始化")


# ========== 请求/响应模型 ==========

class AnalysisRequest(BaseModel):
    code: str = Field(..., description="股票代码，如 600519")
    name: str = Field(default="", description="股票名称")
    include_history: bool = Field(default=False, description="是否包含历史分析")
    max_iterations: int = Field(default=3, ge=1, le=5, description="最大迭代次数")
    # 分析模式
    mode: Literal["tradingagents", "aihedgefund", "fusion"] = Field(
        default="fusion",
        description="分析模式: tradingagents(8阶段), aihedgefund(4层), fusion(Leader决策)"
    )
    # Leader选择（fusion/aihedgefund模式需要）
    leader_id: Optional[str] = Field(
        default=None,
        description="投资大师ID，如 warren_buffett, ben_graham 等"
    )
    # 风险偏好
    risk_level: Optional[Literal["conservative", "moderate", "aggressive"]] = Field(
        default=None,
        description="风险偏好: conservative(保守), moderate(中性), aggressive(激进)"
    )
    # 收敛参数
    convergence_gap: Optional[float] = Field(
        default=15.0,
        ge=5.0,
        le=30.0,
        description="置信度差距阈值，低于此值认为收敛"
    )
    early_stop_gap: Optional[float] = Field(
        default=10.0,
        ge=5.0,
        le=20.0,
        description="提前停止阈值，高置信度时提前停止"
    )


class SignalModel(BaseModel):
    agent: str
    agent_id: str
    signal: Literal["bullish", "bearish", "neutral"]
    confidence: int
    reasoning: str


class RecommendationModel(BaseModel):
    action: Literal["buy", "hold", "sell", "watch"]
    confidence: int
    entry_price: Optional[float] = None
    exit_price: Optional[float] = None
    stop_loss: Optional[float] = None
    position_size: Optional[float] = None
    timeframe: str
    risks: list[str]


class AnalysisResponse(BaseModel):
    code: str
    name: str
    timestamp: int
    duration_ms: int
    iterations: int
    signals: list[SignalModel]
    debate_result: Optional[dict] = None
    summary: str
    model: str
    total_tokens: int
    recommendation: RecommendationModel
    error: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    llm_configured: bool
    llm_provider: str


class QuoteResponse(BaseModel):
    code: str
    name: str
    price: float
    change: float
    change_percent: float
    volume: float
    amount: float
    high: float
    low: float
    open: float
    prev_close: float
    pe: Optional[float] = None
    pb: Optional[float] = None
    market_cap: Optional[str] = None


# ========== API 端点 ==========

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """健康检查"""
    return HealthResponse(
        status="healthy",
        llm_configured=llm_service.is_configured(),
        llm_provider=llm_service.get_provider(),
    )


@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_stock(request: AnalysisRequest):
    """
    分析股票

    根据 mode 参数选择不同的工作流:
    - tradingagents: 8阶段工作流 (市场/社交/新闻/基本面分析 + 多空辩论 + 风险辩论 + 组合管理)
    - aihedgefund: 4层架构 (数据收集 + 动态分析师选择 + 风险评估 + 领袖决策)
    - fusion: 5层架构 (数据收集 + 5位固定分析师 + 多空辩论 + 简化风险评估 + 领袖决策)

    参数:
    - mode: 分析模式
    - leader_id: 投资大师ID (fusion/aihedgefund模式必需)
    - risk_level: 风险偏好 (tradingagents模式使用)
    - convergence_gap: 置信度收敛阈值
    - early_stop_gap: 提前停止阈值
    """
    start_time = datetime.now()

    try:
        # 获取股票数据
        stock_data = await data_service.get_stock_data(request.code)
        name = request.name or stock_data.get("name", f"股票{request.code}")

        # 构建初始状态 - 包含所有工作流需要的字段
        initial_state = {
            "code": request.code,
            "name": name,
            "stock_data": stock_data,
            "iteration": 0,
            "max_iterations": request.max_iterations,
            "analyst_signals": [],
            "bullish_signal": None,
            "bearish_signal": None,
            "debate_history": [],
            "final_summary": "",
            "recommendation": None,
            "total_tokens": 0,
            "error": None,
            # 新增参数
            "mode": request.mode,
            "leader_id": request.leader_id,
            "risk_level": request.risk_level,
            "convergence_gap": request.convergence_gap,
            "early_stop_gap": request.early_stop_gap,
        }

        # 根据 mode 获取并运行对应工作流
        mode = request.mode
        print(f"[analyze] 使用 {mode} 工作流分析 {request.code}...")

        workflow = get_workflow(mode, llm_service)
        result = workflow.invoke(initial_state)

        duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)

        # 处理响应
        signals = result.get("analyst_signals", [])
        if not isinstance(signals, list):
            signals = []

        debate_result = result.get("debate_history")
        if isinstance(debate_result, list) and len(debate_result) > 0:
            debate_result = debate_result[-1]
        elif debate_result is None:
            debate_result = None

        # 处理 recommendation
        recommendation_data = result.get("recommendation", {})
        if not recommendation_data:
            recommendation_data = {
                "action": "watch",
                "confidence": 0,
                "timeframe": "unknown",
                "risks": [result.get("error", "分析失败")]
            }

        return AnalysisResponse(
            code=request.code,
            name=name,
            timestamp=int(datetime.now().timestamp() * 1000),
            duration_ms=duration_ms,
            iterations=result.get("iteration", 0),
            signals=[SignalModel(**sig) for sig in signals],
            debate_result=debate_result,
            summary=result.get("final_summary", ""),
            model=llm_service.get_provider(),
            total_tokens=result.get("total_tokens", 0),
            recommendation=RecommendationModel(**recommendation_data),
            error=result.get("error"),
        )

    except Exception as e:
        duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/leaders")
async def get_leaders():
    """
    获取所有投资大师列表

    返回格式:
    {
        "leaders": [
            {
                "id": "warren_buffett",
                "name": "沃伦·巴菲特",
                "name_en": "Warren Buffett",
                "style": "价值投资",
                "avatar": "🎯",
                "description": "奥马哈先知，价值投资教父"
            },
            ...
        ]
    }
    """
    return {
        "leaders": [
            {
                "id": leader["id"],
                "name": leader["name"],
                "name_en": leader.get("name_en", leader["name"]),
                "style": leader["style"],
                "avatar": leader.get("avatar", "👤"),
                "description": leader["description"],
            }
            for leader in LEADERS
        ]
    }


@app.get("/quote/{code}", response_model=QuoteResponse)
async def get_quote(code: str):
    """获取股票行情"""
    try:
        data = await data_service.get_stock_data(code)
        return QuoteResponse(**data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/llm/test")
async def test_llm():
    """测试 LLM 连接"""
    if not llm_service.is_configured():
        raise HTTPException(status_code=400, detail="LLM 未配置，请设置 API Key")
    
    try:
        result = await llm_service.complete([
            {"role": "user", "content": "请回复'连接成功'"}
        ])
        return {
            "success": True,
            "content": result["content"],
            "model": result.get("model", "unknown"),
            "tokens": result.get("tokens", 0),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========== 启动 ==========

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
