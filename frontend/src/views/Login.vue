<template>
  <div class="min-h-screen flex items-center justify-center p-6" style="background: var(--color-bg-body)">
    <div class="card rounded-2xl p-8 w-full max-w-sm" style="box-shadow: var(--shadow-lg)">
      <!-- Title -->
      <div class="text-center mb-8">
        <div class="inline-flex items-center justify-center w-14 h-14 rounded-xl mb-4" style="background: transparent">
          <img src="@/assets/logo.png" class="w-10 h-10 object-contain" alt="logo" />
        </div>
        <h1 class="text-2xl font-bold" style="color: var(--color-text-heading)">Super PMS</h1>
        <p class="mt-2 text-sm" style="color: var(--color-text-muted)">登录以继续使用</p>
      </div>

      <!-- Error Alert -->
      <n-alert v-if="errorMsg" type="error" :title="errorMsg" class="mb-5" closable @close="errorMsg = ''" />

      <!-- Login Form -->
      <n-form ref="formRef" :model="formData" :rules="rules" size="large">
        <n-form-item path="username">
          <n-input
            v-model:value="formData.username"
            placeholder="请输入用户名"
            :input-props="{ autocomplete: 'username' }"
            clearable
          >
            <template #prefix>
              <PersonOutline class="w-4 h-4" style="color: var(--color-text-muted)" />
            </template>
          </n-input>
        </n-form-item>

        <n-form-item path="password">
          <n-input
            v-model:value="formData.password"
            type="password"
            placeholder="请输入密码"
            :input-props="{ autocomplete: 'current-password' }"
            show-password-on="click"
            @keyup.enter="handleLogin"
          >
            <template #prefix>
              <LockClosedOutline class="w-4 h-4" style="color: var(--color-text-muted)" />
            </template>
          </n-input>
        </n-form-item>

        <n-button
          type="primary" block
          size="large"
          :loading="loading"
          :disabled="loading"
          class="mt-2"
          @click="handleLogin"
        >
          登 录
        </n-button>
      </n-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import {
  NForm,
  NFormItem,
  NInput,
  NButton,
  NAlert,
  type FormInst,
  type FormRules,
} from 'naive-ui'
import { PersonOutline, LockClosedOutline } from '@vicons/ionicons5'
import { login } from '../api'

const router = useRouter()
const formRef = ref<FormInst | null>(null)
const loading = ref(false)
const errorMsg = ref('')

const formData = reactive({
  username: '',
  password: '',
})

const rules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6位', trigger: 'blur' },
  ],
}

async function handleLogin() {
  errorMsg.value = ''
  try {
    await formRef.value?.validate()
  } catch {
    return
  }

  loading.value = true
  try {
    const res = await login(formData.username, formData.password)
    const token = res.data?.access_token
    if (token) {
      localStorage.setItem('token', token)
      router.replace({ name: 'dashboard' })
    } else {
      errorMsg.value = '登录失败：未获取到令牌'
    }
  } catch (err: any) {
    const msg = err.response?.data?.message || err.message || '登录失败，请重试'
    errorMsg.value = typeof msg === 'string' ? msg : '登录失败，请检查用户名和密码'
  } finally {
    loading.value = false
  }
}
</script>
