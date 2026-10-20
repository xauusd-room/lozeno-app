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

// 以下 K 线仅用于搭建自研波段图的视觉结构，后续替换为真实算法数据。
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

const historyFilters = ['全部记录', '多单', '空单']
const activeHistoryFilter = ref('全部记录')
</script>

<template>
  <main class="live-page">
    <div class="ambient ambient-blue"></div>
    <div class="ambient ambient-purple"></div>

    <section class="terminal-frame">
      <!-- 行情滚动条：透明背景，无外边框 -->
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

      <!-- AI 分析数据区域：保留数据位置，删除标题和说明 -->
      <section class="ai-panel">
        <div class="ai-main-row">
          <div class="direction-block">
            <small>波段方向</small>
            <strong class="direction-neutral">-- <span>待计算</span></strong>
          </div>

          <div class="ai-divider"></div>

          <div class="ai-metric">
            <small>预测概率</small>
            <strong>--<span>%</span></strong>
            <div class="metric-track"><span class="track-blue"></span></div>
          </div>

          <div class="ai-divider"></div>

          <div class="ai-metric">
            <small>波段进度</small>
            <strong>--<span>%</span></strong>
            <div class="metric-track"><span class="track-purple"></span></div>
          </div>

          <div class="ai-divider"></div>

          <div class="ai-summary">
            <span class="summary-icon">⌁</span>
            <div>
              <small>分析状态</small>
              <strong>{{ activeInstrument.id }} · M5 · 等待数据</strong>
            </div>
          </div>
        </div>
      </section>

      <!-- TradingView 图表 -->
      <section class="section-panel tradingview-panel">
        <div class="panel-heading">
          <div class="panel-title">
            <span class="panel-index">01</span>
            <div>
              <h2>沉浸式看盘</h2>
              <p>TRADINGVIEW · INTERACTIVE CHART</p>
            </div>
          </div>

          <div class="chart-meta">
            <span class="selected-symbol">{{ activeInstrument.id }}</span>
            <span class="period-badge">M5</span>
          </div>
        </div>

        <div class="tradingview-toolbar">
          <div class="toolbar-instrument">
            <span class="instrument-dot"></span>
            <strong>{{ activeInstrument.fullName }}</strong>
            <span>{{ activeInstrument.id }}</span>
          </div>

          <div class="toolbar-right">
            <span class="toolbar-period-active">M5</span>
            <span class="toolbar-hint">5 分钟周期</span>
          </div>
        </div>

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

        <div class="chart-panel-footer">
          <span><i class="legend-tv"></i> TradingView 图表</span>
          <span>品种：{{ activeInstrument.id }}</span>
          <span>周期：M5</span>
        </div>
      </section>

      <!-- 自研波段方向 K 线 -->
      <section class="section-panel wave-panel">
        <div class="panel-heading">
          <div class="panel-title">
            <span class="panel-index purple-index">02</span>
            <div>
              <h2>波段方向分析</h2>
              <p>LOZENO · CUSTOM WAVE DIRECTION MODEL</p>
            </div>
          </div>

          <div class="chart-meta">
            <span class="selected-symbol">{{ activeInstrument.id }}</span>
            <span class="period-badge">M5</span>
            <span class="panel-badge purple-badge">演示图形</span>
          </div>
        </div>

        <div class="wave-toolbar">
          <div class="toolbar-instrument">
            <span class="instrument-dot purple-dot"></span>
            <strong>{{ activeInstrument.fullName }}</strong>
            <span>{{ activeInstrument.id }}</span>
          </div>

          <div class="wave-legend">
            <span><i class="legend-up"></i> 上涨 K 线</span>
            <span><i class="legend-down"></i> 下跌 K 线</span>
            <span><i class="legend-projection"></i> 预测区域预留</span>
          </div>
        </div>

        <div class="wave-chart">
          <div class="wave-watermark">LOZENO</div>
          <div class="wave-watermark-sub">WAVE DIRECTION · M5</div>

          <div class="wave-grid">
            <div v-for="n in 6" :key="n" class="wave-grid-row"></div>
            <div v-for="n in 7" :key="`v-${n}`" class="wave-grid-col"></div>
          </div>

          <svg
            class="wave-candles"
            viewBox="0 0 560 300"
            preserveAspectRatio="none"
            role="img"
            aria-label="自研波段方向图演示数据"
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
            <span>预测区域待接入</span>
          </div>

          <div class="wave-corner wave-corner-tl"></div>
          <div class="wave-corner wave-corner-br"></div>
        </div>

        <div class="wave-footer">
          <span><i class="legend-up"></i> 上涨 K 线</span>
          <span><i class="legend-down"></i> 下跌 K 线</span>
          <span class="footer-note">当前为布局演示数据，后续替换为真实 M5 行情和波段算法输出</span>
        </div>
      </section>

      <!-- 实盘交易记录 -->
      <section class="section-panel history-panel">
        <div class="panel-heading history-heading">
          <div class="panel-title">
            <span class="panel-index">03</span>
            <div>
              <h2>实盘交易记录</h2>
              <p>LIVE TRADE HISTORY · REAL EXECUTIONS</p>
            </div>
          </div>

          <span class="history-status"><i></i> 数据库待接入</span>
        </div>

        <div class="history-overview">
          <div class="history-description">
            <strong>真实成交记录</strong>
            <span>展示实际开仓、平仓及盈亏结果，不使用模拟交易记录。</span>
          </div>

          <div class="history-filters">
            <button
              v-for="filter in historyFilters"
              :key="filter"
              type="button"
              :class="{ active: activeHistoryFilter === filter }"
              @click="activeHistoryFilter = filter"
            >
              {{ filter }}
            </button>
          </div>
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
                    <span>接入真实交易数据库后，这里将展示实际成交历史。</span>
                    <small>TRADE HISTORY · WAITING FOR DATA SOURCE</small>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="history-table-footer">
          <span>记录来源：待配置</span>
          <span>当前显示 0 条记录</span>
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

/* 行情滚动栏：直接融入网页 */
.ticker-section {
  padding: 0;
  border: 0;
  background: transparent;
}

.ticker-viewport {
  margin-top: 0;
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
  background: transparent;
  cursor: pointer;
  transition: color .2s;
}

.ticker-item:hover {
  background: transparent;
}

.ticker-item.selected {
  background: transparent;
  box-shadow: inset 0 -2px var(--主色调蓝色, #315bff);
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

.ticker-quote small {
  font-size: 10px;
}

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

/* AI 数据区域 */
.ai-panel {
  position: relative;
  padding: 20px 22px 14px;
  overflow: hidden;
  border: 0;
  border-bottom: 1px solid var(--边框线条颜色, #222630);
  background: transparent;
}

.ai-panel::before {
  display: none;
}

.ai-main-row {
  display: flex;
  align-items: center;
  gap: 24px;
  min-height: 104px;
}

.direction-block { min-width: 150px; }

.direction-block small,
.ai-metric > small,
.ai-summary small {
  display: block;
  color: var(--次要灰色文字, #848e9c);
  font-size: 10px;
}

.direction-block strong {
  display: block;
  margin-top: 8px;
  color: var(--次要灰色文字, #848e9c);
  font-size: 24px;
}

.direction-block strong span {
  margin-left: 6px;
  font-size: 12px;
  font-weight: 500;
}

.ai-divider {
  width: 1px;
  height: 42px;
  background: var(--边框线条颜色, #222630);
}

.ai-metric {
  flex: 1;
  min-width: 100px;
}

.ai-metric strong {
  display: block;
  margin-top: 7px;
  color: var(--主要文字颜色, #fff);
  font-size: 22px;
  font-weight: 700;
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

.ai-summary {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 190px;
}

.summary-icon {
  color: var(--主色调蓝色, #315bff);
  font-size: 26px;
}

.ai-summary strong {
  display: block;
  margin-top: 7px;
  color: var(--次要灰色文字, #848e9c);
  font-size: 11px;
}

/* 图表区域：保留原有结构 */
.section-panel {
  min-width: 0;
  padding: 20px;
  border: 0;
  border-bottom: 1px solid var(--边框线条颜色, #222630);
  background: transparent;
}

.panel-heading,
.panel-title {
  display: flex;
  align-items: center;
}

.panel-heading {
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 16px;
}

.panel-title {
  gap: 11px;
  min-width: 0;
}

.panel-title h2 {
  color: var(--主要文字颜色, #fff);
  font-size: 14px;
  font-weight: 700;
  letter-spacing: .4px;
}

.panel-title p {
  margin-top: 5px;
  color: var(--次要灰色文字, #848e9c);
  font-size: 8px;
  letter-spacing: 1.2px;
}

.panel-index {
  color: var(--主色调蓝色, #315bff);
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 1px;
}

.purple-index { color: #a16bff; }

.chart-meta {
  display: flex;
  align-items: center;
  gap: 9px;
}

.selected-symbol {
  color: var(--主要文字颜色, #fff);
  font-size: 10px;
  font-weight: 700;
}

.period-badge {
  padding: 5px 9px;
  color: var(--主要文字颜色, #fff);
  border: 1px solid var(--边框线条颜色, #222630);
  background: transparent;
  font-size: 9px;
}

.panel-badge {
  padding: 5px 8px;
  font-size: 8px;
  letter-spacing: .7px;
}

.purple-badge {
  color: #bba3ff;
  border: 1px solid var(--边框线条颜色, #222630);
  background: transparent;
}

.tradingview-toolbar,
.wave-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  min-height: 39px;
  padding: 0 12px;
  border: 0;
  border-bottom: 1px solid var(--边框线条颜色, #222630);
  background: transparent;
}

.toolbar-instrument,
.toolbar-right,
.wave-legend {
  display: flex;
  align-items: center;
  gap: 10px;
}

.toolbar-instrument strong {
  color: var(--主要文字颜色, #fff);
  font-size: 11px;
}

.toolbar-instrument > span:last-child {
  color: var(--次要灰色文字, #848e9c);
  font-size: 10px;
}

.instrument-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--主色调蓝色, #315bff);
}

.purple-dot { background: #a16bff; }

.toolbar-period-active {
  padding: 5px 8px;
  color: var(--主要文字颜色, #fff);
  border: 1px solid var(--边框线条颜色, #222630);
  background: transparent;
  font-size: 10px;
}

.toolbar-hint {
  color: var(--次要灰色文字, #848e9c);
  font-size: 9px;
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

.chart-panel-footer,
.wave-footer {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 18px;
  min-height: 34px;
  color: var(--次要灰色文字, #848e9c);
  font-size: 9px;
}

.chart-panel-footer > span,
.wave-footer > span {
  display: flex;
  align-items: center;
  gap: 6px;
}

.legend-tv {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--主色调蓝色, #315bff);
}

.wave-panel {
  background: transparent;
}

.wave-toolbar {
  border-color: var(--边框线条颜色, #222630);
  background: transparent;
}

.wave-legend {
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 12px;
  color: var(--次要灰色文字, #848e9c);
  font-size: 9px;
}

.wave-legend span {
  display: flex;
  align-items: center;
  gap: 5px;
}

.legend-up,
.legend-down {
  display: inline-block;
  width: 6px;
  height: 6px;
}

.legend-up { background: var(--涨势绿色, #0ecb81); }
.legend-down { background: var(--跌势红色, #f6465d); }

.legend-projection {
  width: 14px;
  height: 0;
  border-top: 1px dashed #a16bff;
}

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

.wave-watermark {
  position: absolute;
  top: 37%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: rgba(132, 142, 156, .04);
  font-size: 50px;
  font-weight: 900;
  letter-spacing: 9px;
  pointer-events: none;
}

.wave-watermark-sub {
  position: absolute;
  top: calc(37% + 31px);
  left: 50%;
  transform: translateX(-50%);
  color: rgba(132, 142, 156, .14);
  font-size: 8px;
  letter-spacing: 2px;
  white-space: nowrap;
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

.wave-footer .footer-note {
  margin-left: auto;
  color: var(--次要灰色文字, #848e9c);
}

/* 历史交易记录 */
.history-panel { padding-bottom: 16px; }
.history-heading { margin-bottom: 18px; }

.history-status {
  display: flex;
  align-items: center;
  gap: 7px;
  color: #c5a968;
  font-size: 9px;
  white-space: nowrap;
}

.history-status i {
  flex: 0 0 auto;
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #c5a968;
}

.history-overview {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  margin-bottom: 15px;
}

.history-description {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.history-description strong {
  color: var(--主要文字颜色, #fff);
  font-size: 11px;
}

.history-description span {
  color: var(--次要灰色文字, #848e9c);
  font-size: 10px;
}

.history-filters {
  display: flex;
  gap: 5px;
}

.history-filters button {
  padding: 7px 12px;
  color: var(--次要灰色文字, #848e9c);
  border: 1px solid var(--边框线条颜色, #222630);
  border-radius: var(--小圆角, 6px);
  background: transparent;
  font-size: 10px;
  cursor: pointer;
  transition: color .2s, border-color .2s;
}

.history-filters button:hover {
  color: var(--主要文字颜色, #fff);
  border-color: var(--主色调蓝色, #315bff);
}

.history-filters button.active {
  color: var(--主要文字颜色, #fff);
  border-color: var(--主色调蓝色, #315bff);
  background: transparent;
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
.history-table tbody tr { height: 230px; }

.empty-history {
  display: flex;
  align-items: center;
  flex-direction: column;
  justify-content: center;
  gap: 10px;
  min-height: 230px;
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
  color: var(--主要文字颜色, #fff);
  font-size: 12px;
}

.empty-history > span:not(.empty-history-icon) {
  color: var(--次要灰色文字, #848e9c);
  font-size: 10px;
}

.empty-history small {
  margin-top: 4px;
  color: var(--次要灰色文字, #848e9c);
  font-size: 8px;
  letter-spacing: 1.3px;
}

.history-table-footer {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  padding-top: 12px;
  color: var(--次要灰色文字, #848e9c);
  font-size: 9px;
}

@media (prefers-reduced-motion: reduce) {
  .ticker-track { animation: none; }
}

@media (min-width: 1600px) {
  .live-page { padding-inline: 36px; }
}

@media (max-width: 1100px) {
  .ai-main-row { gap: 15px; }
  .direction-block { min-width: 120px; }
  .ai-summary { min-width: 150px; }
  .ticker-item { min-width: 220px; }
  .section-panel { padding: 17px; }
}

@media (max-width: 850px) {
  .live-page { padding: 24px 14px 34px; }

  .ai-main-row {
    flex-wrap: wrap;
    padding-block: 18px;
  }

  .ai-divider { display: none; }

  .direction-block,
  .ai-metric,
  .ai-summary {
    flex: 1 1 38%;
    min-width: 130px;
  }

  .tradingview-container { height: 480px; }
  .wave-chart { height: 350px; }

  .history-overview {
    align-items: flex-start;
    flex-direction: column;
  }

  .history-filters { width: 100%; }
  .history-filters button { flex: 1; }
}

@media (max-width: 520px) {
  .live-page { padding: 20px 9px 28px; }

  .ticker-item {
    min-width: 205px;
    padding: 13px 12px;
  }

  .ai-panel { padding: 16px 12px 12px; }

  .ai-main-row { gap: 20px 12px; }

  .direction-block,
  .ai-metric,
  .ai-summary {
    flex-basis: 42%;
  }

  .direction-block strong { font-size: 21px; }
  .ai-metric strong { font-size: 20px; }

  .section-panel { padding: 14px 9px; }

  .panel-title { gap: 8px; }
  .panel-title h2 { font-size: 12px; }
  .panel-title p { font-size: 7px; letter-spacing: .7px; }

  .chart-meta { gap: 5px; }
  .selected-symbol { font-size: 9px; }
  .panel-badge { display: none; }

  .tradingview-toolbar,
  .wave-toolbar {
    align-items: flex-start;
    flex-direction: column;
    justify-content: center;
    gap: 9px;
    padding-block: 10px;
  }

  .tradingview-container {
    height: 430px;
    min-height: 350px;
  }

  .wave-chart { height: 280px; }

  .wave-legend {
    justify-content: flex-start;
    font-size: 8px;
  }

  .wave-footer { gap: 10px; }

  .wave-footer .footer-note {
    width: 100%;
    margin-left: 0;
  }

  .history-overview { gap: 12px; }

  .history-description span { line-height: 1.6; }

  .history-table-footer { flex-direction: column; }
}
</style>
