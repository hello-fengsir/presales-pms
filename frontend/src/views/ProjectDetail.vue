<template>
  <div class="space-y-5">
    <!-- ═══ Hero: 项目摘要 ═══ -->
    <div class="flex items-start justify-between gap-4 flex-wrap">
      <div class="flex items-center gap-3 min-w-0">
        <n-button text @click="$router.back()" style="color: var(--color-text-secondary)">
          <template #icon>
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
            </svg>
          </template>
        </n-button>
        <div>
          <h1 class="text-xl font-bold truncate" style="color: var(--color-text-heading)">
            {{ project?.name || '项目详情' }}
          </h1>
          <div class="flex items-center gap-2 mt-1">
            <span class="w-2 h-2 rounded-full flex-shrink-0" :style="{ background: stageColor(project?.stage) }"></span>
            <n-tag :bordered="false" size="small" :type="stageType(project?.stage)" :color="{ color: stageColor(project?.stage), textColor: '#fff' }">
              {{ stageLabel(project?.stage) }}
            </n-tag>
            <span class="text-xs" style="color: var(--color-text-muted)">
              · {{ project?.customer_name || project?.customer?.name || '未关联客户' }}
            </span>
          </div>
        </div>
      </div>
      <n-button type="primary" @click="openEditModal" class="flex-shrink-0">
        <template #icon>
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
          </svg>
        </template>
        编辑项目
      </n-button>
    </div>

    <div v-if="loading" class="flex justify-center py-20"><n-spin size="large" /></div>

    <template v-else-if="project">
      <!-- ═══ 阶段进度条 ═══ -->
      <div class="card p-4">
        <div class="flex items-center justify-between gap-1">
          <div v-for="(s, idx) in stageSteps" :key="s.key" class="flex items-center gap-2 flex-shrink-0">
            <div class="flex flex-col items-center">
              <div
                class="w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold transition-all"
                :style="{
                  background: stageIndex(s.key) <= stageIndex(project.stage) ? stageColor(project.stage) : 'var(--color-bg-hover)',
                  color: stageIndex(s.key) <= stageIndex(project.stage) ? '#fff' : 'var(--color-text-muted)',
                  ringColor: stageIndex(s.key) === stageIndex(project.stage) ? stageColor(project.stage) : 'transparent'
                }"
                :class="stageIndex(s.key) === stageIndex(project.stage) ? 'ring-2 ring-offset-1' : ''"
              >
                <template v-if="stageIndex(s.key) < stageIndex(project.stage)">
                  <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
                  </svg>
                </template>
                <template v-else>{{ idx + 1 }}</template>
              </div>
              <span class="text-xs mt-1.5 font-medium whitespace-nowrap"
                :style="{ color: stageIndex(s.key) <= stageIndex(project.stage) ? stageColor(project.stage) : 'var(--color-text-muted)' }"
              >{{ s.label }}</span>
            </div>
            <div v-if="idx < stageSteps.length - 1" class="h-0.5 mt-[-18px] flex-1 min-w-[16px]"
              :style="{ background: stageIndex(stageSteps[idx + 1].key) <= stageIndex(project.stage) ? stageColor(project.stage) : 'var(--color-border)' }"
            ></div>
          </div>
        </div>
      </div>

      <!-- ═══ KPI 指标 ═══ -->
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div class="card p-3.5 text-center">
          <p class="text-xl font-bold" style="color: var(--color-danger)">{{ formatAmount(project.amount) }}</p>
          <p class="text-xs mt-0.5" style="color: var(--color-text-muted)">项目金额</p>
        </div>
        <div class="card p-3.5 text-center">
          <p class="text-xl font-bold" style="color: var(--color-text-heading)">{{ followUps.length }}</p>
          <p class="text-xs mt-0.5" style="color: var(--color-text-muted)">跟进次数</p>
        </div>
        <div class="card p-3.5 text-center">
          <p class="text-xl font-bold" style="color: var(--color-text-heading)">{{ projectDays }}</p>
          <p class="text-xs mt-0.5" style="color: var(--color-text-muted)">项目周期(天)</p>
        </div>
        <div class="card p-3.5 text-center">
          <p class="text-xl font-bold" style="color: var(--color-primary)">{{ quotationItems.length }}</p>
          <p class="text-xs mt-0.5" style="color: var(--color-text-muted)">报价项数</p>
        </div>
      </div>

      <!-- ═══ 项目背景 / 需求 / 方案 ═══ -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
        <!-- 项目背景 -->
        <div class="card overflow-hidden" v-if="project.customer_background || project.customer_requirement">
          <div class="p-4 border-b flex items-center gap-2" style="border-color: var(--color-border)">
            <svg class="w-4 h-4" style="color: var(--color-text-muted)" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
            </svg>
            <h2 class="text-sm font-semibold" style="color: var(--color-text-heading)">项目背景</h2>
          </div>
          <div class="p-4">
            <div class="space-y-4">
              <div v-if="project.customer_background">
                <p class="text-xs mb-1.5 font-medium" style="color: var(--color-text-muted)">客户背景</p>
                <p class="text-sm leading-relaxed whitespace-pre-wrap" style="color: var(--color-text-secondary)">{{ project.customer_background }}</p>
              </div>
              <div v-if="project.customer_requirement">
                <p class="text-xs mb-1.5 font-medium" style="color: var(--color-text-muted)">需求分析</p>
                <p class="text-sm leading-relaxed whitespace-pre-wrap" style="color: var(--color-text-secondary)">{{ project.customer_requirement }}</p>
              </div>
              <div v-if="project.competitor_info" class="pt-3 border-t" style="border-color: var(--color-border)">
                <p class="text-xs mb-1.5 font-medium" style="color: var(--color-text-muted)">竞品分析</p>
                <p class="text-sm leading-relaxed whitespace-pre-wrap" style="color: var(--color-text-secondary)">{{ project.competitor_info }}</p>
              </div>
            </div>
          </div>
        </div>
        <!-- 解决方案 -->
        <div class="card overflow-hidden" v-if="project.solution_description || project.solution_value">
          <div class="p-4 border-b flex items-center gap-2" style="border-color: var(--color-border)">
            <svg class="w-4 h-4" style="color: var(--color-text-muted)" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
            <h2 class="text-sm font-semibold" style="color: var(--color-text-heading)">解决方案</h2>
          </div>
          <div class="p-4">
            <div class="space-y-4">
              <div v-if="project.solution_description">
                <p class="text-xs mb-1.5 font-medium" style="color: var(--color-text-muted)">方案描述</p>
                <p class="text-sm leading-relaxed whitespace-pre-wrap" style="color: var(--color-text-secondary)">{{ project.solution_description }}</p>
              </div>
              <div v-if="project.solution_value">
                <p class="text-xs mb-1.5 font-medium" style="color: var(--color-text-muted)">方案价值</p>
                <p class="text-sm leading-relaxed whitespace-pre-wrap" style="color: var(--color-text-secondary)">{{ project.solution_value }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ═══ 方案拓扑：改进前 / 改进后 ═══ -->
      <div class="card overflow-hidden" v-if="project.topology_image || project.topology_image_after">
        <div class="p-4 border-b flex items-center justify-between" style="border-color: var(--color-border)">
          <div class="flex items-center gap-2">
            <svg class="w-4 h-4" style="color: var(--color-text-muted)" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            <h2 class="text-sm font-semibold" style="color: var(--color-text-heading)">方案拓扑</h2>
          </div>
        </div>
        <div class="p-4">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
            <!-- 改进前 -->
            <div>
              <div class="flex items-center justify-between mb-2">
                <span class="text-xs font-semibold px-2 py-0.5 rounded" style="background: #FEF2F2; color: #DC2626">改进前</span>
                <n-upload :show-file-list="false" accept="image/*" @change="(opts: any) => handleTopologyUpload(opts, 'before')">
                  <n-button size="tiny" quaternary :loading="uploadingTopoBefore" style="color: var(--color-text-muted)">
                    <template #icon><svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" /></svg></template>
                    {{ project.topology_image ? '更换' : '上传' }}
                  </n-button>
                </n-upload>
              </div>
              <div v-if="project.topology_image" class="rounded-lg overflow-hidden border" style="border-color: var(--color-border)">
                <img :src="project.topology_image" alt="改进前拓扑" class="w-full" style="max-height: 350px; object-fit: contain; background: var(--color-bg-hover)" />
              </div>
              <div v-else class="rounded-lg border border-dashed flex items-center justify-center" style="height: 200px; border-color: var(--color-border); color: var(--color-text-muted)">
                <p class="text-xs">点击上传改进前拓扑图</p>
              </div>
            </div>
            <!-- 改进后 -->
            <div>
              <div class="flex items-center justify-between mb-2">
                <span class="text-xs font-semibold px-2 py-0.5 rounded" style="background: #ECFDF5; color: #059669">改进后</span>
                <n-upload :show-file-list="false" accept="image/*" @change="(opts: any) => handleTopologyUpload(opts, 'after')">
                  <n-button size="tiny" quaternary :loading="uploadingTopoAfter" style="color: var(--color-text-muted)">
                    <template #icon><svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" /></svg></template>
                    {{ project.topology_image_after ? '更换' : '上传' }}
                  </n-button>
                </n-upload>
              </div>
              <div v-if="project.topology_image_after" class="rounded-lg overflow-hidden border" style="border-color: var(--color-border)">
                <img :src="project.topology_image_after" alt="改进后拓扑" class="w-full" style="max-height: 350px; object-fit: contain; background: var(--color-bg-hover)" />
              </div>
              <div v-else class="rounded-lg border border-dashed flex items-center justify-center" style="height: 200px; border-color: var(--color-border); color: var(--color-text-muted)">
                <p class="text-xs">点击上传改进后拓扑图</p>
              </div>
            </div>
          </div>
          <p v-if="project.topology_notes" class="text-xs mt-3" style="color: var(--color-text-muted)">{{ project.topology_notes }}</p>
        </div>
      </div>

      <!-- ═══ 双栏主体：跟进 + 信息 ═══ -->
      <div class="grid grid-cols-1 lg:grid-cols-5 gap-5">
        <!-- 左栏：跟进记录 -->
        <div class="lg:col-span-3 space-y-5">
          <div class="card overflow-hidden">
            <div class="p-4 border-b flex items-center justify-between" style="border-color: var(--color-border)">
              <h2 class="text-base font-semibold" style="color: var(--color-text-heading)">跟进记录</h2>
              <span class="text-xs px-2 py-0.5 rounded-full" style="background: var(--color-bg-hover); color: var(--color-text-muted)">{{ followUps.length }} 条</span>
            </div>
            <div class="p-4 space-y-4">
              <div class="p-3.5 rounded-lg" style="background: var(--color-bg-hover)">
                <div class="flex items-center gap-2 mb-2.5">
                  <span class="text-xs flex-shrink-0" style="color: var(--color-text-muted)">沟通方式：</span>
                  <n-select v-model:value="newFollowUpType" :options="followTypeOptions" size="small" style="width: 140px" placeholder="选择方式" />
                </div>
                <n-input v-model:value="newFollowUpContent" type="textarea" placeholder="记录跟进内容… 支持 Markdown" :autosize="{ minRows: 2, maxRows: 4 }" @keydown.enter.ctrl="submitFollowUp" />
                <div class="flex justify-between items-center mt-2.5">
                  <span class="text-xs" style="color: var(--color-text-muted)">Ctrl+Enter 快捷提交</span>
                  <n-button type="primary" size="small" @click="submitFollowUp" :loading="submittingFollowUp" :disabled="!newFollowUpContent.trim()">提交跟进</n-button>
                </div>
              </div>
              <!-- Timeline -->
              <div v-if="followUps.length === 0" class="text-center py-10">
                <svg class="w-10 h-10 mx-auto mb-3" style="color: var(--color-text-muted)" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
                <p class="text-sm" style="color: var(--color-text-muted)">暂无跟进记录</p>
              </div>
              <div v-else class="space-y-1">
                <div v-for="(item, idx) in followUps" :key="item.id || idx" class="flex gap-3">
                  <div class="flex flex-col items-center">
                    <div class="w-2.5 h-2.5 rounded-full mt-2 border-2 flex-shrink-0"
                      :style="{ background: idx === 0 ? 'var(--color-primary)' : 'var(--color-bg-surface)', borderColor: 'var(--color-primary)' }"
                    ></div>
                    <div v-if="idx < followUps.length - 1" class="w-0.5 flex-1 mt-0.5" style="background: var(--color-border)"></div>
                  </div>
                  <div class="flex-1 pb-5">
                    <div class="flex items-center gap-2 mb-1.5">
                      <span class="text-xs px-2 py-0.5 rounded font-medium" style="background: var(--color-primary-light); color: var(--color-primary)">{{ item.author || '系统' }}</span>
                      <span class="text-xs" style="color: var(--color-text-muted)">{{ formatTime(item.followed_at || item.created_at) }}</span>
                    <n-popconfirm size="tiny" @positive-click="handleDeleteFollowUp(item.id)" :style="{ marginLeft: auto }"><template #trigger><span class="text-xs cursor-pointer hover:underline" style="color: var(--color-danger); margin-left: auto">删除</span></template>确认删除此跟进？</n-popconfirm>
                    </div>
                    <div class="flex items-baseline gap-1.5">
                      <span class="text-xs px-2 py-0.5 rounded font-medium flex-shrink-0" style="background: var(--color-warning-light, #FEF3C7); color: var(--color-warning, #D97706)">{{ followTypeLabel(item.follow_type) }}</span>
                      <div class="text-sm whitespace-pre-wrap leading-relaxed flex-1" style="color: var(--color-text-secondary)" v-html="renderMarkdown(item.content)"></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 右栏：信息 + 报价摘要 -->
        <div class="lg:col-span-2 space-y-5">
          <div class="card overflow-hidden">
            <div class="p-4 border-b flex items-center gap-2" style="border-color: var(--color-border)">
              <svg class="w-4 h-4" style="color: var(--color-text-muted)" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <h2 class="text-sm font-semibold" style="color: var(--color-text-heading)">基本信息</h2>
            </div>
            <div class="p-4 space-y-3">
              <div class="flex justify-between items-center"><span class="text-xs" style="color: var(--color-text-muted)">关联客户</span><span class="text-sm font-medium" style="color: var(--color-text-primary)">{{ project.customer_name || project.customer?.name || '—' }}</span></div>
              <div class="flex justify-between items-center"><span class="text-xs" style="color: var(--color-text-muted)">负责人</span><span class="text-sm font-medium" style="color: var(--color-text-primary)">{{ project.owner || '—' }}</span></div>
              <div class="flex justify-between items-center"><span class="text-xs" style="color: var(--color-text-muted)">渠道类型</span><span class="text-sm font-medium" style="color: var(--color-text-primary)">{{ project.channel_name || '—' }}</span></div>
              <div class="flex justify-between items-center"><span class="text-xs" style="color: var(--color-text-muted)">创建时间</span><span class="text-sm font-medium" style="color: var(--color-text-primary)">{{ formatTime(project.created_at) }}</span></div>
            </div>
          </div>

          <!-- 渠道信息 -->
          <div class="card overflow-hidden" v-if="project.channel_name">
            <div class="p-4 border-b flex items-center gap-2" style="border-color: var(--color-border)">
              <svg class="w-4 h-4" style="color: var(--color-text-muted)" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              <h2 class="text-sm font-semibold" style="color: var(--color-text-heading)">渠道信息</h2>
            </div>
            <div class="p-4 space-y-3">
              <div class="flex justify-between items-center"><span class="text-xs" style="color: var(--color-text-muted)">渠道名称</span><span class="text-sm font-medium" style="color: var(--color-text-primary)">{{ project.channel_name }}</span></div>
              <div v-if="project.channel_type" class="flex justify-between items-center"><span class="text-xs" style="color: var(--color-text-muted)">渠道类型</span><span class="text-sm font-medium tag tag-blue text-xs">{{ project.channel_type }}</span></div>
              <div v-if="project.channel_contact" class="flex justify-between items-center"><span class="text-xs" style="color: var(--color-text-muted)">联系人</span><span class="text-sm font-medium" style="color: var(--color-text-primary)">{{ project.channel_contact }}</span></div>
              <div v-if="project.channel_phone" class="flex justify-between items-center"><span class="text-xs" style="color: var(--color-text-muted)">联系电话</span><span class="text-sm font-medium" style="color: var(--color-text-primary)">{{ project.channel_phone }}</span></div>
            </div>
          </div>

          <!-- 报价摘要 -->
          <div class="card overflow-hidden">
            <div class="p-4 border-b flex items-center justify-between" style="border-color: var(--color-border)">
              <div class="flex items-center gap-2">
                <svg class="w-4 h-4" style="color: var(--color-text-muted)" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                </svg>
                <h2 class="text-sm font-semibold" style="color: var(--color-text-heading)">报价摘要</h2>
              </div>
              <span class="text-xs px-2 py-0.5 rounded-full" style="background: var(--color-bg-hover); color: var(--color-text-muted)">{{ quotationItems.length }} 项</span>
            </div>
            <div class="p-4">
              <div v-if="quotationItems.length === 0" class="text-center py-6">
                <p class="text-sm" style="color: var(--color-text-muted)">暂无报价 — 在下方上传 Excel</p>
              </div>
              <div v-else class="space-y-2.5">
                <div v-for="(item, i) in quotationItems" :key="i" class="flex justify-between items-center text-sm">
                  <div class="min-w-0 flex-1">
                    <p class="truncate font-medium" style="color: var(--color-text-primary)">{{ item[0] || '未命名' }}</p>
                    <p class="text-xs truncate" style="color: var(--color-text-muted)">{{ item[1] || '' }} · ×{{ item[2] || 0 }}</p>
                  </div>
                  <span class="font-semibold ml-3 flex-shrink-0" style="color: var(--color-text-heading)">{{ formatAmount(parseFloat(item[item.length-1] || 0)) }}</span>
                </div>
                <div class="pt-2 mt-1 border-t flex justify-between items-center" style="border-color: var(--color-border)">
                  <span class="text-sm font-semibold" style="color: var(--color-text-heading)">合计</span>
                  <span class="text-lg font-bold" style="color: var(--color-danger)">{{ formatAmount(quotationTotal) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ═══ 报价明细：Excel 上传 + 预览 ═══ -->
      <div class="card overflow-hidden">
        <div class="p-4 border-b flex items-center justify-between" style="border-color: var(--color-border)">
          <div class="flex items-center gap-2">
            <svg class="w-4 h-4" style="color: var(--color-text-muted)" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <h2 class="text-base font-semibold" style="color: var(--color-text-heading)">报价明细</h2>
          </div>
          <div class="flex items-center gap-2">
            <n-upload
              :show-file-list="false"
              accept=".xlsx,.xls"
              @change="handleExcelUpload"
            >
              <n-button size="small" type="primary" ghost :loading="uploadingExcel">
                <template #icon>
                  <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
                  </svg>
                </template>
                上传 Excel
              </n-button>
            </n-upload>
            <n-button v-if="excelAttId" size="small" @click="clearExcel" style="color: var(--color-text-muted)">清空</n-button>
          </div>
        </div>
        <div class="p-4">
          <!-- 已保存的报价附件 -->
          <div v-if="quotationAttachments.length > 0" class="mb-3 pb-3 border-b" style="border-color: var(--color-border)">
            <div class="text-xs mb-2" style="color: var(--color-text-muted)">已保存的报价文件 ({{ quotationAttachments.length }})</div>
            <div v-for="att in quotationAttachments" :key="att.id" class="flex items-center justify-between py-1.5 px-2 rounded text-sm hover:bg-opacity-50" style="background: var(--color-bg-hover); margin-bottom: 4px">
              <div class="flex items-center gap-2 min-w-0">
                <svg class="w-3.5 h-3.5 flex-shrink-0" style="color: var(--color-success, #10B981)" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                <span class="truncate" style="color: var(--color-text-primary)">{{ att.original_name }}</span>
                <span class="text-xs flex-shrink-0" style="color: var(--color-text-muted)">{{ formatFileSize(att.file_size) }}</span>
              </div>
              <div class="flex items-center gap-1 flex-shrink-0 ml-2">
                <n-button size="tiny" text @click="previewAttachment(att.id)" :style="{ color: 'var(--color-primary)' }">预览</n-button>
                <n-button size="tiny" text @click="downloadAttachment(att.id)" :style="{ color: 'var(--color-text-muted)' }">下载</n-button>
                <n-popconfirm size="tiny" @positive-click="deleteQuotationAttachment(att.id)"><template #trigger><span class="text-xs cursor-pointer hover:underline" style="color: var(--color-danger)">删除</span></template>确认删除此附件？</n-popconfirm>
              </div>
            </div>
          </div>
          <!-- Excel Sheet 选择 -->
          <div v-if="excelSheets.length > 1" class="flex items-center gap-2 mb-3">
            <span class="text-xs" style="color: var(--color-text-muted)">Sheet:</span>
            <n-radio-group v-model:value="excelSheet" size="small" @update:value="loadExcelPreview">
              <n-radio-button v-for="s in excelSheets" :key="s" :value="s" :label="s" />
            </n-radio-group>
          </div>
          <!-- 表格预览 -->
          <div v-if="excelHeaders.length > 0 && excelRows.length > 0" class="overflow-x-auto">
            <table class="w-full border-collapse text-sm">
              <thead>
                <tr style="background: var(--color-bg-hover)">
                  <th class="text-left py-2 px-3 text-xs font-semibold uppercase" style="color: var(--color-text-muted)" v-for="(h, hi) in excelHeaders" :key="hi">{{ h }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(row, ri) in excelRows" :key="ri" class="border-b" :style="{ borderColor: 'var(--color-border)', background: ri % 2 === 0 ? 'var(--color-bg-surface)' : 'var(--color-bg-hover)' }">
                  <td class="py-1.5 px-3" style="color: var(--color-text-secondary)" v-for="(cell, ci) in row" :key="ci">{{ cell }}</td>
                </tr>
              </tbody>
            </table>
            <p class="text-xs mt-2" style="color: var(--color-text-muted)">共 {{ excelRows.length }} 行 · 文件: {{ excelFileName }}</p>
          </div>
          <!-- 空状态 -->
          <div v-if="!excelAttId" class="text-center py-8">
            <svg class="w-10 h-10 mx-auto mb-2" style="color: var(--color-text-muted)" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <p class="text-sm" style="color: var(--color-text-muted)">上传 Excel 报价单（.xlsx）自动解析并预览</p>
            <p class="text-xs mt-1" style="color: var(--color-text-muted)">支持多 Sheet，自动识别表头</p>
          </div>
          <div v-if="excelError" class="mt-2 p-2 rounded text-xs" style="background: #FEF2F2; color: #DC2626">{{ excelError }}</div>
        </div>
      </div>
    </template>

    <!-- ═══ 编辑弹窗 ═══ -->
    <n-modal v-model:show="showEditModal" :mask-closable="false" preset="card" title="编辑项目" style="max-width: 680px; max-height: 80vh" :style="{ width: '92%', overflow: 'auto' }">
      <n-form ref="editFormRef" :model="editForm" :rules="formRules" label-placement="left" label-width="80">
        <n-form-item label="项目名称" path="name">
          <n-input v-model:value="editForm.name" placeholder="请输入项目名称" />
        </n-form-item>
        <n-form-item label="项目金额" path="amount">
          <n-input-number v-model:value="editForm.amount" placeholder="请输入金额" :min="0" :style="{ width: '100%' }" />
        </n-form-item>
        <n-form-item label="项目阶段" path="stage">
          <n-select v-model:value="editForm.stage" :options="stageSelectOptions" placeholder="选择阶段" />
        </n-form-item>
        <n-form-item label="关联渠道">
          <n-select v-model:value="editForm.channel_id" :options="channelOptions" placeholder="选择渠道" clearable filterable />
        </n-form-item>
        <n-form-item label="负责人">
          <n-input v-model:value="editForm.owner" placeholder="负责人姓名" />
        </n-form-item>
        <n-divider style="margin: 8px 0; color: var(--color-text-muted); font-size: 12px">项目详情</n-divider>
        <n-form-item label="客户背景">
          <n-input v-model:value="editForm.customer_background" type="textarea" placeholder="客户公司背景、行业地位、IT现状等" :autosize="{ minRows: 2, maxRows: 4 }" />
        </n-form-item>
        <n-form-item label="需求分析">
          <n-input v-model:value="editForm.customer_requirement" type="textarea" placeholder="客户痛点、核心需求、预算范围等" :autosize="{ minRows: 2, maxRows: 4 }" />
        </n-form-item>
        <n-form-item label="方案描述">
          <n-input v-model:value="editForm.solution_description" type="textarea" placeholder="解决方案概述、技术架构、部署方案等" :autosize="{ minRows: 2, maxRows: 6 }" />
        </n-form-item>
        <n-form-item label="方案价值">
          <n-input v-model:value="editForm.solution_value" type="textarea" placeholder="为客户创造的价值、ROI分析等" :autosize="{ minRows: 2, maxRows: 4 }" />
        </n-form-item>
        <n-form-item label="竞品分析">
          <n-input v-model:value="editForm.competitor_info" type="textarea" placeholder="竞争对手情况、优劣势对比等" :autosize="{ minRows: 2, maxRows: 4 }" />
        </n-form-item>
        <n-form-item label="拓扑说明">
          <n-input v-model:value="editForm.topology_notes" type="textarea" placeholder="拓扑图说明文字" :autosize="{ minRows: 1, maxRows: 3 }" />
        </n-form-item>
      </n-form>
      <template #footer>
        <div class="flex justify-end gap-3">
          <n-button @click="showEditModal = false">取消</n-button>
          <n-popconfirm @positive-click="handleDelete"><template #trigger><n-button type="error" :loading="deleting">删除</n-button></template>确定删除此项目？此操作不可撤销。</n-popconfirm>
          <n-button type="primary" @click="handleEditSubmit" :loading="submitting">保存</n-button>
        </div>
      </template>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  NButton, NTag, NInput, NInputNumber, NSelect, NUpload,
  NModal, NForm, NFormItem, NSpin, NDivider, NRadioGroup, NRadioButton, NPopconfirm
} from 'naive-ui'
import {
  getProject, updateProject, deleteProject,
  getFollowUps, createFollowUp, deleteFollowUp,
  uploadAttachment, getAttachments, deleteAttachment,
  getChannels, uploadTopology
} from '../api'
import api from '../api'

interface Project {
  id: number
  name: string
  customer_name?: string
  customer?: { name: string }
  amount?: number
  stage: string
  channel_name?: string
  channel_type?: string
  channel_contact?: string
  channel_phone?: string
  channel?: { name: string }
  owner?: string
  customer_background?: string
  customer_requirement?: string
  solution_description?: string
  solution_value?: string
  competitor_info?: string
  topology_image?: string
  topology_image_after?: string
  topology_notes?: string
  project_progress?: string
  created_at?: string
  updated_at?: string
}

interface FollowUp {
  id?: number
  content: string
  author?: string
  follow_type?: string
  followed_at?: string
  created_at?: string
}

const route = useRoute()
const router = useRouter()
const message = { error: (msg: string) => console.error('[CRM]', msg), success: (msg: string) => console.log('[CRM]', msg) }

const loading = ref(false)
const submitting = ref(false)
const submittingFollowUp = ref(false)
const deleting = ref(false)
const project = ref<Project | null>(null)
const followUps = ref<FollowUp[]>([])
const newFollowUpContent = ref('')
const newFollowUpType = ref('电话')
const showEditModal = ref(false)

const editForm = ref<Record<string, any>>({
  name: '', amount: null, stage: '', channel_id: null as number | null, owner: '',
  customer_background: '', customer_requirement: '', solution_description: '',
  solution_value: '', competitor_info: '', topology_notes: ''
})

const editFormRef = ref<any>(null)
const formRules = {
  name: [{ required: true, message: '请输入项目名称', trigger: 'blur' }],
}

// Excel quotation state
const uploadingExcel = ref(false)
const excelAttId = ref<number | null>(null)
const excelFileName = ref('')
const excelSheets = ref<string[]>([])
const excelSheet = ref('')
const excelHeaders = ref<string[]>([])
const excelRows = ref<string[][]>([])
const excelError = ref('')
const quotationAttachments = ref<any[]>([])  // saved quotation files
const uploadingTopoBefore = ref(false)
const uploadingTopoAfter = ref(false)
const channels = ref<{id: number, name: string, type: string}[]>([])
const channelOptions = computed(() => channels.value.map(c => ({ label: `${c.name} (${c.type})`, value: c.id })))

const productPrices: Record<string, number> = {
  '云安全管理平台': 185000, '超融合一体机': 320000, '数据备份恢复系统': 156000,
  'SD-WAN 网关': 28000, '下一代防火墙': 45000, '堡垒机': 38000,
  '数据库审计系统': 52000, '日志审计平台': 42000, '终端检测与响应': 18500,
  '零信任访问网关': 65000,
}

const quotationItems = computed(() => {
  if (excelRows.value.length > 0) return excelRows.value
  // Auto-generate from project.product_names with realistic pricing
  const names = project.value?.product_names || []
  if (names.length === 0) return []
  return names.map((name, i) => {
    const qty = i === 0 ? 2 : 1  // First product gets 2 units for realism
    const unitPrice = productPrices[name] || 50000
    const subtotal = unitPrice * qty
    return [name, `¥${(unitPrice/10000).toFixed(1)}万/套`, String(qty), String(subtotal.toFixed(2))]
  })
})

const quotationTotal = computed(() => {
  if (excelHeaders.value.length === 0 && excelRows.value.length === 0) {
    // Auto-calculate from product names
    return quotationItems.value.reduce((sum, row) => {
      const v = parseFloat(row[row.length - 1] || '0')
      return sum + (isNaN(v) ? 0 : v)
    }, 0)
  }
  if (excelHeaders.value.length === 0 || excelRows.value.length === 0) return 0
  const lastCol = excelHeaders.value.length - 1
  return excelRows.value.reduce((sum, row) => {
    const v = parseFloat(row[lastCol] || '0')
    return sum + (isNaN(v) ? 0 : v)
  }, 0)
})

const stageSteps = [
  { key: '线索', label: '线索' },
  { key: '需求确认', label: '需求确认' },
  { key: '方案报价', label: '方案报价' },
  { key: '商务谈判', label: '商务谈判' },
  { key: '已签约', label: '已签约' },
]

const stageSelectOptions = [
  { label: '线索', value: '线索' },
  { label: '需求确认', value: '需求确认' },
  { label: '方案报价', value: '方案报价' },
  { label: '商务谈判', value: '商务谈判' },
  { label: '已签约', value: '已签约' },
  { label: '丢单', value: '丢单' },
]

const stageColors: Record<string, string> = {
  '线索': '#3B82F6', '需求确认': '#F59E0B', '方案报价': '#8B5CF6',
  '商务谈判': '#EF4444', '已签约': '#10B981', '丢单': '#6B7280',
}

const stageTypeMap: Record<string, 'default' | 'info' | 'success' | 'warning' | 'error'> = {
  '线索': 'info', '需求确认': 'warning', '方案报价': 'info',
  '商务谈判': 'warning', '已签约': 'success', '丢单': 'error',
}

const stageOrder = ['线索', '需求确认', '方案报价', '商务谈判', '已签约']

const followTypeLabels: Record<string, string> = {
  电话: '📞 电话', 微信: '💬 微信', 线上会议: '🎥 线上会议', 线下会面: '🤝 线下会面', 邮件: '📧 邮件', 其他: '📝 其他',
  call: '📞 电话', meeting: '🎥 线上会议', email: '📧 邮件', note: '📝 记录',
}

const followTypeOptions = [
  { label: '📞 电话', value: '电话' },
  { label: '💬 微信', value: '微信' },
  { label: '🎥 线上会议', value: '线上会议' },
  { label: '🤝 线下会面', value: '线下会面' },
  { label: '📧 邮件', value: '邮件' },
  { label: '📝 其他', value: '其他' },
]

function stageIndex(stage?: string): number {
  if (!stage) return -1
  const idx = stageOrder.indexOf(stage)
  return idx >= 0 ? Math.min(idx, 4) : -1
}

function stageColor(stage?: string): string {
  return stageColors[stage || ''] || '#6B7280'
}

function stageLabel(stage?: string): string {
  return stage || '未知'
}

function stageType(stage?: string): 'default' | 'info' | 'success' | 'warning' | 'error' {
  return stageTypeMap[stage || ''] || 'default'
}

function followTypeLabel(t?: string): string {
  return followTypeLabels[t || ''] || t || '记录'
}

const projectDays = computed(() => {
  if (!project.value) return '—'
  const created = project.value.created_at
  if (!created) return '—'
  try {
    const diff = Date.now() - new Date(created).getTime()
    return Math.max(1, Math.ceil(diff / (1000 * 60 * 60 * 24)))
  } catch { return '—' }
})

function formatAmount(amount?: number): string {
  if (!amount && amount !== 0) return '—'
  if (amount >= 10000) return `¥${(amount / 10000).toFixed(1)}万`
  return `¥${amount.toLocaleString()}`
}

function formatTime(t?: string): string {
  if (!t) return '—'
  try {
    return new Date(t).toLocaleString('zh-CN', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
  } catch { return t }
}

function renderMarkdown(text: string): string {
  if (!text) return ''
  return text
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    .replace(/`(.+?)`/g, '<code>$1</code>')
    .replace(/\\n/g, '<br>')
}

// Excel upload
async function handleExcelUpload(options: { file: { file?: File } }) {
  const file = options.file?.file
  if (!file) return
  uploadingExcel.value = true
  excelError.value = ''
  try {
    const pid = Number(route.params.id)
    const res = await api.post(
      `/projects/${pid}/attachments`,
      (() => { const fd = new FormData(); fd.append('file', file); fd.append('attachment_type', 'quotation'); return fd })(),
      { headers: { 'Content-Type': 'multipart/form-data' } }
    )
    const att = res.data
    excelAttId.value = att.id
    excelFileName.value = file.name
    // Refresh saved attachments list
    const pid2 = Number(route.params.id)
    const attRes = await getAttachments(pid2, 'quotation')
    const atts = attRes.data?.data ?? attRes.data ?? []
    quotationAttachments.value = Array.isArray(atts) ? atts : []
    await loadExcelPreview()
  } catch (err: any) {
    excelError.value = '上传失败: ' + (err.response?.data?.detail || err.message || '未知错误')
  } finally {
    uploadingExcel.value = false
  }
}

async function loadExcelPreview() {
  if (!excelAttId.value) return
  try {
    const pid = Number(route.params.id)
    const params = excelSheet.value ? { sheet: excelSheet.value } : {}
    const res = await api.get(`/projects/${pid}/attachments/${excelAttId.value}/excel-preview`, { params })
    const data = res.data
    excelSheets.value = data.sheets || []
    excelSheet.value = data.current_sheet || (data.sheets?.[0] || '')
    excelHeaders.value = data.headers || []
    excelRows.value = data.rows || []
    if (data.truncated) excelError.value = 'Excel 行数较多，仅显示前 100 行预览'
  } catch (err: any) {
    excelError.value = '解析失败: ' + (err.response?.data?.detail || err.message || '')
    excelHeaders.value = []
    excelRows.value = []
  }
}

async function handleTopologyUpload(opts: any, type: 'before' | 'after') {
  const file = opts.file?.file
  if (!file) return
  const pid = Number(route.params.id)
  if (type === 'before') {
    uploadingTopoBefore.value = true
    try {
      const res = await uploadTopology(pid, file)
      project.value = { ...project.value!, topology_image: res.data?.url || res.data?.data?.url }
      message.success('拓扑图(改进前)已上传')
    } catch (err: any) {
      message.error('上传失败: ' + (err.response?.data?.detail || err.message || '未知错误'))
    } finally { uploadingTopoBefore.value = false }
  } else {
    uploadingTopoAfter.value = true
    try {
      const res = await api.post(`/projects/${pid}/topology/after`, (() => { const fd = new FormData(); fd.append('file', file); return fd })(), { headers: { 'Content-Type': 'multipart/form-data' } })
      project.value = { ...project.value!, topology_image_after: res.data?.url || res.data?.data?.url }
      message.success('拓扑图(改进后)已上传')
    } catch (err: any) {
      message.error('上传失败: ' + (err.response?.data?.detail || err.message || '未知错误'))
    } finally { uploadingTopoAfter.value = false }
  }
}

function clearExcel() {
  excelAttId.value = null
  excelFileName.value = ''
  excelSheets.value = []
  excelSheet.value = ''
  excelHeaders.value = []
  excelRows.value = []
  excelError.value = ''
}

// Load existing quotation attachment from project
async function loadExistingQuotation() {
  try {
    const pid = Number(route.params.id)
    const res = await getAttachments(pid, 'quotation')
    const atts = res.data?.data ?? res.data ?? []
    quotationAttachments.value = Array.isArray(atts) ? atts : []
    if (Array.isArray(atts) && atts.length > 0) {
      const att = atts[0]
      excelAttId.value = att.id
      excelFileName.value = att.original_name
      await loadExcelPreview()
    }
  } catch { /* no quotation yet */ }
}

async function deleteQuotationAttachment(attId: number) {
  try {
    const pid = Number(route.params.id)
    await deleteAttachment(pid, attId)
    quotationAttachments.value = quotationAttachments.value.filter(a => a.id !== attId)
    if (excelAttId.value === attId) {
      excelAttId.value = null
      excelFileName.value = ''
      excelHeaders.value = []
      excelRows.value = []
      excelSheets.value = []
    }
    message.success('附件已删除')
  } catch (err: any) {
    message.error('删除失败: ' + (err.response?.data?.detail || err.message))
  }
}

async function previewAttachment(attId: number) {
  excelAttId.value = attId
  const att = quotationAttachments.value.find(a => a.id === attId)
  if (att) excelFileName.value = att.original_name
  await loadExcelPreview()
}

function downloadAttachment(attId: number) {
  const pid = Number(route.params.id)
  window.open(`/api/v1/presales/projects/${pid}/attachments/${attId}/file`, '_blank')
}

function formatFileSize(bytes: number): string {
  if (!bytes) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB']
  let i = 0
  let size = bytes
  while (size >= 1024 && i < units.length - 1) { size /= 1024; i++ }
  return size.toFixed(i === 0 ? 0 : 1) + ' ' + units[i]
}

async function fetchProject() {
  loading.value = true
  try {
    const id = Number(route.params.id)
    const [projRes, followUpRes] = await Promise.all([
      getProject(id),
      getFollowUps(id),
    ])
    const projData = projRes.data?.data ?? projRes.data
    project.value = projData
    // Restore channel_id for edit form
    if (projData?.channel_id) {
      editForm.value.channel_id = projData.channel_id
    }
    followUps.value = followUpRes.data?.data ?? followUpRes.data ?? []
    await loadExistingQuotation()
  } catch (err: any) {
    message.error('加载项目详情失败: ' + (err.message || '未知错误'))
    router.push('/work/projects')
  } finally {
    loading.value = false
  }
}

async function submitFollowUp() {
  if (!newFollowUpContent.value.trim()) return
  submittingFollowUp.value = true
  try {
    const id = Number(route.params.id)
    await createFollowUp(id, { content: newFollowUpContent.value.trim(), follow_type: newFollowUpType.value })
    newFollowUpContent.value = ''
    newFollowUpType.value = '电话'
    message.success('跟进记录已添加')
    const followUpRes = await getFollowUps(id)
    followUps.value = followUpRes.data?.data ?? followUpRes.data ?? []
  } catch (err: any) {
    message.error('提交失败: ' + (err.response?.data?.detail || err.message || '未知错误'))
  } finally {
    submittingFollowUp.value = false
  }
}

function openEditModal() {
  if (!project.value) return
  editForm.value = {
    name: project.value.name,
    amount: project.value.amount ?? null,
    stage: project.value.stage,
    channel_id: (project.value as any).channel_id ?? null,
    owner: project.value.owner || '',
    customer_background: project.value.customer_background || '',
    customer_requirement: project.value.customer_requirement || '',
    solution_description: project.value.solution_description || '',
    solution_value: project.value.solution_value || '',
    competitor_info: project.value.competitor_info || '',
    topology_notes: project.value.topology_notes || '',
  }
  showEditModal.value = true
}

async function handleEditSubmit() {
  try { await editFormRef.value?.validate() } catch { return }
  submitting.value = true
  try {
    const id = Number(route.params.id)
    await updateProject(id, {
      name: editForm.value.name,
      amount: editForm.value.amount ?? undefined,
      stage: editForm.value.stage,
      channel_id: editForm.value.channel_id ?? undefined,
      owner: editForm.value.owner,
      customer_background: editForm.value.customer_background,
      customer_requirement: editForm.value.customer_requirement,
      solution_description: editForm.value.solution_description,
      solution_value: editForm.value.solution_value,
      competitor_info: editForm.value.competitor_info,
      topology_notes: editForm.value.topology_notes,
    })
    message.success('项目已更新')
    showEditModal.value = false
    await fetchProject()
  } catch (err: any) {
    message.error('更新失败: ' + (err.response?.data?.detail || err.message || '未知错误'))
  } finally {
    submitting.value = false
  }
}

async function handleDelete() {
  deleting.value = true
  try {
    const id = Number(route.params.id)
    await deleteProject(id)
    message.success('项目已删除')
    router.push('/work/projects')
  } catch (err: any) {
    message.error('删除失败: ' + (err.response?.data?.detail || err.message || '未知错误'))
  } finally {
    deleting.value = false
  }
}

async function handleDeleteFollowUp(fuId: number | undefined) {
  if (!fuId) return
  try {
    const pid = Number(route.params.id)
    await deleteFollowUp(pid, fuId)
    message.success('跟进已删除')
    const followUpRes = await getFollowUps(pid)
    followUps.value = followUpRes.data?.data ?? followUpRes.data ?? []
  } catch (err: any) {
    message.error('删除失败: ' + (err.response?.data?.detail || err.message || '未知错误'))
  }
}

async function fetchChannels() {
  try {
    const res = await getChannels()
    channels.value = res.data?.data ?? res.data ?? []
  } catch { /* channels load silently */ }
}

onMounted(() => { fetchProject(); fetchChannels() })
</script>