<template>
  <n-config-provider :locale="zhCN" :date-locale="dateZhCN" :theme-overrides="themeOverrides">
    <n-message-provider>
      <n-dialog-provider>
        <div class="flex h-screen overflow-hidden">
          <!-- Mobile top bar -->
          <div v-if="$route.name !== 'login'" class="mobile-topbar">
            <button class="hamburger" @click="sidebarOpen = !sidebarOpen">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round">
                <line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/>
              </svg>
            </button>
            <span class="brand">Super PMS</span>
          </div>
          <!-- Sidebar overlay -->
          <div v-if="sidebarOpen" class="sidebar-overlay" @click="sidebarOpen = false"></div>
          <Sidebar v-if="$route.name !== 'login'" :open="sidebarOpen" @close="sidebarOpen = false" />
          <main class="flex-1 overflow-y-auto bg-slate-50 mobile-main">
            <div class="max-w-7xl mx-auto flex flex-col gap-6 p-6 mobile-container">
              <router-view />
            </div>
          </main>
        </div>
      </n-dialog-provider>
    </n-message-provider>
  </n-config-provider>
</template>

<script setup lang="ts">
import { ref } from "vue"
import Sidebar from "./components/Sidebar.vue"
const sidebarOpen = ref(false)
import { zhCN, dateZhCN } from "naive-ui"
import type { GlobalThemeOverrides } from "naive-ui"

const themeOverrides: GlobalThemeOverrides = {
  common: {
    primaryColor: "#2563EB",
    primaryColorHover: "#1D4ED8",
    primaryColorPressed: "#1D4ED8",
    primaryColorSuppl: "#1D4ED8",
    // Fixed: proper light theme colors
    bodyColor: "#F1F5F9",
    cardColor: "#FFFFFF",
    modalColor: "#FFFFFF",
    popoverColor: "#FFFFFF",
    borderColor: "#E2E8F0",
    dividerColor: "#E2E8F0",
    inputColor: "#FFFFFF",
    inputColorDisabled: "#F1F5F9",
    textColor1: "#1E293B",
    textColor2: "#475569",
    textColor3: "#94A3B8",
    borderRadius: "12px",
    fontSize: "14px",
    closeColorHover: "#2563EB",
    hoverColor: "rgba(37,99,235,0.05)",
    pressedColor: "rgba(37,99,235,0.08)",
  },
}
</script>

<style>
/* Mobile top bar */
.mobile-topbar {
  display: none;
  position: fixed;
  top: 0; left: 0; right: 0;
  height: 52px;
  background: #fff;
  border-bottom: 1px solid #E2E8F0;
  z-index: 999;
  align-items: center;
  padding: 0 16px;
  gap: 12px;
}
.hamburger {
  background: none;
  border: none;
  cursor: pointer;
  padding: 6px;
  color: #475569;
  display: flex;
  align-items: center;
}
.brand {
  font-size: 1.1em;
  font-weight: 700;
  background: linear-gradient(to right, #3B82F6, #2563EB);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.sidebar-overlay {
  display: none;
  position: fixed;
  inset: 0;
  background: rgba(15,23,42,0.4);
  z-index: 999;
  backdrop-filter: blur(2px);
}

@media (max-width: 767px) {
  .mobile-topbar { display: flex; }
  .sidebar-overlay { display: block; }
  .mobile-main { padding-top: 52px !important; }
  .mobile-container { padding: 12px !important; }
}
@media (min-width: 768px) {
  .mobile-topbar { display: none !important; }
  .sidebar-overlay { display: none !important; }
}
</style>
