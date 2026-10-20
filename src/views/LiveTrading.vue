<script setup>
import { computed, ref } from 'vue'

const instruments = [
  { id: 'BTCUSD', name: 'BTC', fullName: 'Bitcoin', symbol: 'BITSTAMP:BTCUSD', price: '67,842.50', change: '+1.28%', up: true, color: '#f4b860' },
  { id: 'ETHUSD', name: 'ETH', fullName: 'Ethereum', symbol: 'COINBASE:ETHUSD', price: '2,485.60', change: '+0.86%', up: true, color: '#9b9fff' },
  { id: 'XAUUSD', name: 'GOLD', fullName: '黄金现货', symbol: 'OANDA:XAUUSD', price: '4,365.80', change: '-0.32%', up: false, color: '#f3c66b' },
  { id: 'USOIL', name: 'WTI', fullName: 'WTI 原油', symbol: 'TVC:USOIL', price: '61.42', change: '+0.54%', up: true, color: '#65d9c0' },
  { id: 'XAGUSD', name: 'SILVER', fullName: '白银现货', symbol: 'OANDA:XAGUSD', price: '52.18', change: '-0.15%', up: false, color: '#b4c5dc' },
  { id: 'SOLUSD', name: 'SOL', fullName: 'Solana', symbol: 'COINBASE:SOLUSD', price: '184.26', change: '+2.14%', up: true, color: '#a98aff' }
]

const selectedInstrument = ref('XAUUSD')

const activeInstrument = computed(() =>
  instruments.find(item => item.id === selectedInstrument.value) || instruments[2]
)

function selectInstrument(item) {
  selectedInstrument.value = item.id
}

const tradingViewUrl = computed(() => {
  const params = new URLSearchParams({
    symbol: activeInstrument.value.symbol,
    interval: '5',
    theme: 'dark',
    style: '1',
    locale: 'zh_CN',
    timezone: 'Etc/UTC',
    withdateranges: '1',
    hide_side_toolbar: '0',
    allow_symbol_change: '1',
    saveimage: '0',
    calendar: '0',
    hideideas: '1'
  })

  return `https://www.tradingview.com/widgetembed/?${params.toString()}`
})

// 临时演示 K 线，后续接入真实行情和波段算法数据。
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

const waveCandles = computed(() =>
  candles.value.map((c, i) => ({
    ...c,
    x: 10 + i * 11.2,
    yHigh: 18 + (65 - c.high) * 4.1,
    yLow: 18 + (65 - c.low) * 4.1,
    yOpen: 18 + (65 - c.open) * 4.1,
    yClose: 18 + (65 - c.close) * 4.1
  }))
)
</script>

<template>
  <main class="live-page">
    <div class="ambient ambient-blue"></div>
    <div class="ambient ambient-purple"></div>

    <section class="terminal-frame">
      <!-- 行情滚动条 -->
      <section class="ticker-section">
        <div class="ticker-viewport">
          <div class="ticker-track">
            <button
              v-for="(item, index) in [...instruments, ...instruments]"
              :key="`${item.id}-${index}`"
              type="button"
              class="ticker-item"
              :class="{
                selected: selectedInstrument === item.id,
                'ticker-up': item.up,
                'ticker-down': !item.up
              }"
              @click="selectInstrument(item)"
            >
              <span class="ticker-symbol-icon" :style="{ color: item.color }">
                {{ item.name === 'GOLD' ? 'Au' : item.name.slice(0, 1) }}
              </span>

              <span class="ticker-info">
                <span class="ticker-name">{{ item.name }}</span>
                <span class="ticker-full-name">{{ item.fullName }}</span>
              </span>

              <span class="ticker-quote">
                <strong>{{ item.price }}</strong>
                <small>{{ item.change }}</small>
              </span>

              <span class="ticker-arrow">{{ item.up ? '↗' : '↘' }}</span>
            </button>
          </div>
        </div>
      </section>

      <!-- 三个指标保持在同一排 -->
      <section class="ai-panel">
        <div class="ai-main-row">
          <div class="direction-block">
            <small>波段方向</small>
            <strong class="direction-neutral">-- <span>待计算</span></strong>
          </div>

          <div class="ai-metric">
            <small>预测概率</small>
            <strong>--<span>%</span></strong>
            <div class="metric-track"><span class="track-blue"></span></div>
          </div>

          <div class="ai-metric">
            <small>波段进度</small>
            <strong>--<span>%</span></strong>
            <div class="metric-track"><span class="track-purple"></span></div>
          </div>
        </div>
      </section>

      <!-- TradingView 看盘 -->
      <section class="section-panel tradingview-panel">
        <div class="tradingview-container">
          <iframe
            :key="activeInstrument.symbol"
            :src="tradingViewUrl"
            :title="`${activeInstrument.id} TradingView M5 图表`"
            loading="lazy"
            allowfullscreen
            referrerpolicy="no-referrer-when-downgrade"
          ></iframe>
        </div>
      </section>

      <!-- 自研波段方向图 -->
      <section class="section-panel wave-panel">
        <div class="wave-chart">
          <div class="wave-grid">
            <div v-for="n in 6" :key="n" class="wave-grid-row"></div>
            <div v-for="n in 7" :key="`v-${n}`" class="wave-grid-col"></div>
          </div>

          <svg
            class="wave-candles"
            viewBox="0 0 560 300"
            preserveAspectRatio="none"
            role="img"
            aria-label="波段方向 K 线图"
          >
            <defs>
              <linearGradient id="waveGreen" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stop-color="#36f0c1" />
                <stop offset="100%" stop-color="#00a98f" />
              </linearGradient>
            </defs>

            <g v-for="c in waveCandles" :key="c.i">
              <line
                :x1="c.x"
                :x2="c.x"
                :y1="c.yHigh"
                :y2="c.yLow"
                :stroke="c.up ? '#36e9bd' : '#ff5b86'"
                stroke-width="1"
              />

              <rect
                :x="c.x - 3.1"
                :y="Math.min(c.yOpen, c.yClose)"
                width="6.2"
                :height="Math.max(2, Math.abs(c.yClose - c.yOpen))"
                :fill="c.up ? 'url(#waveGreen)' : '#ff5b86'"
                opacity=".88"
              />
            </g>
          </svg>

          <div class="wave-price-axis">
            <span>高点</span>
            <span>价格轴</span>
            <span>低点</span>
          </div>

          <div class="wave-time-axis">
            <span>历史走势</span>
            <span>当前波段</span>
          </div>

          <div class="wave-corner wave-corner-tl"></div>
          <div class="wave-corner wave-corner-br"></div>
        </div>
      </section>

      <!-- 实盘交易记录 -->
      <section class="section-panel history-panel">
        <div class="history-heading">
          <h2>实盘交易记录</h2>
        </div>

        <div class="history-overview">
          <strong class="history-description">真实成交记录</strong>
        </div>

        <div class="history-table-wrap">
          <table class="history-table">
            <thead>
              <tr>
                <th>开仓时间</th>
                <th>平仓时间</th>
                <th>交易品种</th>
                <th>方向</th>
                <th>手数</th>
                <th>开仓价格</th>
                <th>平仓价格</th>
                <th>盈亏 (USD)</th>
                <th>持仓时长</th>
              </tr>
            </thead>

            <tbody>
              <tr>
                <td colspan="9">
                  <div class="empty-history">
                    <span class="empty-history-icon">
                      <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
                        <rect x="4" y="3.5" width="16" height="17" rx="2" stroke="currentColor" stroke-width="1.4" />
                        <path d="M8 8h8M8 12h8M8 16h5" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" />
                      </svg>
                    </span>
                    <strong>暂无交易记录</strong>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </section>
  </main>
</template>

<style scoped>
.live-page {
  --blue: #426bff;
  --cyan: #00dfff;
  --purple: #a16bff;
  --line: var(--边框线条颜色, #222630);
  position: relative;
  isolation: isolate;
  min-height: calc(100vh - 74px);
  overflow: hidden;
  padding: 30px 24px 46px;
  color: var(--主要文字颜色, #fff);
  background: var(--主页面背景色, #0b0d12);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
}

.live-page::before {
  position: absolute;
  z-index: -1;
  inset: 0;
  content: "";
  pointer-events: none;
  opacity: .12;
  background-image:
    linear-gradient(rgba(55, 98, 180, .05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(55, 98, 180, .05) 1px, transparent 1px);
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
  opacity: .06;
}

.ambient-blue { top: 200px; left: -250px; background: #126bff; }
.ambient-purple { top: 780px; right: -260px; background: #9c3dff; }

.terminal-frame {
  position: relative;
  width: 100%;
  max-width: var(--页面最大宽度, 1320px);
  margin-inline: auto;
  border: 0;
  background: transparent;
  box-shadow: none;
}

.terminal-frame::before,
.terminal-frame::after {
  display: none;
}

/* 行情滚动条：无背景、无边框、无下划线 */
.ticker-section,
.ticker-viewport {
  padding: 0;
  margin: 0;
  overflow: hidden;
  border: 0;
  background: transparent;
}

.ticker-track {
  display: flex;
  width: max-content;
  animation: ticker-scroll 38s linear infinite;
}

.ticker-viewport:hover .ticker-track {
  animation-play-state: paused;
}

.ticker-item {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 245px;
  padding: 15px 18px;
  color: var(--主要文字颜色, #fff);
  text-align: left;
  border: 0;
  border-bottom: 0;
  outline: 0;
  background: transparent;
  box-shadow: none;
  cursor: pointer;
}

.ticker-item:hover,
.ticker-item.selected {
  border: 0;
  background: transparent;
  box-shadow: none;
}

.ticker-symbol-icon {
  display: grid;
  flex: 0 0 auto;
  width: 34px;
  height: 34px;
  place-items: center;
  border: 1px solid currentColor;
  border-radius: 50%;
  background: transparent;
  font-size: 12px;
  font-weight: 800;
}

.ticker-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 64px;
}

.ticker-name {
  color: var(--主要文字颜色, #fff);
  font-size: 11px;
  font-weight: 800;
  letter-spacing: .5px;
}

.ticker-full-name {
  color: var(--次要灰色文字, #848e9c);
  font-size: 9px;
}

.ticker-quote {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-left: auto;
  text-align: right;
}

.ticker-quote strong {
  color: var(--主要文字颜色, #fff);
  font-size: 11px;
  font-variant-numeric: tabular-nums;
}

.ticker-quote small { font-size: 10px; }

.ticker-up .ticker-quote small,
.ticker-up .ticker-arrow {
  color: var(--涨势绿色, #0ecb81);
}

.ticker-down .ticker-quote small,
.ticker-down .ticker-arrow {
  color: var(--跌势红色, #f6465d);
}

.ticker-arrow {
  align-self: flex-start;
  font-size: 14px;
}

@keyframes ticker-scroll {
  from { transform: translateX(0); }
  to { transform: translateX(-50%); }
}

/* 三项指标保持在同一排 */
.ai-panel {
  position: relative;
  padding: 20px 22px 14px;
  overflow: hidden;
  border: 0;
  background: transparent;
}

.ai-main-row {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  align-items: center;
  gap: 24px;
  min-height: 104px;
}

.direction-block,
.ai-metric {
  min-width: 0;
}

.direction-block small,
.ai-metric > small {
  display: block;
  color: var(--次要灰色文字, #848e9c);
  font-size: 10px;
}

.direction-block strong,
.ai-metric strong {
  display: block;
  margin-top: 8px;
  color: var(--主要文字颜色, #fff);
  font-size: 22px;
  font-weight: 700;
}

.direction-block strong span {
  margin-left: 6px;
  color: var(--次要灰色文字, #848e9c);
  font-size: 12px;
  font-weight: 500;
}

.ai-metric strong span {
  margin-left: 3px;
  color: var(--次要灰色文字, #848e9c);
  font-size: 12px;
}

.metric-track {
  width: 100%;
  max-width: 170px;
  height: 3px;
  margin-top: 9px;
  overflow: hidden;
  background: var(--边框线条颜色, #222630);
}

.metric-track span {
  display: block;
  width: 0;
  height: 100%;
}

.track-blue { background: var(--主色调蓝色, #315bff); }
.track-purple { background: #8b70ff; }

/* 图表 */
.section-panel {
  min-width: 0;
  padding: 20px;
  border: 0;
  background: transparent;
}

.tradingview-container {
  position: relative;
  width: 100%;
  height: clamp(420px, 49vw, 660px);
  min-height: 360px;
  overflow: hidden;
  border: 0;
  background: var(--表面卡片背景色, #141722);
}

.tradingview-container iframe {
  display: block;
  width: 100%;
  height: 100%;
  border: 0;
  background: var(--表面卡片背景色, #141722);
}

/* 自研波段 K 线图 */
.wave-panel { background: transparent; }

.wave-chart {
  position: relative;
  height: clamp(300px, 36vw, 450px);
  overflow: hidden;
  border: 0;
  background: var(--表面卡片背景色, #141722);
}

.wave-grid {
  position: absolute;
  inset: 0 54px 25px 0;
}

.wave-grid-row {
  height: 16.666%;
  border-bottom: 1px solid rgba(132, 142, 156, .12);
}

.wave-grid-col {
  position: absolute;
  top: 0;
  bottom: 0;
  width: 1px;
  background: rgba(132, 142, 156, .1);
}

.wave-grid-col:nth-of-type(7) { left: 15%; }
.wave-grid-col:nth-of-type(8) { left: 30%; }
.wave-grid-col:nth-of-type(9) { left: 45%; }
.wave-grid-col:nth-of-type(10) { left: 60%; }
.wave-grid-col:nth-of-type(11) { left: 75%; }
.wave-grid-col:nth-of-type(12) { left: 90%; }

.wave-candles {
  position: absolute;
  inset: 0 48px 25px 0;
  width: calc(100% - 48px);
  height: calc(100% - 25px);
}

.wave-price-axis {
  position: absolute;
  top: 8px;
  right: 8px;
  bottom: 35px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  color: var(--次要灰色文字, #848e9c);
  font-size: 8px;
}

.wave-time-axis {
  position: absolute;
  right: 60px;
  bottom: 8px;
  left: 12px;
  display: flex;
  justify-content: space-between;
  gap: 8px;
  color: var(--次要灰色文字, #848e9c);
  font-size: 9px;
}

.wave-corner {
  position: absolute;
  width: 12px;
  height: 12px;
  pointer-events: none;
}

.wave-corner-tl {
  top: 0;
  left: 0;
  border-top: 1px solid #a16bff;
  border-left: 1px solid #a16bff;
}

.wave-corner-br {
  right: 53px;
  bottom: 24px;
  border-right: 1px solid #a16bff;
  border-bottom: 1px solid #a16bff;
}

/* 实盘交易记录 */
.history-panel { padding-bottom: 16px; }

.history-heading {
  margin-bottom: 18px;
}

.history-heading h2 {
  color: var(--主要文字颜色, #fff);
  font-size: 14px;
  font-weight: 700;
}

.history-overview {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
}

.history-description {
  color: var(--次要灰色文字, #848e9c);
  font-size: 11px;
  font-weight: 500;
}

.history-table-wrap {
  width: 100%;
  overflow-x: auto;
  border: 1px solid var(--边框线条颜色, #222630);
  background: var(--表面卡片背景色, #141722);
}

.history-table {
  width: 100%;
  min-width: 850px;
  border-collapse: collapse;
  text-align: left;
}

.history-table th {
  height: 42px;
  padding: 0 13px;
  color: var(--次要灰色文字, #848e9c);
  border-bottom: 1px solid var(--边框线条颜色, #222630);
  background: transparent;
  font-size: 10px;
  font-weight: 600;
  white-space: nowrap;
}

.history-table td { padding: 0; }
.history-table tbody tr { height: 200px; }

.empty-history {
  display: flex;
  align-items: center;
  flex-direction: column;
  justify-content: center;
  gap: 10px;
  min-height: 200px;
  padding: 28px 12px;
  text-align: center;
}

.empty-history-icon {
  display: grid;
  width: 42px;
  height: 42px;
  place-items: center;
  color: var(--次要灰色文字, #848e9c);
  border: 1px solid var(--边框线条颜色, #222630);
  background: transparent;
}

.empty-history-icon svg {
  width: 21px;
  height: 21px;
}

.empty-history strong {
  color: var(--次要灰色文字, #848e9c);
  font-size: 12px;
}

@media (prefers-reduced-motion: reduce) {
  .ticker-track { animation: none; }
}

@media (min-width: 1600px) {
  .live-page { padding-inline: 36px; }
}

@media (max-width: 850px) {
  .live-page { padding: 24px 14px 34px; }
  .ai-main-row { gap: 16px; }
  .tradingview-container { height: 480px; }
  .wave-chart { height: 350px; }
  .section-panel { padding: 17px; }
}

@media (max-width: 520px) {
  .live-page { padding: 20px 9px 28px; }

  .ticker-item {
    min-width: 205px;
    padding: 13px 12px;
  }

  .ai-panel { padding: 16px 12px 12px; }
  .ai-main-row { gap: 12px; }
  .direction-block strong,
  .ai-metric strong { font-size: 18px; }

  .section-panel { padding: 14px 9px; }

  .tradingview-container {
    height: 430px;
    min-height: 350px;
  }

  .wave-chart { height: 280px; }
}
</style>
