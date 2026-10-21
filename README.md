# LOZENO 网页开发结构

## 1. 项目定位

LOZENO 当前采用 **Vite + Vue 3** 进行网页开发。

项目从原来的多页面 HTML + CSS + JS 结构，逐步重构为：

- Vue 3 组件化开发
- Vite 项目构建
- Vue Router 页面路由
- 独立组件管理 UI
- 独立数据文件管理配置
- `public/data` 管理行情数据

重构原则：

> **保留现有视觉设计，只重构代码架构。**

---

## 2. 当前项目路径

```text
D:\0、聪明钱策略\16-LOZENO\lozeno-app
```

该目录是目前 LOZENO Vue 项目的主要开发目录。

旧项目仍然保留，用于参考，不作为当前主要开发项目。

---

## 3. 项目整体结构

```text
D:\0、聪明钱策略\16-LOZENO\lozeno-app
│
├─ index.html
├─ package.json
├─ vite.config.js
│
├─ public
│  └─ data
│     └─ dashboard.json
│
└─ src
   │
   ├─ main.js
   │
   ├─ data
   │  ├─ marketConfig.js
   │  └─ eaProducts.js
   │
   ├─ components
   │  ├─ Header.vue
   │  ├─ EaCard.vue
   │  │
   │  └─ market
   │     ├─ MarketSummary.vue
   │     ├─ MarketCharts.vue
   │     ├─ MarketSentiment.vue
   │     ├─ MarketSignals.vue
   │     ├─ MarketRiskMatrix.vue
   │     ├─ MarketOutlook.vue
   │     └─ MarketTechnicals.vue
   │
   ├─ views
   │  ├─ Home.vue
   │  ├─ Ranking.vue
   │  ├─ Market.vue
   │  └─ ProductDetail.vue
   │
   ├─ router
   │  └─ index.js
   │
   └─ styles
      └─ ...
```

---

# 4. 各目录职责

## 4.1 `src/main.js`

Vue 项目的程序入口。

主要负责：

```text
创建 Vue 应用
↓
加载 Router
↓
加载全局样式
↓
挂载到 index.html
```

---

## 4.2 `src/views`

页面级组件。

这里放完整页面，例如：

```text
Home.vue
Ranking.vue
Market.vue
ProductDetail.vue
```

### Home.vue

LOZENO 首页。

主要负责：

- 首页标题
- 首页 EA 产品展示
- EA 卡片列表
- 首页整体布局

---

### Ranking.vue

EA 排名页面。

主要负责：

- EA 排名
- 排名列表
- EA 产品数据展示
- 排名页面布局

---

### Market.vue

黄金投资行情页面。

主要负责：

- 页面标题
- 数据加载
- 加载状态
- 错误状态
- 调用行情组件
- 页面整体布局

行情页面内部主要由以下组件组成：

```text
MarketSummary
MarketCharts
MarketSentiment
MarketSignals
MarketRiskMatrix
MarketOutlook
MarketTechnicals
```

`Market.vue` 不应该承担这些组件内部的具体 UI 逻辑。

---

### ProductDetail.vue

EA 产品详情页面。

主要负责：

- EA 基础信息
- EA 策略介绍
- 策略表现
- 产品购买/激活等内容

---

# 5. `src/components`

组件级 UI。

组件应该尽量遵循：

> **一个组件负责一个明确功能。**

---

## 5.1 Header.vue

全站顶部导航。

负责：

- LOZENO Logo
- 搜索框
- 首页
- EA排名
- 插件
- 活动
- 登录
- 注册

Header 应作为全站统一组件使用。

这样可以避免：

```text
index 页面一套 Header
ranking 页面一套 Header
market 页面又一套 Header
```

造成样式不一致。

---

## 5.2 EaCard.vue

EA 产品卡片组件。

负责：

- EA 图片区域
- MT4 / MT5 / AI 平台标识
- EA 名称
- EA 类型
- 收益率
- 激活数
- 胜率
- 胜率进度条
- 收藏按钮
- 点击进入产品详情页

使用方式：

```vue
<EaCard
  v-for="item in eaList"
  :key="item.id"
  v-bind="item"
/>
```

---

# 6. `components/market`

行情页面专用组件。

```text
src/components/market/
```

---

## 6.1 MarketSummary.vue

行情顶部核心数据摘要。

目前包括：

```text
黄金价格
10Y 实际利率
美元指数
市场情绪
综合信号
20日波动率
金银比
GDX 金矿 ETF
```

注意：

`MarketSummary.vue` 负责这些卡片的显示逻辑。

数据来自：

```text
dashboard.json
```

---

## 6.2 MarketCharts.vue

宏观行情图表。

主要负责：

- 金价
- 均线
- 实际利率
- 美元指数
- 通胀预期
- 美联储资产
- VIX
- 金银比
- GDX
- 收益率曲线

以及：

```text
1M
3M
6M
1Y
3Y
```

时间范围切换。

---

## 6.3 MarketSentiment.vue

市场情绪模块。

负责展示：

- 市场情绪
- 情绪指标
- 情绪状态
- 相关情绪数据

---

## 6.4 MarketSignals.vue

利好 / 利空信号。

负责：

- 利好因素
- 利空因素
- 信号状态
- 相关说明

---

## 6.5 MarketRiskMatrix.vue

投资标的风险矩阵。

负责：

- 黄金
- 白银
- GDX 等相关标的
- 风险等级
- 风险因素

---

## 6.6 MarketOutlook.vue

走势预期。

分为：

```text
短期（1–4周）
中期（1–6个月）
长期（1年以上）
```

每个周期包含：

```text
方向
置信度
影响因素
支撑位
阻力位
总结
```

其中卡片使用：

```css
.summary{margin-top:auto}
```

使底部总结区域在不同高度内容下保持底部对齐。

---

## 6.7 MarketTechnicals.vue

技术面快照。

目前包含：

```text
当前价格
50日均线
200日均线
RSI（14）
20日波动率
支撑位
阻力位
MA交叉
利率-金价背离
收益率曲线
```

桌面端固定：

```text
每行 5 个
```

核心布局：

```css
grid-template-columns:repeat(5,minmax(0,1fr))
```

这样可以保证五个卡片平均分布。

---

# 7. `src/data`

数据与配置文件。

---

## 7.1 marketConfig.js

行情页面的统一配置。

目前包括：

### CHART_CONFIGS

定义图表类型：

```js
CHART_CONFIGS
```

例如：

```text
金价 + 均线
实际利率 vs 金价
美元指数 vs 金价
通胀预期
美联储资产 vs 金价
VIX 恐慌指数
金银比
GDX vs 金价
收益率曲线
```

---

### TIME_RANGES

定义图表时间范围：

```text
1M
3M
6M
1Y
3Y
```

---

### KEY_LABELS

统一管理行情字段名称。

例如：

```text
realYield → 10Y实际利率
gold → 黄金价格
goldMA50 → MA50
goldMA200 → MA200
dxy → 美元指数
vix → VIX
gdx → GDX金矿ETF
```

---

### fmt

统一数字格式化函数：

```js
fmt()
```

避免不同组件重复编写数字格式化逻辑。

---

## 7.2 eaProducts.js

EA 产品数据。

负责保存：

```text
EA ID
EA 名称
EA 类型
平台
收益率
激活数
胜率
产品介绍
策略信息
```

后续 EA 产品数量增加时，应优先在这里维护数据，而不是直接在页面 HTML 中大量写死。

---

# 8. `public/data`

行情数据目录：

```text
public/data/dashboard.json
```

行情页面通过：

```js
fetch('/data/dashboard.json')
```

读取。

数据流：

```text
行情数据生成程序
        ↓
dashboard.json
        ↓
Market.vue
        ↓
各 Market 组件
        ↓
网页显示
```

---

# 9. `src/router`

路由系统。

```text
src/router/index.js
```

负责页面地址与 Vue 页面之间的对应关系。

例如：

```text
/
↓
Home.vue

/ranking
↓
Ranking.vue

/market
↓
Market.vue

/product
↓
ProductDetail.vue
```

EA 卡片点击详情时，目前使用：

```js
router.push({
  path: '/product',
  query: { id: props.id }
})
```

因此可以通过 EA ID 区分不同产品。

---

# 10. `src/styles`

全局样式。

目前网站统一使用 CSS 变量管理视觉系统。

核心变量包括：

```css
--主页面背景色
--表面卡片背景色
--输入框背景色
--主色调蓝色
--主色调悬停色
--主色发光特效
--边框线条颜色
--主要文字颜色
--次要灰色文字
--涨势绿色
--跌势红色
--页面最大宽度
```

例如：

```css
:root{
  --主页面背景色:#0b0d12;
  --表面卡片背景色:#141722;
  --输入框背景色:#1b1e26;
  --主色调蓝色:#315bff;
  --边框线条颜色:#222630;
  --主要文字颜色:#fff;
  --次要灰色文字:#848e9c;
  --涨势绿色:#0ecb81;
  --跌势红色:#f6465d;
  --页面最大宽度:1320px;
}
```

---

# 11. 当前开发原则

## 11.1 页面与组件分离

页面：

```text
views/
```

负责页面结构。

组件：

```text
components/
```

负责具体 UI。

---

## 11.2 数据与 UI 分离

数据：

```text
data/
public/data/
```

UI：

```text
components/
views/
```

不要把大量数据直接写死在页面结构中。

---

## 11.3 全站统一视觉变量

颜色、字号、圆角、页面最大宽度等统一通过：

```css
:root
```

管理。

避免每个组件自行定义一套颜色。

---

## 11.4 一个组件一个主要职责

例如：

```text
MarketTechnicals.vue
```

只负责技术面。

不要把：

```text
技术面
走势预期
市场情绪
图表
```

全部塞进一个组件。

---

## 11.5 保持现有视觉效果

本次重构的目标不是重新设计 LOZENO。

核心目标：

```text
旧视觉设计
      ↓
保留
      ↓
重新组织代码
      ↓
Vue 组件化
```

---

# 12. 当前项目开发关系

整个网站可以理解成：

```text
                    LOZENO
                       │
                ┌──────┴──────┐
                │             │
             Vue 3          Vite
                │
        ┌───────┼────────┐
        │       │        │
      views  components  data
        │       │        │
        │       │        ├─ marketConfig.js
        │       │        └─ eaProducts.js
        │       │
        │       ├─ Header.vue
        │       ├─ EaCard.vue
        │       │
        │       └─ market/
        │           ├─ MarketSummary.vue
        │           ├─ MarketCharts.vue
        │           ├─ MarketSentiment.vue
        │           ├─ MarketSignals.vue
        │           ├─ MarketRiskMatrix.vue
        │           ├─ MarketOutlook.vue
        │           └─ MarketTechnicals.vue
        │
        ├─ Home.vue
        ├─ Ranking.vue
        ├─ Market.vue
        └─ ProductDetail.vue
                │
                ↓
          dashboard.json
```

---

# 13. 后续开发规范

以后新增功能时，优先按照下面的顺序判断：

### 新增一个页面

放：

```text
src/views/
```

### 页面中出现可以独立复用的 UI

放：

```text
src/components/
```

### 行情页面新增模块

放：

```text
src/components/market/
```

### 新增静态配置

放：

```text
src/data/
```

### 新增行情数据

放：

```text
public/data/
```

### 新增页面地址

修改：

```text
src/router/index.js
```

### 全站颜色、字号、圆角发生调整

优先修改：

```text
全局 :root CSS 变量
```

而不是逐个组件修改。

---

# 14. 当前架构目标

最终 LOZENO 应形成：

```text
页面
↓
组件
↓
数据
↓
统一配置
```

而不是：

```text
一个 HTML
├─ HTML
├─ CSS
├─ JS
├─ 数据
├─ 页面逻辑
└─ 大量重复代码
```

这样后续增加：

```text
EA 产品
EA 详情页
EA 发布中心
插件
活动
用户系统
EA 购买
EA 激活
跟单系统
行情系统
```

时，可以继续沿用现有组件化架构，而不需要重新搭建网站结构。