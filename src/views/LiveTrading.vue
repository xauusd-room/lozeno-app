<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { createChart, CandlestickSeries, createSeriesMarkers } from 'lightweight-charts'

const router = useRouter()

const HISTORY_LIMIT = 300
const RIGHT_SPACE_BARS = 36
const SIM_TICK_MS = 250
const SIM_SECONDS_PER_TICK = 30
const CANDLE_SECONDS = 300

const INITIAL_BALANCE = 77
const START_BALANCE = 74.40
const TAKE_PROFIT = 1.8
const STOP_LOSS = 4.5
const MAX_HOLD_TICKS = 24

const botDefinitions = [
  { id: '1', name: 'TrendMaster Pro', color: '#4C8DFF', pnl: 0, returnStr: '实盘策略 · 实时运行' },
  { id: '2', name: 'GridScalper X', color: '#FF9F43', pnl: 0, returnStr: '实盘策略 · 实时运行' },
  { id: '3', name: 'NeuralArbitrage', color: '#B084F5', pnl: 0, returnStr: '实盘策略 · 实时运行' },
  { id: '4', name: 'MartinMaster', color: '#20C997', pnl: 0, returnStr: '实盘策略 · 实时运行' },
  { id: '5', name: 'MomentumHunter', color: '#F06595', pnl: 0, returnStr: '实盘策略 · 实时运行' },
  { id: '6', name: 'BreakoutRetest Pro', color: '#F4C542', pnl: 0, returnStr: '实盘策略 · 实时运行' },
  { id: '7', name: 'ReversalMaster', color: '#22D3EE', pnl: 0, returnStr: '实盘策略 · 实时运行' },
  { id: '8', name: 'SmartMoney X', color: '#FF6B6B', pnl: 0, returnStr: '实盘策略 · 实时运行' }
]

const chartHost = ref(null)
const marketPrice = ref(4320)
const accountBalance = ref(START_BALANCE)
const floatingProfit = ref(0)
const tickCount = ref(0)
const simulationRunning = ref(true)

const eaBots = ref([])
const copyLogs = ref([])
const tradingRecords = ref([])
const tradeMarkers = ref([])
const balanceHistory = ref(Array(48).fill(START_BALANCE))

const chartStats = ref({
  trades: 0,
  wins: 0,
  losses: 0,
  grossProfit: 0,
  grossLoss: 0,
  maxDrawdown: 0,
  peakBalance: START_BALANCE
})

const closedTrades = computed(() => chartStats.value.trades)
const winningTrades = computed(() => chartStats.value.wins)
const losingTrades = computed(() => chartStats.value.losses)

const winRate = computed(() =>
  closedTrades.value
    ? Math.round(winningTrades.value / closedTrades.value * 100)
    : 0
)

const totalProfit = computed(() => accountBalance.value - INITIAL_BALANCE)

const totalReturn = computed(() =>
  INITIAL_BALANCE ? totalProfit.value / INITIAL_BALANCE * 100 : 0
)

const profitFactor = computed(() => {
  const { grossProfit, grossLoss } = chartStats.value

  return grossLoss <= 0
    ? (grossProfit > 0 ? Infinity : 0)
    : grossProfit / grossLoss
})

const averageProfit = computed(() =>
  closedTrades.value ? totalProfit.value / closedTrades.value : 0
)

const currentDrawdown = computed(() => {
  const peak = chartStats.value.peakBalance

  return peak
    ? Math.max(0, (peak - accountBalance.value) / peak * 100)
    : 0
})

const formattedBalance = computed(() => formatMoney(accountBalance.value))
const formattedTotalProfit = computed(() => formatSignedMoney(totalProfit.value))
const formattedFloatingProfit = computed(() => formatSignedMoney(floatingProfit.value))

const displayEaBots = computed(() => {
  return [...eaBots.value].sort((a, b) => {
    const aTrading = Boolean(a.position)
    const bTrading = Boolean(b.position)

    if (aTrading !== bTrading) return aTrading ? -1 : 1

    if (aTrading && bTrading) {
      return b.position.openTime - a.position.openTime
    }

    return a.id - b.id
  })
})

const balanceHistoryPath = computed(() => {
  const values = balanceHistory.value

  if (values.length < 2) return 'M0 75 L600 75'

  const minValue = Math.min(...values)
  const maxValue = Math.max(...values)
  const range = maxValue - minValue

  const padding = range === 0
    ? Math.max(0.1, Math.abs(maxValue) * 0.005)
    : range * 0.15

  const lower = minValue - padding
  const upper = maxValue + padding
  const span = upper - lower || 1

  const points = values.map((value, index) => ({
    x: index / (values.length - 1) * 600,
    y: 130 - ((value - lower) / span) * 110
  }))

  let path = `M${points[0].x.toFixed(2)} ${points[0].y.toFixed(2)}`

  for (let i = 1; i < points.length; i++) {
    const previous = points[i - 1]
    const current = points[i]
    const controlX = (previous.x + current.x) / 2

    path += ` C${controlX.toFixed(2)} ${previous.y.toFixed(2)},${controlX.toFixed(2)} ${current.y.toFixed(2)},${current.x.toFixed(2)} ${current.y.toFixed(2)}`
  }

  return path
})

const balanceHistoryAreaPath = computed(() =>
  `${balanceHistoryPath.value} L600 150 L0 150 Z`
)

let chart = null
let candleSeries = null
let markerSeries = null
let resizeObserver = null
let simulationTimer = null

let candleData = []
let simTime = 0
let simPrice = 4320
let recentMomentum = 0
let lastEntryCandleTime = null
let nextRecordId = 100
let nextLogId = 100
let nextBotIndex = 0

function formatMoney(value) {
  return '$' + Number(value || 0).toLocaleString('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  })
}

function formatSignedMoney(value) {
  const number = Number(value || 0)
  return `${number >= 0 ? '+' : '-'}$${Math.abs(number).toFixed(2)}`
}

function formatPrice(value) {
  return Number(value).toLocaleString('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  })
}

function formatDateTime(timestamp) {
  const date = new Date(timestamp * 1000)
  const pad = value => String(value).padStart(2, '0')

  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`
}

function currentCandleTime() {
  return Math.floor(simTime / CANDLE_SECONDS) * CANDLE_SECONDS
}

function currentCandle() {
  return candleData[candleData.length - 1] || null
}

function keepLatestWindow() {
  if (!chart || !candleData.length) return

  chart.timeScale().setVisibleLogicalRange({
    from: Math.max(0, candleData.length - HISTORY_LIMIT),
    to: candleData.length - 1 + RIGHT_SPACE_BARS
  })
}

function seedCandles() {
  const now = Math.floor(Date.now() / 1000)
  const latestCandleTime = Math.floor(now / CANDLE_SECONDS) * CANDLE_SECONDS

  let price = 4320
  const candles = []

  for (let i = HISTORY_LIMIT - 1; i >= 0; i--) {
    const time = latestCandleTime - i * CANDLE_SECONDS
    const open = price
    const close = Math.max(4000, open + (Math.random() - 0.49) * 3.2)

    candles.push({
      time,
      open,
      high: Math.max(open, close) + Math.random() * 1.3,
      low: Math.min(open, close) - Math.random() * 1.3,
      close
    })

    price = close
  }

  candleData = candles
  simTime = latestCandleTime
  simPrice = candles[candles.length - 1].close
  marketPrice.value = simPrice

  if (candleSeries) {
    candleSeries.setData(candleData)
    keepLatestWindow()
  }
}

function updateCandle() {
  simTime += SIM_SECONDS_PER_TICK

  const candleTime = currentCandleTime()
  const last = currentCandle()

  if (!last) return

  if (candleTime === last.time) {
    last.high = Math.max(last.high, simPrice)
    last.low = Math.min(last.low, simPrice)
    last.close = simPrice

    candleSeries?.update({ ...last })
    return
  }

  if (candleTime > last.time) {
    const newCandle = {
      time: candleTime,
      open: last.close,
      high: Math.max(last.close, simPrice),
      low: Math.min(last.close, simPrice),
      close: simPrice
    }

    candleData.push(newCandle)

    if (candleData.length > HISTORY_LIMIT) {
      candleData = candleData.slice(-HISTORY_LIMIT)
      candleSeries?.setData(candleData)
    } else {
      candleSeries?.update(newCandle)
    }

    keepLatestWindow()
    updateTradeMarkers()
  }
}

function updateTradeMarkers() {
  if (!markerSeries) return

  const latestMarker = tradeMarkers.value[0]

  if (!latestMarker) {
    markerSeries.setMarkers([])
    return
  }

  markerSeries.setMarkers(
    candleData.some(candle => candle.time === latestMarker.time)
      ? [latestMarker]
      : []
  )
}

function addTradeMarker(side, isOpen, time, price, bot) {
  const isBuy = side === 'BUY'

  tradeMarkers.value = [{
    time,
    position: isOpen
      ? (isBuy ? 'belowBar' : 'aboveBar')
      : (isBuy ? 'aboveBar' : 'belowBar'),
    color: bot.color,
    shape: isOpen
      ? (isBuy ? 'arrowUp' : 'arrowDown')
      : 'circle',
    text: `${bot.name} ${isOpen ? '开仓' : '平仓'} ${formatPrice(price)}`
  }]

  updateTradeMarkers()
}

function addLog(type, label, text, bot = null) {
  copyLogs.value.unshift({
    id: ++nextLogId,
    type,
    label,
    text,
    botName: bot?.name || '',
    botColor: bot?.color || '',
    time: formatDateTime(simTime)
  })

  copyLogs.value = copyLogs.value.slice(0, 11)
}

function recordBalanceHistory() {
  balanceHistory.value.push(Number(accountBalance.value.toFixed(2)))

  if (balanceHistory.value.length > 48) {
    balanceHistory.value = balanceHistory.value.slice(-48)
  }
}

function refreshFloatingProfit() {
  let total = 0

  for (const bot of eaBots.value) {
    if (!bot.position) continue

    const direction = bot.position.side === 'BUY' ? 1 : -1
    const pnl =
      (simPrice - bot.position.openPrice) *
      direction *
      bot.position.lot *
      100

    bot.position.pnl = pnl
    total += pnl
  }

  floatingProfit.value = total
}

function chooseSide(bot) {
  const trend = recentMomentum
  const bias = ((Number(bot.id) * 7 + tickCount.value) % 11) - 5

  if (Math.abs(trend) > 0.35) {
    return trend * 0.7 + bias * 0.08 >= 0 ? 'BUY' : 'SELL'
  }

  return Math.random() > 0.5 ? 'BUY' : 'SELL'
}

function openTrade(bot) {
  if (bot.position) return

  const side = chooseSide(bot)
  const lotOptions = [0.01, 0.01, 0.02, 0.03]
  const lot = lotOptions[Math.floor(Math.random() * lotOptions.length)]
  const time = currentCandleTime()

  bot.position = {
    side,
    lot,
    openPrice: simPrice,
    openTime: simTime,
    openCandleTime: time,
    holdTicks: 0,
    pnl: 0
  }

  bot.active = true
  lastEntryCandleTime = time

  addTradeMarker(side, true, time, simPrice, bot)

  tradingRecords.value.unshift({
    id: ++nextRecordId,
    time: formatDateTime(simTime),
    bot: bot.name,
    color: bot.color,
    symbol: 'XAUUSD.cn',
    side,
    open: formatPrice(simPrice),
    close: '--',
    lot: lot.toFixed(2),
    pnl: '--',
    status: '持仓中'
  })

  bot.position.recordId = nextRecordId

  addLog(
    'track',
    '开仓',
    `${side === 'BUY' ? '买入' : '卖出'}黄金 · ${lot.toFixed(2)} 手 · ${formatPrice(simPrice)}`,
    bot
  )
}

function closeTrade(bot, reason = '策略平仓') {
  const position = bot.position
  if (!position) return

  const direction = position.side === 'BUY' ? 1 : -1
  const pnl =
    (simPrice - position.openPrice) *
    direction *
    position.lot *
    100

  const time = currentCandleTime()

  accountBalance.value += pnl
  bot.pnl += pnl
  chartStats.value.trades += 1

  if (pnl >= 0) {
    chartStats.value.wins += 1
    chartStats.value.grossProfit += pnl
  } else {
    chartStats.value.losses += 1
    chartStats.value.grossLoss += Math.abs(pnl)
  }

  chartStats.value.peakBalance = Math.max(
    chartStats.value.peakBalance,
    accountBalance.value
  )

  const drawdown = chartStats.value.peakBalance > 0
    ? (chartStats.value.peakBalance - accountBalance.value) /
      chartStats.value.peakBalance * 100
    : 0

  chartStats.value.maxDrawdown = Math.max(
    chartStats.value.maxDrawdown,
    drawdown
  )

  recordBalanceHistory()
  addTradeMarker(position.side, false, time, simPrice, bot)

  const record = tradingRecords.value.find(
    item => item.id === position.recordId
  )

  if (record) {
    record.close = formatPrice(simPrice)
    record.pnl = formatSignedMoney(pnl)
    record.status = '已平仓'
  }

  addLog(
    pnl >= 0 ? 'exit' : 'fill',
    '平仓',
    `${position.side === 'BUY' ? '买入' : '卖出'}平仓 · ${formatSignedMoney(pnl)} · ${reason}`,
    bot
  )

  bot.position = null
  bot.active = false
  bot.nextActionTick = tickCount.value + 1 + Math.floor(Math.random() * 4)

  tradingRecords.value = tradingRecords.value.slice(0, 30)

  refreshFloatingProfit()
}

function processBot(bot) {
  if (!bot.position) return

  const position = bot.position
  position.holdTicks += 1

  const direction = position.side === 'BUY' ? 1 : -1
  const pnl =
    (simPrice - position.openPrice) *
    direction *
    position.lot *
    100

  position.pnl = pnl

  if (position.holdTicks < 5) return
  if (pnl >= TAKE_PROFIT) return closeTrade(bot, '达到止盈')
  if (pnl <= -STOP_LOSS) return closeTrade(bot, '触发止损')

  if (position.holdTicks >= MAX_HOLD_TICKS) {
    closeTrade(bot, '达到持仓时限')
  }
}

function openNextEligibleBot() {
  if (!eaBots.value.length) return

  const candleTime = currentCandleTime()

  if (lastEntryCandleTime === candleTime) return

  const total = eaBots.value.length

  for (let offset = 0; offset < total; offset++) {
    const index = (nextBotIndex + offset) % total
    const bot = eaBots.value[index]

    if (bot.position || tickCount.value < bot.nextActionTick) continue

    openTrade(bot)
    nextBotIndex = (index + 1) % total
    return
  }
}

function advanceMarket() {
  if (!simulationRunning.value) return

  tickCount.value += 1

  const shock = (Math.random() - 0.5) * 2.2
  recentMomentum = recentMomentum * 0.72 + shock * 0.28

  simPrice = Math.max(
    4000,
    simPrice + shock + recentMomentum * 0.32
  )

  marketPrice.value = simPrice

  updateCandle()

  for (const bot of eaBots.value) {
    processBot(bot)
  }

  openNextEligibleBot()
  refreshFloatingProfit()
}

// 点击 EA 卡片跳转到产品详情页
function handleBotClick(bot) {
  router.push(`/product?id=${bot.id}`)
}

function initChart() {
  if (!chartHost.value) return

  const host = chartHost.value

  chart = createChart(host, {
    width: Math.floor(host.clientWidth),
    height: Math.floor(host.clientHeight),

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
      vertLines: { color: '#171b26' },
      horzLines: { color: '#171b26' }
    },

    rightPriceScale: {
      visible: true,
      autoScale: true,
      borderColor: '#222630',
      scaleMargins: {
        top: 0.04,
        bottom: 0.02
      }
    },

    timeScale: {
      borderColor: '#222630',
      timeVisible: true,
      secondsVisible: false,
      rightOffset: RIGHT_SPACE_BARS,
      barSpacing: 9,
      minBarSpacing: 2,
      lockVisibleTimeRangeOnResize: true,
      rightBarStaysOnScroll: true
    },

    crosshair: {
      vertLine: {
        color: '#687386',
        labelBackgroundColor: '#315bff'
      },
      horzLine: {
        color: '#687386',
        labelBackgroundColor: '#315bff'
      }
    },

    localization: {
      locale: 'zh-CN'
    }
  })

  candleSeries = chart.addSeries(CandlestickSeries, {
    upColor: '#0ecb81',
    downColor: '#f6465d',
    borderUpColor: '#0ecb81',
    borderDownColor: '#f6465d',
    wickUpColor: '#0ecb81',
    wickDownColor: '#0ecb81',
    priceLineVisible: true,
    lastValueVisible: true
  })

  markerSeries = createSeriesMarkers(candleSeries, [])

  seedCandles()

  resizeObserver = new ResizeObserver(([entry]) => {
    if (!entry || !chart) return

    const width = Math.floor(entry.contentRect.width)
    const height = Math.floor(entry.contentRect.height)

    if (width <= 0 || height <= 0) return

    chart.applyOptions({ width, height })
    keepLatestWindow()
  })

  resizeObserver.observe(host)
}

function initializeBots() {
  eaBots.value = botDefinitions.map((bot, index) => ({
    ...bot,
    pnl: 0,
    active: false,
    position: null,
    nextActionTick: 2 + index
  }))
}

onMounted(() => {
  initializeBots()

  copyLogs.value = [
    {
      id: 1,
      type: 'sync',
      label: '实盘',
      text: '实盘行情演示已启动',
      botName: '',
      botColor: ''
    },
    {
      id: 2,
      type: 'sync',
      label: '同步',
      text: '8 个实盘 EA 已加载',
      botName: '',
      botColor: ''
    },
    {
      id: 3,
      type: 'track',
      label: '等待',
      text: '正在持续扫描策略信号',
      botName: '',
      botColor: ''
    },
    {
      id: 4,
      type: 'sync',
      label: '连接',
      text: '已成功连接 MT5 交易服务器',
      botName: '',
      botColor: ''
    },
    {
      id: 5,
      type: 'copy',
      label: '初始化',
      text: '账户资金与风控参数校验完成',
      botName: '',
      botColor: ''
    }
  ]

  initChart()
  simulationTimer = setInterval(advanceMarket, SIM_TICK_MS)
})

onBeforeUnmount(() => {
  if (simulationTimer) {
    clearInterval(simulationTimer)
    simulationTimer = null
  }

  resizeObserver?.disconnect()
  resizeObserver = null

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
          <div class="chart-topbar">
            <div class="symbol-badge">XAUUSD</div>
            <div class="simulation-badge">
              <span class="simulation-dot"></span>
              实盘行情 · 持续运行
            </div>
          </div>

          <div ref="chartHost" class="mt5-chart-canvas"></div>
        </div>
      </section>

      <div class="right-top-group">
        <section class="metrics-grid">
          <article class="panel metric-card">
            <span class="panel-label">账户余额</span>
            <div class="panel-main-val" :class="{ positive: accountBalance >= INITIAL_BALANCE, negative: accountBalance < INITIAL_BALANCE }">
              {{ formattedBalance }}
            </div>
            <div class="panel-sub-text">初始余额 {{ formatMoney(INITIAL_BALANCE) }}</div>
          </article>

          <article class="panel metric-card">
            <span class="panel-label">总盈亏</span>
            <div class="panel-main-val" :class="{ positive: totalProfit > 0, negative: totalProfit < 0 }">
              {{ formattedTotalProfit }}
            </div>
            <div class="panel-sub-text" :class="{ positive: totalProfit > 0, negative: totalProfit < 0 }">
              总体收益 {{ totalReturn.toFixed(2) }}%
            </div>
          </article>

          <article class="panel metric-card">
            <span class="panel-label">最大回撤</span>
            <div class="panel-main-val negative">
              -{{ chartStats.maxDrawdown.toFixed(1) }}%
            </div>
            <div class="panel-sub-text">
              当前回撤 -{{ currentDrawdown.toFixed(1) }}% · 峰值
              {{ formatMoney(chartStats.peakBalance) }}
            </div>
          </article>

          <article class="panel metric-card">
            <span class="panel-label">胜率</span>
            <div class="winrate-content">
              <div
                class="winrate-circle"
                :style="{
                  background: `conic-gradient(var(--positive) 0 ${winRate}%, var(--panel-border) ${winRate}% 100%)`
                }"
              >
                <span>{{ winRate }}%</span>
              </div>

              <div class="winrate-badge-text">
                <span class="win">{{ winningTrades }} 次盈利</span>
                /
                <span class="loss">{{ losingTrades }} 次亏损</span>
              </div>
            </div>
          </article>

          <article class="panel metric-card">
            <span class="panel-label">总交易次数</span>
            <div class="panel-main-val">{{ closedTrades }}</div>
            <div class="panel-sub-text">
              盈利 {{ winningTrades }} 次 · 亏损 {{ losingTrades }} 次
            </div>
          </article>

          <article class="panel metric-card">
            <span class="panel-label">盈利因子</span>
            <div class="panel-main-val">
              {{ Number.isFinite(profitFactor) ? profitFactor.toFixed(2) : '∞' }}
            </div>
            <div class="panel-sub-text">总盈利与总亏损之比</div>
          </article>

          <article class="panel metric-card">
            <span class="panel-label">平均每笔盈亏</span>
            <div class="panel-main-val" :class="{ positive: averageProfit > 0, negative: averageProfit < 0 }">
              {{ formatSignedMoney(averageProfit) }}
            </div>
            <div class="panel-sub-text">每笔已平仓交易</div>
          </article>

          <article class="panel metric-card">
            <span class="panel-label">已加载 EA 数量</span>
            <div class="panel-main-val">{{ eaBots.length }}</div>
            <div class="panel-sub-text">个实盘策略持续运行</div>
          </article>
        </section>

        <section class="panel history-panel">
          <div class="panel-heading">
            <span class="panel-label">余额历史</span>
            <span class="history-tag">最近 48 次余额记录</span>
          </div>

          <div class="history-chart">
            <svg
              viewBox="0 0 600 150"
              preserveAspectRatio="none"
              role="img"
              aria-label="账户余额变化曲线"
            >
              <defs>
                <linearGradient id="historyFill" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stop-color="#0ecb81" stop-opacity=".2" />
                  <stop offset="100%" stop-color="#0ecb81" stop-opacity="0" />
                </linearGradient>
              </defs>

              <line
                x1="0" y1="50" x2="600" y2="50"
                stroke="#222630" stroke-dasharray="4 5"
              />
              <line
                x1="0" y1="100" x2="600" y2="100"
                stroke="#222630" stroke-dasharray="4 5"
              />

              <path :d="balanceHistoryAreaPath" fill="url(#historyFill)" />
              <path
                :d="balanceHistoryPath"
                fill="none"
                stroke="#0ecb81"
                stroke-width="2"
                vector-effect="non-scaling-stroke"
              />
            </svg>
          </div>

          <div class="history-axis">
            <span>较早记录</span>
            <span>中间记录</span>
            <span>最新余额</span>
          </div>
        </section>
      </div>

      <section class="panel ea-bots-panel">
        <div class="ea-panel-header">
          <span class="panel-label">EA 机器人列表</span>
          <span class="ea-target-info">
            共 {{ eaBots.length }} 个机器人 · 持仓优先显示 · 点击前往购买
          </span>
        </div>

        <TransitionGroup name="ea-list" tag="div" class="ea-track-grid">
          <article
            v-for="(bot, index) in displayEaBots"
            :key="bot.id"
            class="ea-card clickable-card"
            @click="handleBotClick(bot)"
            :class="{
              active: Boolean(bot.position),
              'lead-trading': Boolean(bot.position) && index === 0,
              'other-trading': Boolean(bot.position) && index !== 0
            }"
            :style="{ '--bot-color': bot.color }"
          >
            <div class="ea-card-header">
              <div
                class="ea-avatar-letter"
                :style="{ background: bot.color, color: '#0b0d12' }"
              >
                {{ bot.name.slice(0, 1) }}
              </div>

              <span
                class="ea-num"
                :class="{ 'trading-label': bot.position }"
                :style="{ color: bot.position ? bot.color : undefined }"
              >
                {{
                  bot.position
                    ? (index === 0 ? '主力交易中' : '交易中')
                    : `第 ${index + 1} 位`
                }}
              </span>
            </div>

            <div class="ea-name" :style="{ color: bot.color }">
              {{ bot.name }}
            </div>

            <div class="ea-return">{{ bot.returnStr }}</div>

            <div
              class="ea-position"
              :class="{ 'position-placeholder': !bot.position }"
            >
              <template v-if="bot.position">
                {{ bot.position.side === 'BUY' ? '买入' : '卖出' }}
                {{ bot.position.lot.toFixed(2) }} 手 · 浮盈
                <span :class="{ positive: bot.position.pnl >= 0, negative: bot.position.pnl < 0 }">
                  {{ formatSignedMoney(bot.position.pnl) }}
                </span>
              </template>
              <span v-else>未持仓</span>
            </div>

            <div class="ea-pnl">
              <span class="ea-pnl-label">累计盈亏</span>
              <span :class="{ positive: bot.pnl >= 0, negative: bot.pnl < 0 }">
                {{ formatSignedMoney(bot.pnl) }}
              </span>
            </div>
          </article>
        </TransitionGroup>
      </section>

      <section class="panel copy-log-panel">
        <div class="panel-heading">
          <span class="panel-label">实时跟单日志</span>
          <span class="live-indicator"><i></i>持续实盘</span>
        </div>

        <div class="copy-log-list">
          <div
            v-for="(log, index) in copyLogs"
            :key="log.id"
            class="log-item"
            :style="{ opacity: Math.max(0.2, 1 - index * 0.08) }"
          >
            <span
              class="log-badge"
              :class="log.type"
              :style="log.botColor ? { color: log.botColor } : undefined"
            >
              [{{ log.label }}]
            </span>

            <span
              v-if="log.botName"
              class="log-bot-name"
              :style="{ color: log.botColor }"
            >
              {{ log.botName }}
            </span>

            <span
              class="log-content"
              :style="log.botColor ? { color: log.botColor } : undefined"
            >
              {{ log.text }}
            </span>
          </div>
        </div>
      </section>
    </div>

    <section class="panel trading-records-panel">
      <div class="records-heading">
        <div>
          <span class="panel-label">实盘交易记录</span>
          <p class="records-subtitle">
            实盘真实订单，已连接交易账户；记录随交易持续更新
          </p>
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
              <td class="record-bot" :style="{ color: record.color }">
                {{ record.bot }}
              </td>
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
                <span
                  class="status-tag"
                  :class="{ running: record.status === '持仓中' }"
                >
                  {{ record.status }}
                </span>
              </td>
            </tr>

            <tr v-if="!tradingRecords.length">
              <td colspan="9" class="empty-records">
                正在等待第一笔实盘交易……
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

.grok-live-page *::-webkit-scrollbar,
:global(html::-webkit-scrollbar),
:global(body::-webkit-scrollbar) {
  display: none;
  width: 0;
  height: 0;
}

:global(html),
:global(body) {
  scrollbar-width: none;
  -ms-overflow-style: none;
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

/* 桌面端上下两行使用相同的网格列宽 */
.main-layout-grid {
  display: grid;
  grid-template-columns: minmax(0, 2.15fr) minmax(0, 0.85fr);
  grid-template-areas:
    "chart right-top"
    "ea logs";
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

/* 顶部左侧图表面板 */
.chart-panel {
  grid-area: chart;
  align-self: stretch;
  width: 100%;
  min-width: 0;
  padding: 8px;
}

/* 右侧区域整体高度由图表所在的第一行决定 */
.right-top-group {
  grid-area: right-top;
  display: flex;
  flex-direction: column;
  gap: 8px;
  height: 100%;
  min-width: 0;
  min-height: 0;
}

/* 8 张小卡片：两列、四行，每行 62px */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  grid-template-rows: repeat(4, 62px);
  flex: 0 0 auto;
  gap: 6px;
  min-width: 0;
}

.metric-card {
  display: flex;
  flex-direction: column;
  justify-content: center;
  height: 62px;
  min-width: 0;
  min-height: 0;
  padding: 6px 8px;
}

.panel-label {
  display: block;
  min-width: 0;
  color: var(--text-sub);
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.3px;
}

.panel-main-val {
  overflow: hidden;
  margin-top: 4px;
  color: var(--text-main);
  font-size: clamp(11px, 0.9vw, 16px);
  font-weight: 750;
  line-height: 1.2;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.panel-main-val.positive,
.panel-sub-text.positive {
  color: var(--positive);
}

.panel-main-val.negative,
.panel-sub-text.negative {
  color: var(--negative);
}

.panel-sub-text {
  margin-top: 3px;
  color: var(--text-sub);
  font-size: 8.5px;
  line-height: 1.3;
  overflow-wrap: anywhere;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 图表自身高度 */
.mt5-chart-container {
  position: relative;
  width: 100%;
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

.chart-topbar {
  position: absolute;
  z-index: 5;
  top: 12px;
  left: 12px;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  max-width: calc(100% - 24px);
  pointer-events: none;
}

.symbol-badge,
.simulation-badge {
  position: relative;
  display: inline-flex;
  align-items: center;
  min-height: 28px;
  padding: 0 10px;
  border: 1px solid #303746;
  border-radius: 5px;
  background: rgba(20, 23, 34, 0.94);
  font-size: 11px;
  font-weight: 750;
}

.symbol-badge {
  color: #e8c56a;
  letter-spacing: 0.5px;
}

.simulation-badge {
  gap: 6px;
  border-color: #263d36;
  color: #0ecb81;
  font-size: 10px;
  font-weight: 500;
}

.simulation-dot {
  width: 6px;
  height: 6px;
  flex: 0 0 6px;
  border-radius: 50%;
  background: #0ecb81;
  box-shadow: 0 0 6px rgba(14, 203, 129, 0.45);
  animation: livePulse 1.5s ease-in-out infinite;
}

@keyframes livePulse {
  50% {
    opacity: 0.35;
  }
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

.live-indicator {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  color: var(--text-sub);
  font-size: 9px;
  white-space: nowrap;
}

.live-indicator i {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: var(--positive);
  box-shadow: 0 0 6px rgba(14, 203, 129, 0.45);
  animation: livePulse 1.5s ease-in-out infinite;
}

/* 余额历史占据右侧剩余空间 */
.history-panel {
  display: flex;
  flex: 1 1 0;
  flex-direction: column;
  min-width: 0;
  min-height: 150px;
  margin: 0;
  padding: 12px;
}

.history-chart {
  flex: 1 1 auto;
  min-width: 0;
  min-height: 60px;
  margin-top: 8px;
}

.history-chart svg {
  display: block;
  width: 100%;
  height: 100%;
  min-height: 60px;
}

.history-axis {
  display: flex;
  justify-content: space-between;
  gap: 5px;
  margin-top: 6px;
  color: var(--text-sub);
  font-size: 9px;
}

.winrate-content {
  display: flex;
  align-items: center;
  flex-wrap: nowrap;
  gap: 5px;
  margin-top: 3px;
  min-width: 0;
}

.winrate-circle {
  position: relative;
  display: grid;
  place-items: center;
  width: 24px;
  height: 24px;
  flex: 0 0 24px;
  border-radius: 50%;
  font-size: 8px;
  font-weight: 750;
}

.winrate-circle::before {
  position: absolute;
  inset: 3px;
  border-radius: 50%;
  background: var(--panel-bg);
  content: "";
}

.winrate-circle span {
  position: relative;
  z-index: 1;
}

.winrate-badge-text {
  font-size: 8px;
  font-weight: 700;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  min-width: 0;
}

.winrate-badge-text .win {
  color: var(--positive);
}

.winrate-badge-text .loss {
  color: var(--text-sub);
}

/* 底部 EA 和日志面板共用同一行网格 */
.ea-bots-panel {
  grid-area: ea;
  align-self: stretch;
  width: 100%;
  height: 100%;
  min-width: 0;
  margin: 0;
  padding: 12px;
}

.copy-log-panel {
  grid-area: logs;
  align-self: stretch;
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
  min-width: 0;
  min-height: 0;
  margin: 0;
  padding: 12px;
  overflow: hidden;
}

/* 8 个 EA 卡片保持固定高度 */
.ea-track-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  grid-auto-rows: 142px;
  align-items: start;
  gap: 10px;
  min-width: 0;
  padding: 12px 3px;
}

.ea-list-move {
  transition: transform 0.38s cubic-bezier(0.18, 0.89, 0.32, 1.28);
  z-index: 5;
}

.ea-card {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: stretch;
  gap: 5px;
  width: 100%;
  height: 142px;
  min-width: 0;
  min-height: 142px;
  max-height: 142px;
  padding: 10px;
  overflow: hidden;
  box-sizing: border-box;
  background: var(--主页面背景色, #0b0d12);
  border: 1px solid var(--panel-border);
  border-radius: var(--小圆角, 6px);
  transform: translateY(0);
  transition:
    border-color 0.28s ease,
    background 0.28s ease,
    box-shadow 0.28s ease;
}

.ea-card.clickable-card {
  cursor: pointer;
}

.ea-card.clickable-card:hover {
  filter: brightness(1.15);
  transform: translateY(-3px);
  box-shadow: 0 6px 18px color-mix(in srgb, var(--bot-color, #4c8dff) 25%, transparent);
}

.ea-card.active {
  border-color: var(--bot-color, #4c8dff);
  background: linear-gradient(
    145deg,
    color-mix(in srgb, var(--bot-color, #4c8dff) 14%, transparent),
    #0b0d12 78%
  );
  box-shadow:
    0 0 12px color-mix(in srgb, var(--bot-color, #4c8dff) 16%, transparent);
}

.ea-card.lead-trading {
  z-index: 3;
  border-color: var(--bot-color, #4c8dff);
  animation: leadEaFloat 1.5s ease-in-out infinite;
}

.ea-card.other-trading {
  border-color: var(--bot-color, #4c8dff);
  box-shadow:
    0 0 10px color-mix(in srgb, var(--bot-color, #4c8dff) 12%, transparent);
}

@keyframes leadEaFloat {
  0%,
  100% {
    transform: translateY(0);
    box-shadow:
      0 0 0 1px color-mix(in srgb, var(--bot-color, #4c8dff) 24%, transparent),
      0 5px 14px color-mix(in srgb, var(--bot-color, #4c8dff) 16%, transparent);
  }

  50% {
    transform: translateY(-8px);
    box-shadow:
      0 0 0 1px color-mix(in srgb, var(--bot-color, #4c8dff) 50%, transparent),
      0 14px 28px color-mix(in srgb, var(--bot-color, #4c8dff) 30%, transparent);
  }
}

.ea-card.lead-trading:hover {
  animation-play-state: paused;
}

.ea-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 4px;
  flex: 0 0 26px;
  min-height: 26px;
}

.ea-avatar-letter {
  display: grid;
  place-items: center;
  width: 26px;
  height: 26px;
  flex: 0 0 26px;
  border-radius: 50%;
  font-size: 10px;
  font-weight: 800;
  box-shadow:
    0 0 12px color-mix(in srgb, var(--bot-color, #4c8dff) 18%, transparent);
}

.ea-num {
  min-width: 0;
  overflow: hidden;
  color: var(--text-sub);
  font-size: 9px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.ea-num.trading-label {
  font-weight: 750;
}

.ea-name {
  flex: 0 0 14px;
  min-width: 0;
  height: 14px;
  overflow: hidden;
  font-size: 11px;
  font-weight: 700;
  line-height: 14px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.ea-return {
  flex: 0 0 13px;
  min-width: 0;
  height: 13px;
  overflow: hidden;
  color: var(--text-sub);
  font-size: 9px;
  line-height: 13px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.ea-position {
  flex: 0 0 14px;
  width: 100%;
  height: 14px;
  min-width: 0;
  overflow: hidden;
  color: #e8c56a;
  font-size: 9px;
  line-height: 14px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.ea-position.position-placeholder {
  visibility: hidden;
}

.ea-position span {
  color: var(--positive);
  font-weight: 700;
}

.ea-position span.negative {
  color: var(--negative);
}

.ea-pnl {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 4px;
  flex: 0 0 14px;
  width: 100%;
  height: 14px;
  min-width: 0;
  margin-top: 2px;
  color: var(--text-sub);
  font-size: 9px;
  line-height: 14px;
}

.ea-pnl-label {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.ea-pnl > span:last-child {
  flex: 0 0 auto;
  color: var(--positive);
  font-weight: 700;
  white-space: nowrap;
}

.ea-pnl > span.negative {
  color: var(--negative);
}

.copy-log-list {
  display: flex;
  flex-direction: column;
  gap: 7px;
  min-width: 0;
  margin-top: 10px;
  flex: 1 1 auto;
  justify-content: space-between;
}

.log-item {
  display: flex;
  align-items: center;
  gap: 6px;
  min-width: 0;
  font-family: monospace;
  font-size: 9px;
  line-height: 1.35;
}

.log-badge {
  flex: 0 0 auto;
  font-weight: 700;
}

.log-badge.exit {
  color: var(--text-sub);
}

.log-badge.sync {
  color: var(--positive);
}

.log-badge.fill {
  color: #f3c66b;
}

.log-badge.track {
  color: #9b9fff;
}

.log-badge.copy {
  color: #a98aff;
}

.log-bot-name {
  flex: 0 0 auto;
  max-width: 110px;
  overflow: hidden;
  font-weight: 750;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.log-content {
  min-width: 0;
  overflow: hidden;
  color: var(--text-sub);
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 交易记录 */
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
  background: rgba(132, 142, 156, 0.05);
}

.record-time {
  color: var(--text-sub) !important;
  font-variant-numeric: tabular-nums;
}

.record-bot {
  font-weight: 700;
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
  background: rgba(14, 203, 129, 0.1);
}

.side-tag.sell {
  color: var(--negative);
  background: rgba(246, 70, 93, 0.1);
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
  background: rgba(132, 142, 156, 0.1);
}

.status-tag.running {
  color: var(--positive);
  background: rgba(14, 203, 129, 0.1);
}

.empty-records {
  padding: 24px !important;
  color: var(--text-sub) !important;
  text-align: center;
}

/* 平板：恢复单列主布局，指标卡片改为四列 */
@media (max-width: 1050px) {
  .grok-live-page {
    --chart-height: clamp(400px, 55vh, 580px);
  }

  .main-layout-grid {
    grid-template-columns: minmax(0, 1fr);
    grid-template-areas:
      "chart"
      "ea"
      "right-top"
      "logs";
    align-items: stretch;
  }

  .right-top-group {
    height: auto;
  }

  .metrics-grid {
    grid-template-columns: repeat(4, minmax(0, 1fr));
    grid-template-rows: auto;
  }

  .metric-card {
    height: auto;
    min-height: 72px;
  }

  .history-panel {
    flex: none;
    min-height: 190px;
  }

  .ea-bots-panel,
  .copy-log-panel {
    height: auto;
  }

  .copy-log-panel {
    min-height: 150px;
  }
}

/* 手机：两列 EA 卡片、两列指标卡片 */
@media (max-width: 620px) {
  .grok-live-page {
    --chart-height: 400px;
    padding: 8px;
  }

  .metrics-grid,
  .ea-track-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .ea-track-grid {
    grid-auto-rows: 142px;
  }

  .metrics-grid {
    grid-template-rows: auto;
    gap: 8px;
  }

  .metric-card {
    height: auto;
    min-height: 76px;
  }

  .panel,
  .trading-records-panel {
    padding: 10px;
  }

  .chart-panel {
    padding: 6px;
  }

  .records-subtitle {
    font-size: 8px;
  }

  .records-table th,
  .records-table td {
    padding: 10px;
  }

  .ea-target-info,
  .history-tag,
  .records-count {
    font-size: 9px;
  }

  .log-bot-name {
    max-width: 90px;
  }

  .chart-topbar {
    top: 8px;
    left: 8px;
    gap: 5px;
    max-width: calc(100% - 16px);
  }

  .symbol-badge,
  .simulation-badge {
    min-height: 26px;
    padding-inline: 7px;
    font-size: 9px;
  }
}
</style>
