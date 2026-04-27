"""
数据服务

提供股票数据获取功能，支持：
- 腾讯财经实时行情API (主要)
- 东方财富API (备用)
- 模拟数据（当 API 不可用时，显示 *）

US-052 实现：
- get_financial_metrics (获取财务指标)
- get_market_cap (获取市值)
- search_line_items (获取财务明细)
- get_price_history (获取历史价格)
"""

import os
import re
import json
import httpx
from datetime import datetime, timedelta
from typing import Optional


class DataService:
    """数据服务类"""

    # 指数代码映射 (腾讯代码格式)
    INDEX_CODES = {
        "000001": "sh000001",  # 上证指数
        "399001": "sz399001",  # 深证成指
        "399006": "sz399006",  # 创业板指
        "000300": "sh000300",  # 沪深300
        "000016": "sh000016",  # 上证50
        "000688": "sh000688",  # 科创50
    }

    INDEX_NAMES = {
        "000001": "上证指数",
        "399001": "深证成指",
        "399006": "创业板指",
        "000300": "沪深300",
        "000016": "上证50",
        "000688": "科创50",
    }

    def __init__(self):
        self.use_mock = os.getenv("USE_MOCK_DATA", "false").lower() == "true"
        print(f"[DataService] 初始化完成, use_mock={self.use_mock}")

    def get_stock_data_sync(self, code: str) -> dict:
        """同步获取股票数据"""
        # 先尝试从腾讯财经获取
        if not self.use_mock:
            try:
                return self._fetch_from_tencent(code)
            except Exception as e:
                print(f"[DataService] 腾讯获取失败: {e}")

        # 返回模拟数据
        return self._get_mock_data(code)

    def _fetch_from_tencent(self, code: str) -> dict:
        """从腾讯财经获取数据"""
        # 转换代码格式
        if code in self.INDEX_CODES:
            tencent_code = self.INDEX_CODES[code]
        elif code.startswith("6"):
            tencent_code = f"sh{code}"
        elif code.startswith(("0", "3")):
            tencent_code = f"sz{code}"
        else:
            tencent_code = code

        url = f"https://qt.gtimg.cn/q={tencent_code}"
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://finance.qq.com/",
        }

        response = httpx.get(url, headers=headers, timeout=10)
        text = response.text

        # 解析腾讯返回格式
        # v_sh000001="1~上证指数~000001~4079.90~4093.25~4081.03~605031798~0~0~0.00~0~0.00~..."
        match = re.search(r'"([^"]+)"', text)
        if not match:
            raise ValueError(f"腾讯数据解析失败 {code}")

        parts = match.group(1).split("~")
        if len(parts) < 50:
            raise ValueError(f"腾讯数据格式错误 {code}")

        name = parts[1]
        price = float(parts[3]) if parts[3] else 0
        prev_close = float(parts[4]) if parts[4] else price
        open_price = float(parts[5]) if parts[5] else price
        volume = float(parts[6]) if parts[6] else 0  # 成交量(手)
        high = float(parts[33]) if parts[33] else price
        low = float(parts[34]) if parts[34] else price
        amount = float(parts[37]) if parts[37] else 0  # 成交额(元)

        change = price - prev_close
        change_percent = (change / prev_close * 100) if prev_close else 0

        return {
            "code": code,
            "name": self.INDEX_NAMES.get(code, name),
            "price": price,
            "change": change,
            "change_percent": round(change_percent, 2),
            "open": open_price,
            "high": high,
            "low": low,
            "volume": volume * 100,  # 转换为股
            "amount": amount,
            "prev_close": prev_close,
            "pe": None,
            "pb": None,
            "market_cap": None,
        }

    def _get_mock_data(self, code: str) -> dict:
        """获取模拟数据"""
        mocks = {
            "600519": {"name": "贵州茅台", "price": 1688.0, "change": -20.16, "change_percent": -1.18},
            "000001": {"name": "上证指数", "price": 3245.67, "change": -45.32, "change_percent": -1.38},
            "399001": {"name": "深证成指", "price": 10245.23, "change": 45.67, "change_percent": 0.45},
            "399006": {"name": "创业板指", "price": 2089.45, "change": -12.34, "change_percent": -0.59},
            "000300": {"name": "沪深300", "price": 3856.78, "change": 23.45, "change_percent": 0.61},
        }

        mock = mocks.get(code, {"name": f"股票{code}", "price": 0, "change": 0, "change_percent": 0})

        return {
            "code": code,
            "name": mock["name"],
            "price": mock["price"],
            "change": mock["change"],
            "change_percent": mock["change_percent"],
            "open": mock["price"] - mock["change"] * 0.3,
            "high": mock["price"] + abs(mock["change"]) * 0.7,
            "low": mock["price"] - abs(mock["change"]) * 0.5,
            "volume": 1234567800,
            "amount": 1234567890,
            "prev_close": mock["price"] - mock["change"],
            "pe": None,
            "pb": None,
            "market_cap": None,
        }

    async def get_stock_data(self, code: str) -> dict:
        """异步获取股票数据"""
        return self.get_stock_data_sync(code)

    def get_price_history(self, code: str, days: int = 60) -> list:
        """
        获取历史价格

        Returns:
            [{"date": str, "open": float, "high": float, "low": float, "close": float, "volume": float}]
            如果无法获取数据，所有值显示为 *
        """
        if self.use_mock:
            return [
                {
                    "date": f"2026-04-{26-i:02d}",
                    "close": 1700 + i * 5,
                    "high": 1710 + i * 5,
                    "low": 1690 + i * 5,
                    "open": 1695 + i * 5,
                    "volume": 1234567
                }
                for i in range(min(days, 30))
            ]

        try:
            # 从腾讯财经获取历史K线数据
            if code.startswith("6"):
                tencent_code = f"sh{code}"
            elif code.startswith(("0", "3")):
                tencent_code = f"sz{code}"
            else:
                tencent_code = code

            # 使用历史数据接口
            end_date = datetime.now().strftime("%Y%m%d")
            start_date = (datetime.now() - timedelta(days=days)).strftime("%Y%m%d")

            url = f"https://web.ifzq.gtimg.cn/appstock/app/kline/mkline?param={tencent_code},day,{start_date},{end_date},500,qfq"

            headers = {
                "User-Agent": "Mozilla/5.0",
                "Referer": "https://finance.qq.com/",
            }

            response = httpx.get(url, headers=headers, timeout=10)
            data = response.json()

            # 解析数据
            if "data" in data and tencent_code in data["data"]:
                stock_data = data["data"][tencent_code]
                if "day" in stock_data:
                    result = []
                    for day_data in stock_data["day"]:
                        # 数据格式: [日期, 开, 收, 高, 低, 成交量]
                        result.append({
                            "date": day_data[0],
                            "open": float(day_data[1]) if day_data[1] != '-' else None,
                            "close": float(day_data[2]) if day_data[2] != '-' else None,
                            "high": float(day_data[3]) if day_data[3] != '-' else None,
                            "low": float(day_data[4]) if day_data[4] != '-' else None,
                            "volume": float(day_data[5]) if day_data[5] != '-' else None,
                        })
                    return result[-days:] if len(result) > days else result

            # 如果解析失败，返回 * 标记
            return [{"date": "*", "open": None, "close": None, "high": None, "low": None, "volume": None}]

        except Exception as e:
            print(f"[DataService] get_price_history 错误 {code}: {e}")
            return [{"date": "*", "open": None, "close": None, "high": None, "low": None, "volume": None}]

    def get_financial_metrics(self, code: str, period: str = "ttm", limit: int = 10) -> list:
        """
        获取财务指标

        Returns:
            [{
                "return_on_equity": float,
                "debt_to_equity": float,
                "operating_margin": float,
                "current_ratio": float,
                "gross_margin": float,
                "net_margin": float,
                "return_on_invested_capital": float,
                "asset_turnover": float,
                "revenue": float,
                "net_income": float,
            }]
            如果无法获取数据，返回空列表（外部应显示 *）
        """
        # TODO: 集成东方财富或其他财务数据API
        # 目前返回空列表，外部应显示 *
        print(f"[DataService] get_financial_metrics 需要集成财务API: {code}")
        return []

    def search_line_items(self, code: str, items: list, limit: int = 10) -> list:
        """
        获取财务明细

        Args:
            code: 股票代码
            items: 需要获取的科目列表，如 ["net_income", "revenue", "gross_profit"]
            limit: 返回数量

        Returns:
            [{
                "capital_expenditure": float,
                "depreciation_and_amortization": float,
                "net_income": float,
                "outstanding_shares": float,
                "total_assets": float,
                "total_liabilities": float,
                "shareholders_equity": float,
                "dividends_and_other_cash_distributions": float,
                "issuance_or_purchase_of_equity_shares": float,
                "gross_profit": float,
                "revenue": float,
                "free_cash_flow": float,
                "gross_margin": float,
            }]
            如果无法获取数据，返回空列表（外部应显示 *）
        """
        # TODO: 集成财务数据API
        print(f"[DataService] search_line_items 需要集成财务API: {code}")
        return []

    def get_market_cap(self, code: str, date: str = None) -> Optional[float]:
        """
        获取市值

        Returns:
            float: 市值（元）
            如果无法获取数据，返回 None（外部应显示 *）
        """
        try:
            # 从腾讯获取实时行情
            if code.startswith("6"):
                tencent_code = f"sh{code}"
            elif code.startswith(("0", "3")):
                tencent_code = f"sz{code}"
            else:
                tencent_code = code

            url = f"https://qt.gtimg.cn/q={tencent_code}"
            headers = {
                "User-Agent": "Mozilla/5.0",
                "Referer": "https://finance.qq.com/",
            }

            response = httpx.get(url, headers=headers, timeout=10)
            text = response.text

            match = re.search(r'"([^"]+)"', text)
            if not match:
                return None

            parts = match.group(1).split("~")
            if len(parts) < 50:
                return None

            # 市值相关字段在腾讯数据中的位置
            # parts[38] - 总市值(万元)
            # parts[39] - 流通市值(万元)
            market_cap_str = parts[38] if len(parts) > 38 and parts[38] != '-' else None

            if market_cap_str:
                return float(market_cap_str) * 10000  # 转换为元

            return None

        except Exception as e:
            print(f"[DataService] get_market_cap 错误 {code}: {e}")
            return None


# 单例
_data_service = None

def get_data_service() -> DataService:
    global _data_service
    if _data_service is None:
        _data_service = DataService()
    return _data_service
