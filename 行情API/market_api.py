# -*- coding: utf-8 -*-
"""LOZENO 公网行情只读 API。"""

import json
import calendar
from datetime import datetime

import redis
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

# ==================== 配置 ====================

SYMBOL = "XAUUSD.cn"

KEY_KLINE = "XAUUSD_M5_KLINE_CACHE"
KEY_TICK = "XAUUSD_M5_TICK_CACHE"
KEY_SIGNAL = "XAUUSD_M5_DIRECTION_SIGNAL"
KEY_STATUS = "XAUUSD_M5_STATUS"
KEY_TRADES = "XAUUSD_M5_TRADES"

R = redis.Redis(
    host="127.0.0.1",
    port=6379,
    db=0,
    decode_responses=True,
    socket_connect_timeout=3,
    socket_timeout=3,
)

app = FastAPI(
    title="LOZENO Market API",
    docs_url=None,
    redoc_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://lozeno.net",
        "https://www.lozeno.net",
    ],
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["Accept"],
)


# ==================== 公共方法 ====================

def read_json(key):
    try:
        raw = R.get(key)
    except redis.RedisError:
        raise HTTPException(
            status_code=503,
            detail="行情缓存暂时不可用",
        )

    if not raw:
        return None

    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        raise HTTPException(
            status_code=503,
            detail=f"行情缓存格式错误：{key}",
        )


def require_data(key):
    data = read_json(key)
    if data is None:
        raise HTTPException(
            status_code=503,
            detail="数据尚未生成，请检查实盘程序是否运行",
        )
    return data


def candle_time(value):
    """现有 K 线日期字符串按 UTC 还原 Unix 秒时间戳。"""
    try:
        dt = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
        return calendar.timegm(dt.timetuple())
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=503,
            detail="K 线时间格式错误",
        )


def check_symbol(symbol):
    if symbol != SYMBOL:
        raise HTTPException(
            status_code=400,
            detail="暂不支持该交易品种",
        )


# ==================== API ====================

@app.get("/api/market/candles")
def get_candles(
    symbol: str = Query(default=SYMBOL),
    timeframe: str = Query(default="M5"),
):
    check_symbol(symbol)

    if timeframe != "M5":
        raise HTTPException(
            status_code=400,
            detail="暂不支持该周期",
        )

    rows = require_data(KEY_KLINE)

    if not isinstance(rows, list):
        raise HTTPException(
            status_code=503,
            detail="K 线数据结构错误",
        )

    candles = []

    for row in rows:
        try:
            candles.append({
                "time": candle_time(row["日期"]),
                "open": float(row["开盘价"]),
                "high": float(row["最高价"]),
                "low": float(row["最低价"]),
                "close": float(row["收盘价"]),
            })
        except (KeyError, TypeError, ValueError):
            continue

    candles.sort(key=lambda item: item["time"])

    # 同一时间戳只保留最后一条
    unique = {item["time"]: item for item in candles}
    candles = sorted(unique.values(), key=lambda item: item["time"])

    if not candles:
        raise HTTPException(
            status_code=503,
            detail="暂无有效 K 线",
        )

    return {
        "symbol": SYMBOL,
        "timeframe": "M5",
        "count": len(candles),
        "candles": candles,
    }


@app.get("/api/market/tick")
def get_tick(symbol: str = Query(default=SYMBOL)):
    check_symbol(symbol)

    data = require_data(KEY_TICK)

    return {
        "symbol": SYMBOL,
        "bid": data.get("bid"),
        "ask": data.get("ask"),
        "last": data.get("last"),
        "time_msc": data.get("time_msc"),
    }


@app.get("/api/market/signal")
def get_signal(symbol: str = Query(default=SYMBOL)):
    check_symbol(symbol)

    data = require_data(KEY_SIGNAL)

    return {
        "symbol": SYMBOL,
        "direction": data.get("predicted_direction"),
        "up_probability": data.get("up_probability"),
        "down_probability": data.get("down_probability"),
        "confidence": data.get("confidence"),
        "progress": data.get("predicted_position"),
        "stage": data.get("predicted_stage_name"),
        "time": data.get("time"),
        "wave_id": data.get("best_wave_id"),
    }


@app.get("/api/market/status")
def get_status():
    data = require_data(KEY_STATUS)

    return {
        "status": data.get("status"),
        "symbol": data.get("symbol"),
        "timeframe": data.get("timeframe"),
        "bars": data.get("bars"),
        "updated_at": data.get("updated_at"),
    }


@app.get("/api/market/trades/summary")
def get_trade_summary():
    data = require_data(KEY_TRADES)

    return {
        "closed_trades": data.get("closed_trades", 0),
        "closed_volume": data.get("closed_volume", 0),
        "net_profit": data.get("net_profit", 0),
        "win_rate": data.get("win_rate", 0),
    }


@app.get("/health")
def health():
    try:
        R.ping()
        return {"status": "ok"}
    except redis.RedisError:
        raise HTTPException(
            status_code=503,
            detail="Redis unavailable",
        )