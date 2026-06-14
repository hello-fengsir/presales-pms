<template>
  <n-modal v-model:show="showModal" preset="card" title="🔑 API Key 配置" style="max-width: 640px" :style="{ width: '95%' }" :mask-closable="false">
    <div class="space-y-5">
      <!-- Step 1: Select Provider -->
      <div>
        <p class="text-sm font-semibold mb-2" style="color: var(--color-text-heading)">选择服务商</p>
        <n-select
          v-model:value="selectedProvider"
          :options="providerOptions"
          placeholder="选择大模型服务商..."
          @update:value="onProviderChange"
        />
      </div>

      <!-- Step 2: Select Model -->
      <div v-if="selectedProvider">
        <p class="text-sm font-semibold mb-2" style="color: var(--color-text-heading)">选择模型</p>
        <n-select
          v-model:value="selectedModel"
          :options="modelOptions"
          placeholder="选择模型版本..."
        />
      </div>

      <!-- Step 3: API Key -->
      <div v-if="selectedModel">
        <p class="text-sm font-semibold mb-2" style="color: var(--color-text-heading)">API Key</p>
        <n-input
          v-model:value="apiKeyInput"
          type="password"
          show-password-on="click"
          placeholder="sk-xxxxxxxxxxxxxxxx"
        />
      </div>

      <!-- Step 4: Test & Save -->
      <div v-if="selectedModel" class="flex gap-3">
        <n-button type="info" @click="handleTest" :loading="testing" :disabled="!apiKeyInput.trim()">
          {{ testing ? '测试中...' : '🔍 测试有效性' }}
        </n-button>
        <n-button type="primary" @click="handleSave" :loading="saving" :disabled="!testPassed">
          💾 保存配置
        </n-button>
      </div>

      <!-- Test Result -->
      <div v-if="testResult !== null" class="rounded-lg p-3 text-sm" :style="testPassed ? { background: '#ECFDF5', color: '#059669' } : { background: '#FEF2F2', color: '#DC2626' }">
        <div class="flex items-center gap-2 font-semibold">
          <span>{{ testPassed ? '✅' : '❌' }}</span>
          <span>{{ testPassed ? '测试通过' : '测试失败' }}</span>
        </div>
        <p v-if="testPassed && testPreview" class="mt-1">返回: "{{ testPreview }}"</p>
        <p v-if="!testPassed && testDetail" class="mt-1 break-all">{{ testDetail }}</p>
      </div>

      <!-- Saved Keys List -->
      <div v-if="savedKeys.length > 0" class="border-t pt-4" style="border-color: var(--color-border)">
        <p class="text-sm font-semibold mb-3" style="color: var(--color-text-heading)">已保存的 Key</p>
        <div class="space-y-2">
          <div
            v-for="key in savedKeys"
            :key="key.id"
            class="flex items-center justify-between rounded-lg p-2.5 text-sm"
            style="background: var(--color-bg-hover)"
          >
            <div class="flex items-center gap-2 min-w-0">
              <n-tag :bordered="false" size="tiny" type="info">{{ getProviderName(key.provider) }}</n-tag>
              <span class="truncate" style="color: var(--color-text-secondary)">{{ key.model }}</span>
              <code class="text-xs" style="color: var(--color-text-muted)">{{ key.api_key }}</code>
            </div>
            <n-button text size="tiny" type="error" @click="handleDelete(key.id)" :loading="deleting === key.id">
              <TrashOutline class="w-3.5 h-3.5" />
            </n-button>
          </div>
        </div>
      </div>
    </div>
  </n-modal>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import {
  NModal, NSelect, NInput, NButton, NTag,
} from 'naive-ui'
import { TrashOutline } from '@vicons/ionicons5'
import api from '../api'

interface Provider {
  id: string
  name: string
  models: { id: string; name: string }[]
}

interface SavedKey {
  id: number
  provider: string
  model: string
  api_key: string
  base_url: string
  is_active: boolean
  created_at: string
}

const props = defineProps<{ show: boolean }>()
const emit = defineEmits<{ 'update:show': [value: boolean] }>()

const showModal = computed({
  get: () => props.show,
  set: (v) => emit('update:show', v),
})

const providers = ref<Provider[]>([])
const selectedProvider = ref<string | null>(null)
const selectedModel = ref<string | null>(null)
const apiKeyInput = ref('')
const testing = ref(false)
const saving = ref(false)
const testResult = ref<boolean | null>(null)
const testPassed = ref(false)
const testPreview = ref('')
const testDetail = ref('')
const savedKeys = ref<SavedKey[]>([])
const deleting = ref<number | null>(null)

const providerOptions = computed(() =>
  providers.value.map(p => ({ label: p.name, value: p.id }))
)

const modelOptions = computed(() => {
  const p = providers.value.find(p => p.id === selectedProvider.value)
  if (!p) return []
  return p.models.map(m => ({ label: `${m.id} (${m.name})`, value: m.id }))
})

const message = {
  error: (msg: string) => { console.error('[ApiKey]', msg); alert(msg) },
  success: (msg: string) => console.log('[ApiKey]', msg),
  warning: (msg: string) => console.warn('[ApiKey]', msg),
}

function getProviderName(id: string): string {
  return providers.value.find(p => p.id === id)?.name || id
}

function onProviderChange() {
  selectedModel.value = null
  testResult.value = null
  testPassed.value = false
}

// Watch modal open to load providers and saved keys
watch(() => props.show, async (v) => {
  if (v) {
    await loadProviders()
    await loadSavedKeys()
  }
})

async function loadProviders() {
  try {
    const res = await api.get('/api-keys/providers')
    providers.value = res.data?.data ?? res.data ?? []
  } catch (e: any) {
    console.error('Load providers failed:', e)
  }
}

async function loadSavedKeys() {
  try {
    const res = await api.get('/api-keys')
    savedKeys.value = res.data?.data ?? res.data ?? []
  } catch (e: any) {
    console.error('Load keys failed:', e)
  }
}

async function handleTest() {
  if (!selectedProvider.value || !selectedModel.value || !apiKeyInput.value.trim()) return
  testing.value = true
  testResult.value = null
  testPassed.value = false
  try {
    const res = await api.post('/api-keys/test', {
      provider: selectedProvider.value,
      model: selectedModel.value,
      api_key: apiKeyInput.value,
    })
    const d = res.data?.data ?? res.data ?? {}
    testResult.value = true
    testPassed.value = d.ok === true
    testPreview.value = d.preview || ''
    testDetail.value = d.detail || ''
  } catch (e: any) {
    testResult.value = true
    testPassed.value = false
    testDetail.value = e.response?.data?.detail || e.message || '未知错误'
  } finally {
    testing.value = false
  }
}

async function handleSave() {
  if (!selectedProvider.value || !selectedModel.value) return
  saving.value = true
  try {
    await api.post('/api-keys', {
      provider: selectedProvider.value,
      model: selectedModel.value,
      api_key: apiKeyInput.value,
    })
    message.success('API Key 已保存')
    apiKeyInput.value = ''
    selectedProvider.value = null
    selectedModel.value = null
    testResult.value = null
    testPassed.value = false
    await loadSavedKeys()
  } catch (e: any) {
    message.error('保存失败: ' + (e.response?.data?.detail || e.message))
  } finally {
    saving.value = false
  }
}

async function handleDelete(id: number) {
  if (!confirm('确定删除该 API Key？')) return
  deleting.value = id
  try {
    await api.delete(`/api-keys/${id}`)
    message.success('已删除')
    await loadSavedKeys()
  } catch (e: any) {
    message.error('删除失败')
  } finally {
    deleting.value = null
  }
}
</script>
