<template>
  <div class="space-y-6">
    <!-- Top bar: Title + Date Filter -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <h1 class="text-xl font-bold" style="color: var(--color-text-heading)">数据看板</h1>
      <div class="flex flex-wrap items-center gap-2">
        <button
          v-for="preset in presets"
          :key="preset.value"
          class="px-3.5 py-1.5 text-sm rounded-lg border transition-colors font-medium"
          :class="selectedPreset === preset.value
            ? 'text-white'
            : 'hover:bg-surface-hover'"
          :style="selectedPreset === preset.value
            ? { background: 'var(--color-primary)', borderColor: 'var(--color-primary)' }
            : { background: 'var(--color-bg-surface)', borderColor: 'var(--color-border)', color: 'var(--color-text-secondary)' }"
          @click="selectedPreset = preset.value; fetchStats()"
        >
          {{ preset.label }}
        </button>
        <n-date-picker
          v-model:value="dateRange"
          type="daterange"
          clearable
          format="yyyy-MM-dd"
          class="w-56"
          :style="{ '--n-border': 'var(--color-border)' }"
        />
        <button
          class="px-4 py-1.5 text-sm font-medium rounded-lg transition-colors"
          style="background: var(--color-primary); color: var(--color-text-inverse)"
          @click="fetchStats"
        >
          查询
        </button>
        <button
          class="px-4 py-1.5 text-sm font-medium rounded-lg border transition-colors hover:bg-surface-hover"
          :style="{ background: 'var(--color-bg-surface)', borderColor: 'var(--color-border)', color: 'var(--color-text-secondary)' }"
          @click="clearFilter"
        >
          清除
        </button>
      </div>
    </div>

    <!-- KPI Cards Grid -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div
        v-for="stat in kpiCards"
        :key="stat.key"
        class="card card-hover p-5 flex items-start gap-4 cursor-pointer"
        @click="stat.onClick?.()"
      >
        <div
          class="w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0"
          :style="{ background: stat.bgColor }"
        >
          <component :is="stat.icon" class="w-5 h-5" :style="{ color: stat.iconColor }" />
        </div>
        <div class="min-w-0">
          <div class="text-2xl font-bold" :style="{ color: stat.valueColor || 'var(--color-primary)' }">{{ stat.value }}<span v-if="stat.suffix" class="text-base ml-0.5">{{ stat.suffix }}</span></div>
          <div class="text-sm mt-0.5 truncate" style="color: var(--color-text-muted)">{{ stat.label }}</div>
          <div v-if="stat.trend !== undefined" class="text-xs mt-1 flex items-center gap-0.5" :class="stat.trend >= 0 ? 'text-emerald-600' : 'text-red-500'">
            <TrendingUpOutline v-if="stat.trend >= 0" class="w-3 h-3" />
            <TrendingDownOutline v-else class="w-3 h-3" />
            {{ Math.abs(stat.trend) }}%
          </div>
        </div>
      </div>
    </div>

    <!-- Bottom 2-col: Sales Funnel Bar Chart + Recent Projects -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Sales Funnel Bar Chart -->
      <div class="card p-6">
        <h2 class="text-base font-semibold mb-5" style="color: var(--color-text-heading)">销售漏斗</h2>
        <div v-if="funnel.length" class="flex items-end justify-around gap-3" style="height: 200px; padding-top: 20px">
          <div v-for="(stage, idx) in funnel" :key="stage.name" class="flex flex-col items-center gap-2 flex-1 min-w-0 self-stretch justify-end">
            <span class="text-base font-bold" style="color: var(--color-primary); background: var(--color-primary-light); padding: 1px 8px; border-radius: 4px;">{{ stage.count }}</span>
            <div
              class="rounded-t-md transition-all duration-500"
              style="min-width: 44px; width: 100%"
              :style="{ height: stage.percent + '%', background: funnelColors[idx % funnelColors.length], border: '2px solid ' + funnelColors[idx % funnelColors.length], borderBottom: 'none', boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }"
            ></div>
            <span class="text-xs text-center leading-tight" style="color: var(--color-text-secondary)">{{ stage.name }}</span>
          </div>
        </div>
        <div v-else class="py-12 text-center text-sm" style="color: var(--color-text-muted)">暂无漏斗数据</div>
      </div>


      <!-- Recent Projects -->
      <div class="card p-6">
        <div class="flex items-center justify-between mb-5">
          <h2 class="text-base font-semibold" style="color: var(--color-text-heading)">近期项目</h2>
          <router-link
            to="/work/projects"
            class="text-sm font-medium hover:underline"
            style="color: var(--color-primary)"
          >
            查看全部
          </router-link>
        </div>
        <div v-if="recentProjects.length" class="space-y-3">
          <div
            v-for="project in recentProjects"
            :key="project.id"
            class="card card-hover p-4 flex items-center justify-between gap-3"
          >
            <div class="min-w-0">
              <div class="text-sm font-medium truncate" style="color: var(--color-text-primary)">
                {{ project.name }}
              </div>
              <div class="text-xs mt-1" style="color: var(--color-text-muted)">
                {{ project.customer || project.company || '-' }}
              </div>
            </div>
            <div class="flex items-center gap-3 flex-shrink-0">
              <span
                class="tag text-xs"
                :class="getStageTagClass(project.stage)"
              >
                {{ project.stage || project.stageName || '未知' }}
              </span>
              <span class="text-sm font-semibold whitespace-nowrap" style="color: var(--color-text-primary)">
                {{ formatAmount(project.amount) }}
              </span>
            </div>
          </div>
        </div>
        <div v-else class="py-12 text-center text-sm" style="color: var(--color-text-muted)">暂无项目数据</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { NDatePicker } from 'naive-ui'
import {
  StatsChartOutline,
  TrendingUpOutline,
  TrendingDownOutline,
  CheckmarkCircleOutline,
  CubeOutline,
  PeopleOutline,
  PersonAddOutline,
  LinkOutline,
  CashOutline,
} from '@vicons/ionicons5'
import { getDashboardStats, getChannels, getCustomers } from '../api'

// ── Filter state ──
const presets = [
  { label: '近1月', value: '1m' },
  { label: '近1季度', value: '1q' },
  { label: '近半年', value: '6m' },
  { label: '近1年', value: '1y' },
  { label: '全部', value: 'all' },
]
const selectedPreset = ref('1m')
const dateRange = ref<[number, number] | null>(null)

// ── Data state ──
const stats = reactive({
  totalProjects: 0,
  inProgressProjects: 0,
  signedProjects: 0,
  deliveredProjects: 0,
  totalCustomers: 0,
  monthlyNewCustomers: 0,
  totalChannels: 0,
  monthlyRevenue: 0,
})

const funnel = ref<Array<{ name: string; count: number; percent: number }>>([])
const recentProjects = ref<Array<{ id: number; name: string; stage: string; amount: number; customer?: string; company?: string; stageName?: string }>>([])
const loading = ref(false)

// ── Funnel colors using CSS variables ──
const funnelColors = [
  'var(--color-primary)',
  'var(--color-primary-hover)',
  'var(--color-success)',
  'var(--color-warning)',
  'var(--color-danger)',
  'var(--color-text-link)',
]

// ── KPI card definitions ──
const kpiCards = computed(() => [
  {
    key: 'totalProjects',
    label: '项目总数',
    value: stats.totalProjects,
    icon: CubeOutline,
    bgColor: 'var(--color-primary-light)',
    iconColor: 'var(--color-primary)',
    trend: undefined as number | undefined,
  },
  {
    key: 'inProgress',
    label: '进行中',
    value: stats.inProgressProjects,
    icon: StatsChartOutline,
    bgColor: 'var(--color-bg-tag)',
    iconColor: 'var(--color-primary)',
    trend: undefined as number | undefined,
  },
  {
    key: 'signed',
    label: '已签约',
    value: stats.signedProjects,
    icon: CheckmarkCircleOutline,
    bgColor: 'var(--color-primary-light)',
    iconColor: 'var(--color-success)',
    trend: undefined as number | undefined,
  },
  {
    key: 'delivered',
    label: '已交付',
    value: stats.deliveredProjects,
    icon: CubeOutline,
    bgColor: 'var(--color-bg-tag)',
    iconColor: 'var(--color-warning)',
    trend: undefined as number | undefined,
  },
  {
    key: 'totalCustomers',
    label: '客户总数',
    value: stats.totalCustomers,
    icon: PeopleOutline,
    bgColor: 'var(--color-primary-light)',
    iconColor: 'var(--color-primary-hover)',
    trend: undefined as number | undefined,
  },
  {
    key: 'monthlyNew',
    label: '本月新增客户',
    value: stats.monthlyNewCustomers,
    icon: PersonAddOutline,
    bgColor: 'var(--color-bg-tag)',
    iconColor: 'var(--color-primary)',
    trend: stats.totalCustomers ? Math.round((stats.monthlyNewCustomers / stats.totalCustomers) * 100) : undefined,
  },
  {
    key: 'totalChannels',
    label: '渠道总数',
    value: stats.totalChannels,
    icon: LinkOutline,
    bgColor: 'var(--color-primary-light)',
    iconColor: 'var(--color-success)',
    trend: undefined as number | undefined,
  },
  {
    key: 'monthlyRevenue',
    label: '本月销售额',
    value: formatAmount(stats.monthlyRevenue),
    suffix: ' 万元',
    valueColor: 'var(--color-success)',
    icon: CashOutline,
    bgColor: 'var(--color-bg-tag)',
    iconColor: 'var(--color-danger)',
    trend: undefined as number | undefined,
  },
])

// ── Helpers ──
function formatAmount(val: number | string | undefined | null): string {
  const n = Number(val)
  if (isNaN(n) || n === 0) return '--'
  if (n >= 10000) return (n / 10000).toFixed(1) + '万'
  return n.toLocaleString()
}

function getStageTagClass(stage: string | undefined): string {
  if (!stage) return 'tag-gray'
  const s = stage.toLowerCase()
  if (s.includes('线索') || s.includes('lead')) return 'tag-gray'
  if (s.includes('需求') || s.includes('requirement') || s.includes('分析')) return 'tag-blue'
  if (s.includes('方案') || s.includes('报价') || s.includes('proposal')) return 'tag-purple'
  if (s.includes('谈判') || s.includes('商务') || s.includes('negotiation')) return 'tag-amber'
  if (s.includes('签约') || s.includes('合同') || s.includes('contract') || s.includes('closed')) return 'tag-green'
  if (s.includes('交付') || s.includes('deliver')) return 'tag-green'
  return 'tag-blue'
}

function getPresetParams(): Record<string, string> {
  const params: Record<string, string> = {}
  if (selectedPreset.value !== 'all') {
    params.period = selectedPreset.value
  }
  if (dateRange.value && dateRange.value.length === 2) {
    params.startDate = String(dateRange.value[0])
    params.endDate = String(dateRange.value[1])
  }
  return params
}

function clearFilter() {
  selectedPreset.value = 'all'
  dateRange.value = null
  fetchStats()
}

async function fetchStats() {
  loading.value = true
  try {
    const params = getPresetParams()
    const res = await getDashboardStats(params)
    const data = res.data

    if (data) {
      // Fetch channel count separately (not in dashboard stats API)
      try {
        const chRes = await getChannels()
        stats.totalChannels = (chRes.data && Array.isArray(chRes.data)) ? chRes.data.length : (chRes.data?.total ?? 0)
      } catch { /* ignore */ }

      // Map API response to local stats (backend uses snake_case)
      stats.totalProjects = data.total_projects ?? 0
      stats.inProgressProjects = data.active_projects ?? 0
      stats.signedProjects = data.signed_this_month ?? 0
      stats.deliveredProjects = data.delivered_projects ?? 0
      stats.totalCustomers = data.total_customers ?? 0
      stats.monthlyNewCustomers = data.monthly_new_customers ?? 0
      // stats.totalChannels already set from getChannels() above
      stats.monthlyRevenue = data.forecast_this_month ?? data.signed_amount ?? 0

      // Funnel data
      if (data.funnel && Array.isArray(data.funnel)) {
        const maxCount = Math.max(...data.funnel.map((f: any) => f.count || 0), 1)
        funnel.value = data.funnel.map((f: any) => ({
          name: f.stage || f.name || '',
          count: f.count || 0,
          percent: maxCount > 0 ? Math.round(((f.count || 0) / maxCount) * 100) : 0,
        }))
      }

      // Recent projects (backend returns snake_case recent_projects)
      const projects = data.recent_projects || data.recentProjects
      if (projects && Array.isArray(projects)) {
        recentProjects.value = projects.slice(0, 6)
      }
    }
  } catch (err) {
    console.error('Failed to fetch dashboard stats:', err)
  } finally {
    loading.value = false
  }
}


// Auto-refresh when filter changes
watch([selectedPreset, dateRange], () => {
  fetchStats()
}, { deep: true })

onMounted(() => {
  fetchStats()
})
</script>