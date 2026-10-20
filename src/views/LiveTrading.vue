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

    <!-- 页面标题：保留原有视觉体系 -->
    <header class="live-heading">
      <div class="heading-left">
        <div class="eyebrow">
          <span class="eyebrow-line"></span>
          LOZENO / LIVE INTELLIGENCE
        </div>
        <h1>实盘<span>直播</span><i class="title-dot"></i></h1>
        <p class="heading-subtitle">AI QUANTITATIVE TRADING COMMAND CENTER</p>
      </div>

      <div class="system-status">
        <span class="status-light"></span>
        <div>
          <strong>演示模式</strong>
          <small>LIVE DATA · NOT CONNECTED</small>
        </div>
        <span class="status-divider"></span>
        <div class="system-clock">
          <small>当前品种</small>
          <strong>{{ activeInstrument.id }}</strong>
        </div>
      </div>
    </header>

    <section class="terminal-frame">
      <div class="frame-topline">
        <span class="corner-label"><i></i> LIVE TERMINAL <b>01</b></span>
        <span class="frame-caption">REAL-TIME MARKET MONITOR</span>
        <span class="demo-state">布局预览 · 数据待接入</span>
      </div>

      <!-- 第一排：全球市场行情滚动条 -->
      <section class="ticker-section">
        <div class="ticker-heading">
          <span class="section-kicker"><i></i> GLOBAL MARKETS</span>
          <span class="ticker-demo">演示报价</span>
        </div>

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

        <div class="ticker-bottom">
          <span>点击品种切换图表</span>
          <span class="ticker-selected">
            当前选择 <b>{{ activeInstrument.name }}</b>
          </span>
        </div>
      </section>

      <!-- 第二排：AI 分析 -->
      <section class="ai-panel">
        <div class="ai-panel-heading">
          <div class="panel-title">
            <span class="ai-emblem"><span>AI</span></span>
            <div>
              <h2>AI 波段分析</h2>
              <p>ALGORITHMIC DIRECTION · M5 ANALYSIS</p>
            </div>
          </div>
          <span class="ai-waiting"><i></i> 等待算法接入</span>
        </div>

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

        <div class="ai-bottom-line">
          <span>MODEL STATUS <b>STANDBY</b></span>
          <span>方向、概率、进度和分析结论将在接入算法后显示</span>
        </div>
      </section>

      <!-- 第三排：TradingView 沉浸式看盘 -->
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

      <!-- 第四排：自研波段方向 K 线 -->
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

      <!-- 第五排：历史真实做单记录的展示框架 -->
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

      <footer class="terminal-footer">
        <div class="footer-brand">
          <span class="footer-brand-mark">L</span>
          LOZENO <span class="footer-separator">/</span> QUANT LIVE
        </div>
        <div class="footer-center">
          <span class="footer-pulse"></span>
          REAL-TIME TRADING OBSERVABILITY
        </div>
        <div class="footer-version">LIVE TERMINAL <b>V1.0</b></div>
      </footer>
    </section>
  </main>
</template>

<style scoped>
.live-page {
  --blue: #426bff;
  --cyan: #00dfff;
  --purple: #a16bff;
  --line: #1c2b43;
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
  opacity: .2;
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
.ambient-purple { top: 780px; right: -260px; background: #9c3dff; }

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
  min-width: 300px;
  padding: 14px 18px;
  border: 1px solid rgba(74, 107, 174, .27);
  background: linear-gradient(120deg, rgba(17, 29, 54, .85), rgba(17, 17, 37, .75));
}

.status-light,
.ai-waiting i,
.history-status i,
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
.system-clock small { display: block; }
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
    linear-gradient(125deg, rgba(0, 229, 255, .65), rgba(49, 91, 255, .25) 32%, rgba(133, 72, 255, .38) 72%, rgba(0, 229, 255, .4)) border-box;
  box-shadow: 0 0 32px rgba(30, 88, 255, .07), inset 0 0 35px rgba(27, 70, 170, .035);
}

.terminal-frame::before,
.terminal-frame::after {
  position: absolute;
  z-index: 2;
  width: 64px;
  height: 2px;
  content: "";
  background: linear-gradient(90deg, #00e5ff, transparent);
  box-shadow: 0 0 12px rgba(0, 229, 255, .6);
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
  border-bottom: 1px solid var(--line);
  background: linear-gradient(90deg, rgba(12, 29, 53, .9), rgba(16, 14, 36, .8));
}

.corner-label { color: #8ca4cf; font-size: 9px; font-weight: 700; letter-spacing: 1.7px; }
.corner-label i { display: inline-block; width: 5px; height: 5px; margin-right: 8px; background: #00e5ff; box-shadow: 0 0 8px #00e5ff; }
.corner-label b { margin-left: 7px; color: #00e5ff; }
.frame-caption { color: #405579; font-size: 8px; letter-spacing: 1.6px; }
.demo-state { color: #d7b77d; font-size: 10px; }

/* 第一排：行情滚动条 */
.ticker-section {
  padding: 15px 0 0;
  border-bottom: 1px solid var(--line);
  background: linear-gradient(90deg, rgba(16, 25, 43, .78), rgba(11, 13, 29, .86));
}

.ticker-heading,
.ticker-bottom {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding-inline: 20px;
}

.section-kicker { color: #8198bd; font-size: 9px; font-weight: 700; letter-spacing: 1.7px; }
.section-kicker i { display: inline-block; width: 5px; height: 5px; margin-right: 7px; background: #00dfff; box-shadow: 0 0 8px #00dfff; }
.ticker-demo { color: #8b7959; font-size: 9px; }

.ticker-viewport {
  margin-top: 12px;
  overflow: hidden;
  border-block: 1px solid rgba(49, 68, 102, .36);
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
  color: #e4edff;
  text-align: left;
  border: 0;
  border-right: 1px solid rgba(49, 68, 102, .42);
  background: transparent;
  cursor: pointer;
  transition: background .2s, box-shadow .2s;
}

.ticker-item:hover { background: rgba(47, 77, 132, .15); }
.ticker-item.selected { background: linear-gradient(180deg, rgba(46, 91, 255, .13), rgba(46, 91, 255, .035)); box-shadow: inset 0 -2px #4779ff; }

.ticker-symbol-icon {
  display: grid;
  flex: 0 0 auto;
  width: 34px;
  height: 34px;
  place-items: center;
  border: 1px solid currentColor;
  border-radius: 50%;
  background: rgba(255, 255, 255, .025);
  font-size: 12px;
  font-weight: 800;
}

.ticker-info { display: flex; flex-direction: column; gap: 4px; min-width: 64px; }
.ticker-name { color: #dce7fb; font-size: 11px; font-weight: 800; letter-spacing: .5px; }
.ticker-full-name { color: #667b9d; font-size: 9px; }
.ticker-quote { display: flex; flex-direction: column; gap: 4px; margin-left: auto; text-align: right; }
.ticker-quote strong { color: #dce7fb; font-size: 11px; font-variant-numeric: tabular-nums; }
.ticker-quote small { font-size: 10px; }
.ticker-up .ticker-quote small,
.ticker-up .ticker-arrow { color: #39d9a8; }
.ticker-down .ticker-quote small,
.ticker-down .ticker-arrow { color: #ff6e8c; }
.ticker-arrow { align-self: flex-start; font-size: 14px; }
.ticker-bottom { min-height: 33px; color: #526987; font-size: 9px; }
.ticker-selected b { margin-left: 4px; color: #8bbaff; }

@keyframes ticker-scroll {
  from { transform: translateX(0); }
  to { transform: translateX(-50%); }
}

/* 第二排：AI 分析 */
.ai-panel {
  position: relative;
  padding: 20px 22px 14px;
  overflow: hidden;
  border-bottom: 1px solid var(--line);
  background: linear-gradient(100deg, rgba(10, 25, 47, .98), rgba(17, 13, 39, .98));
}

.ai-panel::before {
  position: absolute;
  top: 0;
  left: 0;
  width: 25%;
  height: 1px;
  content: "";
  background: linear-gradient(90deg, #00e5ff, transparent);
  box-shadow: 0 0 10px #00bfff;
}

.ai-panel-heading,
.panel-heading,
.panel-title {
  display: flex;
  align-items: center;
}

.ai-panel-heading,
.panel-heading { justify-content: space-between; gap: 12px; }

.panel-title { gap: 11px; min-width: 0; }
.panel-title h2 { color: #e7efff; font-size: 14px; font-weight: 700; letter-spacing: .4px; }
.panel-title p { margin-top: 5px; color: #5a6f92; font-size: 8px; letter-spacing: 1.2px; }
.panel-index { color: #43baff; font-size: 11px; font-weight: 800; letter-spacing: 1px; }
.purple-index { color: #bb88ff; }

.ai-emblem {
  display: grid;
  width: 34px;
  height: 34px;
  place-items: center;
  border: 1px solid rgba(0, 221, 255, .4);
  background: linear-gradient(145deg, rgba(0, 221, 255, .17), rgba(116, 81, 255, .12));
  box-shadow: inset 0 0 10px rgba(0, 221, 255, .07);
  transform: rotate(45deg);
}

.ai-emblem span { color: #7be9ff; font-size: 11px; font-weight: 800; transform: rotate(-45deg); }
.ai-waiting { display: flex; align-items: center; gap: 8px; color: #7c8eaf; font-size: 10px; white-space: nowrap; }
.ai-waiting i { background: #9e75ff; box-shadow: 0 0 8px rgba(158, 117, 255, .5); }

.ai-main-row {
  display: flex;
  align-items: center;
  gap: 24px;
  min-height: 104px;
}

.direction-block { min-width: 150px; }
.direction-block small,
.ai-metric > small,
.ai-summary small { display: block; color: #7185a8; font-size: 10px; }
.direction-block strong { display: block; margin-top: 8px; color: #8ca1c4; font-size: 24px; }
.direction-block strong span { margin-left: 6px; font-size: 12px; font-weight: 500; }
.ai-divider { width: 1px; height: 42px; background: linear-gradient(transparent, #2c3e63, transparent); }
.ai-metric { flex: 1; min-width: 100px; }
.ai-metric strong { display: block; margin-top: 7px; color: #dbe7ff; font-size: 22px; font-weight: 700; }
.ai-metric strong span { margin-left: 3px; color: #7288ad; font-size: 12px; }
.metric-track { width: 100%; max-width: 170px; height: 3px; margin-top: 9px; overflow: hidden; background: #202c44; }
.metric-track span { display: block; width: 0; height: 100%; }
.track-blue { background: linear-gradient(90deg, #315bff, #00e5ff); }
.track-purple { background: linear-gradient(90deg, #6e4cff, #ff4db8); }
.ai-summary { display: flex; align-items: center; gap: 12px; min-width: 190px; }
.summary-icon { color: #9f79ff; font-size: 26px; }
.ai-summary strong { display: block; margin-top: 7px; color: #a9b9d5; font-size: 11px; }
.ai-bottom-line { display: flex; align-items: center; justify-content: space-between; gap: 12px; padding-top: 10px; border-top: 1px solid rgba(67, 94, 143, .18); color: #536b90; font-size: 8px; letter-spacing: .6px; }
.ai-bottom-line b { margin-left: 7px; color: #ac8bff; font-weight: 600; }

/* 第三、四排：统一的图表容器 */
.section-panel {
  min-width: 0;
  padding: 20px;
  border-bottom: 1px solid var(--line);
  background: #080d18;
}

.panel-heading { margin-bottom: 16px; }
.chart-meta { display: flex; align-items: center; gap: 9px; }
.selected-symbol { color: #91bfff; font-size: 10px; font-weight: 700; }
.period-badge { padding: 5px 9px; color: #61dfff; border: 1px solid rgba(0, 207, 255, .24); background: rgba(0, 190, 255, .06); font-size: 9px; }
.panel-badge { padding: 5px 8px; font-size: 8px; letter-spacing: .7px; }
.purple-badge { color: #c59aff; border: 1px solid rgba(164, 105, 255, .3); background: rgba(164, 105, 255, .07); }

.tradingview-toolbar,
.wave-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  min-height: 39px;
  padding: 0 12px;
  border: 1px solid #1a2b44;
  border-bottom: 0;
  background: #0d1422;
}

.toolbar-instrument,
.toolbar-right,
.wave-legend {
  display: flex;
  align-items: center;
  gap: 10px;
}

.toolbar-instrument strong { color: #c7d7f2; font-size: 11px; }
.toolbar-instrument > span:last-child { color: #7488a8; font-size: 10px; }
.instrument-dot { width: 6px; height: 6px; border-radius: 50%; background: #54d9ff; box-shadow: 0 0 8px #54d9ff; }
.purple-dot { background: #b17bff; box-shadow: 0 0 8px #b17bff; }
.toolbar-period-active { padding: 5px 8px; color: #e4edff; border: 1px solid #36518a; background: #1a2c4d; font-size: 10px; }
.toolbar-hint { color: #657b9d; font-size: 9px; }

.tradingview-container {
  position: relative;
  width: 100%;
  height: clamp(420px, 49vw, 660px);
  min-height: 360px;
  overflow: hidden;
  border: 1px solid #1a2b44;
  background:
    radial-gradient(ellipse at 45% 48%, rgba(17, 58, 105, .13), transparent 65%),
    #080e19;
}

.tradingview-container iframe {
  display: block;
  width: 100%;
  height: 100%;
  border: 0;
  background: #080e19;
}

.chart-panel-footer,
.wave-footer {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 18px;
  min-height: 34px;
  color: #637896;
  font-size: 9px;
}

.chart-panel-footer > span,
.wave-footer > span { display: flex; align-items: center; gap: 6px; }
.legend-tv { width: 6px; height: 6px; border-radius: 50%; background: #60b9ff; }
.chart-panel-footer > span:not(:first-child) { color: #526987; }

/* 自研波段 K 线 */
.wave-panel {
  background:
    linear-gradient(180deg, rgba(19, 13, 37, .3), transparent 42%),
    #080d18;
}

.wave-toolbar { border-color: #292448; background: #100f20; }
.wave-legend { flex-wrap: wrap; justify-content: flex-end; gap: 12px; color: #7684a7; font-size: 9px; }
.wave-legend span { display: flex; align-items: center; gap: 5px; }
.legend-up, .legend-down { display: inline-block; width: 6px; height: 6px; }
.legend-up { background: #36e9bd; }
.legend-down { background: #ff5b86; }
.legend-projection { width: 14px; height: 0; border-top: 1px dashed #a16bff; }

.wave-chart {
  position: relative;
  height: clamp(300px, 36vw, 450px);
  overflow: hidden;
  border: 1px solid #292448;
  background:
    radial-gradient(ellipse at 48% 45%, rgba(92, 36, 150, .12), transparent 65%),
    #0a0b19;
}

.wave-grid { position: absolute; inset: 0 54px 25px 0; }
.wave-grid-row { height: 16.666%; border-bottom: 1px solid rgba(100, 108, 164, .13); }
.wave-grid-col { position: absolute; top: 0; bottom: 0; width: 1px; background: rgba(100, 108, 164, .12); }
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
  color: rgba(134, 107, 211, .06);
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
  color: rgba(134, 107, 211, .17);
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
  color: #657192;
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
  color: #657192;
  font-size: 9px;
}

.wave-corner { position: absolute; width: 12px; height: 12px; pointer-events: none; }
.wave-corner-tl { top: 0; left: 0; border-top: 1px solid #b36dff; border-left: 1px solid #b36dff; }
.wave-corner-br { right: 53px; bottom: 24px; border-right: 1px solid #b36dff; border-bottom: 1px solid #b36dff; }
.wave-footer .footer-note { margin-left: auto; color: #536487; }

/* 第五排：历史交易记录 */
.history-panel { padding-bottom: 16px; }
.history-heading { margin-bottom: 18px; }
.history-status { display: flex; align-items: center; gap: 7px; color: #d2b578; font-size: 9px; white-space: nowrap; }
.history-status i { background: #d8ae59; box-shadow: 0 0 7px rgba(216, 174, 89, .4); }

.history-overview {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  margin-bottom: 15px;
}

.history-description { display: flex; flex-direction: column; gap: 6px; }
.history-description strong { color: #c9d7ed; font-size: 11px; }
.history-description span { color: #687c9c; font-size: 10px; }

.history-filters { display: flex; gap: 5px; }
.history-filters button {
  padding: 7px 12px;
  color: #7285a5;
  border: 1px solid #24334d;
  background: #0c1321;
  font-size: 10px;
  cursor: pointer;
  transition: color .2s, border-color .2s, background .2s;
}
.history-filters button:hover { color: #c5d8ff; border-color: #3a5688; }
.history-filters button.active { color: #a7caff; border-color: #365db5; background: rgba(49, 91, 255, .13); }

.history-table-wrap {
  width: 100%;
  overflow-x: auto;
  border: 1px solid #1d2a41;
  background: #090e19;
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
  color: #8295b5;
  border-bottom: 1px solid #24324b;
  background: #101827;
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
  color: #647b9f;
  border: 1px solid #273754;
  background: rgba(41, 65, 107, .13);
}

.empty-history-icon svg { width: 21px; height: 21px; }
.empty-history strong { color: #aabbd5; font-size: 12px; }
.empty-history > span:not(.empty-history-icon) { color: #657996; font-size: 10px; }
.empty-history small { margin-top: 4px; color: #405777; font-size: 8px; letter-spacing: 1.3px; }

.history-table-footer {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  padding-top: 12px;
  color: #536987;
  font-size: 9px;
}

/* 底部 */
.terminal-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  min-height: 43px;
  padding: 0 18px;
  background: #080b14;
}

.footer-brand { display: flex; align-items: center; gap: 7px; color: #8195b9; font-size: 9px; font-weight: 800; letter-spacing: 1.5px; }
.footer-brand-mark { display: grid; width: 17px; height: 17px; place-items: center; color: #07111f; font-size: 10px; background: linear-gradient(135deg, #00e5ff, #536aff); }
.footer-separator { color: #354663; }
.footer-center { display: flex; align-items: center; gap: 8px; color: #43597b; font-size: 8px; letter-spacing: 1px; }
.footer-pulse { width: 5px; height: 5px; background: #687a9b; }
.footer-version { color: #526788; font-size: 8px; letter-spacing: 1px; }
.footer-version b { margin-left: 6px; color: #9baff0; font-weight: 500; }

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
  .live-heading { align-items: flex-start; flex-direction: column; }
  .system-status { width: 100%; min-width: 0; }
  .ai-main-row { flex-wrap: wrap; padding-block: 18px; }
  .ai-divider { display: none; }
  .direction-block, .ai-metric, .ai-summary { flex: 1 1 38%; min-width: 130px; }
  .tradingview-container { height: 480px; }
  .wave-chart { height: 350px; }
  .history-overview { align-items: flex-start; flex-direction: column; }
  .history-filters { width: 100%; }
  .history-filters button { flex: 1; }
}

@media (max-width: 520px) {
  .live-page { padding: 20px 9px 28px; }
  .heading-subtitle { font-size: 8px; letter-spacing: 1.2px; }
  .system-status { padding: 12px; }
  .frame-topline { padding-inline: 10px; }
  .frame-caption { display: none; }
  .ticker-heading, .ticker-bottom { padding-inline: 12px; }
  .ticker-item { min-width: 205px; padding: 13px 12px; }
  .ai-panel { padding: 16px 12px 12px; }
  .ai-main-row { gap: 20px 12px; }
  .direction-block, .ai-metric, .ai-summary { flex-basis: 42%; }
  .direction-block strong { font-size: 21px; }
  .ai-metric strong { font-size: 20px; }
  .ai-bottom-line { align-items: flex-start; flex-direction: column; }
  .section-panel { padding: 14px 9px; }
  .panel-title { gap: 8px; }
  .panel-title h2 { font-size: 12px; }
  .panel-title p { font-size: 7px; letter-spacing: .7px; }
  .chart-meta { gap: 5px; }
  .selected-symbol { font-size: 9px; }
  .panel-badge { display: none; }
  .tradingview-toolbar, .wave-toolbar { align-items: flex-start; flex-direction: column; justify-content: center; gap: 9px; padding-block: 10px; }
  .tradingview-container { height: 430px; min-height: 350px; }
  .wave-chart { height: 280px; }
  .wave-legend { justify-content: flex-start; font-size: 8px; }
  .wave-footer { gap: 10px; }
  .wave-footer .footer-note { width: 100%; margin-left: 0; }
  .history-overview { gap: 12px; }
  .history-description span { line-height: 1.6; }
  .history-table-footer { flex-direction: column; }
  .terminal-footer { align-items: flex-start; flex-direction: column; padding: 12px; }
}
</style>
