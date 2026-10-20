
<script setup>
import { computed, ref, onMounted, onBeforeUnmount, nextTick, watch } from 'vue'
import { createChart, CandlestickSeries, createSeriesMarkers } from 'lightweight-charts'

const API_BASE = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/, '')
const CANDLE_URL = `${API_BASE}/api/market/candles`
const TICK_URL = `${API_BASE}/api/market/tick`
const TRADES_URL = `${API_BASE}/api/trades`

const instruments = [
  { id: 'BTCUSD', name: 'BTC', fullName: 'Bitcoin', price: '--', change: '--', up: true, color: '#f4b860' },
  { id: 'ETHUSD', name: 'ETH', fullName: 'Ethereum', price: '--', change: '--', up: true, color: '#9b9fff' },
  { id: 'XAUUSD', name: 'GOLD', fullName: '黄金现货', price: '--', change: '--', up: true, color: '#f3c66b' },
  { id: 'USOIL', name: 'WTI', fullName: 'WTI 原油', price: '--', change: '--', up: true, color: '#65d9c0' },
  { id: 'XAGUSD', name: 'SILVER', fullName: '白银现货', price: '--', change: '--', up: true, color: '#b4c5dc' },
  { id: 'SOLUSD', name: 'SOL', fullName: 'Solana', price: '--', change: '--', up: true, color: '#a98aff' }
]

const selectedInstrument = ref('XAUUSD')
const activeInstrument = computed(() =>
  instruments.find(item => item.id === selectedInstrument.value) || instruments[2]
)
const dataSymbol = computed(() =>
  selectedInstrument.value === 'XAUUSD' ? 'XAUUSD.cn' : selectedInstrument.value
)

const candles = ref([])
const trades = ref([])
const latestTick = ref(null)
const loading = ref(true)
const dataError = ref('')
const chartHost = ref(null)

let chart = null
let candleSeries = null
let markerSeries = null
let resizeObserver = null
let candleTimer = null
let tickTimer = null
let tradeTimer = null
let requestVersion = 0
let destroyed = false

function selectInstrument(item) {
  if (selectedInstrument.value !== item.id) {
    selectedInstrument.value = item.id
  }
}

function toUnixTime(value) {
  if (typeof value === 'number') {
    return Math.floor(value > 1e12 ? value / 1000 : value)
  }
  if (typeof value === 'string') {
    const numeric = Number(value)
    if (Number.isFinite(numeric) && value.trim() !== '') {
      return Math.floor(numeric > 1e12 ? numeric / 1000 : numeric)
    }
    const parsed = Date.parse(value)
    if (Number.isFinite(parsed)) return Math.floor(parsed / 1000)
  }
  return null
}

function normalizeCandle(item) {
  const time = toUnixTime(item.time ?? item.timestamp ?? item.datetime)
  const open = Number(item.open)
  const high = Number(item.high)
  const low = Number(item.low)
  const close = Number(item.close)

  if (
    time === null ||
    ![open, high, low, close].every(Number.isFinite) ||
    high < low
  ) return null

  return { time, open, high, low, close }
}

function responseRows(payload) {
  if (Array.isArray(payload)) return payload
  if (Array.isArray(payload?.data)) return payload.data
  if (Array.isArray(payload?.candles)) return payload.candles
  if (Array.isArray(payload?.trades)) return payload.trades
  return []
}

async function fetchJson(url) {
  const response = await fetch(url, {
    cache: 'no-store',
    headers: { Accept: 'application/json' }
  })
  if (!response.ok) throw new Error(`HTTP ${response.status}`)
  return response.json()
}

function initChart() {
  if (!chartHost.value || chart || destroyed) return

  chart = createChart(chartHost.value, {
    width: chartHost.value.clientWidth || 800,
    height: chartHost.value.clientHeight || 500,
    layout: {
      background: { color: '#141722' },
      textColor: '#848e9c',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif',
      fontSize: 11
    },
    grid: {
      vertLines: { color: 'rgba(132,142,156,0.10)' },
      horzLines: { color: 'rgba(132,142,156,0.10)' }
    },
    rightPriceScale: {
      borderVisible: false,
      scaleMargins: { top: 0.08, bottom: 0.08 }
    },
    timeScale: {
      borderVisible: false,
      timeVisible: true,
      secondsVisible: false,
      rightOffset: 2,
      barSpacing: 8,
      fixLeftEdge: true,
      fixRightEdge: true
    },
    crosshair: {
      vertLine: { visible: false, labelVisible: false },
      horzLine: { visible: false, labelVisible: false }
    },
    handleScroll: false,
    handleScale: false,
    kineticScroll: { mouse: false, touch: false },
    watermark: { visible: false }
  })

  candleSeries = chart.addSeries(CandlestickSeries, {
    upColor: '#0ecb81',
    downColor: '#f6465d',
    borderUpColor: '#0ecb81',
    borderDownColor: '#f6465d',
    wickUpColor: '#0ecb81',
    wickDownColor: '#f6465d',
    priceLineVisible: false,
    lastValueVisible: true
  })

  markerSeries = createSeriesMarkers(candleSeries, [])

  resizeObserver = new ResizeObserver(entries => {
    if (!chart || !entries.length) return
    const { width, height } = entries[0].contentRect
    chart.applyOptions({
      width: Math.max(1, Math.floor(width)),
      height: Math.max(1, Math.floor(height))
    })
  })
  resizeObserver.observe(chartHost.value)
}

function tradeTime(trade, type) {
  const value = type === 'open'
    ? trade.open_time ?? trade.opened_at ?? trade.entry_time
    : trade.close_time ?? trade.closed_at ?? trade.exit_time

  return toUnixTime(value)
}

function tradeDirection(trade) {
  const value = String(trade.direction ?? trade.type ?? trade.side ?? '').toLowerCase()
  return ['buy', 'long', '多', '多单', '0'].includes(value) ? 'buy' : 'sell'
}

function buildMarkers() {
  const result = []

  for (const trade of trades.value) {
    const direction = tradeDirection(trade)
    const openTime = tradeTime(trade, 'open')
    const closeTime = tradeTime(trade, 'close')
    const openPrice = Number(trade.open_price ?? trade.entry_price)
    const closePrice = Number(trade.close_price ?? trade.exit_price)

    if (openTime !== null && Number.isFinite(openPrice)) {
      result.push({
        time: openTime,
        position: direction === 'buy' ? 'belowBar' : 'aboveBar',
        color: direction === 'buy' ? '#0ecb81' : '#f6465d',
        shape: direction === 'buy' ? 'arrowUp' : 'arrowDown',
        text: `${direction === 'buy' ? '买入' : '卖出'} ${openPrice}`
      })
    }

    if (closeTime !== null && Number.isFinite(closePrice)) {
      result.push({
        time: closeTime,
        position: direction === 'buy' ? 'aboveBar' : 'belowBar',
        color: '#315bff',
        shape: 'circle',
        text: `平仓 ${closePrice}`
      })
    }
  }

  result.sort((a, b) => a.time - b.time)
  markerSeries?.setMarkers(result)
}

function updateDisplayedPrice(price) {
  if (!Number.isFinite(price)) return

  const item = instruments.find(row => row.id === selectedInstrument.value)
  if (!item) return

  const previous = Number(item.price.replace(/,/g, ''))
  item.price = price.toLocaleString('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  })

  if (Number.isFinite(previous) && previous > 0) {
    const change = ((price - previous) / previous) * 100
    item.change = `${change >= 0 ? '+' : ''}${change.toFixed(2)}%`
    item.up = change >= 0
  }
}

async function loadCandles() {
  const version = requestVersion
  try {
    const payload = await fetchJson(
      `${CANDLE_URL}?symbol=${encodeURIComponent(dataSymbol.value)}&timeframe=M5`
    )
    if (destroyed || version !== requestVersion) return

    const rows = responseRows(payload)
      .map(normalizeCandle)
      .filter(Boolean)
      .sort((a, b) => a.time - b.time)

    const unique = new Map(rows.map(row => [row.time, row]))
    candles.value = [...unique.values()]

    if (candleSeries && candles.value.length) {
      candleSeries.setData(candles.value)
      chart?.timeScale().fitContent()
    }

    dataError.value = candles.value.length ? '' : '暂无行情数据'
  } catch (error) {
    if (version === requestVersion) {
      dataError.value = '行情接口暂不可用'
    }
  } finally {
    if (version === requestVersion) loading.value = false
  }
}

async function loadTick() {
  const version = requestVersion
  try {
    const payload = await fetchJson(
      `${TICK_URL}?symbol=${encodeURIComponent(dataSymbol.value)}`
    )
    if (destroyed || version !== requestVersion) return

    const tick = payload?.data ?? payload
    const price = Number(tick.price ?? tick.last ?? tick.bid)
    const time = toUnixTime(tick.time ?? tick.timestamp ?? tick.datetime)

    if (!Number.isFinite(price) || time === null) return

    latestTick.value = { price, time }
    updateDisplayedPrice(price)

    const currentBarTime = Math.floor(time / 300) * 300
    const current = candles.value[candles.value.length - 1]

    if (!current) return

    if (currentBarTime === current.time) {
      const updated = {
        ...current,
        high: Math.max(current.high, price),
        low: Math.min(current.low, price),
        close: price
      }
      candles.value[candles.value.length - 1] = updated
      candleSeries?.update(updated)
    } else if (currentBarTime > current.time) {
      const updated = {
        time: currentBarTime,
        open: current.close,
        high: Math.max(current.close, price),
        low: Math.min(current.close, price),
        close: price
      }
      candles.value.push(updated)
      candleSeries?.update(updated)
    }
  } catch {
    // 保留最后一次有效行情；不生成模拟价格。
  }
}

async function loadTrades() {
  const version = requestVersion
  try {
    const payload = await fetchJson(
      `${TRADES_URL}?symbol=${encodeURIComponent(dataSymbol.value)}`
    )
    if (destroyed || version !== requestVersion) return

    trades.value = responseRows(payload)
    buildMarkers()
  } catch {
    // 接口不可用时不伪造交易记录。
  }
}

function startPolling() {
  stopPolling()
  requestVersion++
  loading.value = true
  dataError.value = ''
  candles.value = []
  trades.value = []
  latestTick.value = null
  candleSeries?.setData([])
  markerSeries?.setMarkers([])

  loadCandles()
  loadTick()
  loadTrades()

  candleTimer = window.setInterval(loadCandles, 5000)
  tickTimer = window.setInterval(loadTick, 200)
  tradeTimer = window.setInterval(loadTrades, 5000)
}

function stopPolling() {
  if (candleTimer) window.clearInterval(candleTimer)
  if (tickTimer) window.clearInterval(tickTimer)
  if (tradeTimer) window.clearInterval(tradeTimer)
  candleTimer = tickTimer = tradeTimer = null
}

const completedTrades = computed(() =>
  trades.value.filter(trade => tradeTime(trade, 'close') !== null)
)

function formatTime(value) {
  const timestamp = toUnixTime(value)
  if (timestamp === null) return '--'
  return new Date(timestamp * 1000).toLocaleString('zh-CN', {
    hour12: false
  })
}

function formatNumber(value, digits = 2) {
  const number = Number(value)
  return Number.isFinite(number) ? number.toFixed(digits) : '--'
}

function tradeDuration(trade) {
  const open = tradeTime(trade, 'open')
  const close = tradeTime(trade, 'close')
  if (open === null || close === null) return '--'

  const minutes = Math.max(0, Math.floor((close - open) / 60))
  if (minutes < 60) return `${minutes} 分钟`
  const hours = Math.floor(minutes / 60)
  const rest = minutes % 60
  if (hours < 24) return `${hours} 小时 ${rest} 分钟`
  return `${Math.floor(hours / 24)} 天 ${hours % 24} 小时`
}

watch(selectedInstrument, async () => {
  await nextTick()
  startPolling()
})

onMounted(async () => {
  await nextTick()
  initChart()
  startPolling()
})

onBeforeUnmount(() => {
  destroyed = true
  stopPolling()
  requestVersion++
  resizeObserver?.disconnect()
  chart?.remove()
  chart = null
  candleSeries = null
  markerSeries = null
})
</script>

<template>
  <main class="live-page">
    <div class="ambient ambient-blue"></div>
    <div class="ambient ambient-purple"></div>

    <section class="terminal-frame">
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

      <section class="section-panel chart-panel">
        <div class="chart-status">
          <span class="status-dot" :class="{ 'status-live': latestTick }"></span>
          <span>{{ loading ? '正在读取行情' : dataError || (latestTick ? '实时行情' : '等待行情') }}</span>
          <span class="chart-symbol">{{ dataSymbol }} · M5</span>
          <span class="chart-count">{{ candles.length }} 根 K 线</span>
        </div>

        <div ref="chartHost" class="chart-host"></div>
      </section>

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
              <tr v-for="(trade, index) in [...completedTrades].reverse()" :key="trade.ticket ?? trade.order ?? index">
                <td>{{ formatTime(trade.open_time ?? trade.opened_at ?? trade.entry_time) }}</td>
                <td>{{ formatTime(trade.close_time ?? trade.closed_at ?? trade.exit_time) }}</td>
                <td>{{ trade.symbol ?? dataSymbol }}</td>
                <td :class="tradeDirection(trade) === 'buy' ? 'profit-text' : 'loss-text'">
                  {{ tradeDirection(trade) === 'buy' ? '多单' : '空单' }}
                </td>
                <td>{{ formatNumber(trade.volume ?? trade.lot, 2) }}</td>
                <td>{{ formatNumber(trade.open_price ?? trade.entry_price) }}</td>
                <td>{{ formatNumber(trade.close_price ?? trade.exit_price) }}</td>
                <td :class="Number(trade.profit ?? trade.pnl) >= 0 ? 'profit-text' : 'loss-text'">
                  {{ formatNumber(trade.profit ?? trade.pnl) }}
                </td>
                <td>{{ tradeDuration(trade) }}</td>
              </tr>

              <tr v-if="completedTrades.length === 0">
                <td colspan="9">
                  <div class="empty-history">
                    <span class="empty-history-icon">
                      <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
                        <rect x="4" y="3.5" width="16" height="17" rx="2" stroke="currentColor" stroke-width="1.4" />
                        <path d="M8 8h8M8 12h8M8 16h5" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" />
                      </svg>
                    </span>
                    <strong>{{ loading ? '正在读取交易记录' : '暂无交易记录' }}</strong>
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
.ticker-viewport:hover .ticker-track { animation-play-state: paused; }

.ticker-item {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 245px;
  padding: 15px 18px;
  color: var(--主要文字颜色, #fff);
  text-align: left;
  border: 0;
  outline: 0;
  background: transparent;
  box-shadow: none;
  cursor: pointer;
}
.ticker-item:hover,
.ticker-item.selected { border: 0; background: transparent; box-shadow: none; }

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
.ticker-info { display: flex; flex-direction: column; gap: 4px; min-width: 64px; }
.ticker-name { color: var(--主要文字颜色, #fff); font-size: 11px; font-weight: 800; letter-spacing: .5px; }
.ticker-full-name { color: var(--次要灰色文字, #848e9c); font-size: 9px; }
.ticker-quote { display: flex; flex-direction: column; gap: 4px; margin-left: auto; text-align: right; }
.ticker-quote strong { color: var(--主要文字颜色, #fff); font-size: 11px; font-variant-numeric: tabular-nums; }
.ticker-quote small { font-size: 10px; }
.ticker-up .ticker-quote small, .ticker-up .ticker-arrow { color: var(--涨势绿色, #0ecb81); }
.ticker-down .ticker-quote small, .ticker-down .ticker-arrow { color: var(--跌势红色, #f6465d); }
.ticker-arrow { align-self: flex-start; font-size: 14px; }

@keyframes ticker-scroll {
  from { transform: translateX(0); }
  to { transform: translateX(-50%); }
}

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
.direction-block, .ai-metric { min-width: 0; }
.direction-block small, .ai-metric > small {
  display: block;
  color: var(--次要灰色文字, #848e9c);
  font-size: 10px;
}
.direction-block strong, .ai-metric strong {
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
.ai-metric strong span { margin-left: 3px; color: var(--次要灰色文字, #848e9c); font-size: 12px; }
.metric-track { width: 100%; max-width: 170px; height: 3px; margin-top: 9px; overflow: hidden; background: var(--边框线条颜色, #222630); }
.metric-track span { display: block; width: 0; height: 100%; }
.track-blue { background: var(--主色调蓝色, #315bff); }
.track-purple { background: #8b70ff; }

.section-panel { min-width: 0; padding: 20px; border: 0; background: transparent; }

.chart-panel { padding-top: 12px; }
.chart-status {
  display: flex;
  align-items: center;
  gap: 9px;
  min-height: 30px;
  color: var(--次要灰色文字, #848e9c);
  font-size: 11px;
}
.status-dot { width: 7px; height: 7px; flex: 0 0 auto; border-radius: 50%; background: #848e9c; }
.status-dot.status-live { background: #0ecb81; }
.chart-symbol { margin-left: auto; color: var(--主要文字颜色, #fff); }
.chart-count { white-space: nowrap; }
.chart-host {
  position: relative;
  width: 100%;
  height: clamp(420px, 49vw, 660px);
  min-height: 360px;
  overflow: hidden;
  background: var(--表面卡片背景色, #141722);
  touch-action: none;
  user-select: none;
  -webkit-user-select: none;
}

.history-panel { padding-bottom: 16px; }
.history-heading { margin-bottom: 18px; }
.history-heading h2 { color: var(--主要文字颜色, #fff); font-size: 14px; font-weight: 700; }
.history-overview { display: flex; align-items: center; margin-bottom: 15px; }
.history-description { color: var(--次要灰色文字, #848e9c); font-size: 11px; font-weight: 500; }
.history-table-wrap { width: 100%; overflow-x: auto; border: 1px solid var(--边框线条颜色, #222630); background: var(--表面卡片背景色, #141722); }
.history-table { width: 100%; min-width: 850px; border-collapse: collapse; text-align: left; }
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
.history-table td { padding: 12px 13px; color: var(--主要文字颜色, #fff); font-size: 11px; white-space: nowrap; border-bottom: 1px solid rgba(132,142,156,.08); }
.profit-text { color: var(--涨势绿色, #0ecb81) !important; }
.loss-text { color: var(--跌势红色, #f6465d) !important; }

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
.empty-history-icon svg { width: 21px; height: 21px; }
.empty-history strong { color: var(--次要灰色文字, #848e9c); font-size: 12px; }

@media (prefers-reduced-motion: reduce) {
  .ticker-track { animation: none; }
}
@media (min-width: 1600px) {
  .live-page { padding-inline: 36px; }
}
@media (max-width: 850px) {
  .live-page { padding: 24px 14px 34px; }
  .ai-main-row { gap: 16px; }
  .chart-host { height: 480px; }
  .section-panel { padding: 17px; }
}
@media (max-width: 520px) {
  .live-page { padding: 20px 9px 28px; }
  .ticker-item { min-width: 205px; padding: 13px 12px; }
  .ai-panel { padding: 16px 12px 12px; }
  .ai-main-row { gap: 12px; }
  .direction-block strong, .ai-metric strong { font-size: 18px; }
  .section-panel { padding: 14px 9px; }
  .chart-host { height: 430px; min-height: 350px; }
  .chart-status { gap: 6px; font-size: 10px; }
  .chart-count { display: none; }
}
</style>
