
<script setup>
import { computed } from 'vue'

const candles = computed(() => {
  let previous = 42
  return Array.from({ length: 48 }, (_, i) => {
    const wave = Math.sin(i * 0.49) * 7 + Math.cos(i * 0.21) * 5
    const open = previous
    const close = 42 + wave + Math.sin(i * 0.83) * 3
    const high = Math.max(open, close) + 2 + (i % 4) * 0.7
    const low = Math.min(open, close) - 2 - (i % 3) * 0.8
    previous = close
    return { i, open, close, high, low, up: close >= open }
  })
})

const liveCandles = computed(() =>
  candles.value.map((c, i) => ({
    ...c,
    x: 18 + i * 11.2,
    yHigh: 18 + (65 - c.high) * 4.1,
    yLow: 18 + (65 - c.low) * 4.1,
    yOpen: 18 + (65 - c.open) * 4.1,
    yClose: 18 + (65 - c.close) * 4.1
  }))
)

const historyCandles = computed(() =>
  candles.value.map((c, i) => ({
    ...c,
    x: 18 + i * 11.2,
    yHigh: 18 + (65 - c.high) * 4.1,
    yLow: 18 + (65 - c.low) * 4.1,
    yOpen: 18 + (65 - c.open) * 4.1,
    yClose: 18 + (65 - c.close) * 4.1
  }))
)

const priceLabels = ['4,365.80', '4,362.50', '4,359.20', '4,355.90', '4,352.60']
</script>

<template>
  <main class="live-page">
    <div class="ambient ambient-blue"></div>
    <div class="ambient ambient-purple"></div>

    <header class="live-heading">
      <div class="heading-left">
        <div class="eyebrow"><span class="eyebrow-line"></span> LOZENO / LIVE INTELLIGENCE</div>
        <h1>实盘<span>直播</span><i class="title-dot"></i></h1>
        <p class="heading-subtitle">AI QUANTITATIVE TRADING COMMAND CENTER</p>
      </div>

      <div class="system-status">
        <span class="status-light"></span>
        <div>
          <strong>等待数据连接</strong>
          <small>MT5 DATA FEED · OFFLINE</small>
        </div>
        <span class="status-divider"></span>
        <div class="system-clock">
          <small>交易品种</small>
          <strong>XAUUSD.cn</strong>
        </div>
      </div>
    </header>

    <section class="terminal-frame">
      <div class="frame-topline">
        <span class="corner-label"><i></i> LIVE TERMINAL <b>01</b></span>
        <span class="frame-caption">REAL-TIME MARKET MONITOR</span>
        <span class="demo-state">预览界面 · 未接入实盘</span>
      </div>

      <div class="market-strip">
        <div class="instrument">
          <span class="gold-icon">Au</span>
          <div>
            <strong>GOLD <span>/ XAUUSD.cn</span></strong>
            <small>黄金现货 · MetaTrader 5</small>
          </div>
        </div>

        <div class="strip-metric">
          <small>时间周期</small>
          <strong>M5 <span class="metric-tag">5 MIN</span></strong>
        </div>

        <div class="strip-metric">
          <small>行情源</small>
          <strong><i class="mini-dot offline"></i> MT5 <span class="muted">待连接</span></strong>
        </div>

        <div class="strip-metric">
          <small>AI 引擎</small>
          <strong><i class="mini-dot purple"></i> QUANT AI <span class="muted">待连接</span></strong>
        </div>

        <div class="strip-metric update-metric">
          <small>数据更新</small>
          <strong>--:--:--.---</strong>
        </div>
      </div>

      <div class="charts-grid">
        <section class="chart-panel">
          <div class="panel-heading">
            <div class="panel-title">
              <span class="panel-index">01</span>
              <div>
                <h2>实时行情</h2>
                <p>LIVE MARKET · M5 CANDLESTICK</p>
              </div>
            </div>
            <span class="panel-badge blue-badge"><i></i> DEMO</span>
          </div>

          <div class="chart-toolbar">
            <span class="toolbar-symbol">XAUUSD.cn</span>
            <span class="toolbar-divider"></span>
            <span class="toolbar-period">M5</span>
            <span class="toolbar-spacer"></span>
            <span class="ohlc-label">O <b>--</b></span>
            <span class="ohlc-label">H <b>--</b></span>
            <span class="ohlc-label">L <b>--</b></span>
            <span class="ohlc-label">C <b>--</b></span>
          </div>

          <div class="chart-area">
            <div class="chart-watermark">LOZENO</div>
            <div class="chart-watermark-sub">MARKET DATA VISUALIZATION</div>

            <div class="chart-grid-lines">
              <div v-for="n in 6" :key="n" class="horizontal-grid">
                <span>{{ priceLabels[(n - 1) % priceLabels.length] }}</span>
              </div>
              <div v-for="n in 7" :key="'v' + n" class="vertical-grid"></div>
            </div>

            <svg class="candlestick-svg" viewBox="0 0 560 300" preserveAspectRatio="none" aria-label="演示用 K 线图">
              <defs>
                <linearGradient id="candleGlow" x1="0" y1="0" x2="1" y2="1">
                  <stop offset="0%" stop-color="#00f5d4" />
                  <stop offset="100%" stop-color="#00a9a0" />
                </linearGradient>
              </defs>
              <g v-for="c in liveCandles" :key="c.i">
                <line
                  :x1="c.x" :x2="c.x"
                  :y1="c.yHigh" :y2="c.yLow"
                  :stroke="c.up ? '#00e5c3' : '#ff4d85'"
                  stroke-width="1"
                />
                <rect
                  :x="c.x - 3.1"
                  :y="Math.min(c.yOpen, c.yClose)"
                  width="6.2"
                  :height="Math.max(2, Math.abs(c.yClose - c.yOpen))"
                  :fill="c.up ? 'url(#candleGlow)' : '#ff4d85'"
                  :opacity="0.88"
                />
              </g>
            </svg>

            <div class="chart-price-line"><span>示意价格</span></div>
            <div class="chart-time-labels">
              <span>09:00</span><span>09:45</span><span>10:30</span><span>11:15</span><span>12:00</span>
            </div>
            <div class="chart-corner chart-corner-tl"></div>
            <div class="chart-corner chart-corner-br"></div>
          </div>

          <div class="chart-footer">
            <span><i class="legend-up"></i> 上涨 K 线</span>
            <span><i class="legend-down"></i> 下跌 K 线</span>
            <span class="footer-note">示意图形，不代表真实行情</span>
          </div>
        </section>

        <section class="chart-panel history-panel">
          <div class="panel-heading">
            <div class="panel-title">
              <span class="panel-index purple-index">02</span>
              <div>
                <h2>历史相似波段</h2>
                <p>HISTORICAL PATTERN MATCHING</p>
              </div>
            </div>
            <span class="panel-badge purple-badge"><i></i> NPZ</span>
          </div>

          <div class="history-summary">
            <div>
              <small>算法匹配状态</small>
              <strong>等待算法数据</strong>
            </div>
            <div class="match-decoration">
              <span></span><span></span><span></span><span></span><span></span>
              <small>WAVE ANALYSIS</small>
            </div>
          </div>

          <div class="chart-toolbar">
            <span class="toolbar-symbol">MATCHED WAVE</span>
            <span class="toolbar-divider"></span>
            <span class="toolbar-period">OHLC</span>
            <span class="toolbar-spacer"></span>
            <span class="ohlc-label">历史完整波段</span>
          </div>

          <div class="chart-area history-chart-area">
            <div class="chart-watermark">PATTERN</div>
            <div class="chart-watermark-sub">HISTORICAL WAVE COMPARISON</div>

            <div class="chart-grid-lines">
              <div v-for="n in 6" :key="n" class="horizontal-grid">
                <span>{{ priceLabels[(n - 1) % priceLabels.length] }}</span>
              </div>
              <div v-for="n in 7" :key="'v' + n" class="vertical-grid"></div>
            </div>

            <svg class="candlestick-svg" viewBox="0 0 560 300" preserveAspectRatio="none" aria-label="历史相似波段演示 K 线图">
              <g v-for="c in historyCandles" :key="c.i">
                <line
                  :x1="c.x" :x2="c.x"
                  :y1="c.yHigh" :y2="c.yLow"
                  :stroke="c.up ? '#a78bfa' : '#ff62bd'"
                  stroke-width="1"
                />
                <rect
                  :x="c.x - 3.1"
                  :y="Math.min(c.yOpen, c.yClose)"
                  width="6.2"
                  :height="Math.max(2, Math.abs(c.yClose - c.yOpen))"
                  :fill="c.up ? '#9b72ff' : '#ff62bd'"
                  :opacity="0.86"
                />
              </g>
            </svg>

            <div class="history-scan"></div>
            <div class="chart-time-labels">
              <span>WAVE 01</span><span>WAVE 02</span><span>WAVE 03</span><span>WAVE 04</span><span>END</span>
            </div>
            <div class="chart-corner chart-corner-tl purple-corner"></div>
            <div class="chart-corner chart-corner-br purple-corner"></div>
          </div>

          <div class="chart-footer">
            <span><i class="legend-purple"></i> 历史波段 OHLC</span>
            <span class="footer-note">等待真实 NPZ 匹配结果</span>
          </div>
        </section>
      </div>

      <section class="ai-panel">
        <div class="ai-panel-heading">
          <div class="panel-title">
            <span class="ai-emblem"><span>AI</span></span>
            <div>
              <h2>AI 实时方向分析</h2>
              <p>ALGORITHMIC DIRECTION · LIVE INFERENCE</p>
            </div>
          </div>
          <span class="ai-waiting"><i></i> 等待模型输出</span>
        </div>

        <div class="ai-main-row">
          <div class="direction-block">
            <small>预测方向</small>
            <strong class="direction-neutral">-- <span>等待计算</span></strong>
          </div>

          <div class="ai-divider"></div>

          <div class="ai-metric">
            <small>方向概率</small>
            <strong>--<span>%</span></strong>
            <div class="metric-track"><span class="track-blue"></span></div>
          </div>

          <div class="ai-divider"></div>

          <div class="ai-metric progress-metric">
            <small>当前波段进度</small>
            <strong>--<span>%</span></strong>
            <div class="metric-track"><span class="track-purple"></span></div>
          </div>

          <div class="ai-divider"></div>

          <div class="ai-summary">
            <span class="summary-icon">⌁</span>
            <div>
              <small>算法状态</small>
              <strong>等待实盘数据接入</strong>
            </div>
          </div>
        </div>
        <div class="ai-bottom-line">
          <span>MODEL STATUS <b>STANDBY</b></span>
          <span>方向、概率及进度将由实际算法结果驱动</span>
        </div>
      </section>

      <section class="metrics-grid">
        <div class="metric-card">
          <div class="metric-card-head"><span class="metric-icon cyan-icon">↗</span><small>当前持仓</small><span class="card-index">01</span></div>
          <strong>-- <small>笔</small></strong>
          <p>POSITION COUNT</p>
          <div class="metric-card-line cyan-line"></div>
        </div>

        <div class="metric-card">
          <div class="metric-card-head"><span class="metric-icon green-icon">＋</span><small>实时浮动盈亏</small><span class="card-index">02</span></div>
          <strong>-- <small>USD</small></strong>
          <p>FLOATING PROFIT / LOSS</p>
          <div class="metric-card-line green-line"></div>
        </div>

        <div class="metric-card">
          <div class="metric-card-head"><span class="metric-icon purple-icon">◎</span><small>历史胜率</small><span class="card-index">03</span></div>
          <strong>-- <small>%</small></strong>
          <p>HISTORICAL WIN RATE</p>
          <div class="metric-card-line purple-line"></div>
        </div>

        <div class="metric-card">
          <div class="metric-card-head"><span class="metric-icon pink-icon">⌁</span><small>累计交易</small><span class="card-index">04</span></div>
          <strong>-- <small>笔</small></strong>
          <p>TOTAL TRADES</p>
          <div class="metric-card-line pink-line"></div>
        </div>
      </section>

      <footer class="terminal-footer">
        <div class="footer-brand"><span class="footer-brand-mark">L</span> LOZENO <span class="footer-separator">/</span> QUANT LIVE</div>
        <div class="footer-center"><span class="footer-pulse"></span> REAL-TIME TRADING OBSERVABILITY</div>
        <div class="footer-version">LIVE TERMINAL <b>V1.0</b></div>
      </footer>
    </section>
  </main>
</template>

<style scoped>
.live-page {
  --neon-blue: #426bff;
  --neon-cyan: #00e5ff;
  --neon-purple: #a16bff;
  --neon-pink: #ff4db8;
  --panel-bg: rgba(10, 15, 30, .94);
  position: relative;
  isolation: isolate;
  min-height: calc(100vh - 74px);
  overflow: hidden;
  padding: 30px 24px 46px;
  color: #eef3ff;
  background:
    radial-gradient(ellipse at 12% 0%, rgba(26, 72, 180, .15), transparent 38%),
    radial-gradient(ellipse at 90% 25%, rgba(113, 46, 191, .11), transparent 34%),
    #070a12;
  font-family: Inter, "Segoe UI", "Microsoft YaHei", sans-serif;
}

.live-page::before {
  position: absolute;
  z-index: -1;
  inset: 0;
  content: "";
  pointer-events: none;
  opacity: .23;
  background-image:
    linear-gradient(rgba(55, 98, 180, .08) 1px, transparent 1px),
    linear-gradient(90deg, rgba(55, 98, 180, .08) 1px, transparent 1px);
  background-size: 34px 34px;
  mask-image: linear-gradient(to bottom, #000, transparent 82%);
}

.ambient {
  position: absolute;
  z-index: -1;
  width: 380px;
  height: 380px;
  border-radius: 50%;
  filter: blur(100px);
  pointer-events: none;
  opacity: .12;
}

.ambient-blue { top: 200px; left: -250px; background: #126bff; }
.ambient-purple { top: 480px; right: -260px; background: #9c3dff; }

.live-heading,
.terminal-frame {
  width: 100%;
  max-width: 1540px;
  margin-inline: auto;
}

.live-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  margin-bottom: 24px;
}

.eyebrow {
  display: flex;
  align-items: center;
  gap: 9px;
  color: #8aa5d9;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 2.4px;
}

.eyebrow-line {
  display: inline-block;
  width: 22px;
  height: 2px;
  background: linear-gradient(90deg, #00e5ff, #456dff);
  box-shadow: 0 0 10px #00bfff;
}

.live-heading h1 {
  margin-top: 10px;
  font-size: clamp(28px, 3vw, 38px);
  font-weight: 800;
  letter-spacing: 3px;
}

.live-heading h1 > span {
  margin-left: 9px;
  color: #76cfff;
  text-shadow: 0 0 20px rgba(0, 183, 255, .38);
}

.title-dot {
  display: inline-block;
  width: 6px;
  height: 6px;
  margin-left: 12px;
  vertical-align: top;
  background: #00e5ff;
  box-shadow: 0 0 12px #00e5ff;
}

.heading-subtitle {
  margin-top: 7px;
  color: #56698b;
  font-size: 9px;
  letter-spacing: 2.3px;
}

.system-status {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 310px;
  padding: 14px 18px;
  border: 1px solid rgba(74, 107, 174, .27);
  background: linear-gradient(120deg, rgba(17, 29, 54, .85), rgba(17, 17, 37, .75));
  box-shadow: inset 0 0 22px rgba(32, 85, 190, .06), 0 0 24px rgba(28, 81, 205, .05);
}

.status-light,
.mini-dot,
.panel-badge i,
.ai-waiting i,
.footer-pulse {
  flex: 0 0 auto;
  width: 7px;
  height: 7px;
  border-radius: 50%;
}

.status-light { background: #f4b34d; box-shadow: 0 0 10px rgba(244, 179, 77, .65); }

.system-status strong,
.system-status small,
.system-clock strong,
.system-clock small {
  display: block;
}

.system-status strong { font-size: 12px; }
.system-status small { margin-top: 4px; color: #687b9d; font-size: 9px; letter-spacing: .8px; }
.status-divider { width: 1px; height: 30px; margin-inline: 6px; background: #293651; }
.system-clock { margin-left: auto; }
.system-clock strong { margin-top: 4px; color: #9bc8ff; font-size: 12px; }

.terminal-frame {
  position: relative;
  border: 1px solid transparent;
  background:
    linear-gradient(#080d18, #080d18) padding-box,
    linear-gradient(125deg, rgba(0, 229, 255, .8), rgba(49, 91, 255, .28) 32%, rgba(133, 72, 255, .45) 72%, rgba(0, 229, 255, .52)) border-box;
  box-shadow: 0 0 32px rgba(30, 88, 255, .08), inset 0 0 35px rgba(27, 70, 170, .035);
}

.terminal-frame::before,
.terminal-frame::after {
  position: absolute;
  z-index: 2;
  width: 64px;
  height: 2px;
  content: "";
  background: linear-gradient(90deg, #00e5ff, transparent);
  box-shadow: 0 0 12px rgba(0, 229, 255, .8);
  pointer-events: none;
}
.terminal-frame::before { top: -1px; left: 34px; }
.terminal-frame::after { right: 34px; bottom: -1px; transform: rotate(180deg); }

.frame-topline {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  min-height: 37px;
  padding: 0 18px;
  border-bottom: 1px solid #1a2940;
  background: linear-gradient(90deg, rgba(12, 29, 53, .9), rgba(16, 14, 36, .8));
}

.corner-label {
  color: #8ca4cf;
  font-size: 9px;
  font-weight: 700;
  letter-spacing: 1.7px;
}
.corner-label i { display: inline-block; width: 5px; height: 5px; margin-right: 8px; background: #00e5ff; box-shadow: 0 0 8px #00e5ff; }
.corner-label b { margin-left: 7px; color: #00e5ff; }
.frame-caption { color: #405579; font-size: 8px; letter-spacing: 1.6px; }
.demo-state { color: #e4b873; font-size: 10px; }

.market-strip {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 22px;
  padding: 17px 20px;
  border-bottom: 1px solid #1a263a;
  background: linear-gradient(90deg, rgba(16, 25, 43, .78), rgba(11, 13, 29, .86));
}

.instrument { display: flex; align-items: center; gap: 12px; min-width: 230px; margin-right: auto; }
.gold-icon {
  display: grid;
  width: 39px;
  height: 39px;
  place-items: center;
  color: #ffe0a0;
  font-size: 15px;
  font-weight: 800;
  border: 1px solid rgba(255, 197, 92, .4);
  background: linear-gradient(145deg, rgba(196, 138, 41, .2), rgba(255, 197, 92, .035));
  box-shadow: inset 0 0 14px rgba(255, 197, 92, .08), 0 0 15px rgba(255, 197, 92, .06);
}
.instrument strong { display: block; font-size: 14px; letter-spacing: .5px; }
.instrument strong span { color: #8e9fbd; font-weight: 500; }
.instrument small, .strip-metric small { display: block; margin-top: 5px; color: #617493; font-size: 10px; }
.strip-metric { min-width: 104px; padding-left: 18px; border-left: 1px solid #253047; }
.strip-metric strong { display: flex; align-items: center; gap: 6px; margin-top: 7px; font-size: 12px; white-space: nowrap; }
.metric-tag { color: #667c9f; font-size: 8px; letter-spacing: 1px; }
.mini-dot.offline { background: #f0b44e; box-shadow: 0 0 8px rgba(240, 180, 78, .45); }
.mini-dot.purple { background: #ae78ff; box-shadow: 0 0 8px rgba(174, 120, 255, .55); }
.muted { color: #60718e; font-size: 10px; font-weight: 400; }

.charts-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.12fr) minmax(0, .88fr);
  gap: 1px;
  border-bottom: 1px solid #1b2941;
  background: #1b2941;
}

.chart-panel {
  min-width: 0;
  padding: 19px 18px 14px;
  background: #080d18;
}

.panel-heading,
.panel-title,
.chart-footer,
.chart-toolbar {
  display: flex;
  align-items: center;
}

.panel-heading { justify-content: space-between; gap: 12px; margin-bottom: 16px; }
.panel-title { gap: 11px; min-width: 0; }
.panel-index { color: #43baff; font-size: 11px; font-weight: 800; letter-spacing: 1px; }
.purple-index { color: #bb88ff; }
.panel-title h2 { font-size: 14px; font-weight: 700; letter-spacing: .4px; }
.panel-title p { margin-top: 5px; color: #5a6f92; font-size: 8px; letter-spacing: 1.2px; }
.panel-badge { display: flex; align-items: center; gap: 6px; padding: 5px 8px; font-size: 8px; letter-spacing: 1px; }
.blue-badge { color: #58d9ff; border: 1px solid rgba(0, 207, 255, .25); background: rgba(0, 190, 255, .06); }
.blue-badge i { background: #00e5ff; box-shadow: 0 0 8px #00e5ff; }
.purple-badge { color: #c59aff; border: 1px solid rgba(164, 105, 255, .3); background: rgba(164, 105, 255, .07); }
.purple-badge i { background: #b17bff; box-shadow: 0 0 8px #b17bff; }

.chart-toolbar {
  min-height: 34px;
  gap: 11px;
  padding: 0 10px;
  border: 1px solid #1a2b44;
  border-bottom: 0;
  background: #0d1422;
}
.toolbar-symbol { color: #b7c9e9; font-size: 10px; font-weight: 700; }
.toolbar-divider { width: 1px; height: 13px; background: #293b58; }
.toolbar-period { color: #52d6ff; font-size: 10px; }
.toolbar-spacer { flex: 1; }
.ohlc-label { color: #536988; font-size: 8px; }
.ohlc-label b { color: #879cbf; font-weight: 500; }

.chart-area {
  position: relative;
  height: clamp(230px, 25vw, 320px);
  overflow: hidden;
  border: 1px solid #1a2b44;
  background:
    radial-gradient(ellipse at 45% 48%, rgba(17, 58, 105, .13), transparent 65%),
    #080e19;
}
.history-chart-area {
  background:
    radial-gradient(ellipse at 45% 48%, rgba(92, 36, 150, .14), transparent 65%),
    #0a0b19;
}
.chart-grid-lines { position: absolute; inset: 0 48px 20px 0; }
.horizontal-grid { position: relative; height: 20%; border-bottom: 1px solid rgba(79, 108, 157, .13); }
.horizontal-grid span { position: absolute; top: -6px; right: -47px; width: 42px; color: #596c8a; font-size: 8px; text-align: right; }
.vertical-grid { position: absolute; top: 0; bottom: 0; width: 1px; background: rgba(79, 108, 157, .12); }
.vertical-grid:nth-of-type(2) { left: 15%; }
.vertical-grid:nth-of-type(3) { left: 30%; }
.vertical-grid:nth-of-type(4) { left: 45%; }
.vertical-grid:nth-of-type(5) { left: 60%; }
.vertical-grid:nth-of-type(6) { left: 75%; }
.vertical-grid:nth-of-type(7) { left: 90%; }
.candlestick-svg { position: absolute; inset: 0 42px 20px 0; width: calc(100% - 42px); height: calc(100% - 20px); overflow: visible; }
.chart-watermark { position: absolute; top: 36%; left: 50%; transform: translate(-50%, -50%); color: rgba(76, 118, 187, .06); font-size: 38px; font-weight: 900; letter-spacing: 7px; pointer-events: none; }
.chart-watermark-sub { position: absolute; top: calc(36% + 24px); left: 50%; transform: translateX(-50%); color: rgba(89, 126, 185, .12); font-size: 7px; letter-spacing: 2px; white-space: nowrap; }
.chart-price-line { position: absolute; top: 47%; left: 0; right: 43px; border-top: 1px dashed rgba(0, 229, 195, .35); }
.chart-price-line span { position: absolute; right: -43px; top: -8px; padding: 3px 4px; color: #071a20; background: #00d8bd; font-size: 7px; }
.chart-time-labels { position: absolute; right: 48px; bottom: 5px; left: 8px; display: flex; justify-content: space-between; color: #526584; font-size: 8px; }
.chart-corner { position: absolute; width: 12px; height: 12px; pointer-events: none; }
.chart-corner-tl { top: 0; left: 0; border-top: 1px solid #00c8ff; border-left: 1px solid #00c8ff; }
.chart-corner-br { right: 42px; bottom: 19px; border-right: 1px solid #00c8ff; border-bottom: 1px solid #00c8ff; }
.purple-corner { border-color: #b36dff; }
.chart-footer { flex-wrap: wrap; gap: 16px; min-height: 29px; color: #637896; font-size: 9px; }
.chart-footer > span { display: flex; align-items: center; gap: 6px; }
.legend-up, .legend-down, .legend-purple { width: 6px; height: 6px; display: inline-block; }
.legend-up { background: #00e5c3; }
.legend-down { background: #ff4d85; }
.legend-purple { background: #a16bff; }
.chart-footer .footer-note { margin-left: auto; color: #4f617d; font-size: 8px; }

.history-summary { display: flex; align-items: center; justify-content: space-between; min-height: 47px; margin: -3px 0 12px; padding: 0 10px; border-left: 2px solid #8f5cff; background: linear-gradient(90deg, rgba(129, 77, 255, .09), transparent); }
.history-summary small { display: block; color: #7181a4; font-size: 9px; }
.history-summary strong { display: block; margin-top: 5px; color: #bba2ff; font-size: 11px; }
.match-decoration { display: flex; align-items: center; gap: 3px; }
.match-decoration > span { display: block; width: 3px; height: 12px; background: #8c5bff; opacity: .75; }
.match-decoration > span:nth-child(2), .match-decoration > span:nth-child(4) { height: 19px; }
.match-decoration > span:nth-child(3) { height: 25px; background: #da6dff; }
.match-decoration small { margin-left: 8px; font-size: 7px; letter-spacing: 1px; }
.history-scan { position: absolute; top: 0; bottom: 20px; left: 18%; width: 22%; background: linear-gradient(90deg, transparent, rgba(150, 90, 255, .035), transparent); pointer-events: none; }

.ai-panel {
  position: relative;
  padding: 20px 22px 14px;
  overflow: hidden;
  border-bottom: 1px solid #1b2941;
  background:
    linear-gradient(100deg, rgba(10, 25, 47, .98), rgba(17, 13, 39, .98)),
    #0d1221;
}
.ai-panel::before { position: absolute; top: 0; left: 0; width: 25%; height: 1px; content: ""; background: linear-gradient(90deg, #00e5ff, transparent); box-shadow: 0 0 10px #00bfff; }
.ai-panel-heading { display: flex; align-items: center; justify-content: space-between; gap: 12px; padding-bottom: 16px; border-bottom: 1px solid rgba(67, 94, 143, .25); }
.ai-emblem { display: grid; width: 34px; height: 34px; place-items: center; border: 1px solid rgba(0, 221, 255, .4); background: linear-gradient(145deg, rgba(0, 221, 255, .17), rgba(116, 81, 255, .12)); box-shadow: 0 0 15px rgba(0, 221, 255, .1), inset 0 0 10px rgba(0, 221, 255, .07); transform: rotate(45deg); }
.ai-emblem span { color: #7be9ff; font-size: 11px; font-weight: 800; transform: rotate(-45deg); }
.ai-waiting { display: flex; align-items: center; gap: 8px; color: #7c8eaf; font-size: 10px; }
.ai-waiting i { background: #9e75ff; box-shadow: 0 0 8px rgba(158, 117, 255, .5); }
.ai-main-row { display: flex; align-items: center; gap: 24px; min-height: 104px; }
.direction-block { min-width: 150px; }
.direction-block small, .ai-metric small, .ai-summary small { display: block; color: #7185a8; font-size: 10px; }
.direction-block strong { display: block; margin-top: 8px; color: #8ca1c4; font-size: 24px; }
.direction-block strong span { margin-left: 6px; font-size: 12px; font-weight: 500; }
.ai-divider { width: 1px; height: 42px; background: linear-gradient(transparent, #2c3e63, transparent); }
.ai-metric { flex: 1; min-width: 100px; }
.ai-metric strong { display: block; margin-top: 7px; color: #dbe7ff; font-size: 22px; font-weight: 700; }
.ai-metric strong span { margin-left: 3px; color: #7288ad; font-size: 12px; }
.metric-track { width: 100%; max-width: 170px; height: 3px; margin-top: 9px; overflow: hidden; background: #202c44; }
.metric-track span { display: block; width: 0; height: 100%; }
.track-blue { background: linear-gradient(90deg, #315bff, #00e5ff); box-shadow: 0 0 8px #00bfff; }
.track-purple { background: linear-gradient(90deg, #6e4cff, #ff4db8); box-shadow: 0 0 8px #a16bff; }
.ai-summary { display: flex; align-items: center; gap: 12px; min-width: 180px; }
.summary-icon { color: #9f79ff; font-size: 26px; text-shadow: 0 0 14px rgba(159, 121, 255, .5); }
.ai-summary strong { display: block; margin-top: 7px; color: #a9b9d5; font-size: 11px; }
.ai-bottom-line { display: flex; align-items: center; justify-content: space-between; gap: 12px; padding-top: 10px; border-top: 1px solid rgba(67, 94, 143, .18); color: #536b90; font-size: 8px; letter-spacing: .6px; }
.ai-bottom-line b { margin-left: 7px; color: #ac8bff; font-weight: 600; }

.metrics-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 1px; background: #1b2941; border-bottom: 1px solid #1b2941; }
.metric-card { position: relative; min-width: 0; padding: 17px 20px 18px; overflow: hidden; background: linear-gradient(145deg, #0d1423, #090e19); }
.metric-card-head { display: flex; align-items: center; gap: 9px; }
.metric-card-head > small { color: #8799b8; font-size: 10px; }
.metric-icon { display: grid; width: 24px; height: 24px; place-items: center; font-size: 15px; border: 1px solid currentColor; background: rgba(255,255,255,.02); }
.cyan-icon { color: #46dfff; }
.green-icon { color: #2bdfa2; }
.purple-icon { color: #b78bff; }
.pink-icon { color: #ff73c7; }
.card-index { margin-left: auto; color: #3e506f; font-size: 8px; }
.metric-card > strong { display: block; margin-top: 17px; color: #e1eaff; font-size: 27px; font-weight: 700; letter-spacing: .5px; }
.metric-card > strong small { color: #788ba9; font-size: 10px; font-weight: 500; }
.metric-card > p { margin-top: 6px; color: #506484; font-size: 8px; letter-spacing: 1.2px; }
.metric-card-line { position: absolute; right: 0; bottom: 0; left: 0; height: 1px; opacity: .8; }
.cyan-line { background: linear-gradient(90deg, transparent, #00d9ff, transparent); }
.green-line { background: linear-gradient(90deg, transparent, #0ecb81, transparent); }
.purple-line { background: linear-gradient(90deg, transparent, #a16bff, transparent); }
.pink-line { background: linear-gradient(90deg, transparent, #ff4db8, transparent); }

.terminal-footer { display: flex; align-items: center; justify-content: space-between; gap: 16px; min-height: 43px; padding: 0 18px; background: #080b14; }
.footer-brand { display: flex; align-items: center; gap: 7px; color: #8195b9; font-size: 9px; font-weight: 800; letter-spacing: 1.5px; }
.footer-brand-mark { display: grid; width: 17px; height: 17px; place-items: center; color: #07111f; font-size: 10px; background: linear-gradient(135deg, #00e5ff, #536aff); }
.footer-separator { color: #354663; }
.footer-center { display: flex; align-items: center; gap: 8px; color: #43597b; font-size: 8px; letter-spacing: 1px; }
.footer-pulse { width: 5px; height: 5px; background: #687a9b; }
.footer-version { color: #526788; font-size: 8px; letter-spacing: 1px; }
.footer-version b { margin-left: 6px; color: #9baff0; font-weight: 500; }

@media (min-width: 1600px) {
  .live-page { padding-inline: 36px; }
}

@media (max-width: 1100px) {
  .market-strip { gap: 16px; }
  .instrument { min-width: 190px; }
  .strip-metric { min-width: auto; padding-left: 12px; }
  .ai-main-row { gap: 15px; }
  .direction-block { min-width: 120px; }
  .ai-summary { min-width: 150px; }
}

@media (max-width: 850px) {
  .live-page { padding: 24px 14px 34px; }
  .live-heading { align-items: flex-start; flex-direction: column; }
  .system-status { width: 100%; min-width: 0; }
  .charts-grid { grid-template-columns: minmax(0, 1fr); }
  .chart-area { height: 280px; }
  .history-panel { border-top: 1px solid #1b2941; }
  .ai-main-row { flex-wrap: wrap; padding-block: 18px; }
  .ai-divider { display: none; }
  .direction-block, .ai-metric, .ai-summary { flex: 1 1 38%; min-width: 130px; }
  .metrics-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .update-metric { display: none; }
}

@media (max-width: 520px) {
  .live-page { padding-inline: 10px; }
  .heading-subtitle { font-size: 8px; letter-spacing: 1.2px; }
  .system-status { padding: 12px; }
  .frame-topline { padding-inline: 10px; }
  .frame-caption { display: none; }
  .market-strip { gap: 13px; padding: 13px 12px; }
  .instrument { width: 100%; }
  .strip-metric { flex: 1; padding-left: 10px; }
  .chart-panel { padding: 14px 10px 10px; }
  .chart-area { height: 230px; }
  .chart-toolbar { gap: 7px; padding-inline: 7px; }
  .ohlc-label:nth-last-child(-n+2) { display: none; }
  .chart-footer { gap: 10px; }
  .chart-footer .footer-note { width: 100%; margin-left: 0; }
  .ai-panel { padding: 16px 12px 12px; }
  .ai-main-row { gap: 20px 12px; }
  .direction-block, .ai-metric, .ai-summary { flex-basis: 42%; }
  .direction-block strong { font-size: 21px; }
  .ai-metric strong { font-size: 20px; }
  .ai-bottom-line { align-items: flex-start; flex-direction: column; }
  .metric-card { padding: 14px 12px; }
  .metric-card > strong { font-size: 24px; }
  .metric-card-head { gap: 6px; }
  .metric-card-head > small { font-size: 9px; }
  .terminal-footer { align-items: flex-start; flex-direction: column; padding: 12px; }
}
</style>
