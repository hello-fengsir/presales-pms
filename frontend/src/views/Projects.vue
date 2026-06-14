<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold" style="color: var(--color-text-heading)">项目管理</h1>
        <p class="text-sm mt-1" style="color: var(--color-text-muted)">看板视图 · 拖拽管理项目阶段</p>
      </div>
      <div class="flex items-center gap-3">
        <n-input
          v-model:value="searchQuery"
          placeholder="搜索项目或客户..."
          clearable
          :style="{ width: '240px' }"
        >
          <template #prefix>
            <svg class="w-4 h-4" style="color: var(--color-text-muted)" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </template>
        </n-input>
        <n-select
          v-model:value="filterChannel"
          :options="channelOptions"
          placeholder="全部渠道"
          clearable
          :style="{ width: '140px' }"
        />
        <n-button type="primary" @click="openCreateModal" class="!rounded-lg">
          <template #icon>
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
          </template>
          新建项目
        </n-button>
        <n-button secondary @click="showImportModal = true" class="!rounded-lg">
          <template #icon>
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
            </svg>
          </template>
          快速导入
        </n-button>
      </div>
    </div>

    <!-- Quick Import Modal -->
    <n-modal v-model:show="showImportModal" preset="card" title="快速导入 · AI 解析会议纪要" style="max-width: 700px" :style="{ width: '95%' }" :mask-closable="false">
      <div class="space-y-4">
        <!-- Step 1: Textarea -->
        <div>
          <p class="text-sm font-medium mb-2" style="color: var(--color-text-heading)">📝 粘贴会议纪要</p>
          <n-input
            v-model:value="importNotes"
            type="textarea"
            placeholder="粘贴会议纪要内容，AI 将自动提取项目信息..."
            :autosize="{ minRows: 5, maxRows: 12 }"
          />
        </div>

        <div class="flex gap-3">
          <n-button type="primary" @click="handleParse" :loading="parsing" :disabled="!importNotes.trim()">
            ✨ 一键排版
          </n-button>
          <n-button @click="showImportModal = false; importNotes = ''; importResult = null; parsing = false; abortController?.value?.abort()">取消</n-button>
        </div>

        <!-- Step 2: Preview -->
        <div v-if="importResult" class="rounded-lg p-4 space-y-2" style="background: var(--color-bg-hover)">
          <p class="text-sm font-semibold" style="color: var(--color-text-heading)">📋 解析结果预览</p>
          <div class="grid grid-cols-2 gap-2 text-sm">
            <div><span style="color: var(--color-text-muted)">项目名称：</span><span class="font-medium">{{ importResult.project_name }}</span></div>
            <div>
              <span style="color: var(--color-text-muted)">客户：</span><span class="font-medium">{{ importResult.customer_name }}</span>
              <!-- Customer match status -->
              <span v-if="importResult.customer_matches?.exact" class="ml-2 px-1.5 py-0.5 text-xs rounded" style="background: var(--color-success); color: #fff">✅ 已匹配</span>
              <span v-else-if="importResult.customer_matches?.similar?.length" class="ml-2 px-1.5 py-0.5 text-xs rounded" style="background: var(--color-warning); color: #fff">⚠️ 相似</span>
              <span v-else class="ml-2 px-1.5 py-0.5 text-xs rounded" style="background: var(--color-primary); color: #fff">🆕 新建</span>
            </div>
            <div><span style="color: var(--color-text-muted)">预估金额：</span><span class="font-medium" style="color: var(--color-danger)">{{ importResult.amount ? '¥'+importResult.amount+'万' : '—' }}</span></div>
            <div><span style="color: var(--color-text-muted)">阶段：</span><span class="font-medium">{{ importResult.stage }}</span></div>
            <div><span style="color: var(--color-text-muted)">销售模式：</span><span class="font-medium">{{ importResult.sales_mode }}</span></div>
            <!-- Channel match -->
            <div v-if="importResult.channel_matches?.exact || importResult.channel_matches?.similar?.length || importResult.channel_name">
              <span style="color: var(--color-text-muted)">渠道：</span>
              <span v-if="importResult.channel_matches?.exact" class="ml-1 px-1.5 py-0.5 text-xs rounded" style="background: var(--color-success); color: #fff">✅ {{ importResult.channel_matches.exact.name }}</span>
              <span v-else-if="importResult.channel_matches?.similar?.length" class="ml-1 px-1.5 py-0.5 text-xs rounded" style="background: var(--color-warning); color: #fff">⚠️ 相似渠道</span>
              <span v-else class="ml-1 px-1.5 py-0.5 text-xs rounded" style="background: var(--color-primary); color: #fff">🆕 新建</span>
            </div>
          </div>
          
          <!-- Similar customer matches -->
          <div v-if="importResult.customer_matches?.similar?.length && !importResult.customer_matches?.exact" class="rounded p-3 text-sm" style="background: var(--color-bg-surface); border: 1px solid var(--color-warning)">
            <p class="font-medium mb-1" style="color: var(--color-warning)">⚠️ 发现相似客户，请确认：</p>
            <div class="flex flex-wrap gap-2">
              <button
                v-for="c in importResult.customer_matches.similar"
                :key="c.id"
                class="px-3 py-1 text-xs rounded-lg border transition-colors"
                :style="selectedCustomerId === c.id
                  ? { background: 'var(--color-primary)', color: '#fff', borderColor: 'var(--color-primary)' }
                  : { background: 'var(--color-bg-hover)', borderColor: 'var(--color-border)', color: 'var(--color-text-primary)' }"
                @click="selectedCustomerId = c.id; createNewCustomer = false"
              >
                {{ c.name }}
              </button>
              <button
                class="px-3 py-1 text-xs rounded-lg border transition-colors"
                :style="createNewCustomer
                  ? { background: 'var(--color-primary)', color: '#fff', borderColor: 'var(--color-primary)' }
                  : { background: 'var(--color-bg-hover)', borderColor: 'var(--color-border)', color: 'var(--color-text-primary)' }"
                @click="selectedCustomerId = null; createNewCustomer = true"
              >
                🆕 新建 "{{ importResult.customer_name }}"
              </button>
            </div>
          </div>
          
          <!-- Similar channel matches -->
          <div v-if="importResult.channel_matches?.similar?.length && !importResult.channel_matches?.exact" class="rounded p-3 text-sm" style="background: var(--color-bg-surface); border: 1px solid var(--color-warning)">
            <p class="font-medium mb-1" style="color: var(--color-warning)">⚠️ 发现相似渠道，请确认：</p>
            <div class="flex flex-wrap gap-2">
              <button
                v-for="ch in importResult.channel_matches.similar"
                :key="ch.id"
                class="px-3 py-1 text-xs rounded-lg border transition-colors"
                :style="selectedChannelId === ch.id
                  ? { background: 'var(--color-primary)', color: '#fff', borderColor: 'var(--color-primary)' }
                  : { background: 'var(--color-bg-hover)', borderColor: 'var(--color-border)', color: 'var(--color-text-primary)' }"
                @click="selectedChannelId = ch.id; createNewChannel = false"
              >
                {{ ch.name }}
              </button>
              <button
                class="px-3 py-1 text-xs rounded-lg border transition-colors"
                :style="createNewChannel
                  ? { background: 'var(--color-primary)', color: '#fff', borderColor: 'var(--color-primary)' }
                  : { background: 'var(--color-bg-hover)', borderColor: 'var(--color-border)', color: 'var(--color-text-primary)' }"
                @click="selectedChannelId = null; createNewChannel = true"
              >
                🆕 新建渠道
              </button>
            </div>
          </div>
          
          <div v-if="importResult.customer_requirement" class="text-sm">
            <span style="color: var(--color-text-muted)">需求：</span>
            <span style="color: var(--color-text-secondary)">{{ importResult.customer_requirement }}</span>
          </div>
          <div v-if="importResult.competitor_info" class="text-sm">
            <span style="color: var(--color-text-muted)">竞品：</span>
            <span style="color: var(--color-warning)">{{ importResult.competitor_info }}</span>
          </div>
          <div class="pt-2">
            <n-button type="success" @click="handleImportProject" :loading="importing" :disabled="!importResult.project_name">
              📥 项目导入
            </n-button>
          </div>
        </div>
      </div>
    </n-modal>

    <!-- Kanban Columns -->
    <div class="flex gap-4 overflow-x-auto pb-2" style="min-height: calc(100vh - 280px)">
      <div
        v-for="stage in stages"
        :key="stage.key"
        class="flex-1 min-w-[240px] rounded-lg p-3"
        style="background: var(--color-bg-hover)"
      >
        <!-- Column Header -->
        <div class="flex items-center justify-between mb-3 px-1">
          <div class="flex items-center gap-2">
            <span class="w-2 h-2 rounded-full" :style="{ background: stage.color }"></span>
            <span class="text-sm font-semibold" style="color: var(--color-text-heading)">{{ stage.label }}</span>
          </div>
          <n-tag :bordered="false" size="small" :style="{ background: stage.color + '20', color: stage.color }">
            {{ getStageCount(stage.key) }}
          </n-tag>
        </div>

        <!-- Cards -->
        <div class="space-y-3">
          <div
            v-for="project in getStageProjects(stage.key)"
            :key="project.id"
            class="card card-hover p-4 cursor-pointer"
            @click="goDetail(project.id)"
          >
            <!-- Row 1: Project name + sales mode badge -->
            <div class="flex items-start justify-between mb-2">
              <h3 class="font-semibold text-sm leading-tight truncate mr-2" style="color: var(--color-text-heading)">
                {{ project.name }}
              </h3>
              <span
                class="shrink-0 text-xs px-1.5 py-0.5 rounded-full font-medium"
                :style="project.sales_mode === '直客'
                  ? { background: '#2563EB15', color: '#2563EB', border: '1px solid #2563EB30' }
                  : { background: '#F59E0B15', color: '#D97706', border: '1px solid #F59E0B30' }"
              >{{ project.sales_mode === '直客' ? '直客' : '渠道' }}</span>
            </div>

            <!-- Row 2: Customer info -->
            <p class="text-sm truncate mb-1" style="color: var(--color-text-secondary)">
              👤 {{ project.customer_name || project.customer?.name || '未关联客户' }}
            </p>

            <!-- Row 3: Channel name (only for channel projects) -->
            <p
              v-if="project.sales_mode === '渠道' && (project.channel_name || project.channel?.name)"
              class="text-xs truncate mb-1"
              style="color: var(--color-warning)"
            >📋 {{ project.channel_name || project.channel?.name }}</p>

            <!-- Row 4: Tags -->
            <div class="flex flex-wrap gap-1.5 mb-2">
              <span
                v-for="tag in (project.tech_tags || project.tags || [])"
                :key="tag"
                class="tag tag-blue"
              >{{ tag }}</span>
            </div>

            <!-- Row 5: Amount + assignee -->
            <div class="flex items-center justify-between">
              <span class="text-sm font-semibold" style="color: var(--color-danger)">
                {{ formatAmount(project.amount) }}
              </span>
              <div v-if="project.owner || project.assignee" class="flex items-center gap-1">
                <div class="w-5 h-5 rounded-full flex items-center justify-center text-xs font-medium text-white" style="background: var(--color-primary)">
                  {{ ((project.owner || project.assignee || '?')[0]) }}
                </div>
                <span class="text-xs" style="color: var(--color-text-muted)">{{ project.owner || project.assignee }}</span>
              </div>
            </div>
          </div>

          <!-- Empty state -->
          <div
            v-if="getStageProjects(stage.key).length === 0"
            class="text-center py-8 rounded-lg"
            style="color: var(--color-text-muted); border: 1px dashed var(--color-border)"
          >
            <p class="text-sm">暂无项目</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Archived / Closed section -->
    <div v-if="closedProjects.length > 0" class="rounded-lg p-4" style="background: var(--color-bg-hover)">
      <h3 class="text-sm font-semibold mb-3" style="color: var(--color-text-secondary)">
        已归档 <span class="text-xs font-normal" style="color: var(--color-text-muted)">({{ closedProjects.length }})</span>
      </h3>
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
        <div
          v-for="project in closedProjects"
          :key="project.id"
          class="card card-hover p-3 cursor-pointer"
          @click="goDetail(project.id)"
        >
          <div class="flex items-center justify-between mb-1">
            <h4 class="font-semibold text-sm truncate" style="color: var(--color-text-heading)">{{ project.name }}</h4>
            <n-tag :bordered="false" size="tiny" :type="project.stage === '已签约' ? 'success' : 'error'">
              {{ project.stage === '已签约' ? '已签约' : '丢单' }}
            </n-tag>
          </div>
          <p class="text-xs truncate" style="color: var(--color-text-muted)">
            {{ project.customer_name || project.customer?.name || '未关联客户' }}
          </p>
        </div>
      </div>
    </div>

    <!-- Loading overlay -->
    <div v-if="loading && projects.length === 0" class="flex justify-center py-20">
      <n-spin size="large" />
    </div>

    <!-- Create / Edit Modal -->
    <n-modal v-model:show="showModal" :mask-closable="false" preset="card" :title="editingProject ? '编辑项目' : '新建项目'" style="max-width: 600px" :style="{ width: '90%' }">
      <n-form ref="formRef" :model="formData" :rules="formRules" label-placement="left" label-width="80">
        <n-form-item label="项目名称" path="name">
          <n-input v-model:value="formData.name" placeholder="请输入项目名称" />
        </n-form-item>
        <n-form-item label="关联客户" path="customer_id">
          <n-select
            v-model:value="formData.customer_id"
            :options="customerSelectOptions"
            placeholder="选择客户"
            filterable
            clearable
          />
        </n-form-item>
        <n-form-item label="项目金额" path="amount">
          <n-input-number v-model:value="formData.amount" placeholder="请输入金额" :min="0" :style="{ width: '100%' }" />
        </n-form-item>
        <n-form-item label="项目阶段" path="stage">
          <n-select v-model:value="formData.stage" :options="stageOptions" placeholder="选择阶段" />
        </n-form-item>
        <n-form-item label="渠道类型" path="channel_type">
          <n-input v-model:value="formData.channel_type" placeholder="如：直销、渠道、线上" />
        </n-form-item>
        <n-form-item label="负责人" path="assignee">
          <n-input v-model:value="formData.assignee" placeholder="负责人姓名" />
        </n-form-item>
        <n-form-item label="技术标签" path="tech_tags">
          <n-dynamic-tags v-model:value="formData.tech_tags" />
        </n-form-item>
      </n-form>
      <template #footer>
        <div class="flex justify-end gap-3">
          <n-button @click="showModal = false">取消</n-button>
          <n-button type="primary" @click="handleSubmit" :loading="submitting">
            {{ editingProject ? '保存' : '创建' }}
          </n-button>
        </div>
      </template>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import {
  NInput, NSelect, NButton, NTag, NModal, NForm, NFormItem,
  NInputNumber, NDynamicTags, NSpin, useMessage
} from 'naive-ui'
import {
  getProjects, createProject, updateProject,
  getCustomers, parseNotes
} from '../api'

interface Project {
  id: number
  name: string
  customer_id?: number
  customer_name?: string
  customer?: { name: string }
  amount?: number
  stage: string
  sales_mode?: string
  channel_id?: number | null
  channel_name?: string
  channel_type?: string
  channel_contact?: string
  channel_phone?: string
  channel?: { name: string }
  owner?: string
  assignee?: string
  tech_tags?: string[]
  tags?: string[]
}

interface Customer {
  id: number
  name: string
}

const router = useRouter()
const message = { error: (msg) => console.error("[CRM]", msg), success: (msg) => console.log("[CRM]", msg), warning: (msg) => console.warn("[CRM]", msg), info: (msg) => console.info("[CRM]", msg) }

const loading = ref(false)
const submitting = ref(false)
const projects = ref<Project[]>([])

// Quick import
const showImportModal = ref(false)
const importNotes = ref('')
const parsing = ref(false)
const importing = ref(false)
const importResult = ref<any>(null)
const abortController = ref<AbortController | null>(null)
// Smart matching state
const selectedCustomerId = ref<number | null>(null)
const selectedChannelId = ref<number | null>(null)
const createNewCustomer = ref(true)
const createNewChannel = ref(true)
const customers = ref<Customer[]>([])
const searchQuery = ref('')
const filterChannel = ref<string | null>(null)
const showModal = ref(false)
const editingProject = ref<Project | null>(null)
const formRef = ref<any>(null)

const formData = ref({
  name: '',
  customer_id: null as number | null,
  amount: null as number | null,
  stage: 'lead',
  channel_type: '',
  assignee: '',
  tech_tags: [] as string[],
})

const formRules = {
  name: [{ required: true, message: '请输入项目名称', trigger: 'blur' }],
  stage: [{ required: true, message: '请选择阶段', trigger: 'change' }],
}

const stages = [
  { key: '线索', label: '线索', color: '#6366F1' },
  { key: '需求确认', label: '需求确认', color: '#F59E0B' },
  { key: '方案报价', label: '方案报价', color: '#2563EB' },
  { key: '商务谈判', label: '商务谈判', color: '#10B981' },
]

const stageOptions = [
  { label: '线索', value: '线索' },
  { label: '需求确认', value: '需求确认' },
  { label: '方案报价', value: '方案报价' },
  { label: '商务谈判', value: '商务谈判' },
  { label: '已签约', value: '已签约' },
  { label: '丢单', value: '丢单' },
]

const channelOptions = computed(() => {
  const channels = new Set<string>()
  projects.value.forEach(p => {
    const ch = p.channel_type || p.channel?.name
    if (ch) channels.add(ch)
  })
  return Array.from(channels).map(c => ({ label: c, value: c }))
})

const customerSelectOptions = computed(() =>
  customers.value.map(c => ({ label: c.name, value: c.id }))
)

const filteredProjects = computed(() => {
  let list = projects.value
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    list = list.filter(p =>
      p.name.toLowerCase().includes(q) ||
      (p.customer_name || p.customer?.name || '').toLowerCase().includes(q)
    )
  }
  if (filterChannel.value) {
    list = list.filter(p =>
      (p.channel_type || p.channel?.name) === filterChannel.value
    )
  }
  return list
})

const activeProjects = computed(() =>
  filteredProjects.value.filter(p => !['已签约', '丢单'].includes(p.stage))
)

const closedProjects = computed(() =>
  filteredProjects.value.filter(p => ['已签约', '丢单'].includes(p.stage))
)

function getStageProjects(stage: string) {
  return activeProjects.value.filter(p => p.stage === stage)
}

function getStageCount(stage: string) {
  return getStageProjects(stage).length
}

function formatAmount(amount?: number): string {
  if (!amount && amount !== 0) return '—'
  if (amount >= 10000) return `¥${(amount / 10000).toFixed(1)}万`
  return `¥${amount.toLocaleString()}`
}

function goDetail(id: number) {
  router.push(`/work/projects/${id}`)
}

async function fetchProjects() {
  loading.value = true
  try {
    const res = await getProjects()

    projects.value = res.data?.data ?? res.data ?? []
  } catch (err: any) {
    message.error('加载项目列表失败: ' + (err.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

async function fetchCustomers() {
  try {
    const res = await getCustomers()
    customers.value = res.data?.data ?? res.data ?? []
  } catch (err) {
    // silently fail
  }
}

async function handleParse() {
  if (!importNotes.value.trim()) return
  // Abort any in-flight request
  abortController.value?.abort()
  abortController.value = new AbortController()
  parsing.value = true
  importResult.value = null
  try {
    const res = await parseNotes(importNotes.value, abortController.value.signal)
    importResult.value = res.data?.data ?? res.data ?? res
  } catch (err: any) {
    if (err?.name === 'CanceledError' || err?.code === 'ERR_CANCELED') return
    message.error('AI解析失败: ' + (err.response?.data?.detail || err.message))
  } finally {
    parsing.value = false
    abortController.value = null
  }
}

async function handleImportProject() {
  if (!importResult.value?.project_name) return
  importing.value = true
  const d = importResult.value
  
  // Determine customer handling
  let customerId = null
  let customerName = ''
  let autoCreateCust = false
  if (d.customer_matches?.exact) {
    customerId = d.customer_matches.exact.id
  } else if (selectedCustomerId.value) {
    customerId = selectedCustomerId.value
  } else if (createNewCustomer.value) {
    customerName = d.customer_name || ''
    autoCreateCust = true
  }
  
  // Determine channel handling
  let channelId = null
  let channelName = ''
  let autoCreateChan = false
  if (d.channel_matches?.exact) {
    channelId = d.channel_matches.exact.id
  } else if (selectedChannelId.value) {
    channelId = selectedChannelId.value
  } else if (createNewChannel.value && d.channel_matches?.exact === undefined && (d.channel_matches?.similar?.length || d.channel_name)) {
    channelName = (d.channel_matches?.similar?.[0]?.name) || d.channel_name || ''
    autoCreateChan = !!channelName
  }
  
  try {
    await createProject({
      name: d.project_name,
      customer_id: customerId,
      customer_name: customerName,
      auto_create_customer: autoCreateCust,
      amount: d.amount || 0,
      stage: d.stage || '线索',
      sales_mode: d.sales_mode || '直客',
      channel_id: channelId,
      channel_name: channelName,
      auto_create_channel: autoCreateChan,
    })
    message.success('项目导入成功: ' + d.project_name)
    showImportModal.value = false
    importNotes.value = ''
    importResult.value = null
    await fetchProjects()
  } catch (err: any) {
    message.error('导入失败: ' + (err.response?.data?.detail || err.message))
  } finally {
    importing.value = false
  }
}

function openCreateModal() {
  editingProject.value = null
  formData.value = {
    name: '',
    customer_id: null,
    amount: null,
    stage: 'lead',
    channel_type: '',
    assignee: '',
    tech_tags: [],
  }
  showModal.value = true
}

async function handleSubmit() {
  try {
    await formRef.value?.validate()
  } catch {
    return
  }
  submitting.value = true
  try {
    const payload = {
      ...formData.value,
      amount: formData.value.amount ?? undefined,
    }
    if (editingProject.value) {
      await updateProject(editingProject.value.id, payload)
      message.success('项目已更新')
    } else {
      await createProject(payload)
      message.success('项目已创建')
    }
    showModal.value = false
    await fetchProjects()
  } catch (err: any) {
    message.error('操作失败: ' + (err.response?.data?.message || err.message || '未知错误'))
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  fetchProjects()
  fetchCustomers()
})

onBeforeUnmount(() => {
  abortController.value?.abort()
})
</script>
