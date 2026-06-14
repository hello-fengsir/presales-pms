<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold" style="color: var(--color-text-heading)">渠道管理</h1>
        <p class="mt-1 text-sm" style="color: var(--color-text-secondary)">管理所有销售渠道与合作伙伴</p>
      </div>
      <n-button type="primary" @click="showCreateModal = true">
        <template #icon><n-icon><add-outline /></n-icon></template>
        新建渠道
      </n-button>
    </div>

    <!-- Table Card -->
    <div class="card overflow-hidden">
      <n-data-table
        :columns="columns"
        :data="channels"
        :loading="loading"
        :pagination="{ pageSize: 10 }"
        :row-class-name="() => 'hover:bg-slate-50/50'"
        striped
      />
    </div>

    <!-- Create Modal -->
    <n-modal
      v-model:show="showCreateModal"
      preset="card"
      :title="editing ? '编辑渠道' : '新建渠道'"
      style="max-width: 520px"
      :mask-closable="false"
    >
      <n-form
        ref="formRef"
        :model="formData"
        :rules="rules"
        label-placement="top"
        @submit.prevent="handleCreate"
      >
        <n-form-item label="渠道名称" path="name">
          <n-input v-model:value="formData.name" placeholder="请输入渠道名称" />
        </n-form-item>
        <n-form-item label="渠道类型" path="type">
          <n-select
            v-model:value="formData.type"
            :options="typeOptions"
            placeholder="请选择渠道类型"
          />
        </n-form-item>
        <n-form-item label="联系人" path="contact_name">
          <n-input v-model:value="formData.contact_name" placeholder="请输入联系人姓名" />
        </n-form-item>
        <n-form-item label="联系电话">
          <n-input v-model:value="formData.contact_phone" placeholder="请输入联系电话" />
        </n-form-item>
        <n-form-item label="佣金比例(%)">
          <n-input-number v-model:value="formData.commission_rate" :min="0" :max="100" style="width:100%" />
        </n-form-item>
        <n-form-item label="结算周期">
          <n-input v-model:value="formData.settlement_cycle" placeholder="如：月结、季度结" />
        </n-form-item>
        <n-form-item label="备注">
          <n-input v-model:value="formData.notes" type="textarea" placeholder="备注信息" :autosize="{ minRows: 2 }" />
        </n-form-item>
        <div class="flex justify-end gap-3 mt-2">
          <n-button @click="showCreateModal = false">取消</n-button>
          <n-button type="primary" attr-type="submit" :loading="submitting">{{ editing ? '保存修改' : '确认创建' }}</n-button>
        </div>
      </n-form>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, h } from 'vue'
// useMessage replaced with safe wrapper
import { AddOutline, CreateOutline, TrashOutline } from '@vicons/ionicons5'
import {
  NButton, NModal, NForm, NFormItem, NInput, NInputNumber, NSelect,
  NTag, NIcon, NPopconfirm
} from 'naive-ui'
import { getChannels, createChannel, updateChannel, deleteChannel } from '../api'
import type { DataTableColumns, FormInst, FormRules } from 'naive-ui'

interface Channel {
  id: number
  name: string
  type: string
  contact: string
  phone: string
  project_count: number
  won_amount: number
  won_count: number
  active_count: number
  lost_count: number
}

const message = { error: (msg) => console.error('[CRM]', msg), success: (msg) => console.log('[CRM]', msg), warning: (msg) => console.warn('[CRM]', msg), info: (msg) => console.info('[CRM]', msg) }
const loading = ref(false)
const showCreateModal = ref(false)
const submitting = ref(false)
const editing = ref(false)
const editingId = ref<number | null>(null)
const formRef = ref<FormInst | null>(null)
const channels = ref<Channel[]>([])

const formData = ref({ name: '', type: '', contact_name: '', contact_phone: '', commission_rate: 0, settlement_cycle: '', notes: '' })
const rules: FormRules = {
  name: [{ required: true, message: '请输入渠道名称', trigger: 'blur' }],
  type: [{ required: true, message: '请选择渠道类型', trigger: 'change' }],
}

const typeOptions = [
  { label: '直营渠道', value: '直营渠道' },
  { label: '代理商', value: '代理商' },
  { label: '合作伙伴', value: '合作伙伴' },
  { label: '线上渠道', value: '线上渠道' },
  { label: '其他', value: '其他' },
]

const columns: DataTableColumns<Channel> = [
  {
    title: '渠道名称',
    key: 'name',
    width: 200,
    render(row) {
      return h('span', { style: { fontWeight: 600, color: 'var(--color-text-heading)' } }, row.name)
    },
  },
  {
    title: '类型',
    key: 'type',
    width: 120,
    render(row) {
      return h('span', { class: 'tag tag-blue' }, row.type)
    },
  },
  { title: '联系人', key: 'contact', width: 100 },
  { title: '电话', key: 'phone', width: 130 },
  { title: '关联项目', key: 'project_count', width: 90, align: 'center' as const, sorter: true },
  { title: '已成交金额', key: 'won_amount', width: 110, align: 'right' as const, sorter: true,
    render(row) { return row.won_amount ? '¥'+row.won_amount.toFixed(1)+'万' : '—' } },
  { title: '成交数', key: 'won_count', width: 80, align: 'center' as const, sorter: true },
  { title: '有效商机', key: 'active_count', width: 90, align: 'center' as const, sorter: true },
  { title: '无效商机', key: 'lost_count', width: 90, align: 'center' as const, sorter: true },
  {
    title: '操作',
    key: 'actions',
    width: 120,
    align: 'center' as const,
    render(row) {
      return h('div', { class: 'flex items-center justify-center gap-2' }, [
        h(
          'button',
          { class: 'text-blue-600 hover:text-blue-700 text-sm font-medium transition-colors', onClick: () => openEdit(row) },
          '编辑'
        ),
        h(
          NPopconfirm,
          { onPositiveClick: () => handleDelete(row.id) },
          {
            default: () => '确定删除此渠道？',
            trigger: () => h(
              'button',
              { class: 'text-red-500 hover:text-red-600 text-sm font-medium transition-colors' },
              '删除'
            )
          }
        ),
      ])
    },
  },
]

const fetchChannels = async () => {
  loading.value = true
  try {
    const { data } = await getChannels()
    const list = data.data || data || []
    channels.value = (Array.isArray(list) ? list : []).map((c: any) => ({
      ...c,
      contact: c.contact_name || c.contact || '',
      phone: c.contact_phone || c.phone || '',
    }))
  } catch {
    message.error('获取渠道列表失败')
  } finally {
    loading.value = false
  }
}

const openEdit = (channel: Channel) => {
  editing.value = true
  editingId.value = channel.id
  formData.value = {
    name: channel.name,
    type: channel.type,
    contact_name: channel.contact || '',
    contact_phone: channel.phone || '',
    commission_rate: (channel as any).commission_rate || 0,
    settlement_cycle: (channel as any).settlement_cycle || '',
    notes: (channel as any).notes || '',
  }
  showCreateModal.value = true
}

const handleDelete = async (id: number) => {
  try {
    await deleteChannel(id)
    message.success('渠道已删除')
    await fetchChannels()
  } catch {
    message.error('删除失败')
  }
}

const handleCreate = async () => {
  try {
    await formRef.value?.validate()
  } catch {
    return
  }
  submitting.value = true
  try {
    if (editing.value && editingId.value) {
      await updateChannel(editingId.value, formData.value)
      message.success('渠道已更新')
    } else {
      await createChannel(formData.value)
      message.success('渠道创建成功')
    }
    showCreateModal.value = false
    editing.value = false
    editingId.value = null
    formData.value = { name: '', type: '', contact_name: '', contact_phone: '', commission_rate: 0, settlement_cycle: '', notes: '' }
    await fetchChannels()
  } catch {
    message.error(editing.value ? '更新失败' : '创建渠道失败')
  } finally {
    submitting.value = false
  }
}

onMounted(() => fetchChannels())
</script>