<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold" style="color: var(--color-text-heading)">客户管理</h1>
        <p class="text-sm mt-1" style="color: var(--color-text-muted)">管理所有客户信息及关联项目</p>
      </div>
      <div class="flex items-center gap-3">
        <n-input
          v-model:value="searchQuery"
          placeholder="搜索客户名称、行业..."
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
          v-model:value="filterIndustry"
          :options="industryOptions"
          placeholder="全部行业"
          clearable
          :style="{ width: '140px' }"
        />
        <n-button
          v-if="selectedIds.size > 0"
          type="warning"
          @click="handleAIEnrich"
          :loading="enriching"
          class="!rounded-lg"
        >
          <template #icon>
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </template>
          AI补全 ({{ selectedIds.size }})
        </n-button>
        <n-button type="primary" @click="openCreateModal" class="!rounded-lg">
          <template #icon>
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
          </template>
          新建客户
        </n-button>
      </div>
    </div>

    <!-- Stats bar -->
    <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
      <div class="card p-4">
        <p class="text-xs" style="color: var(--color-text-muted)">客户总数</p>
        <p class="text-2xl font-bold mt-1" style="color: var(--color-text-heading)">{{ customers.length }}</p>
      </div>
      <div class="card p-4">
        <p class="text-xs" style="color: var(--color-text-muted)">信息不全</p>
        <p class="text-2xl font-bold mt-1" style="color: var(--color-warning)">{{ incompleteCount }}</p>
      </div>
      <div class="card p-4">
        <p class="text-xs" style="color: var(--color-text-muted)">行业分布</p>
        <p class="text-2xl font-bold mt-1" style="color: var(--color-success)">{{ industryCount }}</p>
      </div>
      <div class="card p-4">
        <p class="text-xs" style="color: var(--color-text-muted)">本月新增</p>
        <p class="text-2xl font-bold mt-1" style="color: var(--color-text-heading)">{{ newThisMonth }}</p>
      </div>
    </div>

    <!-- Table -->
    <div class="card overflow-hidden">
      <div v-if="loading && customers.length === 0" class="flex justify-center py-20">
        <n-spin size="large" />
      </div>

      <div v-else-if="filteredCustomers.length === 0 && !loading" class="text-center py-20">
        <p class="text-sm" style="color: var(--color-text-muted)">
          {{ searchQuery || filterIndustry ? '没有匹配的客户' : '暂无客户数据，点击上方按钮创建' }}
        </p>
      </div>

      <div v-else class="overflow-x-auto">
        <table class="w-full border-collapse">
          <thead>
            <tr style="background: var(--color-bg-hover)">
              <th class="w-10 py-3 px-3">
                <n-checkbox
                  :checked="isAllSelected"
                  :indeterminate="isIndeterminate"
                  @update:checked="toggleAll"
                />
              </th>
              <th class="text-left py-3 px-4 text-xs font-medium uppercase" style="color: var(--color-text-muted)">客户名称</th>
              <th class="text-left py-3 px-4 text-xs font-medium uppercase" style="color: var(--color-text-muted)">行业</th>
              <th class="text-left py-3 px-4 text-xs font-medium uppercase" style="color: var(--color-text-muted)">联系人</th>
              <th class="text-left py-3 px-4 text-xs font-medium uppercase" style="color: var(--color-text-muted)">电话</th>
              <th class="text-center py-3 px-4 text-xs font-medium uppercase" style="color: var(--color-text-muted)">项目数</th>
              <th class="text-center py-3 px-4 text-xs font-medium uppercase" style="color: var(--color-text-muted)">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="customer in filteredCustomers"
              :key="customer.id"
              class="border-b transition-colors cursor-pointer"
              style="border-color: var(--color-border)"
              :style="{ background: selectedIds.has(customer.id) ? 'var(--color-primary)' + '0D' : 'transparent' }"
              @click="goDetail(customer.id)"
            >
              <td class="py-3 px-3" @click.stop>
                <n-checkbox
                  :checked="selectedIds.has(customer.id)"
                  @update:checked="(val: boolean) => toggleOne(customer.id, val)"
                />
              </td>
              <td class="py-3 px-4">
                <div class="flex items-center gap-2">
                  <span class="text-sm font-medium" style="color: var(--color-text-heading)">{{ customer.name }}</span>
                  <span
                    v-if="isIncomplete(customer)"
                    class="inline-flex items-center px-1.5 py-0.5 rounded text-xs font-medium"
                    style="background: #FEF3C7; color: #D97706; border: 1px solid #FCD34D"
                  >不全</span>
                </div>
              </td>
              <td class="py-3 px-4">
                <span v-if="customer.industry" class="tag tag-blue">{{ customer.industry }}</span>
                <span v-else class="text-sm" style="color: var(--color-text-muted)">—</span>
              </td>
              <td class="py-3 px-4">
                <span class="text-sm" style="color: var(--color-text-secondary)">
                  {{ customer.contact_name || customer.contact || '—' }}
                </span>
              </td>
              <td class="py-3 px-4">
                <span class="text-sm" style="color: var(--color-text-secondary)">
                  {{ customer.phone || customer.contact_phone || '—' }}
                </span>
              </td>
              <td class="py-3 px-4 text-center">
                <n-tag :bordered="false" size="small" :type="(customer.project_count || 0) > 0 ? 'info' : 'default'">
                  {{ customer.project_count || customer.projects?.length || 0 }}
                </n-tag>
              </td>
              <td class="py-3 px-4 text-center">
                <div class="flex items-center justify-center gap-1" @click.stop>
                  <n-button text size="small" @click="openEditModal(customer)" style="color: var(--color-primary)">
                    编辑
                  </n-button>
                  <n-popconfirm @positive-click="handleDelete(customer.id)">
                    <template #trigger>
                      <n-button text size="small" type="error">删除</n-button>
                    </template>
                    确认删除客户「{{ customer.name }}」？
                  </n-popconfirm>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Create / Edit Modal -->
    <n-modal v-model:show="showModal" :mask-closable="false" preset="card" :title="editingCustomer ? '编辑客户' : '新建客户'" style="max-width: 560px" :style="{ width: '90%' }">
      <n-form ref="formRef" :model="formData" :rules="formRules" label-placement="left" label-width="80">
        <n-form-item label="客户名称" path="name">
          <n-input v-model:value="formData.name" placeholder="请输入客户名称" />
        </n-form-item>
        <n-form-item label="所属行业" path="industry">
          <n-input v-model:value="formData.industry" placeholder="如：金融、教育、制造" />
        </n-form-item>
        <n-form-item label="联系人" path="contact_name">
          <n-input v-model:value="formData.contact_name" placeholder="主要联系人姓名" />
        </n-form-item>
        <n-form-item label="联系电话" path="phone">
          <n-input v-model:value="formData.phone" placeholder="联系电话" />
        </n-form-item>
        <n-form-item label="电子邮箱" path="email">
          <n-input v-model:value="formData.email" placeholder="电子邮箱" />
        </n-form-item>
        <n-form-item label="公司地址" path="address">
          <n-input v-model:value="formData.address" placeholder="公司地址" />
        </n-form-item>
        <n-form-item label="备注" path="notes">
          <n-input v-model:value="formData.notes" type="textarea" placeholder="备注信息" :autosize="{ minRows: 2, maxRows: 4 }" />
        </n-form-item>
      </n-form>

      <template #footer>
        <div class="flex justify-end gap-3">
          <n-button @click="showModal = false">取消</n-button>
          <n-button type="primary" @click="handleSubmit" :loading="submitting">
            {{ editingCustomer ? '保存' : '创建' }}
          </n-button>
        </div>
      </template>
    </n-modal>

    <!-- AI Enrichment Result Modal -->
    <n-modal v-model:show="showEnrichModal" preset="card" title="AI 企业信息补全结果" style="max-width: 800px" :style="{ width: '90%' }" :mask-closable="false">
      <div v-if="enrichError" class="mb-4 p-3 rounded-lg text-sm" style="background: #FEF2F2; color: #DC2626; border: 1px solid #FECACA">
        {{ enrichError }}
      </div>
      <div v-if="enrichResults.length > 0" class="overflow-x-auto">
        <table class="w-full border-collapse text-sm">
          <thead>
            <tr style="background: var(--color-bg-hover)">
              <th class="text-left py-2 px-3 text-xs font-medium uppercase" style="color: var(--color-text-muted)">客户</th>
              <th class="text-left py-2 px-3 text-xs font-medium uppercase" style="color: var(--color-text-muted)">行业</th>
              <th class="text-left py-2 px-3 text-xs font-medium uppercase" style="color: var(--color-text-muted)">规模</th>
              <th class="text-left py-2 px-3 text-xs font-medium uppercase" style="color: var(--color-text-muted)">区域</th>
              <th class="text-left py-2 px-3 text-xs font-medium uppercase" style="color: var(--color-text-muted)">简介</th>
              <th class="text-center py-2 px-3 text-xs font-medium uppercase" style="color: var(--color-text-muted)">可信度</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="item in enrichResults"
              :key="item.customer_id"
              class="border-b"
              style="border-color: var(--color-border)"
            >
              <td class="py-2 px-3 font-medium" style="color: var(--color-text-heading)">{{ item.name }}</td>
              <td class="py-2 px-3" style="color: var(--color-text-secondary)">
                <span v-if="item.industry" class="tag tag-blue">{{ item.industry }}</span>
                <span v-else style="color: var(--color-text-muted)">—</span>
              </td>
              <td class="py-2 px-3" style="color: var(--color-text-secondary)">{{ item.scale || '—' }}</td>
              <td class="py-2 px-3" style="color: var(--color-text-secondary)">{{ item.region || '—' }}</td>
              <td class="py-2 px-3 truncate" style="color: var(--color-text-secondary); max-width: 200px">
                {{ item.notes || '—' }}
              </td>
              <td class="py-2 px-3 text-center">
                <n-tag :bordered="false" size="small" :type="item.confidence === 'high' ? 'success' : 'warning'">
                  {{ item.confidence === 'high' ? '高' : '低' }}
                </n-tag>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-else-if="!enriching" class="text-center py-10">
        <p class="text-sm" style="color: var(--color-text-muted)">没有获取到补全结果</p>
      </div>
      <div v-if="enriching" class="flex justify-center py-10">
        <n-spin size="medium" />
        <span class="ml-3 text-sm" style="color: var(--color-text-muted)">AI 正在分析企业信息...</span>
      </div>
      <!-- Paste raw info for AI extraction -->
      <div class="mt-4 pt-4" style="border-top: 1px solid var(--color-border)">
        <p class="text-xs mb-2" style="color: var(--color-text-muted)">或粘贴已有客户信息，AI 自动提取整理：</p>
        <n-input
          v-model:value="rawCustomerText"
          type="textarea"
          placeholder="粘贴客户信息，如：腾讯科技，互联网行业，深圳南山，员工约10万人，主营社交、游戏、云计算..."
          :autosize="{ minRows: 2, maxRows: 5 }"
        />
        <div class="flex justify-end mt-3">
          <n-button
            size="small"
            type="info"
            @click="handleExtractFromText"
            :loading="extracting"
            :disabled="!rawCustomerText.trim()"
          >
            AI 提取录入
          </n-button>
        </div>
      </div>

      <template #footer>
        <div class="flex justify-end gap-3">
          <n-button @click="showEnrichModal = false">取消</n-button>
          <n-button type="primary" @click="handleSaveEnriched" :loading="saving">
            保存到数据库
          </n-button>
        </div>
      </template>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  NInput, NSelect, NButton, NTag, NModal, NForm, NFormItem,
  NPopconfirm, NSpin, NCheckbox, useMessage
} from 'naive-ui'
import {
  getCustomers, createCustomer, updateCustomer, deleteCustomer,
  enrichCustomers, enrichCustomersFromText,
} from '../api'

interface Customer {
  id: number
  name: string
  industry?: string
  contact_name?: string
  contact?: string
  phone?: string
  contact_phone?: string
  email?: string
  address?: string
  notes?: string
  project_count?: number
  projects?: any[]
  scale?: string
  region?: string
  source?: string
}

interface EnrichItem {
  customer_id: number
  name: string
  industry: string
  scale: string
  region: string
  notes: string
  confidence: string
  error?: string | null
}

const router = useRouter()
const message = {
  error: (msg: string) => console.error('[CRM]', msg),
  success: (msg: string) => console.log('[CRM]', msg),
  warning: (msg: string) => console.warn('[CRM]', msg),
  info: (msg: string) => console.info('[CRM]', msg),
}

const loading = ref(false)
const submitting = ref(false)
const customers = ref<Customer[]>([])
const searchQuery = ref('')
const filterIndustry = ref<string | null>(null)
const showModal = ref(false)
const editingCustomer = ref<Customer | null>(null)
const formRef = ref<any>(null)

// ── Multi-select + Enrichment ──
const selectedIds = ref<Set<number>>(new Set())
const enriching = ref(false)
const saving = ref(false)
const showEnrichModal = ref(false)
const enrichResults = ref<EnrichItem[]>([])
const enrichError = ref('')
const rawCustomerText = ref('')
const extracting = ref(false)

const formData = ref({
  name: '',
  industry: '',
  contact_name: '',
  phone: '',
  email: '',
  address: '',
  notes: '',
})

const formRules = {
  name: [{ required: true, message: '请输入客户名称', trigger: 'blur' }],
}

// ── Incomplete detection ──
function isIncomplete(c: Customer): boolean {
  const missingCount = [
    c.industry,
    c.scale,
    c.region,
    c.source,
    c.notes,
    c.contact_name || c.contact,
    c.phone || c.contact_phone,
  ].filter(v => !v || v === '').length
  return missingCount >= 3
}

const incompleteCount = computed(() =>
  customers.value.filter(c => isIncomplete(c)).length
)

// ── Selection ──
const isAllSelected = computed(() =>
  filteredCustomers.value.length > 0 &&
  filteredCustomers.value.every(c => selectedIds.value.has(c.id))
)

const isIndeterminate = computed(() =>
  !isAllSelected.value &&
  filteredCustomers.value.some(c => selectedIds.value.has(c.id))
)

function toggleAll(checked: boolean) {
  if (checked) {
    filteredCustomers.value.forEach(c => selectedIds.value.add(c.id))
  } else {
    filteredCustomers.value.forEach(c => selectedIds.value.delete(c.id))
  }
  // Trigger reactivity
  selectedIds.value = new Set(selectedIds.value)
}

function toggleOne(id: number, checked: boolean) {
  if (checked) {
    selectedIds.value.add(id)
  } else {
    selectedIds.value.delete(id)
  }
  selectedIds.value = new Set(selectedIds.value)
}

// ── AI Enrichment ──
async function handleAIEnrich() {
  if (selectedIds.value.size === 0) return

  enriching.value = true
  enrichError.value = ''
  enrichResults.value = []
  showEnrichModal.value = true

  try {
    const ids = Array.from(selectedIds.value)
    const res = await enrichCustomers(ids, false) // preview only, don't save yet
    const data = res.data?.data ?? res.data
    if (data?.results) {
      enrichResults.value = data.results
      if (data.results.length === 0) {
        enrichError.value = 'AI 未返回任何结果，请确认已配置 API Key'
      }
    }
  } catch (err: any) {
    enrichError.value = 'AI 补全失败: ' + (err.response?.data?.detail || err.response?.data?.message || err.message || '未知错误')
  } finally {
    enriching.value = false
  }
}

async function handleExtractFromText() {
  if (!rawCustomerText.value.trim() || selectedIds.value.size === 0) return
  extracting.value = true
  enrichError.value = ''
  try {
    const ids = Array.from(selectedIds.value)
    const res = await enrichCustomersFromText(ids, rawCustomerText.value)
    const data = res.data?.data ?? res.data
    if (data?.results && data.results.length > 0) {
      enrichResults.value = data.results
    } else {
      enrichError.value = 'AI 未能从文本中提取到有效信息'
    }
  } catch (err: any) {
    enrichError.value = '提取失败: ' + (err.response?.data?.detail || err.response?.data?.message || err.message || '未知错误')
  } finally {
    extracting.value = false
  }
}

async function handleSaveEnriched() {
  saving.value = true
  try {
    const ids = Array.from(selectedIds.value)
    await enrichCustomers(ids, true) // save=true this time
    showEnrichModal.value = false
    selectedIds.value = new Set()
    await fetchCustomers()
    message.success('企业信息已自动补全')
  } catch (err: any) {
    enrichError.value = '保存失败: ' + (err.response?.data?.detail || err.response?.data?.message || err.message || '未知错误')
  } finally {
    saving.value = false
  }
}

// ── Filters ──
const industryOptions = computed(() => {
  const industries = new Set<string>()
  customers.value.forEach(c => { if (c.industry) industries.add(c.industry) })
  return Array.from(industries).sort().map(i => ({ label: i, value: i }))
})

const filteredCustomers = computed(() => {
  let list = customers.value
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    list = list.filter(c =>
      c.name.toLowerCase().includes(q) ||
      (c.industry || '').toLowerCase().includes(q) ||
      (c.contact_name || c.contact || '').toLowerCase().includes(q)
    )
  }
  if (filterIndustry.value) {
    list = list.filter(c => c.industry === filterIndustry.value)
  }
  return list
})

const industryCount = computed(() =>
  new Set(customers.value.map(c => c.industry).filter(Boolean)).size
)

const newThisMonth = computed(() => {
  const now = new Date()
  const monthStart = new Date(now.getFullYear(), now.getMonth(), 1)
  return customers.value.filter(c => {
    if (!c.created_at && !(c as any).createdAt) return false
    const d = new Date(c.created_at || (c as any).createdAt)
    return d >= monthStart
  }).length
})

function goDetail(id: number) {
  router.push(`/work/customers/${id}`)
}

async function fetchCustomers() {
  loading.value = true
  try {
    const res = await getCustomers()
    customers.value = res.data?.data ?? res.data ?? []
  } catch (err: any) {
    message.error('加载客户列表失败: ' + (err.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

function openCreateModal() {
  editingCustomer.value = null
  formData.value = { name: '', industry: '', contact_name: '', phone: '', email: '', address: '', notes: '' }
  showModal.value = true
}

function openEditModal(customer: Customer) {
  editingCustomer.value = customer
  formData.value = {
    name: customer.name,
    industry: customer.industry || '',
    contact_name: customer.contact_name || customer.contact || '',
    phone: customer.phone || customer.contact_phone || '',
    email: customer.email || '',
    address: customer.address || '',
    notes: customer.notes || '',
  }
  showModal.value = true
}

async function handleSubmit() {
  try { await formRef.value?.validate() } catch { return }
  submitting.value = true
  try {
    if (editingCustomer.value) {
      await updateCustomer(editingCustomer.value.id, formData.value)
      message.success('客户信息已更新')
    } else {
      await createCustomer(formData.value)
      message.success('客户已创建')
    }
    showModal.value = false
    await fetchCustomers()
  } catch (err: any) {
    message.error('操作失败: ' + (err.response?.data?.message || err.message || '未知错误'))
  } finally {
    submitting.value = false
  }
}

async function handleDelete(id: number) {
  try {
    await deleteCustomer(id)
    message.success('客户已删除')
    await fetchCustomers()
  } catch (err: any) {
    message.error('删除失败: ' + (err.response?.data?.message || err.message || '未知错误'))
  }
}

onMounted(() => { fetchCustomers() })
</script>
