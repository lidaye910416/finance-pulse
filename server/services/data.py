"""
数据服务

提供股票数据获取功能，支持：
- AKShare 免费数据
- 模拟数据（当 AKShare 不可用时）
"""

import os
from typing import Optional

import httpx


class DataService:
    """数据服务类"""
    
    # AKShare API 基础 URL (使用他们的测试接口)
    AKSHARE_BASE_URL = "https://akshare.akfamily.cn"
    
    def __init__(self):
        self.use_mock = os.getenv("USE_MOCK_DATA", "false").lower() == "true"
        print(f"[DataService] 初始化完成, use_mock={self.use_mock}")
    
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
        import random
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
