# mt5_websocket.py
# MT5 实时行情服务：历史 M5 K线 + 实时 Tick + 当前未收盘 K线

import asyncio
import json
import time

import MetaTrader5 as mt5
import websockets

HOST = "127.0.0.1"
PORT = 8001
SYMBOL = "XAUUSD.cn"
TIMEFRAME = mt5.TIMEFRAME_M5
TIMEFRAME_SECONDS = 300
HISTORY_COUNT = 300
POLL_INTERVAL = 0.2

clients = set()
candles_cache = []
latest_tick = None
last_tick_key = None


def get_tick():
    tick = mt5.symbol_info_tick(SYMBOL)
    if tick is None:
        return None

    return {
        "time": int(tick.time),
        "bid": float(tick.bid),
        "ask": float(tick.ask),
        "last": float(tick.last),
    }


def get_candles():
    rates = mt5.copy_rates_from_pos(
        SYMBOL,
        TIMEFRAME,
        0,
        HISTORY_COUNT,
    )

    if rates is None or len(rates) == 0:
        return []

    candles = [
        {
            "time": int(rate["time"]),
            "open": float(rate["open"]),
            "high": float(rate["high"]),
            "low": float(rate["low"]),
            "close": float(rate["close"]),
        }
        for rate in rates
    ]

    candles.sort(key=lambda item: item["time"])

    unique = {}
    for candle in candles:
        unique[candle["time"]] = candle

    return list(unique.values())[-HISTORY_COUNT:]


async def broadcast(message):
    if not clients:
        return

    payload = json.dumps(message, ensure_ascii=False)
    connected = list(clients)

    results = await asyncio.gather(
        *(client.send(payload) for client in connected),
        return_exceptions=True,
    )

    for client, result in zip(connected, results):
        if isinstance(result, Exception):
            clients.discard(client)


async def websocket_handler(websocket):
    clients.add(websocket)

    try:
        await websocket.send(json.dumps({
            "type": "snapshot",
            "symbol": SYMBOL,
            "server_time": int(time.time()),
            "candles": list(candles_cache),
            "tick": latest_tick,
        }, ensure_ascii=False))

        await websocket.wait_closed()
    finally:
        clients.discard(websocket)


def update_current_candle(tick):
    """
    只使用最新 Tick 更新内存中的当前 K 线。
    返回发生变化的 K 线；没有变化则返回 None。
    """
    if not candles_cache:
        return None

    bid = tick["bid"]
    if bid <= 0:
        return None

    candle_time = tick["time"] // TIMEFRAME_SECONDS * TIMEFRAME_SECONDS
    current = candles_cache[-1]

    # 新的 M5 周期
    if candle_time > current["time"]:
        candle = {
            "time": candle_time,
            "open": bid,
            "high": bid,
            "low": bid,
            "close": bid,
        }

        candles_cache.append(candle)

        if len(candles_cache) > HISTORY_COUNT:
            del candles_cache[:-HISTORY_COUNT]

        return candle.copy()

    # 迟到或过期的 Tick，不回写已经结束的 K 线
    if candle_time < current["time"]:
        return None

    # 当前未收盘 K 线：只更新发生变化的 OHLC
    changed = False

    if bid > current["high"]:
        current["high"] = bid
        changed = True

    if bid < current["low"]:
        current["low"] = bid
        changed = True

    if bid != current["close"]:
        current["close"] = bid
        changed = True

    return current.copy() if changed else None


async def market_loop():
    global last_tick_key, latest_tick

    while True:
        try:
            tick = get_tick()

            if tick is not None:
                latest_tick = tick

                tick_key = (
                    tick["time"],
                    tick["bid"],
                    tick["ask"],
                    tick["last"],
                )

                # Tick 有变化才发送行情消息
                if tick_key != last_tick_key:
                    last_tick_key = tick_key

                    await broadcast({
                        "type": "tick",
                        "symbol": SYMBOL,
                        "tick": tick,
                    })

                # 只更新内存中的当前 K 线，不重复读取历史 K 线
                candle = update_current_candle(tick)

                if candle is not None:
                    await broadcast({
                        "type": "candle_update",
                        "symbol": SYMBOL,
                        "candle": candle,
                    })

        except Exception as exc:
            print(f"[行情读取错误] {exc}")

        await asyncio.sleep(POLL_INTERVAL)


async def main():
    global candles_cache, latest_tick, last_tick_key

    if not mt5.initialize():
        print(f"MT5 初始化失败：{mt5.last_error()}")
        return

    try:
        if mt5.symbol_info(SYMBOL) is None:
            print(f"找不到交易品种：{SYMBOL}")
            return

        if not mt5.symbol_select(SYMBOL, True):
            print(f"无法启用交易品种：{SYMBOL}")
            return

        # 启动时只读取一次历史 K 线
        candles_cache = get_candles()

        if not candles_cache:
            print("历史 K 线获取失败，请检查 MT5 行情数据。")
            return

        latest_tick = get_tick()

        if latest_tick is not None:
            last_tick_key = (
                latest_tick["time"],
                latest_tick["bid"],
                latest_tick["ask"],
                latest_tick["last"],
            )

            # 用启动时的最新 Tick 校准当前未收盘 K 线
            update_current_candle(latest_tick)

        print(f"MT5 已连接：{SYMBOL}")
        print(f"历史 K 线：{len(candles_cache)} 根")
        print(f"WebSocket 地址：ws://{HOST}:{PORT}")
        print(f"Tick 轮询间隔：{int(POLL_INTERVAL * 1000)} 毫秒")
        print("按 Ctrl+C 停止服务")

        async with websockets.serve(
            websocket_handler,
            HOST,
            PORT,
            ping_interval=20,
            ping_timeout=20,
        ):
            await market_loop()

    finally:
        mt5.shutdown()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("行情服务已停止")