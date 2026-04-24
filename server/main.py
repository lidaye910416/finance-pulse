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
from typing import Literal
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from graph.workflow import create_workflow, CompiledGraph
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

# 创建 LangGraph 工作流
workflow = create_workflow(llm_service)
graph: CompiledGraph = workflow.compile()

print("[FinancePulse] LangGraph 工作流已初始化")


# ========== 请求/响应模型 ==========

class AnalysisRequest(BaseModel):
    code: str = Field(..., description="股票代码，如 600519")
    name: str = Field(default="", description="股票名称")
    include_history: bool = Field(default=False, description="是否包含历史分析")
    max_iterations: int = Field(default=3, ge=1, le=5, description="最大迭代次数")


class SignalModel(BaseModel):
    agent: str
    agent_id: str
    signal: Literal["bullish", "bearish", "neutral"]
    confidence: int
    reasoning: str


class RecommendationModel(BaseModel):
    action: Literal["buy", "hold", "sell", "watch"]
    confidence: int
    entry_price: float | None = None
    exit_price: float | None = None
    stop_loss: float | None = None
    position_size: float | None = None
    timeframe: str
    risks: list[str]


class AnalysisResponse(BaseModel):
    code: str
    name: str
    timestamp: int
    duration_ms: int
    iterations: int
    signals: list[SignalModel]
    debate_result: dict | None = None
    summary: str
    model: str
    total_tokens: int
    recommendation: RecommendationModel
    error: str | None = None


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
    pe: float | None = None
    pb: float | None = None
    market_cap: str | None = None


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
    
    基于 LangGraph 多智能体工作流:
    1. 数据收集
    2. 并行 Agent 分析
    3. 多空辩论 (循环直到收敛或达到最大迭代)
    4. 综合决策
    """
    start_time = datetime.now()
    
    try:
        # 获取股票数据
        stock_data = await data_service.get_stock_data(request.code)
        name = request.name or stock_data.get("name", f"股票{request.code}")
        
        # 构建初始状态
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
        }
        
        # 运行 LangGraph 工作流
        result = graph.invoke(initial_state)
        
        duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        
        return AnalysisResponse(
            code=request.code,
            name=name,
            timestamp=int(datetime.now().timestamp() * 1000),
            duration_ms=duration_ms,
            iterations=result.get("iteration", 0),
            signals=[
                SignalModel(**sig) for sig in result.get("analyst_signals", [])
            ],
            debate_result=result.get("debate_history")[-1] if result.get("debate_history") else None,
            summary=result.get("final_summary", ""),
            model=llm_service.get_provider(),
            total_tokens=result.get("total_tokens", 0),
            recommendation=RecommendationModel(**result.get("recommendation", {})),
            error=result.get("error"),
        )
        
    except Exception as e:
        duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        raise HTTPException(status_code=500, detail=str(e))


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
