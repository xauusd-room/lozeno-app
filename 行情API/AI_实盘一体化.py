
# -*- coding: utf-8 -*-
"""XAUUSD.cn M5 实盘一体化系统：实时K线走Redis，收盘计算，交易记录写SQLite。"""
import os, time, json, sqlite3
from datetime import datetime
import numpy as np
import pandas as pd
import MetaTrader5 as mt5
import redis

# ==================== 公共配置 ====================
SYMBOL, LOT, MAGIC, DEVIATION = "XAUUSD.cn", 0.05, 20260910, 20
R = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)
POLL = 0.1
KEY_KLINE = "XAUUSD_M5_KLINE_CACHE"
KEY_SWING = "XAUUSD_M5_SWING_CACHE"
KEY_PEN = "XAUUSD_M5_PEN_CACHE"
KEY_SEGMENT = "XAUUSD_M5_SEGMENT_CACHE"
KEY_DIRECTION = "XAUUSD_M5_WAVE_DIRECTION_CACHE"
KEY_FEATURE = "XAUUSD_M5_FEATURE_CACHE"
KEY_WAVES = "XAUUSD_M5_COMPLETE_WAVES_CACHE"
KEY_SIGNAL = "XAUUSD_M5_DIRECTION_SIGNAL"
KEY_STATUS = "XAUUSD_M5_STATUS"
KEY_TRADES = "XAUUSD_M5_TRADES"
KEY_OPEN_TRADES = "XAUUSD_M5_OPEN_TRADES"
NPZ_PATH = r"D:\AI\完整波段_MACD连续序列训练数据.npz"
TRADE_DB = r"D:\AI\交易记录\实盘交易.db"
MAX_TIME_RATIO, TIME_PENALTY_LAMBDA, TOP_N, EPS = 1.5, 0.10, 20, 1e-8
LEFT_BARS = RIGHT_BARS = 5
STATUS_LINE_LENGTH = 0
STATUS_REFRESH_SECONDS = 0.1

# ==================== AI01：读取301根，含当前未收盘K线 ====================
def get_klines():
    rates = mt5.copy_rates_from_pos(SYMBOL, mt5.TIMEFRAME_M5, 0, 301)
    if rates is None or len(rates) < 21: return None
    df = pd.DataFrame(rates)
    df["日期"] = pd.to_datetime(df.pop("time"), unit="s").dt.strftime("%Y-%m-%d %H:%M:%S")
    df = df.rename(columns={"open":"开盘价","high":"最高价","low":"最低价","close":"收盘价","tick_volume":"TICK_VOLUME"})
    return df[["日期","开盘价","最高价","最低价","收盘价","TICK_VOLUME"]].sort_values("日期").drop_duplicates("日期", keep="last").tail(301).reset_index(drop=True)

# ==================== AI02：分型 ====================
def calc_fractals(df):
    highs, lows = df["最高价"].to_numpy(), df["最低价"].to_numpy()
    out = []
    for i in range(LEFT_BARS, len(df)-RIGHT_BARS):
        h, l = highs[i], lows[i]
        if all(highs[i-j] <= h for j in range(1, LEFT_BARS+1)) and all(highs[i+j] < h for j in range(1, RIGHT_BARS+1)):
            out.append({"日期":df.iloc[i]["日期"],"类型":"HIGH","价格":round(float(h),4),"确认时间":df.iloc[i+RIGHT_BARS]["日期"]})
        if all(lows[i-j] >= l for j in range(1, LEFT_BARS+1)) and all(lows[i+j] > l for j in range(1, RIGHT_BARS+1)):
            out.append({"日期":df.iloc[i]["日期"],"类型":"LOW","价格":round(float(l),4),"确认时间":df.iloc[i+RIGHT_BARS]["日期"]})
    return sorted(out, key=lambda x:(x["日期"],x["类型"]))

# ==================== AI03：分型转笔 ====================
def calc_pens(fractals):
    nodes = []
    for f in fractals:
        d,t,p = f["日期"],f["类型"],float(f["价格"])
        if not nodes: nodes.append([d,t,p]); continue
        if t == nodes[-1][1]:
            if (t=="HIGH" and p>nodes[-1][2]) or (t=="LOW" and p<nodes[-1][2]): nodes[-1] = [d,t,p]
        else: nodes.append([d,t,p])
    hp=lp=None; out=[]
    for d,t,p in nodes:
        if t=="HIGH": lab="hh" if hp is None or p>hp else "lh"; hp=p
        else: lab="ll" if lp is None or p<lp else "hl"; lp=p
        out.append({"日期":d,"笔":lab,"笔价格":p,"类型":t})
    return out

# ==================== AI04：笔转线段 ====================
def calc_segments(pens):
    nodes=[]
    for x in pens:
        if x["笔"] not in ("hh","ll"): continue
        typ="HH" if x["笔"]=="hh" else "LL"; p=float(x["笔价格"])
        if not nodes: nodes.append({"日期":x["日期"],"线段":typ,"线段价格":p}); continue
        last=nodes[-1]
        if typ!=last["线段"]: nodes.append({"日期":x["日期"],"线段":typ,"线段价格":p})
        elif (typ=="HH" and p>last["线段价格"]) or (typ=="LL" and p<last["线段价格"]): nodes[-1]={"日期":x["日期"],"线段":typ,"线段价格":p}
    return nodes

# ==================== AI05：波段方向 ====================
def calc_directions(df,segments):
    out=[None]*len(df); ix={d:i for i,d in enumerate(df["日期"])}
    for a,b in zip(segments,segments[1:]):
        if a["日期"] not in ix or b["日期"] not in ix: continue
        direction=1 if a["线段"]=="LL" and b["线段"]=="HH" else -1 if a["线段"]=="HH" and b["线段"]=="LL" else None
        if direction is not None:
            for i in range(ix[a["日期"]],ix[b["日期"]]+1): out[i]=direction
    return out

# ==================== AI06：MACD特征 ====================
def calc_features(df):
    close=pd.to_numeric(df["收盘价"],errors="coerce")
    hist=close.ewm(span=12,adjust=False).mean()-close.ewm(span=26,adjust=False).mean()
    df["MACD_HIST"]=hist.astype(float); df["MACD_HIST_SLOPE"]=hist.diff().fillna(0).astype(float)
    return df

# ==================== AI07：波段ID ====================
def calc_wave_ids(df,segments):
    id1=[None]*len(df); id2=[None]*len(df); ix={d:i for i,d in enumerate(df["日期"])}; wave_id=1
    for a,b in zip(segments,segments[1:]):
        expected=1 if a["线段"]=="LL" and b["线段"]=="HH" else -1 if a["线段"]=="HH" and b["线段"]=="LL" else None
        if expected is None or a["日期"] not in ix or b["日期"] not in ix: continue
        for i in range(ix[a["日期"]],ix[b["日期"]]+1):
            if id1[i] is None: id1[i]=wave_id
            elif id2[i] is None: id2[i]=wave_id
        wave_id+=1
    df["波段ID_1"],df["波段ID_2"]=id1,id2
    return df

# ==================== AI08：历史波段匹配预测 ====================
def resample(a,n):
    if len(a)==n: return a.astype(np.float32)
    if n==1: return np.array([a[0]],dtype=np.float32)
    if len(a)==1: return np.full(n,a[0],dtype=np.float32)
    return np.interp(np.linspace(0,1,n),np.linspace(0,1,len(a)),a).astype(np.float32)

def load_library():
    if not os.path.isfile(NPZ_PATH): return None
    d=np.load(NPZ_PATH,allow_pickle=False); X,offsets,Y,META=d["X"],d["OFFSETS"],d["Y"],d["META"]
    if len(offsets)<len(Y)+1: raise ValueError("NPZ的OFFSETS长度与Y不匹配")
    waves=[]
    for i in range(len(Y)):
        s,e=int(offsets[i]),int(offsets[i+1])
        if e>s: waves.append((int(META[i]["wave_id"]),int(Y[i]),X[s:e,0],X[s:e,1]))
    return waves,max(float(np.std(X[:,0])),EPS),max(float(np.std(X[:,1])),EPS)

def predict(ch,cs,library):
    waves,hstd,sstd=library; n=len(ch); curh=ch/hstd; curs=cs/sstd; candidates=[]
    for wid,direction,hh,ss in waves:
        L=len(hh)
        if L<n: continue
        best=best_k=None
        for k in range(n,min(L,max(n,int(np.floor(n*MAX_TIME_RATIO))))+1):
            h=resample(hh[:k],n)/hstd; s=resample(ss[:k],n)/sstd
            dist=.5*(np.mean(np.abs(curh-h))+np.mean(np.abs(curs-s)))*(1+TIME_PENALTY_LAMBDA*abs(np.log(k/n)))
            if best is None or dist<best: best,best_k=float(dist),k
        if best is not None: candidates.append((best,wid,direction,L,best_k,best_k/L))
    if not candidates: return None
    candidates=sorted(candidates,key=lambda x:x[0])[:TOP_N]
    weights=np.array([1/(x[0]+EPS) for x in candidates]); dirs=np.array([x[2] for x in candidates]); total=weights.sum()
    up=float(weights[dirs==1].sum()/total); down=float(weights[dirs==-1].sum()/total); pos=float(candidates[0][5])
    stage=0 if pos<.2 else 1 if pos<.4 else 2 if pos<.6 else 3 if pos<.8 else 4
    return {"predicted_direction":1 if up>=down else -1,"up_probability":up,"down_probability":down,"confidence":max(up,down),"predicted_position":pos,"predicted_stage":stage,"predicted_stage_name":("早期","发展期","中期","后期","尾端")[stage],"best_distance":candidates[0][0],"best_wave_id":candidates[0][1]}

def predict_current(df,library):
    if library is None or len(df)<30: return None
    dirs=df["波段方向"].tolist(); start=len(df)
    while start>0 and pd.isna(dirs[start-1]): start-=1
    rows=df.iloc[start:]
    if len(rows)<2: return None
    ch=rows["MACD_HIST"].to_numpy(dtype=np.float32); cs=rows["MACD_HIST_SLOPE"].to_numpy(dtype=np.float32)
    if not np.isfinite(ch).all() or not np.isfinite(cs).all(): return None
    result=predict(ch,cs,library)
    if result is None: return None
    result.update({"time":str(rows.iloc[-1]["日期"]),"wave_start_time":str(rows.iloc[0]["日期"]),"x_len":len(rows),"end_time":str(rows.iloc[-1]["日期"])})
    return result

# ==================== AI09：交易与SQLite ====================
def db_init():
    os.makedirs(os.path.dirname(TRADE_DB),exist_ok=True)
    with sqlite3.connect(TRADE_DB) as c:
        c.execute("""CREATE TABLE IF NOT EXISTS trades(id INTEGER PRIMARY KEY AUTOINCREMENT,position_id INTEGER UNIQUE,ticket INTEGER,direction TEXT,volume REAL,open_time TEXT,close_time TEXT,hold_seconds INTEGER,open_price REAL,close_price REAL,up_probability REAL,down_probability REAL,profit REAL,commission REAL,swap REAL,net_profit REAL)""")
        c.execute("""CREATE TABLE IF NOT EXISTS open_trades(position_id INTEGER PRIMARY KEY,ticket INTEGER,direction TEXT,volume REAL,open_time TEXT,open_price REAL,up_probability REAL,down_probability REAL)""")

def positions():
    return [p for p in (mt5.positions_get(symbol=SYMBOL) or []) if p.magic==MAGIC]

def console_log(message):
    global STATUS_LINE_LENGTH
    if STATUS_LINE_LENGTH: print("\r"+" "*STATUS_LINE_LENGTH+"\r",end="",flush=True); STATUS_LINE_LENGTH=0
    print(message,flush=True)

def update_status_line(line):
    global STATUS_LINE_LENGTH
    width=max(STATUS_LINE_LENGTH,len(line)); print("\r"+line.ljust(width),end="",flush=True); STATUS_LINE_LENGTH=width


def position_summary():
    """根据最新TICK实时计算持仓浮盈，包含库存隔夜利息，不含尚未发生的平仓手续费。"""
    ps = positions()
    tick = mt5.symbol_info_tick(SYMBOL)
    result = {}

    for label, typ in (
        ("BUY", mt5.POSITION_TYPE_BUY),
        ("SELL", mt5.POSITION_TYPE_SELL),
    ):
        group = [p for p in ps if p.type == typ]
        lots = sum(float(p.volume) for p in group)

        avg_open = (
            sum(float(p.price_open) * float(p.volume) for p in group) / lots
            if lots else None
        )

        floating = 0.0

        for p in group:
            swap = float(getattr(p, "swap", 0.0))

            if tick is None:
                floating += float(p.profit) + swap
                continue

            # 买单按Bid平仓，卖单按Ask平仓
            close_price = (
                float(tick.bid)
                if p.type == mt5.POSITION_TYPE_BUY
                else float(tick.ask)
            )

            order_type = (
                mt5.ORDER_TYPE_BUY
                if p.type == mt5.POSITION_TYPE_BUY
                else mt5.ORDER_TYPE_SELL
            )

            profit = mt5.order_calc_profit(
                order_type,
                SYMBOL,
                float(p.volume),
                float(p.price_open),
                close_price,
            )

            # 计算失败时回退到MT5持仓浮盈
            if profit is None:
                profit = float(p.profit)

            floating += float(profit) + swap

        result[label] = {
            "lots": lots,
            "open_price": avg_open,
            "floating": floating,
            "count": len(group),
        }

    result["TOTAL_FLOATING"] = (
        result["BUY"]["floating"] + result["SELL"]["floating"]
    )

    return result


def fmt_price(value,digits=2):
    return "--" if value is None else f"{value:.{digits}f}"

def save_open(p,up,down):
    with sqlite3.connect(TRADE_DB) as c:
        c.execute("INSERT OR REPLACE INTO open_trades VALUES(?,?,?,?,?,?,?,?)",(int(p.identifier),int(p.ticket),"BUY" if p.type==0 else "SELL",p.volume,time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(p.time)),p.price_open,up,down))

def save_close(p,close_price):
    deals=mt5.history_deals_get(position=int(p.identifier)); profit=commission=swap=0.0
    for d in deals or []: profit+=d.profit; commission+=d.commission; swap+=d.swap
    with sqlite3.connect(TRADE_DB) as c:
        row=c.execute("SELECT open_time,open_price,up_probability,down_probability FROM open_trades WHERE position_id=?",(int(p.identifier),)).fetchone()
        opened,open_price,up,down=row if row else (time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(p.time)),p.price_open,0.0,0.0)
        close_time=time.strftime("%Y-%m-%d %H:%M:%S"); hold=max(0,int(time.time()-p.time)); net=profit+commission+swap
        c.execute("INSERT OR IGNORE INTO trades(position_id,ticket,direction,volume,open_time,close_time,hold_seconds,open_price,close_price,up_probability,down_probability,profit,commission,swap,net_profit) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(int(p.identifier),int(p.ticket),"BUY" if p.type==0 else "SELL",p.volume,opened,close_time,hold,open_price,close_price,up,down,profit,commission,swap,net))
        c.execute("DELETE FROM open_trades WHERE position_id=?",(int(p.identifier),))
    return net

def close_type(pos_type):
    for p in positions():
        if p.type!=pos_type: continue
        tick=mt5.symbol_info_tick(SYMBOL)
        if not tick: continue
        typ=mt5.ORDER_TYPE_SELL if p.type==mt5.POSITION_TYPE_BUY else mt5.ORDER_TYPE_BUY
        price=tick.bid if p.type==mt5.POSITION_TYPE_BUY else tick.ask
        res=mt5.order_send({"action":mt5.TRADE_ACTION_DEAL,"symbol":SYMBOL,"volume":p.volume,"type":typ,"position":p.ticket,"price":price,"deviation":DEVIATION,"magic":MAGIC,"comment":"AI_CLOSE","type_time":mt5.ORDER_TIME_GTC,"type_filling":mt5.ORDER_FILLING_IOC})
        if res and res.retcode==mt5.TRADE_RETCODE_DONE: console_log(f"平仓成功 {p.ticket} | 手数={p.volume} | 净盈亏={save_close(p,res.price):+.2f}")
        else: console_log(f"平仓失败 {p.ticket}: {res.comment if res else mt5.last_error()}")

def open_trade(direction,signal):
    tick=mt5.symbol_info_tick(SYMBOL)
    if not tick: return False
    typ=mt5.ORDER_TYPE_BUY if direction==1 else mt5.ORDER_TYPE_SELL; price=tick.ask if direction==1 else tick.bid
    res=mt5.order_send({"action":mt5.TRADE_ACTION_DEAL,"symbol":SYMBOL,"volume":LOT,"type":typ,"price":price,"sl":0.0,"tp":0.0,"deviation":DEVIATION,"magic":MAGIC,"comment":"AI_BUY" if direction==1 else "AI_SELL","type_time":mt5.ORDER_TIME_GTC,"type_filling":mt5.ORDER_FILLING_IOC})
    if not res or res.retcode!=mt5.TRADE_RETCODE_DONE:
        console_log(f"开仓失败：{res.comment if res else mt5.last_error()}"); return False
    time.sleep(.1)
    same=[p for p in positions() if p.type==(mt5.POSITION_TYPE_BUY if direction==1 else mt5.POSITION_TYPE_SELL)]
    if same: save_open(max(same,key=lambda p:p.time),signal["up_probability"],signal["down_probability"])
    console_log(f"开仓成功 {'BUY' if direction==1 else 'SELL'} | 手数={LOT} | 价格={res.price}")
    return True

def trade_signal(signal):
    direction=int(signal["predicted_direction"]); ps=positions()
    same_type=mt5.POSITION_TYPE_BUY if direction==1 else mt5.POSITION_TYPE_SELL
    opposite=mt5.POSITION_TYPE_SELL if direction==1 else mt5.POSITION_TYPE_BUY
    if any(p.type==same_type for p in ps): return
    if any(p.type==opposite for p in ps):
        console_log("检测到反向持仓，开始平仓"); close_type(opposite); time.sleep(.2)
        if any(p.type==opposite for p in positions()): console_log("反向持仓未平完，本次不反手"); return
    open_trade(direction,signal)

def trade_stats():
    with sqlite3.connect(TRADE_DB) as c:
        count,closed_volume,net_profit,wins=c.execute("SELECT COUNT(*),COALESCE(SUM(volume),0),COALESCE(SUM(net_profit),0),COALESCE(SUM(CASE WHEN net_profit>0 THEN 1 ELSE 0 END),0) FROM trades").fetchone()
    return int(count),float(closed_volume),float(net_profit),float(wins/count if count else 0.0)

# ==================== 总控：K线实时刷新，计算只在新M5开始时执行 ====================
def main():
    db_init(); R.ping()
    if not mt5.initialize(): raise RuntimeError(f"MT5初始化失败：{mt5.last_error()}")
    terminal=mt5.terminal_info(); account=mt5.account_info()
    if terminal is None: raise RuntimeError(f"无法读取MT5终端状态：{mt5.last_error()}")
    if account is None: raise RuntimeError(f"MT5未登录交易账户或账户信息读取失败：{mt5.last_error()}")
    print(f"MT5连接成功  账号={account.login}")
    if not mt5.symbol_select(SYMBOL,True): raise RuntimeError(f"无法选择交易品种：{SYMBOL} | {mt5.last_error()}")
    if mt5.symbol_info(SYMBOL) is None: raise RuntimeError(f"读取品种信息失败：{SYMBOL} | {mt5.last_error()}")
    library=load_library()
    if library is None: print(f"等待NPZ训练库：{NPZ_PATH}（暂不发交易信号）")
    last_bar_time=None; last_signal_time=""; last_status_log=0.0; last_display_time=0.0; last_stats_time=0.0
    latest_signal=None; computed_df=None; fractals=[]; pens=[]; segments=[]
    try:
        while True:
            live_df=get_klines(); now=time.time()
            if live_df is None:
                if now-last_status_log>=10: print(f"等待MT5行情 | 品种={SYMBOL} | last_error={mt5.last_error()}"); last_status_log=now
                time.sleep(POLL); continue

            # 当前最新行是未收盘K线；时间戳变化表示上一根M5已经收盘。
            current=live_df.iloc[-1].copy(); current_bar_time=str(current["日期"])
            new_bar=current_bar_time!=last_bar_time

            if new_bar:
                closed_df=live_df.iloc[:-1].tail(300).copy()
                if len(closed_df)>=20:
                    fractals=calc_fractals(closed_df); pens=calc_pens(fractals); segments=calc_segments(pens)
                    closed_df=calc_features(closed_df)
                    closed_df["波段方向"]=calc_directions(closed_df,segments)
                    computed_df=calc_wave_ids(closed_df,segments)

                    R.set(KEY_SWING,json.dumps(fractals,ensure_ascii=False))
                    R.set(KEY_PEN,json.dumps(pens,ensure_ascii=False))
                    R.set(KEY_SEGMENT,json.dumps(segments,ensure_ascii=False))
                    R.set(KEY_DIRECTION,json.dumps([{"日期":d,"波段方向":None if pd.isna(v) else int(v)} for d,v in zip(computed_df["日期"],computed_df["波段方向"])],ensure_ascii=False))
                    R.set(KEY_FEATURE,computed_df[["日期","MACD_HIST","MACD_HIST_SLOPE"]].to_json(orient="records",force_ascii=False))
                    R.set(KEY_WAVES,computed_df[["日期","波段方向","波段ID_1","波段ID_2"]].to_json(orient="records",force_ascii=False))

                    signal=predict_current(computed_df,library)
                    if signal:
                        latest_signal=signal; R.set(KEY_SIGNAL,json.dumps(signal,ensure_ascii=False))
                        if signal["time"]!=last_signal_time:
                            side="BUY" if signal["predicted_direction"]==1 else "SELL"
                            dominant=signal["up_probability"] if signal["predicted_direction"]==1 else signal["down_probability"]
                            console_log(f"交易信号：{side} | 对应概率={dominant:.2%} | 对标历史波段ID={signal['best_wave_id']} | 历史波段进度={signal['predicted_position']:.2%} | 匹配长度={signal['x_len']}根 | {signal['wave_start_time']} 至 {signal['end_time']}")
                            trade_signal(signal); last_signal_time=signal["time"]
                last_bar_time=current_bar_time

            # 每轮只更新K线缓存：299根已收盘K线 + 1根实时K线。
            # 当前K线的MACD字段置空，避免误将未收盘指标当作已确认结果。
            if computed_df is not None and len(computed_df):
                view_df=computed_df.tail(299).copy()
                current_row=current.to_dict()
                current_row["MACD_HIST"]=None; current_row["MACD_HIST_SLOPE"]=None
                for col in ("波段方向","波段ID_1","波段ID_2"):
                    current_row[col]=None
                view_df=pd.concat([view_df,pd.DataFrame([current_row])],ignore_index=True)
                view_df=view_df.drop(columns=["波段方向","波段ID_1","波段ID_2"],errors="ignore").tail(300)
                R.set(KEY_KLINE,view_df.to_json(orient="records",force_ascii=False))
                R.set(f"{KEY_KLINE}_LAST_DATE",current_bar_time)

            R.set(KEY_STATUS,json.dumps({"status":"running","symbol":SYMBOL,"timeframe":"M5","bars":300 if computed_df is not None else len(live_df),"updated_at":datetime.now().isoformat(timespec="seconds")},ensure_ascii=False))

            # 交易统计无需每0.1秒查询SQLite，约每秒更新一次。
            if now-last_stats_time>=1.0:
                stats=trade_stats()
                R.set(KEY_TRADES,json.dumps({"closed_trades":stats[0],"closed_volume":stats[1],"net_profit":stats[2],"win_rate":stats[3]},ensure_ascii=False))
                last_stats_time=now

            # 实时显示价格与持仓；预测数据沿用最近一次收盘计算结果。
            if now-last_display_time>=STATUS_REFRESH_SECONDS:
                tick=mt5.symbol_info_tick(SYMBOL); info=mt5.symbol_info(SYMBOL); digits=int(info.digits) if info else 2
                if tick:
                    price=float(tick.last) if getattr(tick,"last",0) and float(tick.last)>0 else float(tick.bid)
                    if price<=0: price=float(tick.ask)
                else: price=float(current["收盘价"])
                ps=position_summary()
                if latest_signal:
                    side="BUY" if latest_signal["predicted_direction"]==1 else "SELL"
                    signal_text=f"信号 {side} | 上涨 {latest_signal['up_probability']:.2%} / 下跌 {latest_signal['down_probability']:.2%} | 波段进度 {latest_signal['predicted_position']:.2%} | 对标ID {latest_signal['best_wave_id']}"
                else: signal_text="信号等待预测 | 上涨 -- / 下跌 -- | 波段进度 -- | 对标ID --"
                active=[f"持仓 {label} {ps[label]['lots']:.2f}手 @ {fmt_price(ps[label]['open_price'],digits)} | 浮盈 {ps[label]['floating']:+.2f}" for label in ("BUY","SELL") if ps[label]["count"]]
                position_text=" | ".join(active) if active else "持仓 无 | 浮盈 +0.00"
                stats=trade_stats()
                update_status_line(f"{signal_text} | 现价 {price:.{digits}f} | {position_text} | 历史净盈亏 {stats[2]:+.2f} | 历史胜率 {stats[3]:.2%} ({stats[0]}笔)")
                last_display_time=now
            time.sleep(POLL)
    except KeyboardInterrupt:
        console_log("系统停止")
    finally:
        mt5.shutdown()

if __name__=="__main__": main()
