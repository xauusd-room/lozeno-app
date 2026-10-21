import { reactive } from 'vue'
const API_BASE = 'https://lozeno-api.aaa375750526.workers.dev'
export const eaProducts = reactive({
  1: { id: 1, name: 'TrendMaster Pro', subtitle: '自动趋势交易 EA · 为 MetaTrader 5 设计', tags: ['MT5', '趋势跟踪', '风险管理', '版本 2.1.0'], desc: 'TrendMaster Pro 是一款面向趋势行情的自动交易工具。用户可配置入场参数、止损止盈规则与风险控制选项，启用实盘前建议通过历史回测和模拟账户验证策略表现。', price: '$99.00', ret: '+24.50%', dd: '12.40%', win: '68.20%', pf: '1.76', platform: 'MetaTrader 5', platformTag: 'MT5', market: '外汇 / 贵金属', period: 'M15 / H1', update: '2026-10-01', type: '趋势跟踪', license: '单账户授权' },
  2: { id: 2, name: 'GridScalper X', subtitle: '网格震荡交易 EA · 面向 MetaTrader 4', tags: ['MT4', '网格策略', '参数可配置', '演示数据'], desc: 'GridScalper X 是一款以震荡行情为主要应用场景的网格交易 EA。网格策略在单边行情中可能累积较大浮亏，启用前应重点验证最大回撤、仓位上限与极端行情风险。', price: '$129.00', ret: '+112.80%', dd: '24.60%', win: '91.45%', pf: '1.42', platform: 'MetaTrader 4', platformTag: 'MT4', market: '以经纪商支持为准', period: 'M5 / M15', update: '2026-10-01', type: '网格震荡', license: '单账户授权' },
  3: { id: 3, name: 'NeuralArbitrage', subtitle: '算法套利 EA · 示例产品页面', tags: ['AI', '套利策略', '执行环境敏感', '演示数据'], desc: 'NeuralArbitrage 是一个算法套利类产品的页面示例。此类策略对行情延迟、点差、滑点和交易执行质量较为敏感，页面数据仅为布局演示，不能作为真实业绩依据。', price: '$149.00', ret: '-1.20%', dd: '8.70%', win: '54.10%', pf: '0.94', platform: 'AI / 独立系统', platformTag: 'AI', market: '以实际运行环境为准', period: '以实际策略为准', update: '2026-10-01', type: '高频套利', license: '单账户授权' },
  4: { id: 4, name: 'MartinMaster', subtitle: '马丁策略 EA · 面向 MetaTrader 4', tags: ['MT4', '马丁策略', '仓位风险', '演示数据'], desc: 'MartinMaster 是一款马丁类策略的产品页面示例。此类策略可能通过递增仓位应对连续亏损，但在持续单边行情中存在快速扩大回撤甚至爆仓的风险。', price: '$109.00', ret: '+45.20%', dd: '19.80%', win: '74.80%', pf: '1.21', platform: 'MetaTrader 4', platformTag: 'MT4', market: '以实际经纪商为准', period: '以实际策略为准', update: '2026-10-01', type: '马丁策略', license: '单账户授权' },
  5: { id: 5, name: 'MomentumHunter', subtitle: '动量追踪 EA · 捕捉行情加速阶段', tags: ['MT5', '动量追踪', '趋势过滤', '演示数据'], desc: 'MomentumHunter 面向动量行情设计，关注价格加速与趋势延续机会。当前业绩为模拟展示数据，实际表现需要通过历史回测和模拟账户验证。', price: '$99.00', ret: '+28.60%', dd: '9.20%', win: '71.30%', pf: '1.84', platform: 'MetaTrader 5', platformTag: 'MT5', market: '外汇 / 贵金属', period: 'M5 / M15', update: '2026-10-21', type: '动量追踪', license: '单账户授权' },
  6: { id: 6, name: 'BreakoutRetest Pro', subtitle: '突破回踩 EA · 识别关键位突破', tags: ['MT5', '突破交易', '回踩确认', '演示数据'], desc: 'BreakoutRetest Pro 关注关键价格区域的有效突破与回踩确认。当前业绩为模拟展示数据，实际策略表现需要通过历史行情与模拟交易验证。', price: '$119.00', ret: '+36.40%', dd: '10.80%', win: '69.70%', pf: '1.91', platform: 'MetaTrader 5', platformTag: 'MT5', market: '外汇 / 贵金属', period: 'M5 / M15 / H1', update: '2026-10-21', type: '突破回踩', license: '单账户授权' },
  7: { id: 7, name: 'ReversalMaster', subtitle: '趋势反转 EA · 识别潜在转折区域', tags: ['MT5', '趋势反转', '风险控制', '演示数据'], desc: 'ReversalMaster 用于研究潜在的趋势反转机会。当前业绩为模拟展示数据，实际使用前应验证反转确认条件、止损机制和仓位管理。', price: '$109.00', ret: '+22.70%', dd: '11.50%', win: '66.80%', pf: '1.63', platform: 'MetaTrader 5', platformTag: 'MT5', market: '外汇 / 贵金属', period: 'M5 / M15', update: '2026-10-21', type: '趋势反转', license: '单账户授权' },
  8: { id: 8, name: 'SmartMoney X', subtitle: '智能资金结构 EA · 结合 SMC 分析', tags: ['AI', 'SMC', 'FVG / CHoCH', '演示数据'], desc: 'SmartMoney X 面向智能资金概念设计，可围绕市场结构、流动性区域、FVG 和 CHoCH 等条件构建分析逻辑。当前业绩为模拟展示数据。', price: '$159.00', ret: '+42.80%', dd: '8.40%', win: '73.60%', pf: '2.08', platform: 'AI / 独立系统', platformTag: 'AI', market: '外汇 / 贵金属', period: 'M5 / M15', update: '2026-10-21', type: '智能资金 SMC', license: '单账户授权' },
  9: { id: 9, name: 'TitanTrend', subtitle: '大趋势跟踪 EA · 捕捉中长期趋势', tags: ['MT5', '大趋势', '趋势过滤', '演示数据'], desc: 'TitanTrend 面向中长期趋势行情设计，重点关注趋势方向、延续条件与动态风险控制。当前业绩为模拟展示数据，不代表真实交易结果。', price: '$139.00', ret: '+32.80%', dd: '8.60%', win: '72.40%', pf: '1.92', platform: 'MetaTrader 5', platformTag: 'MT5', market: '外汇 / 贵金属', period: 'M15 / H1 / H4', update: '2026-10-21', type: '大趋势跟踪', license: '单账户授权' },
  10: { id: 10, name: 'GoldSniper X', subtitle: '黄金短线 EA · 面向 XAUUSD 交易', tags: ['MT5', '黄金专用', '短线交易', '演示数据'], desc: 'GoldSniper X 面向黄金短线交易场景设计。当前业绩为模拟展示数据，实际使用前应结合经纪商点差、滑点、交易时段和止损规则进行测试。', price: '$129.00', ret: '+38.60%', dd: '7.90%', win: '76.20%', pf: '2.01', platform: 'MetaTrader 5', platformTag: 'MT5', market: 'XAUUSD 黄金', period: 'M1 / M5', update: '2026-10-21', type: '黄金短线', license: '单账户授权' },
  11: { id: 11, name: 'QuantumGrid', subtitle: '智能网格 EA · 自适应网格管理', tags: ['MT5', '智能网格', '仓位管理', '演示数据'], desc: 'QuantumGrid 面向网格交易场景设计，重点考虑网格间距、仓位上限与风险约束。当前业绩为模拟展示数据，网格策略仍需重点验证单边行情风险。', price: '$139.00', ret: '+57.20%', dd: '16.80%', win: '88.40%', pf: '1.57', platform: 'MetaTrader 5', platformTag: 'MT5', market: '外汇 / 贵金属', period: 'M5 / M15', update: '2026-10-21', type: '智能网格', license: '单账户授权' },
  12: { id: 12, name: 'ApexMartingale', subtitle: '马丁策略 EA · 强调仓位与风险管理', tags: ['MT4', '马丁策略', '风险管理', '演示数据'], desc: 'ApexMartingale 面向马丁类交易方案设计，重点考虑加仓规则、最大仓位和整体风险限制。当前业绩为模拟展示数据，连续亏损和持续单边行情可能导致较大资金回撤。', price: '$119.00', ret: '+64.30%', dd: '22.40%', win: '86.70%', pf: '1.38', platform: 'MetaTrader 4', platformTag: 'MT4', market: '以经纪商支持为准', period: 'M5 / M15', update: '2026-10-21', type: '马丁风险管理', license: '单账户授权' },
  13: { id: 13, name: 'LiquidityHunter', subtitle: '流动性分析 EA · 识别关键流动性区域', tags: ['MT5', '流动性分析', '价格结构', '演示数据'], desc: 'LiquidityHunter 关注前高前低、流动性聚集区域及潜在扫损行为。当前业绩为模拟展示数据，实际入场条件和风险参数需要通过历史行情验证。', price: '$139.00', ret: '+34.70%', dd: '9.70%', win: '70.80%', pf: '1.88', platform: 'MetaTrader 5', platformTag: 'MT5', market: '外汇 / 贵金属', period: 'M5 / M15', update: '2026-10-21', type: '流动性分析', license: '单账户授权' },
  14: { id: 14, name: 'BreakoutPulse', subtitle: '突破动量 EA · 追踪关键位突破后的动能', tags: ['MT5', '突破动量', '趋势确认', '演示数据'], desc: 'BreakoutPulse 关注价格突破关键区域后的动量变化，结合趋势确认与风险控制规则筛选交易机会。当前业绩为模拟展示数据。', price: '$119.00', ret: '+29.50%', dd: '8.90%', win: '68.90%', pf: '1.79', platform: 'MetaTrader 5', platformTag: 'MT5', market: '外汇 / 贵金属', period: 'M5 / M15', update: '2026-10-21', type: '突破动量', license: '单账户授权' },
  15: { id: 15, name: 'FVG Phantom', subtitle: '公允价值缺口 EA · FVG 结构分析', tags: ['MT5', 'FVG', '价格失衡', '演示数据'], desc: 'FVG Phantom 围绕公允价值缺口与价格失衡区域设计。当前业绩为模拟展示数据，实际交易需要明确缺口识别、入场触发、失效条件和止损止盈规则。', price: '$129.00', ret: '+41.60%', dd: '9.10%', win: '74.30%', pf: '2.04', platform: 'MetaTrader 5', platformTag: 'MT5', market: '外汇 / 贵金属', period: 'M5 / M15', update: '2026-10-21', type: 'FVG 缺口交易', license: '单账户授权' },
  16: { id: 16, name: 'OrderFlow AI', subtitle: '订单流分析 EA · 辅助判断市场压力', tags: ['AI', '订单流分析', '市场结构', '演示数据'], desc: 'OrderFlow AI 面向订单流与市场压力分析场景设计。当前业绩为模拟展示数据，实际使用前应确认数据来源、指标定义和交易执行条件。', price: '$159.00', ret: '+31.90%', dd: '7.60%', win: '71.80%', pf: '1.96', platform: 'AI / 独立系统', platformTag: 'AI', market: '以实际数据源为准', period: '以实际策略为准', update: '2026-10-21', type: '订单流分析', license: '单账户授权' }
})

export const eaPriceState = {
  loading: false,
  loaded: false,
  error: '',
  usdToCnyRate: 7,
  usdtNetwork: 'TRC20',
  usdtAddress: ''
}

export async function loadEaProductPrices() {
  if (eaPriceState.loading) return false

  eaPriceState.loading = true
  eaPriceState.error = ''

  try {
    const response = await fetch(`${API_BASE}/api/products`, {
      method: 'GET',
      headers: { Accept: 'application/json' }
    })

    if (!response.ok) {
      throw new Error(`价格接口请求失败：HTTP ${response.status}`)
    }

    const data = await response.json()

    if (data.success === false) {
      throw new Error(data.message || '后端价格接口返回失败')
    }

    const remoteProducts = Array.isArray(data.products)
      ? data.products
      : Array.isArray(data.data)
        ? data.data
        : null

    if (!remoteProducts) {
      throw new Error('价格接口未返回 products 数组，请检查 Worker 的 /api/products 响应格式')
    }

    let updatedCount = 0

    for (const remote of remoteProducts) {
      const id = Number(remote.id)
      const local = eaProducts[id]
      if (!local) continue

      const usd = Number(remote.price_usdt ?? remote.price)
      const cny = Number(remote.price_cny)
      const usdt = Number(remote.price_usdt ?? remote.price)

      if (!Number.isFinite(usd) || usd <= 0) continue

      local.priceUsd = usd
      local.priceUsdt = Number.isFinite(usdt) && usdt > 0 ? usdt : usd
      local.priceCny = Number.isFinite(cny) && cny > 0 ? cny : null
      local.price = `$${usd.toFixed(2)}`
      local.priceSynced = true

      updatedCount++
    }

    if (updatedCount === 0) {
      throw new Error('没有同步到有效商品价格，请检查 Worker 返回字段与商品 ID')
    }

    if (Number.isFinite(Number(data.usd_to_cny_rate)) && Number(data.usd_to_cny_rate) > 0) {
      eaPriceState.usdToCnyRate = Number(data.usd_to_cny_rate)
    }

    if (data.usdt_network) {
      eaPriceState.usdtNetwork = String(data.usdt_network)
    }

    if (data.usdt_address) {
      eaPriceState.usdtAddress = String(data.usdt_address)
    }

    eaPriceState.loaded = true
    eaPriceState.error = ''

    return true
  } catch (error) {
    eaPriceState.error = error instanceof Error ? error.message : '商品价格同步失败'

    for (const product of Object.values(eaProducts)) {
      product.priceSynced = false
    }

    console.error('[LOZENO] 商品价格同步失败：', eaPriceState.error)
    return false
  } finally {
    eaPriceState.loading = false
  }
}
