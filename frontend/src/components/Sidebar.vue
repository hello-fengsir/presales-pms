<template>
  <aside
  class="sidebar-panel w-56 h-screen flex flex-col bg-white border-r transition-transform duration-300 ease-in-out"
  :class="{ 'sidebar-open': open }"
  style="border-color: var(--color-border)"
>
    <!-- Logo -->
    <div class="flex items-center gap-2 px-5 py-5">
      <div class="w-8 h-8 rounded-lg flex items-center justify-center overflow-hidden" style="background: transparent"><img src="@/assets/logo.png" class="w-full h-full object-contain" alt="logo" />
      </div>
      <h1 class="text-xl font-bold bg-gradient-to-r from-blue-500 to-blue-600 bg-clip-text text-transparent">
        Super PMS
      </h1>
    </div>

    <!-- Navigation Menu -->
    <nav class="flex-1 px-3 py-2 space-y-1 overflow-y-auto">
      <router-link
        v-for="item in menuItems"
        @click="emit('close')"
        :key="item.route"
        :to="item.route"
        class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors duration-150"
        :class="isActive(item.route)
          ? 'text-primary'
          : 'hover:bg-surface-hover'"
        :style="isActive(item.route)
          ? { background: 'var(--color-primary-light)', color: 'var(--color-primary)' }
          : { color: 'var(--color-text-secondary)' }"
      >
        <component :is="item.icon" class="w-5 h-5 flex-shrink-0" />
        <span>{{ item.label }}</span>
      </router-link>
    </nav>

    <!-- User footer -->
    <div class="border-t" style="border-color: var(--color-border)">
      <!-- User row -->
      <div class="flex items-center justify-between px-4 py-3">
        <div class="flex items-center gap-2.5">
          <div class="w-8 h-8 rounded-full flex items-center justify-center text-white text-xs font-semibold" style="background: transparent">
            H
          </div>
          <span class="text-sm" style="color: var(--color-text-primary)">hello-fengsir</span>
        </div>
        <button
          class="w-8 h-8 rounded-lg flex items-center justify-center transition-colors hover:bg-surface-hover"
          :style="{ color: 'var(--color-text-muted)' }"
          title="退出登录"
          @click="handleLogout"
        >
          <LogOutOutline class="w-4 h-4" />
        </button>
      </div>

      <!-- Action row: API Key + GitHub -->
      <div class="flex items-center gap-1 px-3 pb-3">
        <button
          class="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs transition-colors hover:bg-surface-hover flex-1"
          :style="{ color: 'var(--color-text-muted)' }"
          title="API Key 配置"
          @click="showApiModal = true"
        >
          <KeyOutline class="w-3.5 h-3.5" />
          <span>API配置</span>
        </button>
        <a
          href="https://github.com/hello-fengsir"
          target="_blank"
          class="w-7 h-7 rounded-lg flex items-center justify-center transition-colors hover:bg-surface-hover"
          :style="{ color: 'var(--color-text-muted)' }"
          title="作者: 峰Sir · GitHub"
        >
          <!-- GitHub icon SVG -->
          <svg class="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/>
          </svg>
        </a>
      </div>
    </div>

    <!-- API Key Modal -->
    <ApiKeyModal v-model:show="showApiModal" />
  </aside>
</template>

<script setup lang="ts">
import { ref, defineProps, defineEmits } from 'vue'

const props = defineProps<{ open?: boolean }>()
const emit = defineEmits<{ (e: 'close'): void }>()
import { useRoute, useRouter } from 'vue-router'
import {
  BarChartOutline,
  DocumentTextOutline,
  PeopleOutline,
  LinkOutline,
  CubeOutline,
  WalletOutline,
  TrendingUpOutline,
  LogOutOutline,
  KeyOutline,
} from '@vicons/ionicons5'
import ApiKeyModal from './ApiKeyModal.vue'

const route = useRoute()
const router = useRouter()
const showApiModal = ref(false)

const menuItems = [
  { label: '数据看板', route: '/work/dashboard', icon: BarChartOutline },
  { label: '项目管理', route: '/work/projects', icon: DocumentTextOutline },
  { label: '客户管理', route: '/work/customers', icon: PeopleOutline },
  { label: '渠道管理', route: '/work/channels', icon: LinkOutline },
  { label: '产品线', route: '/work/products', icon: CubeOutline },
  { label: '销售管理', route: '/work/sales', icon: WalletOutline },
  { label: '项目汇报', route: '/work/reports', icon: TrendingUpOutline },
]

function isActive(target: string): boolean {
  if (target === '/work/dashboard' && route.path === '/work/dashboard') return true
  return route.path.startsWith(target) && target !== '/work/dashboard'
}

function handleLogout() {
  localStorage.removeItem('token')
  router.push({ name: 'login' })
}
</script>

<style scoped>
@media (max-width: 767px) {
  .sidebar-panel {
    position: fixed !important;
    left: 0; top: 0; bottom: 0;
    z-index: 1000;
    transform: translateX(-100%);
    box-shadow: none;
  }
  .sidebar-panel.sidebar-open {
    transform: translateX(0);
    box-shadow: 4px 0 20px rgba(0,0,0,0.15);
  }
}
</style>
