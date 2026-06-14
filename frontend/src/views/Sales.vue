<template>
  <div class="space-y-6">
    <!-- Header -->
    <div>
      <h1 class="text-2xl font-bold" style="color: var(--color-text-heading)">销售管理</h1>
      <p class="mt-1 text-sm" style="color: var(--color-text-secondary)">销售漏斗概览与团队业绩追踪</p>
    </div>

    <!-- KPI Summary Cards -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div class="card p-5">
        <div class="text-sm font-medium" style="color: var(--color-text-secondary)">项目总数</div>
        <div class="mt-2 text-3xl font-bold" style="color: var(--color-text-heading)">
          {{ stats.total_projects ?? '-' }}
        </div>
        <div class="mt-1 text-xs" style="color: var(--color-text-muted)">
          较上月 {{ stats.projects_change ?? 0 > 0 ? '+' : '' }}{{ stats.projects_change ?? 0 }}%
        </div>
      </div>
      <div class="card p-5">
        <div class="text-sm font-medium" style="color: var(--color-text-secondary)">总金额</div>
        <div class="mt-2 text-3xl font-bold" style="color: var(--color-primary)">
          ¥{{ formatAmount(stats.total_amount) }}
        </div>
        <div class="mt-1 text-xs" style="color: var(--color-text-muted)">
          较上月 {{ stats.amount_change ?? 0 > 0 ? '+' : '' }}{{ stats.amount_change ?? 0 }}%
        </div>
      </div>
      <div class="card p-5">
        <div class="text-sm font-medium" style="color: var(--color-text-secondary)">赢单率</div>
        <div class="mt-2 text-3xl font-bold" style="color: var(--color-success)">
          {{ stats.win_rate ?? 0 }}%
        </div>
        <div class="mt-1 text-xs" style="color: var(--color-text-muted)">
          已签约 {{ stats.won_count ?? 0 }} / 总 {{ stats.total_projects ?? 0 }} 个项目
        </div>
      </div>
    </div>

    <!-- Monthly Revenue Line Chart -->
    <div class="card px-0 py-4">
      <h3 class="text-base font-semibold mb-1" style="color: var(--color-text-heading)">近1年每月成交金额（万元）</h3>
      <p class="text-xs mb-4" style="color: var(--color-text-muted)">已签约项目 · {{ monthlyRevenue.length }} 个月</p>
      <div v-if="monthlyRevenue.length" style="height:200px">
        <svg viewBox="0 0 600 200" preserveAspectRatio="xMidYMid meet" style="width:100%;height:200px">
          <!-- Grid lines — horizontal -->
          <line v-for="(_, i) in 5" :key="'gl'+i"
            :x1="PAD_L" :y1="PAD_T + (4-i) * plotH / 4" :x2="CHART_W - PAD_R" :y2="PAD_T + (4-i) * plotH / 4"
            stroke="var(--color-border)" stroke-width="0.5" stroke-dasharray="4,4" />
          <!-- Grid lines — vertical for each month -->
          <line v-for="(d, i) in monthlyRevenue" :key="'vg'+i"
            :x1="xPos(i)" :y1="PAD_T" :x2="xPos(i)" :y2="PAD_T + plotH"
            stroke="var(--color-border)" stroke-width="0.3" stroke-dasharray="2,4" />
          <!-- Y-axis labels -->
          <text v-for="(val, i) in yLabels" :key="'yl'+i"
            :x="PAD_L - 6" :y="PAD_T + (4-i) * plotH / 4 + 4" text-anchor="end"
            fill="var(--color-text-muted)" font-size="10">{{ val }}</text>
          <!-- X-axis labels — show every month clearly -->
          <text v-for="(d, i) in monthlyRevenue" :key="'xl'+i"
            :x="xPos(i)" :y="CHART_H - 4" text-anchor="middle"
            fill="var(--color-text-muted)" font-size="9"
            :transform="monthlyRevenue.length > 8 ? `rotate(-35, ${xPos(i)}, ${CHART_H - 4})` : ''">{{ d.month.slice(5) }}月</text>
          <!-- Area fill -->
          <polygon :points="areaPoints" fill="var(--color-primary)" opacity="0.1" />
          <!-- Line -->
          <polyline :points="linePoints" fill="none" stroke="var(--color-primary)" stroke-width="2" stroke-linejoin="round" stroke-linecap="round" />
          <!-- Dots -->
          <circle v-for="(d, i) in monthlyRevenue" :key="'dot'+i"
            :cx="xPos(i)" :cy="yPos(d.amount)" r="3.5"
            fill="var(--color-primary)" stroke="white" stroke-width="1.5">
            <title>{{ d.month }}: ¥{{ formatAmount(d.amount) }}</title>
          </circle>
        </svg>
      </div>
      <div v-else class="flex items-center justify-center text-sm" style="height:200px; color: var(--color-text-muted)">
        暂无数据
      </div>
    </div>

    <!-- Sales Rep List — grouped by department -->
    <div v-if="deptGroups.length" class="space-y-6">
      <div v-for="group in deptGroups" :key="group.dept">
        <!-- Department Header -->
        <div class="flex items-center gap-3 mb-3">
          <h3 class="text-base font-semibold" style="color: var(--color-text-heading)">{{ group.dept }}</h3>
          <span class="tag text-xs" style="background: var(--color-primary-light); color: var(--color-primary)">
            {{ group.reps.length }} 人 · ¥{{ formatAmount(group.totalAmount) }}
          </span>
        </div>

        <!-- Rep Cards -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div
            v-for="rep in group.reps"
            :key="rep.id"
            class="card card-hover p-5 cursor-pointer" @click="toggleRepProjects(rep)"
          >
            <!-- Rep Header -->
            <div class="flex items-start justify-between mb-4">
              <div class="flex items-center gap-3 flex-1 min-w-0">
                <div
                  class="w-10 h-10 rounded-full flex items-center justify-center text-white font-bold text-sm flex-shrink-0"
                  :style="{ backgroundColor: `var(--color-primary)` }"
                >
                  {{ rep.name?.charAt(0) }}
                </div>
                <div class="flex-1 min-w-0">
                  <h4 class="font-semibold text-sm truncate" style="color: var(--color-text-heading)">{{ rep.name }}</h4>
                  <p class="text-xs truncate" style="color: var(--color-text-muted)">{{ rep.title || rep.department || '销售部' }}</p>
                </div>
                <span class="tag tag-green text-xs">{{ rep.status === '离职' ? '离职' : (rep.rank || '初级') }}</span>
              </div>
              <div class="flex items-center gap-1 ml-2 flex-shrink-0">
                <n-button text size="tiny" @click.stop="openEdit(rep)" title="编辑">
                  <template #icon><n-icon size="16"><create-outline /></n-icon></template>
                </n-button>
                <n-popconfirm @positive-click="handleDelete(rep.id)" @click.stop>
                  <template #trigger>
                    <n-button text size="tiny" type="error" title="删除">
                      <template #icon><n-icon size="16"><trash-outline /></n-icon></template>
                    </n-button>
                  </template>
                  确定删除此销售代表？
                </n-popconfirm>
              </div>
            </div>

            <!-- Metrics -->
            <div class="grid grid-cols-2 gap-3 mb-4">
              <div>
                <div class="text-xs" style="color: var(--color-text-muted)">项目数</div>
                <div class="text-lg font-bold" style="color: var(--color-text-heading)">{{ rep.project_count ?? 0 }}</div>
              </div>
              <div>
                <div class="text-xs" style="color: var(--color-text-muted)">总金额</div>
                <div class="text-lg font-bold" style="color: var(--color-primary)">¥{{ formatAmount(rep.total_amount) }}</div>
              </div>
            </div>

            <!-- Win Rate Bar -->
            <div>
              <div class="flex justify-between text-xs mb-1">
                <span style="color: var(--color-text-secondary)">赢单率</span>
                <span class="font-semibold" style="color: var(--color-success)">{{ rep.win_rate ?? 0 }}%</span>
              </div>
              <div class="w-full h-2 rounded-full overflow-hidden" style="background: var(--color-bg-body)">
                <div
                  class="h-full rounded-full transition-all duration-500"
                  :style="{ width: (rep.win_rate ?? 0) + '%', backgroundColor: 'var(--color-success)' }"
                />
              </div>
            </div>

            <!-- Expanded Projects -->
            <div v-if="expandedRepId === rep.id" class="mt-4 pt-4" style="border-top: 1px solid var(--color-border)">
              <div v-if="repProjectsLoading" class="flex justify-center py-4">
                <n-spin size="small" />
              </div>
              <div v-else-if="repProjects[rep.id]?.length" class="space-y-2">
                <div
                  v-for="proj in repProjects[rep.id]"
                  :key="proj.id"
                  class="flex items-center justify-between p-2 rounded-lg text-sm hover:bg-surface-hover transition-colors"
                  style="background: var(--color-bg-hover)"
                  @click.stop="goProject(proj.id)"
                >
                  <div class="flex-1 min-w-0">
                    <span class="font-medium truncate block" style="color: var(--color-text-primary)">{{ proj.name }}</span>
                    <span class="text-xs" style="color: var(--color-text-muted)">{{ proj.customer_name || '' }}</span>
                  </div>
                  <div class="flex items-center gap-3 flex-shrink-0 ml-2">
                    <n-tag :bordered="false" size="tiny" :type="proj.stage === '已签约' ? 'success' : proj.stage === '丢单' ? 'error' : 'info'">
                      {{ proj.stage }}
                    </n-tag>
                    <span class="text-sm font-semibold" style="color: var(--color-primary)">¥{{ formatAmount(proj.amount) }}</span>
                  </div>
                </div>
              </div>
              <div v-else class="text-center py-3 text-xs" style="color: var(--color-text-muted)">
                暂无项目
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="!salesReps.length && !loading" class="card p-12 text-center text-sm" style="color: var(--color-text-muted)">
      暂无销售代表数据
    </div>

    <!-- Edit Modal -->
    <n-modal
      v-model:show="showEditModal"
      preset="card"
      title="编辑销售代表"
      style="max-width: 520px"
      :mask-closable="false"
    >
      <n-form
        ref="formRef"
        :model="editFormData"
        label-placement="top"
      >
        <n-form-item label="姓名" path="name">
          <n-input v-model:value="editFormData.name" placeholder="请输入姓名" />
        </n-form-item>
        <n-form-item label="电话" path="phone">
          <n-input v-model:value="editFormData.phone" placeholder="请输入电话" />
        </n-form-item>
        <n-form-item label="邮箱" path="email">
          <n-input v-model:value="editFormData.email" placeholder="请输入邮箱" />
        </n-form-item>
        <n-form-item label="部门" path="department">
          <n-input v-model:value="editFormData.department" placeholder="请输入部门" />
        </n-form-item>
        <n-form-item label="职位" path="title">
          <n-input v-model:value="editFormData.title" placeholder="请输入职位" />
        </n-form-item>
        <n-form-item label="状态" path="status">
          <n-select
            v-model:value="editFormData.status"
            :options="statusOptions"
            placeholder="请选择状态"
          />
        </n-form-item>
        <div class="flex justify-end gap-3 mt-2">
          <n-button @click="showEditModal = false">取消</n-button>
          <n-button type="primary" @click="handleSave" :loading="submitting">保存</n-button>
        </div>
      </n-form>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { CreateOutline, TrashOutline } from '@vicons/ionicons5'
import {
  NButton, NModal, NForm, NFormItem, NInput, NSelect,
  NIcon, NPopconfirm
} from 'naive-ui'
import type { FormInst } from 'naive-ui'
import { getSales, getMonthlyRevenue, updateSales, deleteSales, getProjects } from '../api'

interface SalesRep {
  id: number
  name: string
  phone: string
  email: string
  department: string
  title: string
  status: string
  rank: string
  project_count: number
  total_amount: number
  win_rate: number
}

interface DeptGroup {
  dept: string
  reps: SalesRep[]
  totalAmount: number
}

interface SalesStats {
  total_projects: number
  total_amount: number
  win_rate: number
  projects_change: number
  amount_change: number
  won_count: number
}

interface MonthlyPoint {
  month: string
  amount: number
}

const router = useRouter()
const loading = ref(false)
const stats = ref<SalesStats>({} as SalesStats)
const salesReps = ref<SalesRep[]>([])
const monthlyRevenue = ref<MonthlyPoint[]>([])
const expandedRepId = ref<number | null>(null)
const repProjects = ref<Record<number, any[]>>({})
const repProjectsLoading = ref(false)

// Chart dimensions
const CHART_W = 600
const CHART_H = 200  
const PAD_L = 44
const PAD_R = 16
const PAD_T = 12
const PAD_B = 18
const plotW = CHART_W - PAD_L - PAD_R
const plotH = CHART_H - PAD_T - PAD_B

const yLabels = computed(() => {
  const max = Math.max(...monthlyRevenue.value.map(d => d.amount), 1)
  // Nice round ceiling: 0→10, 10→50, 100→500, 1000→5000 etc
  const mag = Math.pow(10, Math.floor(Math.log10(max)))
  const niceTop = Math.ceil(max / mag) * mag
  const step = niceTop / 4
  return [0, 1, 2, 3, 4].map(i => {
    const v = Math.round(step * i)
    return v >= 10000 ? (v / 10000).toFixed(1) + '万' : v.toLocaleString()
  })
})

function xPos(i: number): number {
  const n = monthlyRevenue.value.length
  if (n <= 1) return PAD_L + plotW / 2
  return PAD_L + (i / (n - 1)) * plotW
}

function yPos(amount: number): number {
  const max = Math.max(...monthlyRevenue.value.map(d => d.amount), 1)
  const mag = Math.pow(10, Math.floor(Math.log10(max)))
  const niceTop = Math.ceil(max / mag) * mag
  return PAD_T + plotH - (amount / niceTop) * plotH
}

const linePoints = computed(() => {
  return monthlyRevenue.value.map((d, i) => `${xPos(i)},${yPos(d.amount)}`).join(' ')
})

const areaPoints = computed(() => {
  if (!monthlyRevenue.value.length) return ''
  const pts = monthlyRevenue.value.map((d, i) => `${xPos(i)},${yPos(d.amount)}`).join(' ')
  const lastX = xPos(monthlyRevenue.value.length - 1)
  const firstX = xPos(0)
  const baseY = PAD_T + plotH
  return `${firstX},${baseY} ${pts} ${lastX},${baseY}`
})

// Department grouping
const deptOrder = ['销售一部', '销售二部', '售前技术部']
const deptGroups = computed<DeptGroup[]>(() => {
  const map: Record<string, SalesRep[]> = {}
  for (const rep of salesReps.value) {
    const dept = rep.department || '其他'
    if (!map[dept]) map[dept] = []
    map[dept].push(rep)
  }
  const keys = Object.keys(map).sort((a, b) => {
    const ai = deptOrder.indexOf(a), bi = deptOrder.indexOf(b)
    if (ai !== -1 && bi !== -1) return ai - bi
    if (ai !== -1) return -1
    if (bi !== -1) return 1
    return a.localeCompare(b, 'zh-CN')
  })
  return keys.map(dept => ({
    dept,
    reps: map[dept],
    totalAmount: map[dept].reduce((s, r) => s + (r.total_amount || 0), 0),
  }))
})

// Edit state
const showEditModal = ref(false)
const editingId = ref<number | null>(null)
const submitting = ref(false)
const formRef = ref<FormInst | null>(null)
const editFormData = ref({
  name: '', phone: '', email: '', department: '', title: '', status: '在职',
})
const statusOptions = [
  { label: '在职', value: '在职' },
  { label: '离职', value: '离职' },
]

const formatAmount = (val: number | undefined): string => {
  if (val == null) return '-'
  if (val >= 10000) return (val / 10000).toFixed(1) + '万'
  return val.toLocaleString()
}

async function fetchMonthlyRevenue() {
  try {
    const res = await getMonthlyRevenue()
    monthlyRevenue.value = res.data ?? []
  } catch { /* ignore */ }
}

const fetchSales = async () => {
  loading.value = true
  try {
    const res = await getSales()
    const reps: any[] = res.data?.data ?? res.data ?? []

    const total_projects = reps.reduce((sum: number, r: any) => sum + (r.project_count || 0), 0)
    const total_amount = reps.reduce((sum: number, r: any) => sum + (r.total_amount || 0), 0)
    const active_count = reps.reduce((sum: number, r: any) => sum + (r.active_projects || 0), 0)

    stats.value = {
      total_projects, total_amount,
      win_rate: total_projects > 0 ? Math.round((active_count / total_projects) * 100) : 0,
      projects_change: 0, amount_change: 0, won_count: active_count,
    }

    salesReps.value = reps.map((r: any) => ({
      id: r.id, name: r.name, phone: r.phone || '', email: r.email || '',
      department: r.department || '其他', title: r.title || '',
      status: r.status || '在职', rank: r.title || r.department || '销售代表',
      project_count: r.project_count || 0, total_amount: r.total_amount || 0,
      win_rate: r.project_count > 0 ? Math.round((r.active_projects / r.project_count) * 100) : 0,
    }))
  } catch {
    console.error('获取销售数据失败')
  } finally {
    loading.value = false
  }
}

const openEdit = (rep: SalesRep) => {
  editingId.value = rep.id
  editFormData.value = {
    name: rep.name, phone: rep.phone || '', email: rep.email || '',
    department: rep.department || '', title: rep.title || '',
    status: rep.status || '在职',
  }
  showEditModal.value = true
}

const handleDelete = async (id: number) => {
  try { await deleteSales(id); await fetchSales() }
  catch { console.error('删除失败') }
}

const handleSave = async () => {
  if (!editingId.value) return
  submitting.value = true
  try {
    await updateSales(editingId.value, editFormData.value)
    showEditModal.value = false
    editingId.value = null
    await fetchSales()
  } catch { console.error('更新失败') }
  finally { submitting.value = false }
}

async function toggleRepProjects(rep: SalesRep) {
  if (expandedRepId.value === rep.id) { expandedRepId.value = null; return }
  expandedRepId.value = rep.id
  if (repProjects.value[rep.id]) return
  repProjectsLoading.value = true
  try {
    const res = await getProjects({ owner: rep.name })
    repProjects.value = { ...repProjects.value, [rep.id]: res.data?.data ?? res.data ?? [] }
  } catch (err) { console.error('Failed to load rep projects:', err) }
  finally { repProjectsLoading.value = false }
}

function goProject(id: number) { router.push('/work/projects/' + id) }

onMounted(() => { fetchSales(); fetchMonthlyRevenue() })
</script>

