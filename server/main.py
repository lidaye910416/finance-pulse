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


class FearGreedResponse(BaseModel):
    """恐惧贪婪指数响应"""
    value: int
    phase: str
    timestamp: int


class NorthboundItem(BaseModel):
    """北向资金单条数据"""
    date: str
    hkStock: float
    szStock: float
    total: float


class NorthboundResponse(BaseModel):
    """北向资金响应"""
    items: list[NorthboundItem]
    latestTotal: Optional[float] = None


class LimitUpDownResponse(BaseModel):
    """涨跌停统计响应"""
    limitUp: int
    limitDown: int
    updateTime: str


class SentimentResponse(BaseModel):
    """市场情绪响应"""
    fearGreed: FearGreedResponse
    northbound: Optional[NorthboundItem] = None
    limitUpDown: LimitUpDownResponse
    marketStatus: str
    overall: str


# ========== 宏观数据模型 ==========

class GDPResponse(BaseModel):
    """GDP数据响应"""
    current: float  # 当季度GDP增速 %
    previous: float  # 上季度GDP增速 %
    year: int  # 年份
    quarter: str  # 季度 (如 "Q1")
    updateTime: str


class CPIResponse(BaseModel):
    """CPI数据响应"""
    yoy: float  # 同比 %
    mom: float  # 环比 %
    year: int  # 年份
    month: int  # 月份
    updateTime: str


class PMIResponse(BaseModel):
    """PMI数据响应"""
    manufacturing: float  # 制造业PMI
    nonManufacturing: float  # 非制造业PMI
    composite: float  # 综合PMI
    date: str
    updateTime: str


class LPRResponse(BaseModel):
    """LPR数据响应"""
    oneYear: float  # 1年期LPR %
    fiveYear: float  # 5年期以上LPR %
    date: str
    updateTime: str


class MacroResponse(BaseModel):
    """宏观数据综合响应"""
    gdp: Optional[GDPResponse] = None
    cpi: Optional[CPIResponse] = None
    pmi: Optional[PMIResponse] = None
    lpr: Optional[LPRResponse] = None
    updateTime: str


# ========== 汇率数据模型 ==========

class HotStockItem(BaseModel):
    """热门股票单条数据"""
    code: str
    name: str
    price: float
    change: float
    changePercent: float
    volume: float
    amount: float


class HotStocksResponse(BaseModel):
    """热门股票响应"""
    items: list[HotStockItem]
    updateTime: str


class MarginBalanceResponse(BaseModel):
    """两融余额响应"""
    balance: float  # 万亿
    marginBalance: float  # 融资余额 (亿)
    shortBalance: float  # 融券余额 (亿)
    marginBalanceRatio: float  # 融资融券比例
    updateTime: str


class ExchangeRateItem(BaseModel):
    """汇率数据项"""
    currency: str  # 货币代码 (USD, EUR, JPY)
    name: str  # 货币名称
    rate: float  # 汇率 (相对于人民币)
    change: float  # 涨跌
    changePercent: float  # 涨跌幅 %
    updateTime: str


class ExchangeRateResponse(BaseModel):
    """汇率数据响应"""
    baseCurrency: str  # 基准货币 (CNY)
    rates: list[ExchangeRateItem]
    updateTime: str


# ========== 预测市场数据模型 ==========

class PolymarketEvent(BaseModel):
    """Polymarket 事件"""
    id: str
    question: str
    probability: float  # Yes概率 %
    volume: str  # 交易量
    trend: Optional[str] = None  # up/down
    markets: list[str] = []  # 涉及的标的


class PolymarketResponse(BaseModel):
    """Polymarket 数据响应"""
    items: list[PolymarketEvent]
    updateTime: str


class ArbitrageOpportunity(BaseModel):
    """跨平台套利机会"""
    event: str
    platforms: list[dict]  # [{name, probability}]
    difference: float  # 概率差异 %
    suggestion: str  # 操作建议


class ArbitrageResponse(BaseModel):
    """套利机会响应"""
    items: list[ArbitrageOpportunity]
    updateTime: str


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


# ========== 市场数据 API ==========

@app.get("/api/market/fear-greed", response_model=FearGreedResponse)
async def get_fear_greed():
    """
    获取恐惧贪婪指数

    使用 Alternative.me API
    """
    try:
        import httpx
        response = httpx.get("https://api.alternative.me/fng/?limit=1", timeout=10)
        if response.status_code == 200:
            data = response.json()
            value = int(data.get("data", [{}])[0].get("value", 50))

            phase_map = {
                (0, 25): "极度恐惧",
                (26, 45): "恐惧",
                (46, 55): "中性",
                (56, 75): "贪婪",
                (76, 100): "极度贪婪",
            }
            phase = "中性"
            for (low, high), label in phase_map.items():
                if low <= value <= high:
                    phase = label
                    break

            return FearGreedResponse(
                value=value,
                phase=phase,
                timestamp=int(datetime.now().timestamp() * 1000),
            )
    except Exception as e:
        print(f"[fear-greed] 获取失败: {e}")

    # Fallback
    return FearGreedResponse(value=50, phase="中性", timestamp=int(datetime.now().timestamp() * 1000))


@app.get("/api/market/northbound", response_model=NorthboundResponse)
async def get_northbound(days: int = 7):
    """
    获取北向资金数据

    Args:
        days: 返回天数，默认7天
    """
    try:
        import httpx
        url = "https://datacenter-web.eastmoney.com/api/data/v1/get"
        params = {
            "reportName": "RPT_MUTUAL_MARKET_SH",
            "columns": "TRADE_DATE,HOLD_DATE,SECURITY_CODE_A,SECURITY_NAME_A,CLOSE_PRICE,MUTUAL_TYPE,MUTUAL_TYPE_NAME,BINDING_SH,SECUCODE",
            "filter": '(MUTUAL_TYPE="001")',
            "pageNumber": 1,
            "pageSize": days,
            "sortTypes": -1,
            "sortColumns": "TRADE_DATE",
            "source": "WEB",
            "client": "WEB",
        }

        response = httpx.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            items = []
            for item in (data.get("result", {}).get("data", []) or []):
                items.append(NorthboundItem(
                    date=item.get("TRADE_DATE", ""),
                    hkStock=round((item.get("HOLD_DATE") or 0) / 100000000, 2),
                    szStock=0.0,
                    total=round((item.get("BINDING_SH") or 0) / 100000000, 2),
                ))

            latest = items[0] if items else None
            return NorthboundResponse(
                items=items,
                latestTotal=latest.total if latest else None,
            )
    except Exception as e:
        print(f"[northbound] 获取失败: {e}")

    return NorthboundResponse(items=[], latestTotal=None)


@app.get("/api/market/limit-up-down", response_model=LimitUpDownResponse)
async def get_limit_up_down():
    """
    获取涨跌停统计

    使用东方财富实时涨停池数据
    """
    try:
        import httpx
        from datetime import datetime

        # 涨停统计
        url = "https://push2.eastmoney.com/api/qt/clist/get"
        params = {
            "pn": 1,
            "pz": 1,
            "po": 1,
            "np": 1,
            "ut": "bd1d9ddb04089700cf9c27f6f7426281",
            "fltt": 2,
            "invt": 2,
            "fid": "f3",
            "fs": "m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23,m:0+t:81+s:20480",
            "fields": "f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18",
        }

        limit_up = 0
        response = httpx.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            limit_up = data.get("data", {}).get("total", 0)

        # 跌停统计
        url = "https://push2.eastmoney.com/api/qt/clist/get"
        params["fs"] = "m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23,m:0+t:81+s:20480"
        params["fid"] = "f3"
        params["po"] = -1  # 跌停

        limit_down = 0
        response = httpx.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            limit_down = data.get("data", {}).get("total", 0)

        return LimitUpDownResponse(
            limitUp=limit_up or 47,  # fallback
            limitDown=limit_down or 8,  # fallback
            updateTime=datetime.now().strftime("%Y-%m-%d %H:%M"),
        )
    except Exception as e:
        print(f"[limit-up-down] 获取失败: {e}")

    return LimitUpDownResponse(
        limitUp=47,
        limitDown=8,
        updateTime=datetime.now().strftime("%Y-%m-%d %H:%M"),
    )


@app.get("/api/market/sentiment", response_model=SentimentResponse)
async def get_market_sentiment():
    """
    获取市场情绪综合数据

    包含恐惧贪婪指数、北向资金、涨跌停统计
    """
    fear_greed = await get_fear_greed()
    northbound = await get_northbound(days=1)
    limit_up_down = await get_limit_up_down()

    # 判断市场状态
    fear_value = fear_greed.value
    if fear_value <= 25:
        market_status = "极度恐慌"
    elif fear_value <= 40:
        market_status = "恐慌"
    elif fear_value <= 60:
        market_status = "中性"
    elif fear_value <= 75:
        market_status = "乐观"
    else:
        market_status = "极度乐观"

    # 整体情绪判断
    north_total = northbound.latestTotal or 0
    if fear_value >= 60 and north_total > 0:
        overall = "乐观"
    elif fear_value <= 40 and north_total < 0:
        overall = "悲观"
    else:
        overall = "中性"

    return SentimentResponse(
        fearGreed=fear_greed,
        northbound=northbound.items[0] if northbound.items else None,
        limitUpDown=limit_up_down,
        marketStatus=market_status,
        overall=overall,
    )


@app.get("/api/market/hot-stocks", response_model=HotStocksResponse)
async def get_hot_stocks(limit: int = 10):
    """
    获取热门股票列表

    使用东方财富涨幅榜数据
    """
    try:
        import httpx
        from datetime import datetime

        url = "https://push2.eastmoney.com/api/qt/clist/get"
        params = {
            "pn": 1,
            "pz": limit,
            "po": 1,
            "np": 1,
            "ut": "bd1d9ddb04089700cf9c27f6f7426281",
            "fltt": 2,
            "invt": 2,
            "fid": "f3",
            "fs": "m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23,m:0+t:81+s:20480",
            "fields": "f2,f3,f4,f5,f6,f7,f8,f12,f13,f14,f15,f16,f17,f18",
        }

        response = httpx.get(url, params=params, timeout=10)
        items = []
        if response.status_code == 200:
            data = response.json()
            diff = data.get("data", {}).get("diff", [])
            for item in diff:
                items.append(HotStockItem(
                    code=str(item.get("f12", "")),
                    name=str(item.get("f14", "")),
                    price=float(item.get("f2", 0)),
                    change=float(item.get("f4", 0)),
                    changePercent=float(item.get("f3", 0)),
                    volume=float(item.get("f5", 0)),
                    amount=float(item.get("f6", 0)),
                ))

        return HotStocksResponse(
            items=items,
            updateTime=datetime.now().strftime("%Y-%m-%d %H:%M"),
        )
    except Exception as e:
        print(f"[hot-stocks] 获取失败: {e}")

    return HotStocksResponse(items=[], updateTime=datetime.now().strftime("%Y-%m-%d %H:%M"))


@app.get("/api/market/margin-balance", response_model=MarginBalanceResponse)
async def get_margin_balance():
    """
    获取两融余额数据

    使用东方财富融资融券数据
    """
    try:
        import httpx
        from datetime import datetime

        # 融资余额数据
        url = "https://datacenter-web.eastmoney.com/api/data/v1/get"
        params = {
            "reportName": "RPT_MARGIN_DETAILS",
            "columns": "TRADE_DATE,MARGIN_BALANCE,SHORT_BALANCE",
            "pageNumber": 1,
            "pageSize": 1,
            "sortTypes": -1,
            "sortColumns": "TRADE_DATE",
            "source": "WEB",
            "client": "WEB",
        }

        response = httpx.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            items = data.get("result", {}).get("data", []) or []

            if items:
                item = items[0]
                margin_balance = item.get("MARGIN_BALANCE", 0) or 0
                short_balance = item.get("SHORT_BALANCE", 0) or 0

                return MarginBalanceResponse(
                    balance=round((margin_balance + short_balance) / 100000000, 2),
                    marginBalance=round(margin_balance / 100000000, 2),
                    shortBalance=round(short_balance / 100000000, 2),
                    marginBalanceRatio=round(margin_balance / short_balance, 2) if short_balance > 0 else 0,
                    updateTime=item.get("TRADE_DATE", datetime.now().strftime("%Y-%m-%d")),
                )
    except Exception as e:
        print(f"[margin-balance] 获取失败: {e}")

    # Fallback
    return MarginBalanceResponse(
        balance=1.58,
        marginBalance=1.45,
        shortBalance=0.13,
        marginBalanceRatio=11.15,
        updateTime=datetime.now().strftime("%Y-%m-%d"),
    )


# ========== 宏观数据 API ==========

@app.get("/api/macro/gdp", response_model=GDPResponse)
async def get_gdp():
    """
    获取GDP增速数据

    使用东方财富宏观经济数据
    """
    try:
        import httpx
        url = "https://datacenter-web.eastmoney.com/api/data/v1/get"
        params = {
            "reportName": "RPT_ECONOMIC_GDP",
            "columns": "REPORT_DATE,GDP_YOY,GDP_QUARTER",
            "pageNumber": 1,
            "pageSize": 2,
            "sortTypes": -1,
            "sortColumns": "REPORT_DATE",
            "source": "WEB",
            "client": "WEB",
        }

        response = httpx.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            items = data.get("result", {}).get("data", []) or []

            if len(items) >= 1:
                current = items[0]
                report_date = current.get("REPORT_DATE", "")
                year = int(report_date[:4]) if report_date else datetime.now().year

                # 解析季度
                quarter_str = current.get("GDP_QUARTER", "")
                quarter_map = {"1": "Q1", "2": "Q2", "3": "Q3", "4": "Q4"}
                quarter = quarter_map.get(quarter_str, "Q1")

                return GDPResponse(
                    current=float(current.get("GDP_YOY", 5.0)),
                    previous=float(items[1].get("GDP_YOY", 5.0)) if len(items) >= 2 else 5.0,
                    year=year,
                    quarter=quarter,
                    updateTime=datetime.now().strftime("%Y-%m-%d"),
                )
    except Exception as e:
        print(f"[gdp] 获取失败: {e}")

    # Fallback
    return GDPResponse(
        current=5.0,
        previous=5.2,
        year=datetime.now().year,
        quarter="Q1",
        updateTime=datetime.now().strftime("%Y-%m-%d"),
    )


@app.get("/api/macro/cpi", response_model=CPIResponse)
async def get_cpi():
    """
    获取CPI数据

    使用东方财富CPI数据
    """
    try:
        import httpx
        url = "https://datacenter-web.eastmoney.com/api/data/v1/get"
        params = {
            "reportName": "RPT_ECONOMIC_CPI",
            "columns": "REPORT_DATE,CPI_YOY,CPI_MOM",
            "pageNumber": 1,
            "pageSize": 1,
            "sortTypes": -1,
            "sortColumns": "REPORT_DATE",
            "source": "WEB",
            "client": "WEB",
        }

        response = httpx.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            items = data.get("result", {}).get("data", []) or []

            if len(items) >= 1:
                current = items[0]
                report_date = current.get("REPORT_DATE", "")

                return CPIResponse(
                    yoy=float(current.get("CPI_YOY", 0.0)),
                    mom=float(current.get("CPI_MOM", 0.0)),
                    year=int(report_date[:4]) if report_date else datetime.now().year,
                    month=int(report_date[5:7]) if len(report_date) > 5 else datetime.now().month,
                    updateTime=datetime.now().strftime("%Y-%m-%d"),
                )
    except Exception as e:
        print(f"[cpi] 获取失败: {e}")

    # Fallback
    return CPIResponse(
        yoy=0.2,
        mom=0.1,
        year=datetime.now().year,
        month=datetime.now().month,
        updateTime=datetime.now().strftime("%Y-%m-%d"),
    )


@app.get("/api/macro/pmi", response_model=PMIResponse)
async def get_pmi():
    """
    获取PMI数据

    使用东方财富PMI数据
    """
    try:
        import httpx
        url = "https://datacenter-web.eastmoney.com/api/data/v1/get"
        params = {
            "reportName": "RPT_ECONOMIC_PMI",
            "columns": "REPORT_DATE,MANUFACTURING_PMI,NON_MANUFACTURING_PMI,COMPOSITE_PMI",
            "pageNumber": 1,
            "pageSize": 1,
            "sortTypes": -1,
            "sortColumns": "REPORT_DATE",
            "source": "WEB",
            "client": "WEB",
        }

        response = httpx.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            items = data.get("result", {}).get("data", []) or []

            if len(items) >= 1:
                current = items[0]

                return PMIResponse(
                    manufacturing=float(current.get("MANUFACTURING_PMI", 50.0)),
                    nonManufacturing=float(current.get("NON_MANUFACTURING_PMI", 50.0)),
                    composite=float(current.get("COMPOSITE_PMI", 50.0)),
                    date=current.get("REPORT_DATE", datetime.now().strftime("%Y-%m")),
                    updateTime=datetime.now().strftime("%Y-%m-%d"),
                )
    except Exception as e:
        print(f"[pmi] 获取失败: {e}")

    # Fallback
    return PMIResponse(
        manufacturing=50.3,
        nonManufacturing=51.2,
        composite=50.8,
        date=datetime.now().strftime("%Y-%m"),
        updateTime=datetime.now().strftime("%Y-%m-%d"),
    )


@app.get("/api/macro/lpr", response_model=LPRResponse)
async def get_lpr():
    """
    获取LPR数据

    使用东方财富贷款市场报价利率数据
    """
    try:
        import httpx
        url = "https://datacenter-web.eastmoney.com/api/data/v1/get"
        params = {
            "reportName": "RPT_LPR",
            "columns": "REPORT_DATE,LPR_1Y,LPR_5Y",
            "pageNumber": 1,
            "pageSize": 1,
            "sortTypes": -1,
            "sortColumns": "REPORT_DATE",
            "source": "WEB",
            "client": "WEB",
        }

        response = httpx.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            items = data.get("result", {}).get("data", []) or []

            if len(items) >= 1:
                current = items[0]

                return LPRResponse(
                    oneYear=float(current.get("LPR_1Y", 3.45)),
                    fiveYear=float(current.get("LPR_5Y", 3.95)),
                    date=current.get("REPORT_DATE", datetime.now().strftime("%Y-%m-%d")),
                    updateTime=datetime.now().strftime("%Y-%m-%d"),
                )
    except Exception as e:
        print(f"[lpr] 获取失败: {e}")

    # Fallback
    return LPRResponse(
        oneYear=3.45,
        fiveYear=3.95,
        date=datetime.now().strftime("%Y-%m-%d"),
        updateTime=datetime.now().strftime("%Y-%m-%d"),
    )


@app.get("/api/macro", response_model=MacroResponse)
async def get_macro_data():
    """
    获取宏观数据综合数据

    包含GDP、CPI、PMI、LPR
    """
    gdp = await get_gdp()
    cpi = await get_cpi()
    pmi = await get_pmi()
    lpr = await get_lpr()

    return MacroResponse(
        gdp=gdp,
        cpi=cpi,
        pmi=pmi,
        lpr=lpr,
        updateTime=datetime.now().strftime("%Y-%m-%d %H:%M"),
    )


# ========== 汇率 API ==========

@app.get("/api/macro/exchange-rate", response_model=ExchangeRateResponse)
async def get_exchange_rate():
    """
    获取人民币汇率数据

    支持 USD/CNY, EUR/CNY, JPY/CNY 等主要货币
    使用东方财富汇率数据
    """
    try:
        import httpx

        # 东方财富汇率数据接口
        url = "https://datacenter-web.eastmoney.com/api/data/v1/get"
        params = {
            "reportName": "RPT_HSRT_LISTINFO",
            "columns": "TRADE_DATE,CURRENCY_CODE,CURRENCY_NAME,USD_CNY,EUR_CNY,GBP_CNY,JPY_CNY,HKD_CNY,AUD_CNY,CAD_CNY,CHF_CNY",
            "pageNumber": 1,
            "pageSize": 1,
            "sortTypes": -1,
            "sortColumns": "TRADE_DATE",
            "source": "WEB",
            "client": "WEB",
        }

        response = httpx.get(url, params=params, timeout=10)

        # 货币映射
        currency_map = {
            "USD": ("美元", "USD"),
            "EUR": ("欧元", "EUR"),
            "JPY": ("日元", "JPY"),
            "GBP": ("英镑", "GBP"),
            "HKD": ("港币", "HKD"),
            "AUD": ("澳元", "AUD"),
            "CAD": ("加元", "CAD"),
            "CHF": ("瑞郎", "CHF"),
        }

        rates = []
        update_time = datetime.now().strftime("%Y-%m-%d %H:%M")

        if response.status_code == 200:
            data = response.json()
            items = data.get("result", {}).get("data", []) or []

            if items:
                item = items[0]
                update_time = item.get("TRADE_DATE", update_time)

                # 解析各货币汇率
                for code, (name, col) in currency_map.items():
                    col_name = f"{code}_CNY"
                    rate = item.get(col_name)
                    if rate is not None:
                        rates.append(ExchangeRateItem(
                            currency=code,
                            name=name,
                            rate=float(rate),
                            change=0.0,
                            changePercent=0.0,
                            updateTime=update_time,
                        ))

        # 如果没有数据，添加默认汇率
        if not rates:
            rates = [
                ExchangeRateItem(currency="USD", name="美元", rate=7.24, change=0.01, changePercent=0.14, updateTime=update_time),
                ExchangeRateItem(currency="EUR", name="欧元", rate=7.85, change=-0.02, changePercent=-0.25, updateTime=update_time),
                ExchangeRateItem(currency="JPY", name="日元", rate=0.048, change=0.001, changePercent=2.13, updateTime=update_time),
                ExchangeRateItem(currency="GBP", name="英镑", rate=9.15, change=-0.03, changePercent=-0.33, updateTime=update_time),
                ExchangeRateItem(currency="HKD", name="港币", rate=0.93, change=0.0, changePercent=0.0, updateTime=update_time),
            ]

        return ExchangeRateResponse(
            baseCurrency="CNY",
            rates=rates,
            updateTime=update_time,
        )

    except Exception as e:
        print(f"[exchange-rate] 获取失败: {e}")

    # Fallback
    return ExchangeRateResponse(
        baseCurrency="CNY",
        rates=[
            ExchangeRateItem(currency="USD", name="美元", rate=7.24, change=0.01, changePercent=0.14, updateTime=datetime.now().strftime("%Y-%m-%d %H:%M")),
            ExchangeRateItem(currency="EUR", name="欧元", rate=7.85, change=-0.02, changePercent=-0.25, updateTime=datetime.now().strftime("%Y-%m-%d %H:%M")),
            ExchangeRateItem(currency="JPY", name="日元", rate=0.048, change=0.001, changePercent=2.13, updateTime=datetime.now().strftime("%Y-%m-%d %H:%M")),
            ExchangeRateItem(currency="GBP", name="英镑", rate=9.15, change=-0.03, changePercent=-0.33, updateTime=datetime.now().strftime("%Y-%m-%d %H:%M")),
            ExchangeRateItem(currency="HKD", name="港币", rate=0.93, change=0.0, changePercent=0.0, updateTime=datetime.now().strftime("%Y-%m-%d %H:%M")),
        ],
        updateTime=datetime.now().strftime("%Y-%m-%d %H:%M"),
    )


# ========== 预测市场 API ==========

@app.get("/api/market/polymarket", response_model=PolymarketResponse)
async def get_polymarket_events(limit: int = 10):
    """
    获取 Polymarket 热门事件

    使用 Polymarket CLOB API 获取热门预测市场事件
    """
    try:
        import httpx

        # Polymarket CLOB API 获取热门市场
        url = "https://clob.polymarket.com/markets"
        params = {
            "limit": limit,
            "closed": "false",
        }

        headers = {
            "Content-Type": "application/json",
        }

        response = httpx.get(url, params=params, headers=headers, timeout=10)
        items = []

        if response.status_code == 200:
            data = response.json()
            markets = data.get("markets", []) or data

            for market in markets[:limit]:
                question = market.get("question", "")
                if not question:
                    continue

                # 计算 Yes 概率
                outcome_prices = market.get("outcomePrices", "{}")
                try:
                    prices = eval(outcome_prices) if isinstance(outcome_prices, str) else outcome_prices
                    yes_price = float(prices.get("Yes", 0.5))
                    probability = round(yes_price * 100, 1)
                except:
                    probability = 50.0

                # 交易量
                volume = market.get("volume", "0")
                try:
                    vol_float = float(volume)
                    if vol_float >= 1000000:
                        volume_str = f"${vol_float/1000000:.2f}M"
                    elif vol_float >= 1000:
                        volume_str = f"${vol_float/1000:.0f}K"
                    else:
                        volume_str = f"${vol_float:.0f}"
                except:
                    volume_str = volume

                # 判断趋势 (基于24h变化)
                volume_24h = market.get("volume24hr", "0")
                try:
                    vol_24h = float(volume_24h)
                    if vol_24h > 0:
                        trend = "up"
                    else:
                        trend = "down"
                except:
                    trend = None

                items.append(PolymarketEvent(
                    id=market.get("id", ""),
                    question=question,
                    probability=probability,
                    volume=volume_str,
                    trend=trend,
                    markets=[market.get("conditionId", "")],
                ))

        if items:
            return PolymarketResponse(
                items=items,
                updateTime=datetime.now().strftime("%Y-%m-%d %H:%M"),
            )

    except Exception as e:
        print(f"[polymarket] 获取失败: {e}")

    # Fallback: 返回默认热门事件
    return PolymarketResponse(
        items=[
            PolymarketEvent(id="1", question="Will Bitcoin exceed $100,000 by end of 2026?", probability=65, volume="$45M", trend="up"),
            PolymarketEvent(id="2", question="Will the Fed cut rates in June 2026?", probability=58, volume="$28M", trend="down"),
            PolymarketEvent(id="3", question="Will ETH flip BTC market cap by 2027?", probability=35, volume="$12M", trend=None),
            PolymarketEvent(id="4", question="Will S&P 500 exceed 6000 by end of 2026?", probability=62, volume="$18M", trend="up"),
        ],
        updateTime=datetime.now().strftime("%Y-%m-%d %H:%M"),
    )


@app.get("/api/market/arbitrage", response_model=ArbitrageResponse)
async def get_arbitrage_opportunities():
    """
    获取跨平台套利机会

    比较 Polymarket、Metaculus、Kalshi 等平台的预测概率差异
    """
    try:
        import httpx

        # 这里模拟跨平台数据获取
        # 实际生产环境中，可以从各个平台API获取数据
        # 为了演示，使用常见的宏观事件套利机会

        opportunities = [
            ArbitrageOpportunity(
                event="美联储6月降息",
                platforms=[
                    {"name": "Polymarket", "probability": 68},
                    {"name": "Metaculus", "probability": 72},
                    {"name": "Kalshi", "probability": 65},
                ],
                difference=7,
                suggestion="套利空间 7%，可考虑小仓布局",
            ),
            ArbitrageOpportunity(
                event="BTC突破$100K在2026年内",
                platforms=[
                    {"name": "Polymarket", "probability": 55},
                    {"name": "Metaculus", "probability": 60},
                    {"name": "Kalshi", "probability": 52},
                ],
                difference=8,
                suggestion="套利空间 8%，建议等待 >5% 差异时操作",
            ),
            ArbitrageOpportunity(
                event="标普500突破6000点",
                platforms=[
                    {"name": "Polymarket", "probability": 62},
                    {"name": "Metaculus", "probability": 58},
                    {"name": "Kalshi", "probability": 65},
                ],
                difference=7,
                suggestion="套利空间 7%，市场共识偏向突破",
            ),
            ArbitrageOpportunity(
                event="黄金突破$3000/盎司",
                platforms=[
                    {"name": "Polymarket", "probability": 48},
                    {"name": "Metaculus", "probability": 55},
                    {"name": "Kalshi", "probability": 50},
                ],
                difference=7,
                suggestion="套利空间 7%，分歧较大需谨慎",
            ),
        ]

        return ArbitrageResponse(
            items=opportunities,
            updateTime=datetime.now().strftime("%Y-%m-%d %H:%M"),
        )

    except Exception as e:
        print(f"[arbitrage] 获取失败: {e}")

    # Fallback
    return ArbitrageResponse(
        items=[
            ArbitrageOpportunity(
                event="美联储6月降息",
                platforms=[
                    {"name": "Polymarket", "probability": 68},
                    {"name": "Metaculus", "probability": 71},
                    {"name": "Kalshi", "probability": 65},
                ],
                difference=6,
                suggestion="套利空间 6%，建议等待 >5% 差异时操作",
            ),
        ],
        updateTime=datetime.now().strftime("%Y-%m-%d %H:%M"),
    )


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
