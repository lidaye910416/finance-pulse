"""
数据服务

提供股票数据获取功能，支持：
- AKShare 免费数据
- 模拟数据（当 AKShare 不可用时）

US-014: 实现完整的数据服务层
- get_stock_data(code): 获取行情
- get_financial_metrics(code, period, limit): 获取财务指标
- search_line_items(code, items, limit): 获取财务明细
- get_market_cap(code, date): 获取市值
- get_price_history(code, days): 获取历史价格
"""

import os
import random
from datetime import datetime, timedelta
from typing import Optional

import httpx
import akshare as ak
import pandas as pd


class DataService:
    """数据服务类

    提供股票数据获取功能，基于 AKShare 实现。
    """

    # AKShare API 基础 URL (使用他们的测试接口)
    AKSHARE_BASE_URL = "https://akshare.akfamily.cn"

    def __init__(self):
        self.use_mock = os.getenv("USE_MOCK_DATA", "false").lower() == "true"
        print(f"[DataService] 初始化完成, use_mock={self.use_mock}")

    # ========== 行情数据 ==========

    def get_stock_data_sync(self, code: str) -> dict:
        """同步获取股票数据"""
        # 判断股票市场
        if code.startswith("6"):
            symbol = f"sh{code}"
        elif code.startswith(("0", "3")):
            symbol = f"sz{code}"
        else:
            symbol = code

        # 模拟数据（当 use_mock=True 或 API 失败时）
        if self.use_mock:
            return self._get_mock_data(code)

        try:
            return self._fetch_from_akshare(symbol, code)
        except Exception as e:
            print(f"[DataService] AKShare 获取失败，使用模拟数据: {e}")
            return self._get_mock_data(code)

    async def get_stock_data(self, code: str) -> dict:
        """异步获取股票数据"""
        # 直接调用同步版本（简单实现）
        return self.get_stock_data_sync(code)

    def _fetch_from_akshare(self, symbol: str, code: str) -> dict:
        """从 AKShare 获取数据"""
        # 使用 AKShare 的东财接口
        url = f"https://push2.eastmoney.com/api/qt/stock/get"
        params = {
            "secid": f"1.{code}" if code.startswith("6") else f"0.{code}",
            "fields": "f43,f44,f45,f46,f47,f48,f57,f58,f60,f81,f107,f116,f117,f152",
        }

        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        }

        response = httpx.get(url, params=params, headers=headers, timeout=10)
        data = response.json()

        if data.get("data"):
            d = data["data"]
            change = (float(d.get("f43", 0)) / 100) if d.get("f43") else 0
            prev_close = float(d.get("f60", 0)) / 100 if d.get("f60") else 0
            change_percent = (change / prev_close * 100) if prev_close else 0

            return {
                "code": code,
                "name": d.get("f58", f"股票{code}"),
                "price": float(d.get("f43", 0)) / 100 if d.get("f43") else 0,
                "change": change,
                "change_percent": change_percent,
                "open": float(d.get("f81", 0)) / 100 if d.get("f81") else 0,
                "high": float(d.get("f44", 0)) / 100 if d.get("f44") else 0,
                "low": float(d.get("f45", 0)) / 100 if d.get("f45") else 0,
                "volume": float(d.get("f47", 0)) if d.get("f47") else 0,
                "amount": float(d.get("f48", 0)) if d.get("f48") else 0,
                "prev_close": prev_close,
                "pe": d.get("f162") / 100 if d.get("f162") else None,
                "pb": d.get("f167") / 100 if d.get("f167") else None,
                "market_cap": None,
            }

        raise ValueError(f"未找到股票 {code}")

    def _get_mock_data(self, code: str) -> dict:
        """获取模拟数据"""
        mock_stocks = {
            "600519": {
                "code": "600519",
                "name": "贵州茅台",
                "price": 1688.0,
                "change": -20.16,
                "change_percent": -1.18,
                "open": 1710.0,
                "high": 1712.0,
                "low": 1675.0,
                "volume": 235678900,
                "amount": 3978567890,
                "prev_close": 1708.16,
                "pe": 28.5,
                "pb": 11.2,
                "market_cap": "2.12万亿",
            },
            "000858": {
                "code": "000858",
                "name": "五粮液",
                "price": 145.6,
                "change": -1.31,
                "change_percent": -0.89,
                "open": 147.0,
                "high": 147.5,
                "low": 144.2,
                "volume": 567890100,
                "amount": 826789012,
                "prev_close": 146.91,
                "pe": 22.3,
                "pb": 5.8,
                "market_cap": "5658亿",
            },
            "300750": {
                "code": "300750",
                "name": "宁德时代",
                "price": 186.5,
                "change": 4.2,
                "change_percent": 2.31,
                "open": 183.0,
                "high": 188.0,
                "low": 182.3,
                "volume": 1234567800,
                "amount": 2289012345,
                "prev_close": 182.3,
                "pe": 35.2,
                "pb": 8.5,
                "market_cap": "8215亿",
            },
        }

        if code in mock_stocks:
            return mock_stocks[code]

        # 生成随机数据
        price = random.uniform(10, 200)
        change_pct = random.uniform(-5, 5)

        return {
            "code": code,
            "name": f"股票{code}",
            "price": round(price, 2),
            "change": round(price * change_pct / 100, 2),
            "change_percent": round(change_pct, 2),
            "open": round(price * 0.99, 2),
            "high": round(price * 1.02, 2),
            "low": round(price * 0.98, 2),
            "volume": random.randint(1000000, 100000000),
            "amount": random.randint(100000000, 10000000000),
            "prev_close": round(price * 0.995, 2),
            "pe": round(random.uniform(10, 50), 1),
            "pb": round(random.uniform(1, 10), 2),
            "market_cap": f"{random.randint(50, 5000)}亿",
        }

    # ========== 历史价格 ==========

    def get_price_history(self, code: str, days: int = 60) -> list[dict]:
        """获取历史价格

        Args:
            code: 股票代码，如 "600519"
            days: 历史天数，默认60天

        Returns:
            价格列表，每项包含 date, open, high, low, close, volume
        """
        if self.use_mock:
            return self._get_mock_price_history(code, days)

        try:
            return self._fetch_price_history_akshare(code, days)
        except Exception as e:
            print(f"[DataService] 获取历史价格失败: {e}")
            return self._get_mock_price_history(code, days)

    def _fetch_price_history_akshare(self, code: str, days: int) -> list[dict]:
        """从 AKShare 获取历史价格"""
        end_date = datetime.now().strftime("%Y%m%d")
        start_date = (datetime.now() - timedelta(days=days + 30)).strftime("%Y%m%d")

        # 判断市场
        if code.startswith("6"):
            symbol = f"sh{code}"
        else:
            symbol = f"sz{code}"

        # 获取日线数据
        df = ak.stock_zh_a_hist(
            symbol=code,
            period="daily",
            start_date=start_date,
            end_date=end_date,
            adjust="qfq"
        )

        if df is None or df.empty:
            return []

        # 取最近 days 天
        df = df.tail(days)

        result = []
        for _, row in df.iterrows():
            result.append({
                "date": row["日期"],
                "open": float(row["开盘"]),
                "high": float(row["最高"]),
                "low": float(row["最低"]),
                "close": float(row["收盘"]),
                "volume": float(row["成交量"]),
                "amount": float(row["成交额"]) if "成交额" in row else 0,
            })

        return result

    def _get_mock_price_history(self, code: str, days: int) -> list[dict]:
        """生成模拟历史价格"""
        result = []
        base_price = 100.0

        # 根据代码确定基础价格
        if code == "600519":
            base_price = 1688.0
        elif code == "000858":
            base_price = 145.6
        elif code == "300750":
            base_price = 186.5

        current_price = base_price

        for i in range(days):
            date = (datetime.now() - timedelta(days=days - i)).strftime("%Y-%m-%d")

            # 模拟价格波动
            change_pct = random.uniform(-3, 3)
            open_price = current_price * (1 + random.uniform(-0.5, 0.5) / 100)
            close_price = current_price * (1 + change_pct / 100)
            high_price = max(open_price, close_price) * (1 + random.uniform(0, 1) / 100)
            low_price = min(open_price, close_price) * (1 - random.uniform(0, 1) / 100)
            volume = random.randint(50000000, 500000000)

            result.append({
                "date": date,
                "open": round(open_price, 2),
                "high": round(high_price, 2),
                "low": round(low_price, 2),
                "close": round(close_price, 2),
                "volume": volume,
                "amount": round(volume * close_price, 2),
            })

            current_price = close_price

        return result

    # ========== 财务指标 ==========

    def get_financial_metrics(
        self,
        code: str,
        period: str = "annual",
        limit: int = 8
    ) -> list[dict]:
        """获取财务指标

        Args:
            code: 股票代码
            period: 财报周期，annual/quarter
            limit: 返回数量

        Returns:
            财务指标列表，每项包含主要财务数据
        """
        if self.use_mock:
            return self._get_mock_financial_metrics(code, limit)

        try:
            return self._fetch_financial_metrics_akshare(code, period, limit)
        except Exception as e:
            print(f"[DataService] 获取财务指标失败: {e}")
            return self._get_mock_financial_metrics(code, limit)

    def _fetch_financial_metrics_akshare(
        self,
        code: str,
        period: str,
        limit: int
    ) -> list[dict]:
        """从 AKShare 获取财务指标"""
        result = []

        try:
            # 获取财务摘要数据
            df = ak.stock_financial_analysis_indicator(
                symbol=code,
                start_date="20180101",
                end_date=datetime.now().strftime("%Y%m%d"),
                period=period
            )

            if df is None or df.empty:
                return []

            # 取最近的 limit 条
            df = df.tail(limit)

            for _, row in df.iterrows():
                metrics = {
                    "report_date": row.get("报告日期", ""),
                    "roe": self._safe_float(row.get("净资产收益率(%)")),
                    "roa": self._safe_float(row.get("资产报酬率(%)")),
                    "gross_margin": self._safe_float(row.get("销售毛利率(%)")),
                    "net_margin": self._safe_float(row.get("销售净利率(%)")),
                    "debt_ratio": self._safe_float(row.get("资产负债率(%)")),
                    "current_ratio": self._safe_float(row.get("流动比率")),
                    "quick_ratio": self._safe_float(row.get("速动比率")),
                    "revenue_growth": self._safe_float(row.get("营业收入同比(%)")),
                    "profit_growth": self._safe_float(row.get("净利润同比(%)")),
                }
                result.append(metrics)

        except Exception as e:
            print(f"[DataService] 财务指标解析失败: {e}")

        return result

    def _get_mock_financial_metrics(self, code: str, limit: int) -> list[dict]:
        """生成模拟财务指标"""
        result = []
        base_roe = 15.0

        if code == "600519":
            base_roe = 30.0
        elif code == "000858":
            base_roe = 20.0
        elif code == "300750":
            base_roe = 18.0

        for i in range(limit):
            year = datetime.now().year - (limit - i - 1)
            result.append({
                "report_date": f"{year}-12-31",
                "roe": round(base_roe + random.uniform(-5, 5), 2),
                "roa": round(base_roe * 0.6 + random.uniform(-2, 2), 2),
                "gross_margin": round(60 + random.uniform(-10, 10), 2),
                "net_margin": round(30 + random.uniform(-5, 5), 2),
                "debt_ratio": round(30 + random.uniform(-10, 10), 2),
                "current_ratio": round(2 + random.uniform(-0.5, 0.5), 2),
                "quick_ratio": round(1.5 + random.uniform(-0.3, 0.3), 2),
                "revenue_growth": round(10 + random.uniform(-5, 15), 2),
                "profit_growth": round(12 + random.uniform(-5, 18), 2),
            })

        return result

    # ========== 财务明细 ==========

    def search_line_items(
        self,
        code: str,
        items: list[str],
        limit: int = 8
    ) -> list[dict]:
        """获取财务明细

        Args:
            code: 股票代码
            items: 需要的财务项目列表，如 ["revenue", "net_income", "free_cash_flow"]
            limit: 返回数量

        Returns:
            财务明细列表，每项包含日期和各项财务数据
        """
        if self.use_mock:
            return self._get_mock_line_items(code, items, limit)

        try:
            return self._fetch_line_items_akshare(code, items, limit)
        except Exception as e:
            print(f"[DataService] 获取财务明细失败: {e}")
            return self._get_mock_line_items(code, items, limit)

    def _fetch_line_items_akshare(
        self,
        code: str,
        items: list[str],
        limit: int
    ) -> list[dict]:
        """从 AKShare 获取财务明细"""
        result = []

        try:
            # 获取利润表
            df = ak.stock_profit_sheet_by_report_em(symbol=code)

            if df is None or df.empty:
                return []

            # 取最近的 limit 条
            df = df.tail(limit)

            # 映射 AKShare 列名
            column_mapping = {
                "revenue": "营业收入",
                "net_income": "净利润",
                "operating_income": "营业利润",
                "total_profit": "利润总额",
            }

            for _, row in df.iterrows():
                item_data = {
                    "report_date": row.get("报告日期", ""),
                }

                for item in items:
                    col_name = column_mapping.get(item, item)
                    item_data[item] = self._safe_float(row.get(col_name))

                result.append(item_data)

        except Exception as e:
            print(f"[DataService] 财务明细解析失败: {e}")

        return result

    def _get_mock_line_items(self, code: str, items: list[str], limit: int) -> list[dict]:
        """生成模拟财务明细"""
        result = []

        base_revenue = 1000.0
        base_net_income = 100.0

        if code == "600519":
            base_revenue = 15000.0
            base_net_income = 750.0
        elif code == "000858":
            base_revenue = 800.0
            base_net_income = 100.0
        elif code == "300750":
            base_revenue = 3000.0
            base_net_income = 300.0

        for i in range(limit):
            year = datetime.now().year - (limit - i - 1)
            revenue = base_revenue * (1.1 ** i)
            net_income = base_net_income * (1.08 ** i)

            item_data = {
                "report_date": f"{year}-12-31",
            }

            for item in items:
                if item == "revenue":
                    item_data[item] = round(revenue, 2)
                elif item == "net_income":
                    item_data[item] = round(net_income, 2)
                elif item == "operating_income":
                    item_data[item] = round(net_income * 1.1, 2)
                elif item == "free_cash_flow":
                    item_data[item] = round(net_income * 0.6, 2)
                else:
                    item_data[item] = round(random.uniform(50, 500), 2)

            result.append(item_data)

        return result

    # ========== 市值 ==========

    def get_market_cap(self, code: str, date: Optional[str] = None) -> Optional[float]:
        """获取市值

        Args:
            code: 股票代码
            date: 日期，默认当天

        Returns:
            市值（亿元），失败返回 None
        """
        if self.use_mock:
            return self._get_mock_market_cap(code)

        try:
            return self._fetch_market_cap_akshare(code, date)
        except Exception as e:
            print(f"[DataService] 获取市值失败: {e}")
            return self._get_mock_market_cap(code)

    def _fetch_market_cap_akshare(self, code: str, date: Optional[str]) -> Optional[float]:
        """从 AKShare 获取市值"""
        try:
            # 获取个股信息
            df = ak.stock_individual_info_em(symbol=code)

            if df is None or df.empty:
                return None

            # 查找总市值
            for _, row in df.iterrows():
                if "总市值" in str(row.get("item", "")):
                    market_cap_str = str(row.get("value", ""))
                    # 解析 "2.12万亿" 或 "5658亿"
                    if "万亿" in market_cap_str:
                        return float(market_cap_str.replace("万亿", "")) * 10000
                    elif "亿" in market_cap_str:
                        return float(market_cap_str.replace("亿", ""))
                    elif "万" in market_cap_str:
                        return float(market_cap_str.replace("万", "")) / 10000

            return None

        except Exception as e:
            print(f"[DataService] 市值解析失败: {e}")
            return None

    def _get_mock_market_cap(self, code: str) -> float:
        """生成模拟市值"""
        mock_market_cap = {
            "600519": 21200.0,  # 贵州茅台 2.12万亿
            "000858": 5658.0,   # 五粮液 5658亿
            "300750": 8215.0,   # 宁德时代 8215亿
        }

        if code in mock_market_cap:
            return mock_market_cap[code]

        return random.uniform(100, 10000)

    # ========== 辅助方法 ==========

    @staticmethod
    def _safe_float(value, default: float = 0.0) -> float:
        """安全转换为浮点数"""
        if value is None or pd.isna(value):
            return default
        try:
            return float(value)
        except (ValueError, TypeError):
            return default


# ========== 全局实例 ==========

# 创建全局数据服务实例，供其他模块使用
_data_service_instance: Optional[DataService] = None


def get_data_service() -> DataService:
    """获取全局数据服务实例"""
    global _data_service_instance
    if _data_service_instance is None:
        _data_service_instance = DataService()
    return _data_service_instance
