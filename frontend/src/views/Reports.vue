<template>
  <div class="space-y-6">
    <!-- Header -->
    <div>
      <h1 class="text-2xl font-bold" style="color: var(--color-text-heading)">项目报表</h1>
      <p class="mt-1 text-sm" style="color: var(--color-text-secondary)">项目进度追踪与阶段分析</p>
    </div>

    <!-- Summary Stats -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div class="card p-4 text-center">
        <div class="text-2xl font-bold" style="color: var(--color-text-heading)">{{ summary.total ?? '-' }}</div>
        <div class="text-xs mt-1" style="color: var(--color-text-secondary)">项目总数</div>
      </div>
      <div class="card p-4 text-center">
        <div class="text-2xl font-bold" style="color: var(--color-primary)">{{ summary.active ?? '-' }}</div>
        <div class="text-xs mt-1" style="color: var(--color-text-secondary)">进行中</div>
      </div>
      <div class="card p-4 text-center">
        <div class="text-2xl font-bold" style="color: var(--color-success)">{{ summary.won ?? '-' }}</div>
        <div class="text-xs mt-1" style="color: var(--color-text-secondary)">已签约</div>
      </div>
      <div class="card p-4 text-center">
        <div class="text-2xl font-bold" style="color: var(--color-danger)">{{ summary.lost ?? '-' }}</div>
        <div class="text-xs mt-1" style="color: var(--color-text-secondary)">丢单</div>
      </div>
    </div>

    <!-- Project Report Cards -->
    <div class="space-y-4">
      <div
        v-for="(project, idx) in reports"
        :key="project.id || idx"
        class="card card-hover p-5"
      >
        <!-- Project Header -->
        <div class="flex items-start justify-between mb-4">
          <div class="flex-1 min-w-0">
            <h3 class="font-semibold" style="color: var(--color-text-heading)">{{ project.name }}</h3>
            <div class="flex items-center gap-2 mt-1">
              <span class="text-xs" style="color: var(--color-text-muted)">{{ project.customer_name || '未知客户' }}</span>
              <span class="text-xs" style="color: var(--color-text-muted)">·</span>
              <span class="text-xs" style="color: var(--color-text-muted)">金额 ¥{{ formatAmount(project.amount) }}</span>
            </div>
          </div>
          <span class="tag shrink-0" :class="getStageTagClass(project.stage)">
            {{ getStageLabel(project.stage) }}
          </span>
        </div>

        <!-- Stage Timeline -->
        <div class="relative">
          <!-- Progress Line -->
          <div class="absolute top-3 left-0 right-0 h-1 rounded-full"
               style="background: var(--color-border)" />
          <div
            class="absolute top-3 left-0 h-1 rounded-full transition-all duration-500"
            :style="{
              width: getProgressWidth(project) + '%',
              backgroundColor: 'var(--color-primary)',
            }"
          />

          <!-- Stage Dots -->
          <div class="relative flex justify-between">
            <div
              v-for="stage in stageOptions"
              :key="stage.value"
              class="flex flex-col items-center gap-1.5"
              style="width: 64px"
            >
              <div
                class="w-6 h-6 rounded-full border-2 flex items-center justify-center transition-all duration-300 z-10"
                :class="getStageDotClass(project, stage.value)"
                :style="{
                  borderColor: isStageCompleted(project, stage.value)
                    ? 'var(--color-primary)'
                    : 'var(--color-border)',
                  backgroundColor: isStageCompleted(project, stage.value)
                    ? 'var(--color-primary)'
                    : 'var(--color-bg-surface)',
                }"
              >
                <svg
                  v-if="isStageCompleted(project, stage.value)"
                  class="w-3.5 h-3.5 text-white"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  stroke-width="3"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <span
                class="text-xs text-center leading-tight"
                :style="{
                  color: project.stage === stage.value
                    ? 'var(--color-text-heading)'
                    : 'var(--color-text-muted)',
                  fontWeight: project.stage === stage.value ? 600 : 400,
                }"
              >
                {{ stage.label }}
              </span>
            </div>
          </div>
        </div>

        <!-- Project Details -->
        <div v-if="project.project_progress" class="mt-4 pt-3 space-y-1.5"
             style="border-top: 1px solid var(--color-border)">
          <div class="text-xs" style="color: var(--color-text-muted)">进展</div>
          <div class="text-sm" style="color: var(--color-text-secondary)">{{ project.project_progress }}</div>
        </div>
        <div v-if="project.latest_follow_up" class="mt-2 pt-2 space-y-1.5"
             style="border-top: 1px solid var(--color-border)">
          <div class="text-xs" style="color: var(--color-text-muted)">最近跟进</div>
          <div class="text-sm" style="color: var(--color-text-secondary)">{{ project.latest_follow_up }}</div>
        </div>
        <div class="mt-1 flex items-center gap-4 text-xs" style="color: var(--color-text-muted)">
          <span>👤 {{ project.owner || '未分配' }}</span>
          <span>📝 {{ project.follow_ups_count || 0 }}次跟进</span>
        </div>
      </div>
    </div>

    <div v-if="!reports.length && !loading" class="card p-12 text-center text-sm" style="color: var(--color-text-muted)">
      暂无报表数据
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
// useMessage replaced with safe wrapper
import { getReports } from '../api'

interface ProjectReport {
  id: number
  name: string
  customer_name: string
  amount: number
  stage: string
  owner: string
  project_progress: string
  latest_follow_up: string
  follow_ups_count: number
  latest_follow_up_id: number | null
}

interface SummaryStats {
  total: number
  active: number
  won: number
  lost: number
}

const message = { error: (msg) => console.error('[CRM]', msg), success: (msg) => console.log('[CRM]', msg), warning: (msg) => console.warn('[CRM]', msg), info: (msg) => console.info('[CRM]', msg) }
const loading = ref(false)
const reports = ref<ProjectReport[]>([])
const summary = ref<SummaryStats>({ total: 0, active: 0, won: 0, lost: 0 })

const stageOptions = [
  { label: '线索', value: '线索' },
  { label: '需求确认', value: '需求确认' },
  { label: '方案报价', value: '方案报价' },
  { label: '商务谈判', value: '商务谈判' },
  { label: '已签约', value: '已签约' },
  { label: '丢单', value: '丢单' },
]

const stageOrder = stageOptions.map(s => s.value)

const stageTagClassMap: Record<string, string> = {
  线索: 'tag-blue',
  需求确认: 'tag-amber',
  方案报价: 'tag-blue',
  商务谈判: 'tag-purple',
  已签约: 'tag-green',
  丢单: 'tag-red',
}

const stageLabelMap: Record<string, string> = Object.fromEntries(
  stageOptions.map(s => [s.value, s.label])
)

const getStageTagClass = (stage: string) => stageTagClassMap[stage] || 'tag-gray'
const getStageLabel = (stage: string) => stageLabelMap[stage] || stage

const isStageCompleted = (project: ProjectReport, stage: string): boolean => {
  const currentIdx = stageOrder.indexOf(project.stage)
  const stageIdx = stageOrder.indexOf(stage)
  if (project.stage === '丢单') return true
  return stageIdx <= currentIdx
}

const getStageDotClass = (project: ProjectReport, stage: string): string => {
  if (project.stage === stage) return 'ring-2 ring-offset-1'
  return ''
}

const getProgressWidth = (project: ProjectReport): number => {
  const idx = stageOrder.indexOf(project.stage)
  if (idx < 0) return 0
  if (project.stage === '丢单') return 100
  return (idx / (stageOrder.length - 2)) * 100
}

const formatAmount = (val: number | undefined): string => {
  if (val == null) return '-'
  if (val >= 10000) return (val / 10000).toFixed(1) + '万'
  return val.toLocaleString()
}

const fetchReports = async () => {
  loading.value = true
  try {
    const res = await getReports({ report_type: 'daily' })
    const body = res.data || {}
    const list = body.active_projects || body.items || body || []
    reports.value = Array.isArray(list) ? list : []

    const stats = body.period_stats || {}
    const cumulative = body.cumulative || {}
    summary.value = {
      total: cumulative.total_projects || stats.new_projects || reports.value.length,
      active: stats.active_projects || reports.value.filter(r => r.stage !== '已签约' && r.stage !== '丢单').length,
      won: cumulative.signed_count || stats.new_signed || 0,
      lost: cumulative.lost_count || stats.new_lost || 0,
    }
  } catch {
    message.error('获取报表数据失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => fetchReports())
</script>