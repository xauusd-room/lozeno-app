<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { createChart, CandlestickSeries, createSeriesMarkers } from 'lightweight-charts'

const LOCAL_WS_URL = 'ws://127.0.0.1:8001'
const PUBLIC_WS_URL = 'wss://lozeno-market.aaa375750526.workers.dev/ws'

function getWsUrl() {
  const hostname = window.location.hostname

  return ['localhost', '127.0.0.1'].includes(hostname)
    ? LOCAL_WS_URL
    : PUBLIC_WS_URL
}
const HISTORY_LIMIT = 300
const RIGHT_SPACE_BARS = 12

const eaBots = [
  { id: 1, name: 'TrendMaster Pro', pnl: '+$342.50', returnStr: '+793.1k · 近30天', active: false },
  { id: 2, name: 'GridScalper X', pnl: '+$189.00', returnStr: '+599.7k · 近30天', active: false },
  { id: 3, name: 'NeuralArbitrage', pnl: '+$1,245.80', returnStr: '+532.2k · 近30天', active: true },
  { id: 4, name: 'MartinMaster', pnl: '-$42.10', returnStr: '+500.1k · 近30天', active: false },
  { id: 5, name: 'MomentumHunter', pnl: '+$88.30', returnStr: '+497.9k · 近30天', active: false },
  { id: 6, name: 'BreakoutRetest Pro', pnl: '+$512.00', returnStr: '+492.3k · 近30天', active: false },
  { id: 7, name: 'ReversalMaster', pnl: '+$94.20', returnStr: '+458.4k · 近30天', active: false },
  { id: 8, name: 'SmartMoney X', pnl: '+$126.70', returnStr: '+421.6k · 近30天', active: false }
]

const copyLogs = [
  { type: 'exit', label: '平仓', text: '交易机器人卖出黄金 · 已同步平仓' },
  { type: 'sync', label: '同步', text: '8 个机器人已同步 · 延迟 283 毫秒' },
  { type: 'fill', label: '成交', text: '卖出黄金 · -$6.13' },
  { type: 'track', label: '追踪', text: 'MomentumHunter 买入黄金 · 策略信号已触发' },
  { type: 'copy', label: '跟单', text: '跟随 SmartMoney X · 买入黄金' },
  { type: 'fill', label: '成交', text: '卖出黄金 · -$1.38' }
]

const tradingRecords = [
  { id: 1, time: '2026-10-21 19:35:12', bot: 'BreakoutRetest Pro', symbol: 'XAUUSD.cn', side: 'BUY', open: '4,321.50', close: '4,324.10', lot: '0.01', pnl: '+2.60', status: '已平仓' },
  { id: 2, time: '2026-10-21 19:20:45', bot: 'MomentumHunter', symbol: 'XAUUSD.cn', side: 'SELL', open: '4,325.20', close: '4,326.40', lot: '0.01', pnl: '-1.20', status: '已平仓' },
  { id: 3, time: '2026-10-21 19:05:31', bot: 'TrendMaster Pro', symbol: 'XAUUSD.cn', side: 'BUY', open: '4,318.70', close: '4,321.00', lot: '0.02', pnl: '+4.60', status: '已平仓' },
  { id: 4, time: '2026-10-21 18:52:08', bot: 'SmartMoney X', symbol: 'XAUUSD.cn', side: 'BUY', open: '4,316.20', close: '--', lot: '0.01', pnl: '--', status: '持仓中' },
  { id: 5, time: '2026-10-21 18:40:16', bot: 'GridScalper X', symbol: 'XAUUSD.cn', side: 'SELL', open: '4,322.80', close: '4,324.00', lot: '0.01', pnl: '-1.20', status: '已平仓' },
  { id: 6, time: '2026-10-21 18:22:51', bot: 'ReversalMaster', symbol: 'XAUUSD.cn', side: 'BUY', open: '4,310.40', close: '4,313.90', lot: '0.01', pnl: '+3.50', status: '已平仓' }
]

const chartHost = ref(null)
const wsError = ref('')

let chart = null
let candleSeries = null
let markerSeries = null
let socket = null
let reconnectTimer = null
let resizeObserver = null
let manuallyClosed = false
let reconnectDelay = 2000
let candleData = []

function normalizeCandle(raw) {
  if (!raw) return null

  const candle = {
    time: Number(raw.time),
    open: Number(raw.open),
    high: Number(raw.high),
    low: Number(raw.low),
    close: Number(raw.close)
  }

  return Object.values(candle).every(Number.isFinite) ? candle : null
}

function keepLatestWindow() {
  if (!chart || !candleData.length) return

  chart.timeScale().setVisibleLogicalRange({
    from: Math.max(0, candleData.length - HISTORY_LIMIT),
    to: candleData.length - 1 + RIGHT_SPACE_BARS
  })
}

function loadCandles(rawCandles) {
  if (!candleSeries || !Array.isArray(rawCandles)) return

  const sorted = rawCandles
    .map(normalizeCandle)
    .filter(Boolean)
    .sort((a, b) => a.time - b.time)

  const unique = []

  for (const candle of sorted) {
    if (unique.length && unique[unique.length - 1].time === candle.time) {
      unique[unique.length - 1] = candle
    } else {
      unique.push(candle)
    }
  }

  candleData = unique.slice(-HISTORY_LIMIT)
  candleSeries.setData(candleData)
  keepLatestWindow()
}

function updateCandle(raw) {
  const candle = normalizeCandle(raw)
  if (!candle || !candleSeries) return

  try {
    const lastIndex = candleData.length - 1
    const last = candleData[lastIndex]

    if (!last) {
      candleData = [candle]
      candleSeries.setData(candleData)
    } else if (candle.time === last.time) {
      candleData[lastIndex] = candle
      candleSeries.update(candle)
    } else if (candle.time > last.time) {
      candleData.push(candle)

      if (candleData.length > HISTORY_LIMIT) {
        candleData = candleData.slice(-HISTORY_LIMIT)
        candleSeries.setData(candleData)
      } else {
        candleSeries.update(candle)
      }

      keepLatestWindow()
    }
  } catch (error) {
    console.warn('行情蜡烛图更新失败：', error)
  }
}

function updateTradeMarkers(markers = []) {
  if (!markerSeries) return

  try {
    markerSeries.setMarkers(markers.map(({ text, ...marker }) => marker))
  } catch (error) {
    console.warn('交易标记更新失败：', error)
  }
}


function handleMessage(event) {
  let message

  try {
    message = JSON.parse(event.data)
  } catch {
    return
  }

  // Cloudflare 会将 Python 发布的数据包装在 market.data 中
  if (message.type === 'market') {
    message = message.data
  }

  switch (message.type) {
    case 'connected':
      wsError.value = ''
      break

    case 'snapshot':
      loadCandles(message.candles)
      wsError.value = ''
      break

    case 'tick':
      // Tick 用于实时报价；当前页面不单独显示买卖报价
      break

    case 'candle_update':
      updateCandle(message.candle)
      break

    case 'trade_markers':
      updateTradeMarkers(message.markers || [])
      break
  }
}

function scheduleReconnect() {
  if (manuallyClosed) return

  clearTimeout(reconnectTimer)
  reconnectTimer = setTimeout(connectWebSocket, reconnectDelay)
  reconnectDelay = Math.min(reconnectDelay * 1.5, 10000)
}

function connectWebSocket() {
  if (manuallyClosed) return

  clearTimeout(reconnectTimer)

  try {
    socket = new WebSocket(getWsUrl())
  } catch {
    wsError.value = '无法创建行情连接，请检查服务是否启动。'
    scheduleReconnect()
    return
  }

  socket.onopen = () => {
    wsError.value = ''
    reconnectDelay = 2000
  }

  socket.onmessage = handleMessage

  socket.onerror = () => {
    wsError.value = '无法连接行情服务，请检查服务是否启动。'
  }

  socket.onclose = scheduleReconnect
}

function initChart() {
  if (!chartHost.value) return

  chart = createChart(chartHost.value, {
    width: chartHost.value.clientWidth,
    height: chartHost.value.clientHeight,
    handleScroll: false,
    handleScale: false,
    layout: {
      background: { color: '#0b0d12' },
      textColor: '#848e9c',
      fontFamily: 'Arial, sans-serif',
      fontSize: 12,
      attributionLogo: false
    },
    grid: {
      vertLines: { color: '#222630' },
      horzLines: { color: '#222630' }
    },
    rightPriceScale: {
      visible: true,
      autoScale: true,
      borderColor: '#222630',
      scaleMargins: { top: 0.12, bottom: 0.12 }
    },
    timeScale: {
      borderColor: '#222630',
      timeVisible: true,
      secondsVisible: false,
      rightOffset: RIGHT_SPACE_BARS,
      barSpacing: 5,
      minBarSpacing: 2,
      lockVisibleTimeRangeOnResize: true,
      rightBarStaysOnScroll: true
    },
    crosshair: {
      vertLine: { color: '#687386', labelBackgroundColor: '#315bff' },
      horzLine: { color: '#687386', labelBackgroundColor: '#315bff' }
    },
    localization: { locale: 'zh-CN' }
  })

  candleSeries = chart.addSeries(CandlestickSeries, {
    upColor: '#0ecb81',
    downColor: '#f6465d',
    borderUpColor: '#0ecb81',
    borderDownColor: '#f6465d',
    wickUpColor: '#0ecb81',
    wickDownColor: '#f6465d',
    priceLineVisible: true,
    lastValueVisible: true
  })

  markerSeries = createSeriesMarkers(candleSeries, [])

  resizeObserver = new ResizeObserver(([entry]) => {
    if (!entry || !chart) return

    chart.applyOptions({
      width: Math.floor(entry.contentRect.width),
      height: Math.max(280, Math.floor(entry.contentRect.height))
    })

    keepLatestWindow()
  })

  resizeObserver.observe(chartHost.value)
}

onMounted(() => {
  initChart()
  connectWebSocket()
})

onBeforeUnmount(() => {
  manuallyClosed = true
  clearTimeout(reconnectTimer)

  if (socket) {
    socket.onopen = null
    socket.onmessage = null
    socket.onerror = null
    socket.onclose = null
    socket.close()
  }

  resizeObserver?.disconnect()
  chart?.remove()

  candleData = []
  chart = null
  candleSeries = null
  markerSeries = null
})
</script>

<template>
  <main class="grok-live-page">
    <div class="main-layout-grid">
      <section class="panel chart-panel">
        <div class="mt5-chart-container">
          <div class="symbol-badge">XAUUSD</div>
          <div ref="chartHost" class="mt5-chart-canvas"></div>
          <div v-if="wsError" class="chart-error">{{ wsError }}</div>
        </div>
      </section>

      <div class="right-top-group">
        <section class="metrics-grid">
          <article class="panel metric-card">
            <span class="panel-label">账户余额</span>
            <div class="panel-main-val">$74.40</div>
            <div class="panel-sub-text">初始余额 $77.00</div>
          </article>

          <article class="panel metric-card">
            <span class="panel-label">总盈亏</span>
            <div class="panel-main-val negative">-$2.60</div>
            <div class="panel-sub-text negative">总体收益 -3.5%</div>
          </article>

          <article class="panel metric-card">
            <span class="panel-label">最大回撤</span>
            <div class="panel-main-val negative">-10.7%</div>
            <div class="panel-sub-text">当前回撤 -3.3% · 峰值 $77</div>
          </article>

          <article class="panel metric-card">
            <span class="panel-label">胜率</span>
            <div class="winrate-content">
              <div class="winrate-circle"><span>36%</span></div>
              <div class="winrate-badge-text">
                <span class="win">4 次盈利</span> / <span class="loss">7 次亏损</span>
              </div>
            </div>
          </article>

          <article class="panel metric-card">
            <span class="panel-label">总交易次数</span>
            <div class="panel-main-val">11</div>
            <div class="panel-sub-text">盈利 4 次 · 亏损 7 次</div>
          </article>

          <article class="panel metric-card">
            <span class="panel-label">盈利因子</span>
            <div class="panel-main-val">1.28</div>
            <div class="panel-sub-text">总盈利与总亏损之比</div>
          </article>

          <article class="panel metric-card">
            <span class="panel-label">平均每笔盈亏</span>
            <div class="panel-main-val">$0.24</div>
            <div class="panel-sub-text">每笔交易</div>
          </article>

          <article class="panel metric-card">
            <span class="panel-label">已加载 EA 数量</span>
            <div class="panel-main-val">{{ eaBots.length }}</div>
            <div class="panel-sub-text">个策略已加载</div>
          </article>
        </section>

        <section class="panel history-panel">
          <div class="panel-heading">
            <span class="panel-label">余额历史</span>
            <span class="history-tag">48 小时</span>
          </div>

          <div class="history-chart">
            <svg viewBox="0 0 600 150" preserveAspectRatio="none" role="img" aria-label="账户余额变化曲线">
              <defs>
                <linearGradient id="historyFill" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stop-color="#0ecb81" stop-opacity=".2" />
                  <stop offset="100%" stop-color="#0ecb81" stop-opacity="0" />
                </linearGradient>
              </defs>

              <line x1="0" y1="50" x2="600" y2="50" stroke="#222630" stroke-dasharray="4 5" />
              <line x1="0" y1="100" x2="600" y2="100" stroke="#222630" stroke-dasharray="4 5" />

              <path
                d="M0 35 C35 25 48 62 82 54 S130 32 165 61 S218 83 250 65 S300 80 340 57 S390 72 430 88 S490 65 525 93 S570 100 600 112 L600 150 L0 150 Z"
                fill="url(#historyFill)"
              />

              <path
                d="M0 35 C35 25 48 62 82 54 S130 32 165 61 S218 83 250 65 S300 80 340 57 S390 72 430 88 S490 65 525 93 S570 100 600 112"
                fill="none"
                stroke="#0ecb81"
                stroke-width="2"
                vector-effect="non-scaling-stroke"
              />
            </svg>
          </div>

          <div class="history-axis">
            <span>48 小时前</span>
            <span>24 小时前</span>
            <span>现在</span>
          </div>
        </section>
      </div>

      <section class="panel ea-bots-panel">
        <div class="ea-panel-header">
          <span class="panel-label">EA 机器人列表</span>
          <span class="ea-target-info">共 {{ eaBots.length }} 个机器人</span>
        </div>

        <div class="ea-track-grid">
          <article
            v-for="(bot, index) in eaBots"
            :key="bot.id"
            class="ea-card"
            :class="{ active: bot.active }"
          >
            <div class="ea-card-header">
              <div class="ea-avatar-letter" :class="`avatar-${index + 1}`">
                {{ bot.name.slice(0, 1) }}
              </div>
              <span class="ea-num">第 {{ index + 1 }} 名</span>
            </div>

            <div class="ea-name">{{ bot.name }}</div>
            <div class="ea-return">{{ bot.returnStr }}</div>

            <div class="ea-pnl">
              盈亏
              <span :class="{ negative: bot.pnl.startsWith('-') }">{{ bot.pnl }}</span>
            </div>
          </article>
        </div>
      </section>

      <section class="panel copy-log-panel">
        <div class="panel-heading">
          <span class="panel-label">实时跟单日志</span>
          <span class="live-indicator"><i /> 实时</span>
        </div>

        <div class="copy-log-list">
          <div v-for="(log, index) in copyLogs" :key="index" class="log-item">
            <span class="log-badge" :class="log.type">[{{ log.label }}]</span>
            <span class="log-content">{{ log.text }}</span>
          </div>
        </div>
      </section>
    </div>

    <section class="panel trading-records-panel">
      <div class="records-heading">
        <div>
          <span class="panel-label">实盘交易记录</span>
          <p class="records-subtitle">实时交易历史</p>
        </div>
        <span class="records-count">共 {{ tradingRecords.length }} 条记录</span>
      </div>

      <div class="records-table-wrap">
        <table class="records-table">
          <thead>
            <tr>
              <th>交易时间</th>
              <th>机器人</th>
              <th>交易品种</th>
              <th>方向</th>
              <th>开仓价</th>
              <th>平仓价</th>
              <th>手数</th>
              <th>盈亏</th>
              <th>状态</th>
            </tr>
          </thead>

          <tbody>
            <tr v-for="record in tradingRecords" :key="record.id">
              <td class="record-time">{{ record.time }}</td>
              <td class="record-bot">{{ record.bot }}</td>
              <td>{{ record.symbol === 'XAUUSD.cn' ? '黄金' : record.symbol }}</td>
              <td>
                <span class="side-tag" :class="record.side.toLowerCase()">
                  {{ record.side === 'BUY' ? '买入' : '卖出' }}
                </span>
              </td>
              <td>{{ record.open }}</td>
              <td>{{ record.close }}</td>
              <td>{{ record.lot }}</td>
              <td
                class="record-pnl"
                :class="{
                  positive: record.pnl.startsWith('+'),
                  negative: record.pnl.startsWith('-')
                }"
              >
                {{ record.pnl }}
              </td>
              <td>
                <span class="status-tag" :class="{ running: record.status === '持仓中' }">
                  {{ record.status }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </main>
</template>

<style scoped>
.grok-live-page,
.grok-live-page * {
  box-sizing: border-box;
  scrollbar-width: none;
  -ms-overflow-style: none;
}

.grok-live-page *::-webkit-scrollbar {
  display: none;
  width: 0;
  height: 0;
}

:global(html),
:global(body) {
  scrollbar-width: none;
  -ms-overflow-style: none;
}

:global(html::-webkit-scrollbar),
:global(body::-webkit-scrollbar) {
  display: none;
  width: 0;
  height: 0;
}

.grok-live-page {
  --panel-bg: var(--表面卡片背景色, #141722);
  --panel-border: var(--边框线条颜色, #222630);
  --text-main: var(--主要文字颜色, #fff);
  --text-sub: var(--次要灰色文字, #848e9c);
  --positive: var(--涨势绿色, #0ecb81);
  --negative: var(--跌势红色, #f6465d);
  --chart-height: clamp(420px, 55vh, 640px);

  width: 100%;
  max-width: var(--页面最大宽度, 1320px);
  min-width: 0;
  min-height: 100vh;
  margin-inline: auto;
  padding: 16px;
  color: var(--text-main);
  overflow-x: clip;
}

.main-layout-grid {
  display: grid;
  grid-template-columns: minmax(0, 2.15fr) minmax(0, .85fr);
  grid-template-areas: "chart right-top" "ea logs";
  align-items: stretch;
  gap: 12px;
  width: 100%;
  min-width: 0;
}

.panel {
  min-width: 0;
  max-width: 100%;
  padding: 12px;
  background: var(--panel-bg);
  border: 1px solid var(--panel-border);
  border-radius: var(--中圆角, 10px);
}

.chart-panel {
  grid-area: chart;
  align-self: stretch;
  padding: 8px;
}

.right-top-group {
  grid-area: right-top;
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 0;
  min-height: 0;
  height: 100%;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  grid-template-rows: repeat(4, minmax(0, 1fr));
  flex: 0 0 auto;
  gap: 6px;
  min-width: 0;
}

.metric-card {
  display: flex;
  flex-direction: column;
  justify-content: center;
  min-width: 0;
  min-height: 70px;
  padding: 8px;
}

.panel-label {
  display: block;
  min-width: 0;
  color: var(--text-sub);
  font-size: 10px;
  font-weight: 700;
  letter-spacing: .3px;
}

.panel-main-val {
  overflow: hidden;
  margin-top: 7px;
  color: var(--text-main);
  font-size: clamp(13px, 1.05vw, 19px);
  font-weight: 750;
  line-height: 1.2;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.panel-main-val.negative,
.panel-sub-text.negative {
  color: var(--negative);
}

.panel-sub-text {
  margin-top: 5px;
  color: var(--text-sub);
  font-size: 9px;
  line-height: 1.4;
  overflow-wrap: anywhere;
}

.mt5-chart-container {
  position: relative;
  width: 100%;
  max-width: 100%;
  height: var(--chart-height);
  min-width: 0;
  overflow: hidden;
  border-radius: var(--小圆角, 6px);
  background: #0b0d12;
}

.mt5-chart-canvas {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  min-width: 0;
}

.symbol-badge {
  position: absolute;
  z-index: 5;
  top: 12px;
  left: 12px;
  display: inline-flex;
  align-items: center;
  min-height: 28px;
  padding: 0 10px;
  border: 1px solid #303746;
  border-radius: 5px;
  background: rgba(20, 23, 34, .94);
  color: #e8c56a;
  font-size: 11px;
  font-weight: 750;
  letter-spacing: .5px;
  pointer-events: none;
}

.chart-error {
  position: absolute;
  z-index: 6;
  top: 50px;
  left: 12px;
  max-width: calc(100% - 24px);
  padding: 7px 9px;
  border: 1px solid rgba(246, 70, 93, .3);
  border-radius: 5px;
  background: rgba(20, 23, 34, .94);
  color: #f59f9f;
  font-size: 11px;
  pointer-events: none;
}

.panel-heading,
.ea-panel-header,
.records-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.ea-panel-header {
  margin-bottom: 10px;
}

.ea-target-info,
.history-tag,
.records-count {
  color: var(--text-sub);
  font-size: 10px;
  white-space: nowrap;
}

.ea-bots-panel {
  grid-area: ea;
  min-width: 0;
  align-self: stretch;
}

.ea-track-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 8px;
  min-width: 0;
}

.ea-card {
  display: flex;
  flex-direction: column;
  gap: 5px;
  min-width: 0;
  padding: 9px;
  background: var(--主页面背景色, #0b0d12);
  border: 1px solid var(--panel-border);
  border-radius: var(--小圆角, 6px);
}

.ea-card.active {
  border-color: var(--positive);
  box-shadow: 0 0 8px rgba(14, 203, 129, .08);
}

.ea-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.ea-avatar-letter {
  display: grid;
  place-items: center;
  width: 24px;
  height: 24px;
  flex: 0 0 24px;
  border-radius: 50%;
  color: #fff;
  font-size: 10px;
  font-weight: 700;
}

.avatar-1 { background: #3b5bdb; }
.avatar-2 { background: #f59f00; }
.avatar-3 { background: #7048e8; }
.avatar-4 { background: #2b8a3e; }
.avatar-5 { background: #1098ad; }
.avatar-6 { background: #d9480f; }
.avatar-7 { background: #5c940d; }
.avatar-8 { background: #315bff; }

.ea-num {
  color: var(--text-sub);
  font-size: 9px;
}

.ea-name {
  overflow: hidden;
  color: var(--text-main);
  font-size: 11px;
  font-weight: 650;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.ea-return,
.ea-pnl {
  color: var(--text-sub);
  font-size: 9px;
  line-height: 1.4;
}

.ea-pnl {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 4px;
  margin-top: 2px;
}

.ea-pnl span {
  color: var(--positive);
  white-space: nowrap;
}

.ea-pnl span.negative {
  color: var(--negative);
}

.winrate-content {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 7px;
  margin-top: 7px;
}

.winrate-circle {
  position: relative;
  display: grid;
  place-items: center;
  width: 34px;
  height: 34px;
  flex: 0 0 34px;
  border-radius: 50%;
  background: conic-gradient(var(--positive) 0 36%, var(--panel-border) 36% 100%);
  font-size: 9px;
  font-weight: 750;
}

.winrate-circle::before {
  position: absolute;
  inset: 4px;
  border-radius: 50%;
  background: var(--panel-bg);
  content: "";
}

.winrate-circle span {
  position: relative;
  z-index: 1;
}

.winrate-badge-text {
  font-size: 9px;
  font-weight: 700;
}

.winrate-badge-text .win {
  color: var(--positive);
}

.winrate-badge-text .loss {
  color: var(--text-sub);
}

.history-panel {
  display: flex;
  flex: 1 1 0;
  flex-direction: column;
  min-width: 0;
  min-height: 190px;
  margin: 0;
  padding: 12px;
}

.history-chart {
  flex: 1 1 auto;
  min-width: 0;
  min-height: 80px;
  margin-top: 10px;
}

.history-chart svg {
  display: block;
  width: 100%;
  height: 100%;
  min-height: 80px;
}

.history-axis {
  display: flex;
  justify-content: space-between;
  gap: 5px;
  margin-top: 6px;
  color: var(--text-sub);
  font-size: 9px;
}

.copy-log-panel {
  grid-area: logs;
  align-self: stretch;
  min-width: 0;
  min-height: 0;
  height: 100%;
  padding: 12px;
  overflow: hidden;
}

.live-indicator {
  display: flex;
  align-items: center;
  gap: 5px;
  color: var(--positive);
  font-size: 9px;
  font-weight: 700;
}

.live-indicator i {
  width: 6px;
  height: 6px;
  flex: 0 0 6px;
  border-radius: 50%;
  background: var(--positive);
  box-shadow: 0 0 6px rgba(14, 203, 129, .4);
}

.copy-log-list {
  display: flex;
  flex-direction: column;
  gap: 9px;
  min-width: 0;
  margin-top: 12px;
}

.log-item {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
  font-family: monospace;
  font-size: 10px;
  line-height: 1.5;
}

.log-badge {
  flex: 0 0 auto;
  font-weight: 700;
}

.log-badge.exit { color: var(--text-sub); }
.log-badge.sync { color: var(--positive); }
.log-badge.fill { color: #f3c66b; }
.log-badge.track { color: #9b9fff; }
.log-badge.copy { color: #a98aff; }

.log-content {
  min-width: 0;
  overflow: hidden;
  color: var(--text-sub);
  text-overflow: ellipsis;
  white-space: nowrap;
}

.trading-records-panel {
  width: 100%;
  max-width: 100%;
  min-width: 0;
  margin-top: 12px;
}

.records-heading {
  margin-bottom: 14px;
}

.records-subtitle {
  margin-top: 5px;
  color: var(--text-sub);
  font-size: 9px;
}

.records-table-wrap {
  width: 100%;
  max-width: 100%;
  min-width: 0;
  overflow-x: auto;
  overscroll-behavior-x: contain;
}

.records-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 11px;
  text-align: left;
  white-space: nowrap;
}

.records-table th {
  padding: 11px 12px;
  color: var(--text-sub);
  background: var(--主页面背景色, #0b0d12);
  border-bottom: 1px solid var(--panel-border);
  font-size: 10px;
  font-weight: 600;
}

.records-table td {
  padding: 12px;
  color: var(--text-main);
  border-bottom: 1px solid var(--panel-border);
}

.records-table tbody tr:last-child td {
  border-bottom: 0;
}

.records-table tbody tr:hover {
  background: rgba(132, 142, 156, .05);
}

.record-time {
  color: var(--text-sub) !important;
  font-variant-numeric: tabular-nums;
}

.record-bot {
  font-weight: 600;
}

.side-tag,
.status-tag {
  display: inline-flex;
  align-items: center;
  padding: 3px 7px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: 650;
}

.side-tag.buy {
  color: var(--positive);
  background: rgba(14, 203, 129, .1);
}

.side-tag.sell {
  color: var(--negative);
  background: rgba(246, 70, 93, .1);
}

.record-pnl {
  font-weight: 700;
  font-variant-numeric: tabular-nums;
}

.record-pnl.positive {
  color: var(--positive);
}

.record-pnl.negative {
  color: var(--negative);
}

.status-tag {
  color: var(--text-sub);
  background: rgba(132, 142, 156, .1);
}

.status-tag.running {
  color: var(--positive);
  background: rgba(14, 203, 129, .1);
}

@media (max-width: 1050px) {
  .grok-live-page {
    --chart-height: clamp(400px, 55vh, 580px);
  }

  .main-layout-grid {
    grid-template-columns: minmax(0, 1fr);
    grid-template-areas: "chart" "ea" "right-top" "logs";
  }

  .right-top-group {
    height: auto;
  }

  .metrics-grid {
    grid-template-columns: repeat(4, minmax(0, 1fr));
    grid-template-rows: auto;
  }

  .metric-card {
    min-height: 82px;
  }

  .history-panel {
    flex: none;
    min-height: 200px;
  }

  .copy-log-panel {
    height: auto;
    min-height: 150px;
  }
}

@media (max-width: 620px) {
  .grok-live-page {
    --chart-height: 400px;
    padding: 8px;
  }

  .metrics-grid,
  .ea-track-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .metrics-grid {
    grid-template-rows: auto;
    gap: 8px;
  }

  .metric-card {
    min-height: 82px;
  }

  .panel,
  .trading-records-panel {
    padding: 10px;
  }

  .chart-panel {
    padding: 6px;
  }

  .records-table th,
  .records-table td {
    padding: 10px;
  }
}
</style>
