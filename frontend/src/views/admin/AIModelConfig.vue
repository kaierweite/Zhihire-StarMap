<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Brain, Sparkles, Key, Server, Gauge, CheckCircle, XCircle, RefreshCw,
  Save, Plus, Trash2, Eye, EyeOff, Zap, Power, PowerOff,
} from 'lucide-vue-next'
import {
  listAiProviders, createAiProvider, updateAiProvider,
  testAiProvider, deleteAiProvider,
} from '@/api/admin'
import type { AiProviderItem, AiProviderCreateRequest, AiProviderUpdateRequest } from '@/types/admin'

const providers = ref<AiProviderItem[]>([])
const loading = ref(false)
const activeId = ref<number | null>(null)
const testingId = ref<number | null>(null)
const showKeyId = ref<Set<number>>(new Set())

// --- Create/Edit dialog ---
const dialogVisible = ref(false)
const dialogMode = ref<'create' | 'edit'>('create')
const editId = ref<number | null>(null)
const form = ref({
  provider_name: '',
  display_name: '',
  api_key: '',
  base_url: '',
  models: '',
  order_no: 0,
})

const activeProvider = computed(() =>
  providers.value.find(p => p.id === activeId.value) || null
)

// --- Selected provider edit fields ---
const editForm = ref({
  display_name: '',
  api_key: '',
  base_url: '',
  models: '',
  order_no: 0,
})

async function fetchProviders() {
  loading.value = true
  try {
    const res = await listAiProviders()
    providers.value = res.data.data
    if (res.data.data.length > 0 && !activeId.value) {
      activeId.value = res.data.data[0].id
      loadEditForm(res.data.data[0])
    }
  } catch {
    // handled by interceptor
  } finally {
    loading.value = false
  }
}

function loadEditForm(p: AiProviderItem) {
  activeId.value = p.id
  editForm.value = {
    display_name: p.display_name,
    api_key: '',
    base_url: p.base_url || '',
    models: (p.models || []).join(', '),
    order_no: p.order_no,
  }
}

function onSelectProvider(p: AiProviderItem) {
  loadEditForm(p)
  showKeyId.value.delete(p.id)
}

// --- Create provider dialog ---
function openCreate() {
  dialogMode.value = 'create'
  editId.value = null
  form.value = { provider_name: '', display_name: '', api_key: '', base_url: '', models: '', order_no: 0 }
  dialogVisible.value = true
}

function openEditProvider() {
  if (!activeProvider.value) return
  const p = activeProvider.value
  dialogMode.value = 'edit'
  editId.value = p.id
  form.value = {
    provider_name: p.provider_name,
    display_name: p.display_name,
    api_key: '',
    base_url: p.base_url || '',
    models: (p.models || []).join(', '),
    order_no: p.order_no,
  }
  dialogVisible.value = true
}

async function submitForm() {
  const modelsList = form.value.models.split(',').map(s => s.trim()).filter(Boolean)
  if (dialogMode.value === 'create') {
    const data: AiProviderCreateRequest = {
      provider_name: form.value.provider_name,
      display_name: form.value.display_name,
      api_key: form.value.api_key || undefined,
      base_url: form.value.base_url || undefined,
      models: modelsList.length > 0 ? modelsList : undefined,
      order_no: form.value.order_no || undefined,
    }
    try {
      await createAiProvider(data)
      ElMessage.success('AI 提供商已创建')
      dialogVisible.value = false
      await fetchProviders()
    } catch {
      // handled by interceptor
    }
  } else if (editId.value !== null) {
    const data: AiProviderUpdateRequest = {}
    if (form.value.display_name) data.display_name = form.value.display_name
    if (form.value.api_key) data.api_key = form.value.api_key
    if (form.value.base_url) data.base_url = form.value.base_url
    if (modelsList.length > 0) data.models = modelsList
    if (form.value.order_no) data.order_no = form.value.order_no
    try {
      await updateAiProvider(editId.value, data)
      ElMessage.success('AI 提供商已更新')
      dialogVisible.value = false
      await fetchProviders()
    } catch {
      // handled by interceptor
    }
  }
}

// --- Inline save ---
async function handleSave() {
  if (!activeProvider.value) return
  const p = activeProvider.value
  const modelsList = editForm.value.models.split(',').map(s => s.trim()).filter(Boolean)
  const data: AiProviderUpdateRequest = {}
  if (editForm.value.display_name !== p.display_name) data.display_name = editForm.value.display_name
  if (editForm.value.api_key) data.api_key = editForm.value.api_key
  if (editForm.value.base_url !== (p.base_url || '')) data.base_url = editForm.value.base_url || undefined
  const origModels = (p.models || []).join(', ')
  if (editForm.value.models !== origModels) data.models = modelsList
  if (editForm.value.order_no !== p.order_no) data.order_no = editForm.value.order_no
  if (Object.keys(data).length === 0) {
    ElMessage.info('没有需要修改的字段')
    return
  }
  try {
    await updateAiProvider(p.id, data)
    ElMessage.success('配置已保存')
    await fetchProviders()
    // Reload edit form with fresh data
    const updated = providers.value.find(x => x.id === p.id)
    if (updated) loadEditForm(updated)
  } catch {
    // handled by interceptor
  }
}

// --- Test connection ---
async function handleTest(id: number) {
  testingId.value = id
  try {
    const res = await testAiProvider(id)
    const r = res.data.data
    if (r.success) {
      ElMessage.success(`${r.message}${r.latency_ms != null ? ` (${r.latency_ms}ms)` : ''}`)
    } else {
      ElMessage.warning(r.message)
    }
  } catch {
    // handled by interceptor
  } finally {
    testingId.value = null
  }
}

// --- Toggle status ---
async function handleToggleStatus(p: AiProviderItem) {
  const newStatus = p.status === 'NORMAL' ? 'DISABLED' : 'NORMAL'
  const actionText = newStatus === 'DISABLED' ? '禁用' : '启用'
  try {
    await ElMessageBox.confirm(`确认${actionText}提供商「${p.display_name}」？`, '确认操作', {
      type: 'warning',
      confirmButtonText: actionText,
      cancelButtonText: '取消',
    })
    await updateAiProvider(p.id, { status: newStatus })
    ElMessage.success(`已${actionText}「${p.display_name}」`)
    await fetchProviders()
    const updated = providers.value.find(x => x.id === p.id)
    if (updated) activeId.value = updated.id
  } catch {
    // cancelled
  }
}

// --- Delete ---
async function handleDelete(p: AiProviderItem) {
  try {
    await ElMessageBox.confirm(
      `确认删除提供商「${p.display_name}」？此操作不可撤销。`,
      '确认删除',
      { confirmButtonText: '删除', type: 'warning', cancelButtonText: '取消' }
    )
    await deleteAiProvider(p.id)
    ElMessage.success('已删除')
    await fetchProviders()
    if (activeId.value === p.id) {
      activeId.value = providers.value.length > 0 ? providers.value[0].id : null
      if (activeId.value) {
        const next = providers.value.find(x => x.id === activeId.value)
        if (next) loadEditForm(next)
      }
    }
  } catch {
    // cancelled
  }
}

// --- Utility ---
function maskKey(key: string | null): string {
  if (!key || key.length < 8) return key || ''
  return key.slice(0, 6) + '****' + key.slice(-4)
}

function statusLabel(s: string) {
  return s === 'NORMAL' ? '已启用' : '已禁用'
}

function statusClass(s: string) {
  return s === 'NORMAL' ? 'st-ok' : 'st-err'
}

onMounted(fetchProviders)
</script>

<template>
  <div class="ai-config-page">
    <div class="page-header fade-up">
      <div>
        <h1>大模型配置</h1>
        <p>管理云端 AI 模型提供商、API Key 和模型参数</p>
      </div>
      <div class="header-actions">
        <button class="refresh-btn" :disabled="loading" @click="fetchProviders">
          <RefreshCw :size="14" :class="{ spinning: loading }" />
          {{ loading ? '刷新中...' : '刷新' }}
        </button>
        <button class="add-btn" @click="openCreate"><Plus :size="15" /> 新增提供商</button>
      </div>
    </div>

    <div class="config-layout">
      <!-- Left: Provider list -->
      <div class="provider-list fade-up d1">
        <div
          v-for="p in providers" :key="p.id"
          class="provider-item"
          :class="{ active: activeId === p.id, disabled: p.status === 'DISABLED' }"
          @click="onSelectProvider(p)"
        >
          <div class="pi-left">
            <div class="pi-icon" :class="{ enabled: p.status === 'NORMAL' }">
              <Brain :size="18" />
            </div>
            <div class="pi-info">
              <h3>{{ p.display_name }}</h3>
              <span class="pi-status" :class="statusClass(p.status)">{{ statusLabel(p.status) }}</span>
            </div>
          </div>
          <el-switch
            :model-value="p.status === 'NORMAL'"
            size="small"
            @click.stop
            @change="handleToggleStatus(p)"
          />
        </div>
      </div>

      <!-- Right: Config form -->
      <div class="config-form fade-up d2">
        <div v-if="!activeProvider" class="empty-hint">
          <Brain :size="48" class="empty-icon" />
          <p>请选择或新建一个 AI 提供商</p>
        </div>

        <template v-else>
          <div class="form-header">
            <h2>{{ activeProvider.display_name }}</h2>
            <div class="form-header-actions">
              <button class="test-btn" :disabled="testingId === activeProvider.id" @click="handleTest(activeProvider.id)">
                <RefreshCw :size="14" :class="{ spinning: testingId === activeProvider.id }" />
                {{ testingId === activeProvider.id ? '测试中...' : '测试连接' }}
              </button>
              <button class="edit-btn" @click="openEditProvider"><Edit :size="14" /></button>
              <button class="danger-btn" @click="handleDelete(activeProvider)"><Trash2 :size="14" /></button>
            </div>
          </div>

          <!-- Basic info -->
          <div class="form-section">
            <h3><Zap :size="16" /> 基本信息</h3>
            <div class="form-grid">
              <label>
                <span>提供商名称</span>
                <input :value="activeProvider.provider_name" disabled class="input-readonly" />
              </label>
              <label>
                <span>显示名称</span>
                <input v-model="editForm.display_name" placeholder="如：DeepSeek" />
              </label>
            </div>
          </div>

          <!-- API Key -->
          <div class="form-section">
            <h3><Key :size="16" /> API Key</h3>
            <div class="key-row">
              <input
                :type="showKeyId.has(activeProvider.id) ? 'text' : 'password'"
                :value="showKeyId.has(activeProvider.id) ? editForm.api_key || activeProvider.api_key || '' : maskKey(activeProvider.api_key)"
                @input="editForm.api_key = ($event.target as HTMLInputElement).value"
                placeholder="sk-..."
                class="key-input"
              />
              <button class="eye-btn" @click="showKeyId.has(activeProvider.id) ? showKeyId.delete(activeProvider.id) : showKeyId.add(activeProvider.id)">
                <component :is="showKeyId.has(activeProvider.id) ? EyeOff : Eye" :size="16" />
              </button>
            </div>
            <p class="form-hint">API Key 将加密存储，仅用于服务端调用。留空则保留原有密钥。</p>
          </div>

          <!-- Base URL -->
          <div class="form-section">
            <h3><Server :size="16" /> 基础配置</h3>
            <div class="form-grid">
              <label>
                <span>Base URL</span>
                <input v-model="editForm.base_url" placeholder="https://api.example.com/v1" />
              </label>
              <label>
                <span>排序号</span>
                <input v-model.number="editForm.order_no" type="number" min="0" />
              </label>
            </div>
          </div>

          <!-- Models -->
          <div class="form-section">
            <h3><Zap :size="16" /> 可用模型</h3>
            <el-input
              v-model="editForm.models"
              placeholder="deepseek-chat, deepseek-coder（逗号分隔）"
              :rows="2"
              type="textarea"
            />
            <p class="form-hint">多个模型用逗号分隔，如：gpt-4o, gpt-4o-mini</p>
            <div class="model-tags" v-if="activeProvider.models && activeProvider.models.length > 0">
              <span v-for="m in activeProvider.models" :key="m" class="model-tag">{{ m }}</span>
            </div>
          </div>

          <!-- Save -->
          <div class="form-actions">
            <button class="save-btn" @click="handleSave"><Save :size="14" /> 保存配置</button>
          </div>
        </template>
      </div>
    </div>

    <!-- Create/Edit dialog -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogMode === 'create' ? '新增 AI 提供商' : '编辑 AI 提供商'"
      width="500px"
    >
      <el-form :model="form" label-width="110px">
        <el-form-item label="提供商名称" required v-if="dialogMode === 'create'">
          <el-input v-model="form.provider_name" placeholder="如：deepseek" />
        </el-form-item>
        <el-form-item label="显示名称" required>
          <el-input v-model="form.display_name" placeholder="如：DeepSeek" />
        </el-form-item>
        <el-form-item label="API Key" v-if="dialogMode === 'create'">
          <el-input v-model="form.api_key" placeholder="sk-..." type="password" show-password />
        </el-form-item>
        <el-form-item label="API Key" v-else>
          <el-input v-model="form.api_key" placeholder="留空则保留原有密钥" type="password" show-password />
        </el-form-item>
        <el-form-item label="Base URL">
          <el-input v-model="form.base_url" placeholder="https://api.example.com/v1" />
        </el-form-item>
        <el-form-item label="可用模型">
          <el-input v-model="form.models" placeholder="逗号分隔，如：gpt-4o, gpt-4o-mini" />
        </el-form-item>
        <el-form-item label="排序号">
          <el-input-number v-model="form.order_no" :min="0" controls-position="right" style="width:100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm">
          {{ dialogMode === 'create' ? '创建' : '保存' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped lang="scss">
@keyframes fadeUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
@keyframes spin { to { transform: rotate(360deg); } }
.fade-up { opacity: 0; animation: fadeUp 0.5s cubic-bezier(0.22,1,0.36,1) forwards; }
.d1 { animation-delay: 0.08s; } .d2 { animation-delay: 0.15s; }
.spinning { animation: spin 1s linear infinite; }

.page-header {
  display: flex; align-items: center; justify-content: space-between; margin-bottom: 24px;
  h1 { font-size: 28px; font-weight: 700; color: #121c28; margin-bottom: 4px; }
  p { font-size: 14px; color: #404944; }
}
.header-actions { display: flex; gap: 8px; }
.refresh-btn {
  display: flex; align-items: center; gap: 4px; padding: 8px 14px; border-radius: 8px;
  border: 1px solid #bfc9c3; background: #fff; color: #404944; font-size: 13px; font-weight: 500;
  cursor: pointer; &:hover:not(:disabled) { border-color: #003527; color: #003527; }
  &:disabled { opacity: 0.5; cursor: not-allowed; }
}
.add-btn {
  display: flex; align-items: center; gap: 6px; padding: 8px 20px; border-radius: 8px;
  background: #003527; color: #fff; font-size: 13px; font-weight: 600; border: none; cursor: pointer;
  &:hover { background: #064e3b; }
}

.config-layout { display: grid; grid-template-columns: 280px 1fr; gap: 20px; align-items: start; }

/* Left sidebar */
.provider-list { display: flex; flex-direction: column; gap: 6px; }
.provider-item {
  display: flex; align-items: center; justify-content: space-between; padding: 12px 14px;
  background: #fff; border-radius: 10px; border: 2px solid #bfc9c3; cursor: pointer;
  transition: all 0.2s;
  &:hover { border-color: #bfc9c3; }
  &.active { border-color: #003527; box-shadow: 0 4px 12px rgba(26,58,92,0.08); }
  &.disabled { opacity: 0.55; }
}
.pi-left { display: flex; align-items: center; gap: 10px; }
.pi-icon {
  width: 36px; height: 36px; border-radius: 10px; background: #f3f4f5; color: #404944;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
  &.enabled { background: rgba(14,165,233,0.1); color: #064e3b; }
}
.pi-info h3 { font-size: 13px; font-weight: 600; color: #121c28; margin: 0 0 2px 0; }
.pi-status { font-size: 11px; font-weight: 600; &.st-ok { color: #198754; } &.st-err { color: #dc3545; } }

/* Right panel */
.config-form {
  background: #fff; border-radius: 12px; padding: 24px; border: 1px solid #bfc9c3; min-height: 400px;
}
.empty-hint { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 80px 0; color: #bfc9c3; p { margin-top: 12px; font-size: 14px; } }
.form-header {
  display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; padding-bottom: 16px; border-bottom: 1px solid #f0f0f0;
  h2 { font-size: 18px; font-weight: 700; color: #121c28; margin: 0; }
}
.form-header-actions { display: flex; gap: 6px; }
.test-btn, .edit-btn, .danger-btn {
  display: flex; align-items: center; gap: 4px; padding: 6px 12px; border-radius: 6px;
  font-size: 12px; font-weight: 500; cursor: pointer; transition: all 0.2s;
}
.test-btn {
  border: 1px solid #bfc9c3; background: #fff; color: #404944;
  &:hover:not(:disabled) { border-color: #003527; color: #003527; }
  &:disabled { opacity: 0.5; cursor: not-allowed; }
}
.edit-btn { border: 1px solid #bfc9c3; background: #fff; color: #404944; &:hover { border-color: #003527; color: #003527; } }
.danger-btn { border: 1px solid #dc3545; background: #fff; color: #dc3545; &:hover { background: #dc3545; color: #fff; } }

.form-section { margin-bottom: 20px; }
.form-section h3 {
  display: flex; align-items: center; gap: 6px; font-size: 14px; font-weight: 600;
  color: #121c28; margin-bottom: 10px; svg { color: #003527; }
}
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.form-grid label {
  display: flex; flex-direction: column; gap: 4px;
  span { font-size: 12px; color: #404944; font-weight: 500; }
  input, select {
    padding: 8px 10px; border: 1px solid #bfc9c3; border-radius: 6px; font-size: 13px; outline: none;
    &:focus { border-color: #003527; box-shadow: 0 0 0 2px rgba(26,58,92,0.06); }
  }
}
.input-readonly { background: #f8f9fa; color: #404944; cursor: not-allowed; }

.key-row { display: flex; gap: 6px; }
.key-input {
  flex: 1; padding: 8px 10px; border: 1px solid #bfc9c3; border-radius: 6px;
  font-size: 13px; font-family: 'Courier New', monospace; outline: none;
  &:focus { border-color: #003527; box-shadow: 0 0 0 2px rgba(26,58,92,0.06); }
}
.eye-btn {
  width: 36px; height: 36px; border-radius: 6px; border: 1px solid #bfc9c3;
  background: #fff; color: #404944; display: flex; align-items: center; justify-content: center;
  cursor: pointer; &:hover { color: #003527; border-color: #003527; }
}
.form-hint { font-size: 11px; color: #bfc9c3; margin-top: 4px; }

.model-tags { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 8px; }
.model-tag {
  font-size: 12px; padding: 4px 10px; border-radius: 4px;
  background: #f3f4f5; color: #404944; font-weight: 500;
}

.form-actions { padding-top: 16px; border-top: 1px solid #f0f0f0; }
.save-btn {
  display: flex; align-items: center; gap: 6px; padding: 8px 24px; border-radius: 8px;
  background: #003527; color: #fff; font-size: 13px; font-weight: 600; border: none; cursor: pointer;
  &:hover { background: #064e3b; }
}

@media (max-width: 768px) { .config-layout { grid-template-columns: 1fr; } .form-grid { grid-template-columns: 1fr; } }
</style>
