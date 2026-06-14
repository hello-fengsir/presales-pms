<template>
  <div class="space-y-6">
    <!-- Back button + Title -->
    <div class="flex items-center gap-4">
      <n-button text @click="$router.back()" style="color: var(--color-text-secondary)">
        <template #icon>
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
        </template>
        返回
      </n-button>
      <div class="flex-1">
        <h1 class="text-2xl font-bold" style="color: var(--color-text-heading)">{{ customer?.name || '客户详情' }}</h1>
      </div>
      <n-button type="primary" @click="openEditModal">
        <template #icon>
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
          </svg>
        </template>
        编辑客户
      </n-button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex justify-center py-20">
      <n-spin size="large" />
    </div>

    <template v-else-if="customer">
      <!-- Info Cards Row -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Basic Info -->
        <div class="card p-5">
          <h2 class="text-lg font-semibold mb-4" style="color: var(--color-text-heading)">基本信息</h2>
          <div class="space-y-4">
            <div class="flex">
              <span class="w-20 text-sm flex-shrink-0" style="color: var(--color-text-muted)">客户名称</span>
              <span class="text-sm font-medium" style="color: var(--color-text-primary)">{{ customer.name }}</span>
            </div>
            <div class="flex">
              <span class="w-20 text-sm flex-shrink-0" style="color: var(--color-text-muted)">所属行业</span>
              <span v-if="customer.industry" class="tag tag-blue">{{ customer.industry }}</span>
              <span v-else class="text-sm" style="color: var(--color-text-muted)">—</span>
            </div>
            <div class="flex">
              <span class="w-20 text-sm flex-shrink-0" style="color: var(--color-text-muted)">公司地址</span>
              <span class="text-sm" style="color: var(--color-text-primary)">
                {{ customer.address || '—' }}
              </span>
            </div>
            <div class="flex">
              <span class="w-20 text-sm flex-shrink-0" style="color: var(--color-text-muted)">备注</span>
              <span class="text-sm" style="color: var(--color-text-secondary)">
                {{ customer.notes || '—' }}
              </span>
            </div>
          </div>
        </div>

        <!-- Contact Info -->
        <div class="card p-5">
          <h2 class="text-lg font-semibold mb-4" style="color: var(--color-text-heading)">联系信息</h2>
          <div class="space-y-4">
            <div class="flex">
              <span class="w-20 text-sm flex-shrink-0" style="color: var(--color-text-muted)">联系人</span>
              <span class="text-sm font-medium" style="color: var(--color-text-primary)">
                {{ customer.contact_name || customer.contact || '—' }}
              </span>
            </div>
            <div class="flex">
              <span class="w-20 text-sm flex-shrink-0" style="color: var(--color-text-muted)">联系电话</span>
              <span class="text-sm" style="color: var(--color-text-primary)">
                {{ customer.phone || customer.contact_phone || '—' }}
              </span>
            </div>
            <div class="flex">
              <span class="w-20 text-sm flex-shrink-0" style="color: var(--color-text-muted)">电子邮箱</span>
              <span class="text-sm" style="color: var(--color-primary)">
                {{ customer.email || '—' }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Associated Projects -->
      <div class="card overflow-hidden">
        <div class="p-5 pb-0 flex items-center justify-between">
          <h2 class="text-lg font-semibold" style="color: var(--color-text-heading)">
            关联项目
            <span class="text-sm font-normal ml-2" style="color: var(--color-text-muted)">
              ({{ projects.length }})
            </span>
          </h2>
          <n-button size="small" type="primary" @click="goNewProject">
            <template #icon>
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
              </svg>
            </template>
            新建项目
          </n-button>
        </div>

        <div v-if="projects.length === 0" class="p-5 text-center" style="color: var(--color-text-muted)">
          <p class="text-sm">暂无关联项目</p>
        </div>

        <div v-else class="overflow-x-auto">
          <table class="w-full border-collapse">
            <thead>
              <tr style="background: var(--color-bg-hover)">
                <th class="text-left py-3 px-4 text-xs font-medium uppercase" style="color: var(--color-text-muted)">项目名称</th>
                <th class="text-left py-3 px-4 text-xs font-medium uppercase" style="color: var(--color-text-muted)">阶段</th>
                <th class="text-right py-3 px-4 text-xs font-medium uppercase" style="color: var(--color-text-muted)">金额</th>
                <th class="text-left py-3 px-4 text-xs font-medium uppercase" style="color: var(--color-text-muted)">负责人</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="proj in projects"
                :key="proj.id"
                class="border-b transition-colors cursor-pointer"
                style="border-color: var(--color-border)"
                :style="{ background: 'transparent' }"
                @mouseenter="(e: any) => e.currentTarget.style.background = 'var(--color-bg-hover)'"
                @mouseleave="(e: any) => e.currentTarget.style.background = 'transparent'"
                @click="goProject(proj.id)"
              >
                <td class="py-3 px-4">
                  <span class="text-sm font-medium" style="color: var(--color-text-heading)">{{ proj.name }}</span>
                </td>
                <td class="py-3 px-4">
                  <n-tag :bordered="false" size="small" :type="stageType(proj.stage)">
                    {{ stageLabel(proj.stage) }}
                  </n-tag>
                </td>
                <td class="py-3 px-4 text-right">
                  <span class="text-sm font-semibold" style="color: var(--color-danger)">
                    {{ formatAmount(proj.amount) }}
                  </span>
                </td>
                <td class="py-3 px-4">
                  <span class="text-sm" style="color: var(--color-text-secondary)">
                    {{ proj.assignee || '—' }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Follow-up Timeline (recent) -->
      <div class="card p-5">
        <h2 class="text-lg font-semibold mb-4" style="color: var(--color-text-heading)">近期跟进</h2>
        <div v-if="recentFollowUps.length === 0" class="text-center py-8" style="color: var(--color-text-muted)">
          <p class="text-sm">暂无跟进记录</p>
        </div>
        <div v-else class="space-y-4">
          <div
            v-for="(item, idx) in recentFollowUps"
            :key="item.id || idx"
            class="flex gap-3"
          >
            <div class="flex flex-col items-center">
              <div class="w-2.5 h-2.5 rounded-full mt-1.5" style="background: var(--color-primary)"></div>
              <div
                v-if="idx < recentFollowUps.length - 1"
                class="w-px flex-1 mt-1"
                style="background: var(--color-border)"
              ></div>
            </div>
            <div class="flex-1 pb-4">
              <div class="flex items-center gap-2 mb-1">
                <span class="text-sm font-medium" style="color: var(--color-text-heading)">
                  {{ item.author || item.user?.name || '系统' }}
                </span>
                <span
                  v-if="item.project_name"
                  class="text-xs px-1.5 py-0.5 rounded"
                  style="background: var(--color-primary-bg); color: var(--color-primary)"
                >{{ item.project_name }}</span>
                <span class="text-xs" style="color: var(--color-text-muted)">
                  {{ formatTime(item.created_at || item.createdAt) }}
                </span>
              </div>
              <p class="text-sm whitespace-pre-wrap" style="color: var(--color-text-secondary)">
                {{ item.content }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- Edit Modal -->
    <n-modal v-model:show="showEditModal" :mask-closable="false" preset="card" title="编辑客户" style="max-width: 560px" :style="{ width: '90%' }">
      <n-form ref="editFormRef" :model="editForm" :rules="formRules" label-placement="left" label-width="80">
        <n-form-item label="客户名称" path="name">
          <n-input v-model:value="editForm.name" placeholder="请输入客户名称" />
        </n-form-item>
        <n-form-item label="所属行业" path="industry">
          <n-input v-model:value="editForm.industry" placeholder="如：金融、教育、制造" />
        </n-form-item>
        <n-form-item label="联系人" path="contact_name">
          <n-input v-model:value="editForm.contact_name" placeholder="主要联系人姓名" />
        </n-form-item>
        <n-form-item label="联系电话" path="phone">
          <n-input v-model:value="editForm.phone" placeholder="联系电话" />
        </n-form-item>
        <n-form-item label="电子邮箱" path="email">
          <n-input v-model:value="editForm.email" placeholder="电子邮箱" />
        </n-form-item>
        <n-form-item label="公司地址" path="address">
          <n-input v-model:value="editForm.address" placeholder="公司地址" />
        </n-form-item>
        <n-form-item label="备注" path="notes">
          <n-input
            v-model:value="editForm.notes"
            type="textarea"
            placeholder="备注信息"
            :autosize="{ minRows: 2, maxRows: 4 }"
          />
        </n-form-item>
      </n-form>
      <template #footer>
        <div class="flex justify-end gap-3">
          <n-button @click="showEditModal = false">取消</n-button>
          <n-button type="error" @click="handleDelete" :loading="deleting">删除</n-button>
          <n-button type="primary" @click="handleEditSubmit" :loading="submitting">保存</n-button>
        </div>
      </template>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  NButton, NTag, NModal, NForm, NFormItem, NInput, NSpin, useMessage
} from 'naive-ui'
import {
  getCustomer, updateCustomer, deleteCustomer,
  getProjects, getFollowUps
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
  created_at?: string
}

interface Project {
  id: number
  name: string
  amount?: number
  stage: string
  assignee?: string
}

interface FollowUp {
  id?: number
  project_id?: number
  project_name?: string
  content: string
  author?: string
  user?: { name: string }
  created_at?: string
  createdAt?: string
}

const route = useRoute()
const router = useRouter()
const message = { error: (msg) => console.error('[CRM]', msg), success: (msg) => console.log('[CRM]', msg), warning: (msg) => console.warn('[CRM]', msg), info: (msg) => console.info('[CRM]', msg) }

const loading = ref(false)
const submitting = ref(false)
const deleting = ref(false)
const customer = ref<Customer | null>(null)
const projects = ref<Project[]>([])
const allFollowUps = ref<FollowUp[]>([])
const showEditModal = ref(false)

const editForm = ref({
  name: '',
  industry: '',
  contact_name: '',
  phone: '',
  email: '',
  address: '',
  notes: '',
})

const editFormRef = ref<any>(null)

const formRules = {
  name: [{ required: true, message: '请输入客户名称', trigger: 'blur' }],
}

const stageMap: Record<string, string> = {
  线索: '线索',
  需求确认: '需求确认',
  方案报价: '方案报价',
  商务谈判: '商务谈判',
  已签约: '已签约',
  丢单: '丢单',
}

const stageTypeMap: Record<string, 'default' | 'info' | 'success' | 'warning' | 'error'> = {
  线索: 'info',
  需求确认: 'warning',
  方案报价: 'info',
  商务谈判: 'warning',
  已签约: 'success',
  丢单: 'error',
}

const recentFollowUps = computed(() =>
  allFollowUps.value.slice(0, 10)
)

function formatAmount(amount?: number): string {
  if (!amount && amount !== 0) return '—'
  if (amount >= 10000) return `¥${(amount / 10000).toFixed(1)}万`
  return `¥${amount.toLocaleString()}`
}

function formatTime(t?: string): string {
  if (!t) return '—'
  try {
    return new Date(t).toLocaleString('zh-CN')
  } catch {
    return t
  }
}

function stageLabel(stage: string): string {
  return stageMap[stage] || stage
}

function stageType(stage: string): 'default' | 'info' | 'success' | 'warning' | 'error' {
  return stageTypeMap[stage] || 'default'
}

function goProject(id: number) {
  router.push(`/work/projects/${id}`)
}

function goNewProject() {
  router.push('/work/projects')
}

async function fetchCustomer() {
  loading.value = true
  try {
    const id = Number(route.params.id)
    const [custRes, projRes] = await Promise.all([
      getCustomer(id),
      getProjects({ customer_id: String(id) }),
    ])

    customer.value = custRes.data?.data ?? custRes.data
    projects.value = projRes.data?.data ?? projRes.data ?? []

    // Collect follow-ups from all associated projects
    if (projects.value.length > 0) {
      const followUpResults = await Promise.allSettled(
        projects.value.map(p => getFollowUps(p.id))
      )
      const allFUs: FollowUp[] = []
      followUpResults.forEach(result => {
        if (result.status === 'fulfilled') {
          const data = result.value.data?.data ?? result.value.data ?? []
          allFUs.push(...data)
        }
      })
      // Sort by time descending
      allFUs.sort((a, b) => {
        const ta = new Date(a.created_at || a.createdAt || 0).getTime()
        const tb = new Date(b.created_at || b.createdAt || 0).getTime()
        return tb - ta
      })
      allFollowUps.value = allFUs
    }
  } catch (err: any) {
    message.error('加载客户详情失败: ' + (err.message || '未知错误'))
    router.push('/work/customers')
  } finally {
    loading.value = false
  }
}

function openEditModal() {
  if (!customer.value) return
  editForm.value = {
    name: customer.value.name,
    industry: customer.value.industry || '',
    contact_name: customer.value.contact_name || customer.value.contact || '',
    phone: customer.value.phone || customer.value.contact_phone || '',
    email: customer.value.email || '',
    address: customer.value.address || '',
    notes: customer.value.notes || '',
  }
  showEditModal.value = true
}

async function handleEditSubmit() {
  try {
    await editFormRef.value?.validate()
  } catch {
    return
  }
  submitting.value = true
  try {
    const id = Number(route.params.id)
    await updateCustomer(id, editForm.value)
    message.success('客户信息已更新')
    showEditModal.value = false
    await fetchCustomer()
  } catch (err: any) {
    message.error('更新失败: ' + (err.response?.data?.message || err.message || '未知错误'))
  } finally {
    submitting.value = false
  }
}

async function handleDelete() {
  deleting.value = true
  try {
    const id = Number(route.params.id)
    await deleteCustomer(id)
    message.success('客户已删除')
    router.push('/work/customers')
  } catch (err: any) {
    message.error('删除失败: ' + (err.response?.data?.message || err.message || '未知错误'))
  } finally {
    deleting.value = false
  }
}

onMounted(() => {
  fetchCustomer()
})
</script>