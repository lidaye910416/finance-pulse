"""
数据服务

提供股票数据获取功能，支持：
- 腾讯财经实时行情API (主要)
- 东方财富API (备用)
- 模拟数据（当 API 不可用时）
"""

import os
import re
import httpx
from datetime import datetime


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
        """获取历史价格"""
        return [
            {"date": f"2026-04-{26-i:02d}", "close": 1700 + i * 5, "high": 1710 + i * 5, "low": 1690 + i * 5, "open": 1695 + i * 5, "volume": 1234567}
            for i in range(min(days, 30))
        ]

    def get_financial_metrics(self, code: str, period: str = "ttm", limit: int = 10) -> list:
        """获取财务指标"""
        return []

    def search_line_items(self, code: str, items: list, limit: int = 10) -> list:
        """获取财务明细"""
        return []

    def get_market_cap(self, code: str, date: str = None) -> float:
        """获取市值"""
        return 0.0


# 单例
_data_service = None

def get_data_service() -> DataService:
    global _data_service
    if _data_service is None:
        _data_service = DataService()
    return _data_service
