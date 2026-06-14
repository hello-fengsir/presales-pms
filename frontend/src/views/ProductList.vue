<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold" style="color: var(--color-text-heading)">产品列表</h1>
        <p class="mt-1 text-sm" style="color: var(--color-text-secondary)">管理产品目录与型号规格</p>
      </div>
      <n-button type="primary" @click="showCreateModal = true">
        <template #icon><n-icon><add-outline /></n-icon></template>
        新建产品
      </n-button>
    </div>

    <!-- Category Tabs -->
    <div class="flex gap-2 flex-wrap">
      <button
        v-for="cat in categories"
        :key="cat.value"
        @click="activeCategory = cat.value"
        class="px-4 py-1.5 rounded-full text-sm font-medium transition-all duration-200"
        :class="activeCategory === cat.value
          ? 'bg-blue-600 text-white shadow-sm'
          : 'bg-slate-100 text-slate-500 hover:bg-slate-200'"
        style="border: none; cursor: pointer"
      >
        {{ cat.label }}
      </button>
    </div>

    <!-- Batch Operations Bar -->
    <div
      v-if="selectedIds.length > 0"
      class="card px-5 py-3 flex items-center justify-between"
      style="border-color: var(--color-primary); background: var(--color-primary-light)"
    >
      <span class="text-sm font-medium" style="color: var(--color-primary)">
        已选择 {{ selectedIds.length }} 个型号
      </span>
      <div class="flex gap-2">
        <n-button size="small" @click="batchUpdateStatus('上架')">批量上架</n-button>
        <n-button size="small" @click="batchUpdateStatus('下架')">批量下架</n-button>
        <n-button size="small" type="error" @click="batchDelete">批量删除</n-button>
        <n-button size="small" quaternary @click="selectedIds = []">取消选择</n-button>
      </div>
    </div>

    <!-- Products Table -->
    <div class="card overflow-hidden">
      <n-data-table
        :columns="productColumns"
        :data="filteredProducts"
        :loading="loading"
        :pagination="{ pageSize: 10 }"
        :row-key="(row: any) => row.id"
        :row-class-name="() => 'hover:bg-slate-50/50'"
        striped
      />
    </div>

    <!-- Expanded Models Section -->
    <div v-if="expandedProduct" class="card p-5 space-y-4">
      <div class="flex items-center justify-between">
        <h3 class="text-lg font-semibold" style="color: var(--color-text-heading)">
          {{ expandedProduct.name }} · 型号列表
        </h3>
        <n-button size="small" quaternary @click="expandedProduct = null">
          <template #icon><n-icon><close-outline /></n-icon></template>
          收起
        </n-button>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div
          v-for="model in expandedProduct.models"
          :key="model.id"
          class="card card-hover p-4 cursor-pointer"
          :class="{ 'ring-2': selectedIds.includes(model.id) }"
          :style="selectedIds.includes(model.id) ? { ringColor: 'var(--color-primary)' } : {}"
          @click="toggleModelSelect(model.id)"
        >
          <div class="flex items-start justify-between mb-3">
            <h4 class="font-semibold text-sm" style="color: var(--color-text-heading)">{{ model.name }}</h4>
            <span class="tag" :class="model.status === '上架' ? 'tag-green' : 'tag-gray'">
              {{ model.status }}
            </span>
          </div>
          <div class="space-y-1.5 text-xs" style="color: var(--color-text-secondary)">
            <div class="flex justify-between">
              <span>规格</span>
              <span class="font-medium" style="color: var(--color-text-primary)">{{ model.spec }}</span>
            </div>
            <div class="flex justify-between">
              <span>价格</span>
              <span class="font-medium" style="color: var(--color-text-primary)">¥{{ model.price?.toLocaleString() }}</span>
            </div>
            <div class="flex justify-between">
              <span>关联项目</span>
              <span class="font-medium" style="color: var(--color-primary)">{{ model.project_count || 0 }} 个</span>
            </div>
          </div>
        </div>
      </div>
      <div v-if="!expandedProduct.models?.length" class="text-center py-8 text-sm" style="color: var(--color-text-muted)">
        暂无型号数据
      </div>
    </div>

    <!-- Create Product Modal -->
    <n-modal
      v-model:show="showCreateModal"
      preset="card"
      :title="editing ? '编辑产品' : '新建产品'"
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
        <n-form-item label="产品名称" path="name">
          <n-input v-model:value="formData.name" placeholder="请输入产品名称" />
        </n-form-item>
        <n-form-item label="产品分类" path="category">
          <n-select
            v-model:value="formData.category"
            :options="categoryOptions"
            placeholder="请选择分类"
          />
        </n-form-item>
        <n-form-item label="型号数量" path="model_count">
          <n-input-number v-model:value="formData.model_count" :min="0" placeholder="型号数量" style="width: 100%" />
        </n-form-item>
        <n-form-item label="上架状态" path="status">
          <n-select
            v-model:value="formData.status"
            :options="[{ label: '上架', value: '上架' }, { label: '下架', value: '下架' }]"
            placeholder="请选择状态"
          />
        </n-form-item>
        <div class="flex justify-end gap-3 mt-2">
          <n-button @click="closeModal">取消</n-button>
          <n-button type="primary" attr-type="submit" :loading="submitting">{{ editing ? '保存修改' : '确认创建' }}</n-button>
        </div>
      </n-form>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, h } from 'vue'
// useMessage replaced with safe wrapper
import {
  NButton, NDataTable, NModal, NForm, NFormItem,
  NInput, NSelect, NInputNumber, NIcon, NPopconfirm
} from 'naive-ui'
import { AddOutline, CloseOutline } from '@vicons/ionicons5'
import { getProducts, createProduct, updateProduct, deleteProduct, getProductModels } from '../api'
import type { DataTableColumns, FormInst, FormRules } from 'naive-ui'

interface ProductModel {
  id: number
  name: string
  spec: string
  price: number
  status: string
  project_count: number
}

interface Product {
  id: number
  name: string
  category: string
  model_count: number
  status: string
  project_count: number
  models: ProductModel[]
}

const message = { error: (msg) => console.error('[CRM]', msg), success: (msg) => console.log('[CRM]', msg), warning: (msg) => console.warn('[CRM]', msg), info: (msg) => console.info('[CRM]', msg) }
const loading = ref(false)
const showCreateModal = ref(false)
const submitting = ref(false)
const formRef = ref<FormInst | null>(null)
const products = ref<Product[]>([])
const activeCategory = ref('全部')
const expandedProduct = ref<Product | null>(null)
const editingId = ref<number | null>(null)
const editing = ref(false)
const selectedIds = ref<number[]>([])

const categories = [
  { label: '全部', value: '全部' },
  { label: '云计算', value: '云计算' },
  { label: '存储', value: '存储' },
  { label: '网络', value: '网络' },
  { label: '网络安全', value: '网络安全' },
]

const categoryOptions = categories.filter(c => c.value !== '全部')

const formData = ref({ name: '', category: '', model_count: 0, status: '上架' })
const rules: FormRules = {
  name: [{ required: true, message: '请输入产品名称', trigger: 'blur' }],
  category: [{ required: true, message: '请选择分类', trigger: 'change' }],
  status: [{ required: true, message: '请选择状态', trigger: 'change' }],
}

const filteredProducts = computed(() => {
  if (activeCategory.value === '全部') return products.value
  return products.value.filter(p => p.category === activeCategory.value)
})

const productColumns: DataTableColumns<Product> = [
  {
    title: '产品名称',
    key: 'name',
    width: 200,
    render(row) {
      return h(
        'button',
        {
          class: 'font-semibold text-left',
          style: { color: 'var(--color-text-link)', border: 'none', background: 'none', cursor: 'pointer', padding: 0 },
          onClick: () => toggleExpand(row),
        },
        row.name
      )
    },
  },
  {
    title: '分类',
    key: 'category',
    width: 120,
    render(row) {
      return h('span', { class: 'tag tag-blue' }, row.category)
    },
  },
  { title: '型号数', key: 'model_count', width: 100, align: 'center' as const },
  {
    title: '上架',
    key: 'status',
    width: 100,
    align: 'center' as const,
    render(row) {
      return h('span', { class: row.status === '上架' ? 'tag tag-green' : 'tag tag-gray' }, row.status)
    },
  },
  { title: '关联项目', key: 'project_count', width: 100, align: 'center' as const },
  {
    title: '操作',
    key: 'actions',
    width: 120,
    align: 'center' as const,
    render(row) {
      return h('div', { class: 'flex items-center justify-center gap-2' }, [
        h('button', {
          class: 'text-blue-600 hover:text-blue-700 text-sm font-medium transition-colors',
          style: { border: 'none', background: 'none', cursor: 'pointer' },
          onClick: () => editProduct(row),
        }, '编辑'),
        h(NPopconfirm, {
          onPositiveClick: () => handleDelete(row),
        }, {
          default: () => '确认删除该产品？',
          trigger: () => h('button', {
            class: 'text-red-500 hover:text-red-600 text-sm font-medium transition-colors',
            style: { border: 'none', background: 'none', cursor: 'pointer' },
          }, '删除'),
        }),
      ])
    },
  },
]

const fetchProducts = async () => {
  loading.value = true
  try {
    const { data } = await getProducts()
    console.log('[DEBUG Product] raw data type:', typeof data, Array.isArray(data), 'len:', Array.isArray(data) ? data.length : 'n/a')
    console.log('[DEBUG Product] data keys:', Object.keys(data))
    const list = data.data || data || []
    console.log('[DEBUG Product] list length:', list.length)
    products.value = list.map((p: any) => ({ ...p, models: p.models || [] }))
  } catch {
    message.error('获取产品列表失败')
  } finally {
    loading.value = false
  }
}

const toggleExpand = async (product: Product) => {
  if (expandedProduct.value?.id === product.id) {
    expandedProduct.value = null
  } else {
    expandedProduct.value = { ...product, models: [] }
    selectedIds.value = []
    try {
      const res = await getProductModels(product.id)
      const models = res.data?.data ?? res.data ?? []
      expandedProduct.value = { ...expandedProduct.value, models }
    } catch {
      expandedProduct.value = { ...expandedProduct.value, models: [] }
    }
  }
}

const toggleModelSelect = (modelId: number) => {
  const idx = selectedIds.value.indexOf(modelId)
  if (idx >= 0) {
    selectedIds.value.splice(idx, 1)
  } else {
    selectedIds.value.push(modelId)
  }
}

const batchUpdateStatus = (status: string) => {
  message.info(`批量${status} ${selectedIds.value.length} 个型号`)
  selectedIds.value = []
}

const batchDelete = () => {
  if (window.confirm(`确认删除 ${selectedIds.value.length} 个型号？`)) {
    message.info(`已删除 ${selectedIds.value.length} 个型号`)
    selectedIds.value = []
  }
}

const editProduct = (row: Product) => {
  editing.value = true
  editingId.value = row.id
  formData.value = {
    name: row.name,
    category: row.category,
    model_count: row.model_count,
    status: row.status,
  }
  showCreateModal.value = true
}

const handleDelete = async (row: Product) => {
  try {
    await deleteProduct(row.id)
    message.success('删除成功')
    await fetchProducts()
  } catch {
    message.error('删除失败')
  }
}

const closeModal = () => {
  showCreateModal.value = false
  editing.value = false
  editingId.value = null
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
      await updateProduct(editingId.value, formData.value)
      message.success('修改保存成功')
    } else {
      await createProduct(formData.value)
      message.success('产品创建成功')
    }
    showCreateModal.value = false
    formData.value = { name: '', category: '', model_count: 0, status: '上架' }
    await fetchProducts()
  } catch {
    message.error(editing.value ? '修改保存失败' : '创建产品失败')
  } finally {
    submitting.value = false
    editing.value = false
    editingId.value = null
  }
}

onMounted(() => fetchProducts())
</script>
