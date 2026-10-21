<template>
  <section class="rank-card">
    <table class="rank-table">
      <thead>
        <tr>
          <th>排名</th>
          <th>策略机器人名称</th>
          <th>历史总收益率</th>
          <th>智能高光胜率</th>
          <th>最大风控回撤</th>
          <th>安全运行时间</th>
          <th>状态</th>
        </tr>
      </thead>

      <tbody>
        <tr
          v-for="ea in rankings"
          :key="ea.id"
          class="rank-row"
          tabindex="0"
          role="link"
          :aria-label="`查看 ${ea.name} 详情`"
          @click="goToDetail(ea.id)"
          @keydown.enter="goToDetail(ea.id)"
          @keydown.space.prevent="goToDetail(ea.id)"
        >
          <td>
            <div
              v-if="ea.rank <= 3"
              class="trophy-tag"
              :class="`trophy-${ea.rank}`"
              :title="`第 ${ea.rank} 名`"
              :aria-label="`第 ${ea.rank} 名`"
            >
              <svg viewBox="0 0 48 48" aria-hidden="true">
                <defs>
                  <linearGradient
                    :id="`cup-metal-${ea.rank}`"
                    x1="0" y1="0" x2="1" y2="1"
                  >
                    <stop offset="0%" :stop-color="trophyColors[ea.rank].light" />
                    <stop offset="35%" :stop-color="trophyColors[ea.rank].main" />
                    <stop offset="65%" :stop-color="trophyColors[ea.rank].dark" />
                    <stop offset="100%" :stop-color="trophyColors[ea.rank].light" />
                  </linearGradient>

                  <linearGradient
                    :id="`cup-shine-${ea.rank}`"
                    x1="0" y1="0" x2="1" y2="0"
                  >
                    <stop offset="0%" stop-color="#ffffff" stop-opacity=".7" />
                    <stop offset="100%" stop-color="#ffffff" stop-opacity="0" />
                  </linearGradient>

                  <filter
                    :id="`cup-shadow-${ea.rank}`"
                    x="-30%" y="-30%" width="160%" height="170%"
                  >
                    <feDropShadow
                      dx="0" dy="2" stdDeviation="1.5"
                      flood-color="#000000" flood-opacity=".35"
                    />
                  </filter>
                </defs>

                <g :filter="`url(#cup-shadow-${ea.rank})`">
                  <path
                    d="M15 11H9.5A3.5 3.5 0 0 0 6 14.5v3A8.5 8.5 0 0 0 16 26"
                    fill="none"
                    :stroke="trophyColors[ea.rank].main"
                    stroke-width="3.5"
                    stroke-linecap="round"
                  />

                  <path
                    d="M33 11h5.5a3.5 3.5 0 0 1 3.5 3.5v3A8.5 8.5 0 0 1 32 26"
                    fill="none"
                    :stroke="trophyColors[ea.rank].dark"
                    stroke-width="3.5"
                    stroke-linecap="round"
                  />

                  <path
                    d="M13 7H35L33 20C32.2 27 28.8 31 24 31S15.8 27 15 20L13 7Z"
                    :fill="`url(#cup-metal-${ea.rank})`"
                    :stroke="trophyColors[ea.rank].light"
                    stroke-width=".8"
                    stroke-linejoin="round"
                  />

                  <path
                    d="M15.5 9H19L20.5 23L23 28C18 25 17 20 16.5 16Z"
                    :fill="`url(#cup-shine-${ea.rank})`"
                    opacity=".8"
                  />

                  <path
                    d="M12 6H36V9H12Z"
                    :fill="trophyColors[ea.rank].light"
                    stroke="rgba(255,255,255,.22)"
                    stroke-width=".6"
                  />

                  <path
                    d="M24 12L25.5 16.2L29.5 17.5L25.5 18.8L24 23L22.5 18.8L18.5 17.5L22.5 16.2Z"
                    fill="#ffffff"
                    fill-opacity=".9"
                  />

                  <path
                    d="M20 30H28V35H20Z"
                    :fill="trophyColors[ea.rank].dark"
                  />

                  <path
                    d="M17 35H31L34 39H14Z"
                    :fill="`url(#cup-metal-${ea.rank})`"
                  />

                  <path
                    d="M13 39H35V42H13Z"
                    :fill="trophyColors[ea.rank].main"
                  />

                  <path
                    d="M16 40H32"
                    stroke="#ffffff"
                    stroke-opacity=".45"
                    stroke-width=".8"
                  />
                </g>
              </svg>
            </div>

            <div v-else class="num-tag">
              {{ ea.rank }}
            </div>
          </td>

          <td>
            <div class="ea-info">
              <div class="ea-image">
                <img
                  :src="ea.image"
                  :alt="ea.name"
                  loading="lazy"
                  @error="handleImageError"
                />
              </div>

              <div class="ea-text">
                <div class="ea-name">{{ ea.name }}</div>
                <div class="ea-type">{{ ea.type }}</div>
              </div>
            </div>
          </td>

          <td>
            <span :class="ea.returnValue >= 0 ? 'txt-green' : 'txt-red'">
              {{ ea.returnRate }}
            </span>
          </td>

          <td>
            <span class="txt-bold">{{ ea.winRate }}</span>
          </td>

          <td>
            <span class="txt-bold">{{ ea.drawdown }}</span>
          </td>

          <td>{{ ea.days }}</td>

          <td>
            <span class="active-badge">运行中</span>
          </td>
        </tr>

        <tr v-if="rankings.length === 0">
          <td colspan="7" class="empty-state">
            暂无 EA 排名数据
          </td>
        </tr>
      </tbody>
    </table>

    <div class="ranking-note">
      排名依据 EA 数据中的收益率自动计算。当前业绩数据为演示数据，不代表真实实盘表现。
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { eaProducts } from '../data/eaProducts.js'

const router = useRouter()

const trophyColors = {
  1: {
    light: '#FFF0A6',
    main: '#E8B943',
    dark: '#9C6415'
  },
  2: {
    light: '#F4F7FC',
    main: '#AEBBCC',
    dark: '#586779'
  },
  3: {
    light: '#FFD0A0',
    main: '#C77A43',
    dark: '#773D25'
  }
}

const parsePercent = value => {
  const number = Number(
    String(value ?? '0').replace(/[%+\s,]/g, '')
  )

  return Number.isFinite(number) ? number : 0
}

const rankings = computed(() =>
  Object.values(eaProducts)
    .map(product => ({
      id: product.id,
      name: product.name,
      image: `/images/ea/${product.id}.png`,
      type: product.type || product.subtitle || 'EA 自动交易策略',
      returnValue: parsePercent(product.ret),
      returnRate: product.ret ?? '—',
      winRate: product.win ?? '—',
      drawdown: product.dd ?? '—',
      days: product.days != null ? `${product.days} 天` : '—'
    }))
    .sort((a, b) => b.returnValue - a.returnValue)
    .map((ea, index) => ({
      ...ea,
      rank: index + 1
    }))
)

function goToDetail(id) {
  router.push({
    path: '/product',
    query: { id: String(id) }
  })
}

function handleImageError(event) {
  event.target.style.visibility = 'hidden'
}
</script>

<style scoped>
.rank-card {
  min-width: 0;
  overflow-x: auto;
  background: #141722;
  border: 1px solid #222630;
  border-radius: 16px;
  padding: 16px;
}

.rank-table {
  width: 100%;
  min-width: 760px;
  border-collapse: collapse;
  text-align: left;
  font-size: 14px;
  line-height: 1.65;
}

.rank-table th {
  padding: 14px 16px;
  color: #848e9c;
  font-size: 11px;
  font-weight: 600;
  white-space: nowrap;
  border-bottom: 1px solid #222630;
}

.rank-table td {
  padding: 16px;
  white-space: nowrap;
  vertical-align: middle;
  border-bottom: 1px solid #222630;
}

.rank-table tbody tr:last-child td {
  border-bottom: 0;
}

.rank-row {
  cursor: pointer;
  transition: background 0.2s ease;
  outline: none;
}

.rank-row:hover {
  background: rgba(49, 91, 255, 0.06);
}

.rank-row:focus-visible {
  box-shadow: inset 0 0 0 1px #315bff;
}

/* 金属质感奖杯 */
.trophy-tag {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 38px;
  height: 38px;
  flex: 0 0 38px;
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 10px;
  background: linear-gradient(
    145deg,
    rgba(255, 255, 255, 0.055),
    rgba(255, 255, 255, 0.012)
  );
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.035),
    0 3px 8px rgba(0, 0, 0, 0.12);
}

.trophy-tag svg {
  display: block;
  width: 31px;
  height: 31px;
  overflow: visible;
}

.trophy-1 {
  border-color: rgba(232, 185, 67, 0.2);
  background: linear-gradient(
    145deg,
    rgba(232, 185, 67, 0.12),
    rgba(232, 185, 67, 0.025)
  );
}

.trophy-2 {
  border-color: rgba(174, 187, 204, 0.17);
  background: linear-gradient(
    145deg,
    rgba(174, 187, 204, 0.1),
    rgba(174, 187, 204, 0.02)
  );
}

.trophy-3 {
  border-color: rgba(199, 122, 67, 0.18);
  background: linear-gradient(
    145deg,
    rgba(199, 122, 67, 0.11),
    rgba(199, 122, 67, 0.02)
  );
}

/* 第四名开始使用数字 */
.num-tag {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 38px;
  height: 38px;
  color: #848e9c;
  font-size: 14px;
  font-weight: 800;
}

/* EA 实际产品图片 */
.ea-info {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 190px;
}

.ea-image {
  display: flex;
  flex: 0 0 42px;
  align-items: center;
  justify-content: center;
  width: 42px;
  height: 42px;
  overflow: hidden;
  background: #1b1e26;
  border: 1px solid #292e3b;
  border-radius: 9px;
}

.ea-image img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.ea-text {
  min-width: 0;
}

.ea-name {
  margin-bottom: 2px;
  color: #f0f2f6;
  font-weight: 750;
}

.ea-type {
  color: #848e9c;
  font-size: 11px;
}

.txt-green {
  color: #00c853;
  font-weight: 800;
}

.txt-red {
  color: #ff626e;
  font-weight: 800;
}

.txt-bold {
  font-weight: 700;
}

.active-badge {
  display: inline-block;
  padding: 4px 8px;
  color: #00c853;
  font-size: 12px;
  font-weight: 700;
  background: rgba(0, 200, 83, 0.1);
  border-radius: 6px;
}

.empty-state {
  padding: 36px 16px !important;
  color: #848e9c;
  text-align: center;
}

.ranking-note {
  padding: 14px 16px 2px;
  color: #848e9c;
  font-size: 11px;
  line-height: 1.6;
}
</style>