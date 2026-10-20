
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


.live-page {
  --gold: #c8a96e;
  --gold-bright: #e6c98e;
  --gold-muted: #8e7549;
  --bg: #090909;
  --surface: #10100f;
  --surface-raised: #151412;
  --line: rgba(200, 169, 110, .16);
  --text: #eee9df;
  --muted: #89847a;

  position: relative;
  isolation: isolate;
  min-height: calc(100vh - 74px);
  overflow: hidden;
  padding: 34px 28px 48px;
  color: var(--text);
  background:
    radial-gradient(ellipse at 50% -15%, rgba(174, 133, 59, .09), transparent 48%),
    #090909;
  font-family: Inter, "Segoe UI", "Microsoft YaHei", sans-serif;
}

.live-page::before {
  position: absolute;
  z-index: -1;
  inset: 0;
  content: "";
  pointer-events: none;
  opacity: .15;
  background-image: linear-gradient(rgba(200,169,110,.035) 1px, transparent 1px);
  background-size: 100% 46px;
  mask-image: linear-gradient(to bottom, #000, transparent 78%);
}

.ambient {
  position: absolute;
  z-index: -1;
  width: 320px;
  height: 320px;
  border-radius: 50%;
  filter: blur(120px);
  pointer-events: none;
  opacity: .045;
}

.ambient-blue {
  top: 180px;
  left: -240px;
  background: #d4a84e;
}

.ambient-purple {
  top: 500px;
  right: -250px;
  background: #b68b42;
}

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
  margin-bottom: 28px;
}

.eyebrow {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #a28b62;
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 3px;
}

.eyebrow-line {
  width: 24px;
  height: 1px;
  background: var(--gold);
}

.live-heading h1 {
  margin-top: 13px;
  color: #f0ece4;
  font-family: "Times New Roman", "Songti SC", serif;
  font-size: clamp(30px, 3vw, 40px);
  font-weight: 500;
  letter-spacing: 5px;
}

.live-heading h1 > span {
  margin-left: 10px;
  color: var(--gold-bright);
  text-shadow: none;
}

.title-dot {
  display: inline-block;
  width: 5px;
  height: 5px;
  margin-left: 13px;
  vertical-align: top;
  background: var(--gold);
}

.heading-subtitle {
  margin-top: 10px;
  color: #69645b;
  font-size: 9px;
  letter-spacing: 2.5px;
}

.system-status {
  display: flex;
  align-items: center;
  gap: 13px;
  min-width: 310px;
  padding: 15px 18px;
  border: 1px solid var(--line);
  background: linear-gradient(135deg, #141310, #0d0d0c);
}

.status-light {
  flex: 0 0 auto;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #b99350;
  box-shadow: 0 0 8px rgba(185,147,80,.22);
}

.system-status strong,
.system-status small,
.system-clock strong,
.system-clock small {
  display: block;
}

.system-status strong {
  color: #e2d8c4;
  font-size: 12px;
  font-weight: 500;
}

.system-status small {
  margin-top: 5px;
  color: #6d675c;
  font-size: 9px;
  letter-spacing: 1px;
}

.status-divider {
  width: 1px;
  height: 30px;
  margin-inline: 6px;
  background: #353027;
}

.system-clock {
  margin-left: auto;
}

.system-clock strong {
  margin-top: 5px;
  color: var(--gold);
  font-size: 12px;
  font-weight: 500;
}

.terminal-frame {
  position: relative;
  border: 1px solid rgba(200,169,110,.24);
  background: #0b0b0a;
  box-shadow: 0 18px 65px rgba(0,0,0,.28);
}

.terminal-frame::before,
.terminal-frame::after {
  position: absolute;
  width: 35px;
  height: 1px;
  content: "";
  background: var(--gold);
  opacity: .8;
  pointer-events: none;
}

.terminal-frame::before {
  top: -1px;
  left: 25px;
}

.terminal-frame::after {
  right: 25px;
  bottom: -1px;
}

.frame-topline {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  min-height: 39px;
  padding: 0 20px;
  border-bottom: 1px solid #25221b;
  background: #11100e;
}

.corner-label {
  color: #a99b7c;
  font-size: 9px;
  font-weight: 600;
  letter-spacing: 1.8px;
}

.corner-label i {
  display: inline-block;
  width: 5px;
  height: 5px;
  margin-right: 8px;
  background: var(--gold);
}

.corner-label b {
  margin-left: 7px;
  color: var(--gold);
}

.frame-caption {
  color: #625c50;
  font-size: 8px;
  letter-spacing: 1.5px;
}

.demo-state {
  color: #b99a60;
  font-size: 10px;
}

.market-strip {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 22px;
  padding: 19px 22px;
  border-bottom: 1px solid #25221b;
  background: linear-gradient(100deg, #13120f, #0e0e0c);
}

.instrument {
  display: flex;
  align-items: center;
  gap: 13px;
  min-width: 230px;
  margin-right: auto;
}

.gold-icon {
  display: grid;
  width: 42px;
  height: 42px;
  place-items: center;
  color: #e7ca8e;
  font-family: "Times New Roman", serif;
  font-size: 17px;
  border: 1px solid rgba(200,169,110,.42);
  background: linear-gradient(145deg, #302617, #17140f);
}

.instrument strong {
  display: block;
  color: #e9e3d7;
  font-size: 13px;
  font-weight: 600;
  letter-spacing: .7px;
}

.instrument strong span {
  color: #938a79;
  font-weight: 400;
}

.instrument small,
.strip-metric small {
  display: block;
  margin-top: 6px;
  color: #777064;
  font-size: 10px;
}

.strip-metric {
  min-width: 104px;
  padding-left: 18px;
  border-left: 1px solid #302b21;
}

.strip-metric strong {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 7px;
  color: #d5cbb8;
  font-size: 12px;
  font-weight: 500;
  white-space: nowrap;
}

.metric-tag {
  color: #887a60;
  font-size: 8px;
  letter-spacing: 1px;
}

.mini-dot {
  flex: 0 0 auto;
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

.mini-dot.offline {
  background: #b99451;
}

.mini-dot.purple {
  background: #a99571;
}

.muted {
  color: #777064;
  font-size: 10px;
  font-weight: 400;
}

.charts-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.12fr) minmax(0, .88fr);
  gap: 1px;
  border-bottom: 1px solid #29251d;
  background: #29251d;
}

.chart-panel {
  min-width: 0;
  padding: 21px 19px 14px;
  background: #0d0d0b;
}

.panel-heading,
.panel-title,
.chart-footer,
.chart-toolbar {
  display: flex;
  align-items: center;
}

.panel-heading {
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 17px;
}

.panel-title {
  gap: 12px;
  min-width: 0;
}

.panel-index {
  color: #b79a62;
  font-family: "Times New Roman", serif;
  font-size: 13px;
}

.purple-index {
  color: #b79a62;
}

.panel-title h2 {
  color: #e8e1d4;
  font-size: 14px;
  font-weight: 500;
  letter-spacing: .7px;
}

.panel-title p {
  margin-top: 5px;
  color: #716a5e;
  font-size: 8px;
  letter-spacing: 1.2px;
}

.panel-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 5px 8px;
  font-size: 8px;
  letter-spacing: 1px;
}

.blue-badge,
.purple-badge {
  color: #c3a66d;
  border: 1px solid rgba(200,169,110,.26);
  background: rgba(200,169,110,.045);
}

.panel-badge i {
  flex: 0 0 auto;
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: #bda16a;
}

.chart-toolbar {
  min-height: 35px;
  gap: 11px;
  padding: 0 11px;
  border: 1px solid #302b21;
  border-bottom: 0;
  background: #12110e;
}

.toolbar-symbol {
  color: #c9b995;
  font-size: 10px;
  font-weight: 600;
}

.toolbar-divider {
  width: 1px;
  height: 13px;
  background: #393124;
}

.toolbar-period {
  color: #c6a76b;
  font-size: 10px;
}

.toolbar-spacer {
  flex: 1;
}

.ohlc-label {
  color: #746c5c;
  font-size: 8px;
}

.ohlc-label b {
  color: #bdb19a;
  font-weight: 400;
}

.chart-area {
  position: relative;
  height: clamp(230px, 25vw, 320px);
  overflow: hidden;
  border: 1px solid #302b21;
  background:
    radial-gradient(ellipse at 48% 42%, rgba(167,129,60,.045), transparent 68%),
    #0a0a09;
}

.history-chart-area {
  background:
    radial-gradient(ellipse at 48% 42%, rgba(167,129,60,.055), transparent 68%),
    #0a0a09;
}

.chart-grid-lines {
  position: absolute;
  inset: 0 48px 20px 0;
}

.horizontal-grid {
  position: relative;
  height: 20%;
  border-bottom: 1px solid rgba(200,169,110,.085);
}

.horizontal-grid span {
  position: absolute;
  top: -6px;
  right: -47px;
  width: 42px;
  color: #766d5b;
  font-size: 8px;
  text-align: right;
}

.vertical-grid {
  position: absolute;
  top: 0;
  bottom: 0;
  width: 1px;
  background: rgba(200,169,110,.055);
}

.vertical-grid:nth-of-type(2) { left: 15%; }
.vertical-grid:nth-of-type(3) { left: 30%; }
.vertical-grid:nth-of-type(4) { left: 45%; }
.vertical-grid:nth-of-type(5) { left: 60%; }
.vertical-grid:nth-of-type(6) { left: 75%; }
.vertical-grid:nth-of-type(7) { left: 90%; }

.candlestick-svg {
  position: absolute;
  inset: 0 42px 20px 0;
  width: calc(100% - 42px);
  height: calc(100% - 20px);
  overflow: visible;
}

.chart-watermark {
  position: absolute;
  top: 36%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: rgba(200,169,110,.045);
  font-family: "Times New Roman", serif;
  font-size: 38px;
  font-weight: 600;
  letter-spacing: 8px;
  pointer-events: none;
}

.chart-watermark-sub {
  position: absolute;
  top: calc(36% + 25px);
  left: 50%;
  transform: translateX(-50%);
  color: rgba(200,169,110,.14);
  font-size: 7px;
  letter-spacing: 2px;
  white-space: nowrap;
}

.chart-price-line {
  position: absolute;
  top: 47%;
  left: 0;
  right: 43px;
  border-top: 1px dashed rgba(200,169,110,.25);
}

.chart-price-line span {
  position: absolute;
  top: -8px;
  right: -43px;
  padding: 3px 4px;
  color: #17120a;
  background: #c8a96e;
  font-size: 7px;
}

.chart-time-labels {
  position: absolute;
  right: 48px;
  bottom: 5px;
  left: 8px;
  display: flex;
  justify-content: space-between;
  color: #716957;
  font-size: 8px;
}

.chart-corner {
  position: absolute;
  width: 10px;
  height: 10px;
  pointer-events: none;
}

.chart-corner-tl {
  top: 0;
  left: 0;
  border-top: 1px solid #a78b55;
  border-left: 1px solid #a78b55;
}

.chart-corner-br {
  right: 42px;
  bottom: 19px;
  border-right: 1px solid #a78b55;
  border-bottom: 1px solid #a78b55;
}

.purple-corner {
  border-color: #a78b55;
}

.chart-footer {
  flex-wrap: wrap;
  gap: 16px;
  min-height: 30px;
  color: #8b806c;
  font-size: 9px;
}

.chart-footer > span {
  display: flex;
  align-items: center;
  gap: 6px;
}

.legend-up,
.legend-down,
.legend-purple {
  display: inline-block;
  width: 6px;
  height: 6px;
}

.legend-up { background: #4eb69a; }
.legend-down { background: #b76c70; }
.legend-purple { background: #c1a36a; }

.chart-footer .footer-note {
  margin-left: auto;
  color: #716858;
  font-size: 8px;
}

.history-summary {
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-height: 47px;
  margin: -3px 0 12px;
  padding: 0 11px;
  border-left: 1px solid #b89b63;
  background: linear-gradient(90deg, rgba(200,169,110,.075), transparent);
}

.history-summary small {
  display: block;
  color: #8c806b;
  font-size: 9px;
}

.history-summary strong {
  display: block;
  margin-top: 5px;
  color: #c8b48d;
  font-size: 11px;
  font-weight: 500;
}

.match-decoration {
  display: flex;
  align-items: center;
  gap: 3px;
}

.match-decoration > span {
  display: block;
  width: 3px;
  height: 12px;
  background: #9d8250;
  opacity: .75;
}

.match-decoration > span:nth-child(2),
.match-decoration > span:nth-child(4) {
  height: 19px;
}

.match-decoration > span:nth-child(3) {
  height: 25px;
  background: #d0b477;
}

.match-decoration small {
  margin-left: 8px;
  font-size: 7px;
  letter-spacing: 1px;
}

.history-scan {
  position: absolute;
  top: 0;
  bottom: 20px;
  left: 18%;
  width: 22%;
  background: linear-gradient(90deg, transparent, rgba(200,169,110,.025), transparent);
  pointer-events: none;
}

.ai-panel {
  position: relative;
  padding: 21px 23px 14px;
  overflow: hidden;
  border-bottom: 1px solid #29251d;
  background: linear-gradient(105deg, #15130f, #0e0e0c 72%);
}

.ai-panel::before {
  position: absolute;
  top: 0;
  left: 0;
  width: 23%;
  height: 1px;
  content: "";
  background: linear-gradient(90deg, #d1b174, transparent);
}

.ai-panel-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(200,169,110,.14);
}

.ai-emblem {
  display: grid;
  width: 34px;
  height: 34px;
  place-items: center;
  border: 1px solid rgba(200,169,110,.42);
  background: linear-gradient(145deg, rgba(200,169,110,.13), rgba(200,169,110,.025));
}

.ai-emblem span {
  color: #d5b879;
  font-family: "Times New Roman", serif;
  font-size: 12px;
  font-weight: 600;
}

.ai-waiting {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #a0937b;
  font-size: 10px;
}

.ai-waiting i {
  flex: 0 0 auto;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #ad8e53;
}

.ai-main-row {
  display: flex;
  align-items: center;
  gap: 24px;
  min-height: 104px;
}

.direction-block {
  min-width: 150px;
}

.direction-block small,
.ai-metric small,
.ai-summary small {
  display: block;
  color: #918570;
  font-size: 10px;
}

.direction-block strong {
  display: block;
  margin-top: 8px;
  color: #c5b99f;
  font-size: 24px;
  font-weight: 500;
}

.direction-block strong span {
  margin-left: 6px;
  font-size: 12px;
  font-weight: 400;
}

.ai-divider {
  width: 1px;
  height: 42px;
  background: linear-gradient(transparent, #51432b, transparent);
}

.ai-metric {
  flex: 1;
  min-width: 100px;
}

.ai-metric strong {
  display: block;
  margin-top: 7px;
  color: #e4d7bd;
  font-size: 22px;
  font-weight: 500;
}

.ai-metric strong span {
  margin-left: 3px;
  color: #a99b80;
  font-size: 12px;
}

.metric-track {
  width: 100%;
  max-width: 170px;
  height: 2px;
  margin-top: 10px;
  overflow: hidden;
  background: #30291d;
}

.metric-track span {
  display: block;
  width: 0;
  height: 100%;
}

.track-blue {
  background: #c5a367;
}

.track-purple {
  background: #bca16c;
}

.ai-summary {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 180px;
}

.summary-icon {
  color: #c6a96e;
  font-size: 26px;
}

.ai-summary strong {
  display: block;
  margin-top: 7px;
  color: #c6b99f;
  font-size: 11px;
  font-weight: 400;
}

.ai-bottom-line {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding-top: 10px;
  border-top: 1px solid rgba(200,169,110,.11);
  color: #81745e;
  font-size: 8px;
  letter-spacing: .6px;
}

.ai-bottom-line b {
  margin-left: 7px;
  color: #c2a46a;
  font-weight: 500;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 1px;
  background: #29251d;
  border-bottom: 1px solid #29251d;
}

.metric-card {
  position: relative;
  min-width: 0;
  padding: 19px 21px 20px;
  overflow: hidden;
  background: linear-gradient(145deg, #13120f, #0c0c0b);
}

.metric-card-head {
  display: flex;
  align-items: center;
  gap: 9px;
}

.metric-card-head > small {
  color: #b1a58e;
  font-size: 10px;
}

.metric-icon {
  display: grid;
  width: 25px;
  height: 25px;
  place-items: center;
  font-size: 15px;
  border: 1px solid currentColor;
  background: rgba(255,255,255,.01);
}

.cyan-icon,
.green-icon,
.purple-icon,
.pink-icon {
  color: #c1a168;
}

.card-index {
  margin-left: auto;
  color: #6f624a;
  font-size: 8px;
}

.metric-card > strong {
  display: block;
  margin-top: 18px;
  color: #e6ddca;
  font-family: "Times New Roman", "Microsoft YaHei", serif;
  font-size: 29px;
  font-weight: 500;
  letter-spacing: .5px;
}

.metric-card > strong small {
  color: #9b8d73;
  font-family: Inter, sans-serif;
  font-size: 10px;
  font-weight: 400;
}

.metric-card > p {
  margin-top: 7px;
  color: #786d59;
  font-size: 8px;
  letter-spacing: 1.2px;
}

.metric-card-line {
  position: absolute;
  right: 15%;
  bottom: 0;
  left: 15%;
  height: 1px;
  opacity: .7;
}

.cyan-line,
.green-line,
.purple-line,
.pink-line {
  background: linear-gradient(90deg, transparent, #b79a62, transparent);
}

.terminal-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  min-height: 45px;
  padding: 0 19px;
  background: #0a0a09;
}

.footer-brand {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #c7b58e;
  font-size: 9px;
  font-weight: 600;
  letter-spacing: 1.5px;
}

.footer-brand-mark {
  display: grid;
  width: 18px;
  height: 18px;
  place-items: center;
  color: #171108;
  font-family: "Times New Roman", serif;
  font-size: 11px;
  background: linear-gradient(135deg, #e0c78d, #a58448);
}

.footer-separator {
  color: #51432d;
}

.footer-center {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #726650;
  font-size: 8px;
  letter-spacing: 1px;
}

.footer-pulse {
  flex: 0 0 auto;
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: #b39a66;
}

.footer-version {
  color: #766a54;
  font-size: 8px;
  letter-spacing: 1px;
}

.footer-version b {
  margin-left: 6px;
  color: #b9a477;
  font-weight: 400;
}

@media (min-width: 1600px) {
  .live-page {
    padding-inline: 36px;
  }
}

@media (max-width: 1100px) {
  .market-strip {
    gap: 16px;
  }

  .instrument {
    min-width: 190px;
  }

  .strip-metric {
    min-width: auto;
    padding-left: 12px;
  }

  .ai-main-row {
    gap: 15px;
  }

  .direction-block {
    min-width: 120px;
  }

  .ai-summary {
    min-width: 150px;
  }
}

@media (max-width: 850px) {
  .live-page {
    padding: 24px 14px 34px;
  }

  .live-heading {
    align-items: flex-start;
    flex-direction: column;
  }

  .system-status {
    width: 100%;
    min-width: 0;
  }

  .charts-grid {
    grid-template-columns: minmax(0, 1fr);
  }

  .chart-area {
    height: 280px;
  }

  .history-panel {
    border-top: 1px solid #29251d;
  }

  .ai-main-row {
    flex-wrap: wrap;
    padding-block: 18px;
  }

  .ai-divider {
    display: none;
  }

  .direction-block,
  .ai-metric,
  .ai-summary {
    flex: 1 1 38%;
    min-width: 130px;
  }

  .metrics-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .update-metric {
    display: none;
  }
}

@media (max-width: 520px) {
  .live-page {
    padding-inline: 10px;
  }

  .heading-subtitle {
    font-size: 8px;
    letter-spacing: 1.2px;
  }

  .live-heading h1 {
    letter-spacing: 3px;
  }

  .system-status {
    padding: 12px;
  }

  .frame-topline {
    padding-inline: 10px;
  }

  .frame-caption {
    display: none;
  }

  .market-strip {
    gap: 13px;
    padding: 13px 12px;
  }

  .instrument {
    width: 100%;
  }

  .strip-metric {
    flex: 1;
    padding-left: 10px;
  }

  .chart-panel {
    padding: 14px 10px 10px;
  }

  .chart-area {
    height: 230px;
  }

  .chart-toolbar {
    gap: 7px;
    padding-inline: 7px;
  }

  .ohlc-label:nth-last-child(-n+2) {
    display: none;
  }

  .chart-footer {
    gap: 10px;
  }

  .chart-footer .footer-note {
    width: 100%;
    margin-left: 0;
  }

  .ai-panel {
    padding: 16px 12px 12px;
  }

  .ai-main-row {
    gap: 20px 12px;
  }

  .direction-block,
  .ai-metric,
  .ai-summary {
    flex-basis: 42%;
  }

  .direction-block strong {
    font-size: 21px;
  }

  .ai-metric strong {
    font-size: 20px;
  }

  .ai-bottom-line {
    align-items: flex-start;
    flex-direction: column;
  }

  .metric-card {
    padding: 14px 12px;
  }

  .metric-card > strong {
    font-size: 24px;
  }

  .metric-card-head {
    gap: 6px;
  }

  .metric-card-head > small {
    font-size: 9px;
  }

  .terminal-footer {
    align-items: flex-start;
    flex-direction: column;
    padding: 12px;
  }
}

</style>
