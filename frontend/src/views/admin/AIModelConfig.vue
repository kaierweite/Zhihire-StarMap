<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Brain, Sparkles, Key, Server, Gauge, CheckCircle, XCircle, RefreshCw,
  Save, Plus, Trash2, Eye, EyeOff, Zap,
} from 'lucide-vue-next'

// ====== 模型提供商配置 ======
interface ModelProvider {
  id: string
  name: string
  enabled: boolean
  apiKey: string
  baseUrl: string
  defaultModel: string
  models: string[]
  temperature: number
  maxTokens: number
  status: 'connected' | 'disconnected' | 'testing' | 'unknown'
  showKey: boolean
}

const providers = ref<ModelProvider[]>([
  {
    id: 'deepseek',
    name: 'DeepSeek',
    enabled: true,
    apiKey: 'sk-****************************',
    baseUrl: 'https://api.deepseek.com',
    defaultModel: 'deepseek-chat',
    models: ['deepseek-chat', 'deepseek-coder', 'deepseek-reasoner'],
    temperature: 0.7,
    maxTokens: 4096,
    status: 'connected',
    showKey: false,
  },
  {
    id: 'openai',
    name: 'OpenAI',
    enabled: false,
    apiKey: '',
    baseUrl: 'https://api.openai.com/v1',
    defaultModel: 'gpt-4o',
    models: ['gpt-4o', 'gpt-4o-mini', 'gpt-4-turbo', 'gpt-3.5-turbo'],
    temperature: 0.7,
    maxTokens: 4096,
    status: 'unknown',
    showKey: false,
  },
  {
    id: 'qwen',
    name: '通义千问',
    enabled: false,
    apiKey: '',
    baseUrl: 'https://dashscope.aliyuncs.com/compatible-mode/v1',
    defaultModel: 'qwen-turbo',
    models: ['qwen-turbo', 'qwen-plus', 'qwen-max', 'qwen-long'],
    temperature: 0.7,
    maxTokens: 4096,
    status: 'unknown',
    showKey: false,
  },
])

// 当前激活的提供商
const activeProviderId = ref('deepseek')
const activeProvider = computed(() => providers.value.find(p => p.id === activeProviderId.value)!)

// ====== 操作 ======
async function testConnection(provider: ModelProvider) {
  if (!provider.apiKey) { ElMessage.warning('请先填写 API Key'); return }
  provider.status = 'testing'
  // 模拟测试（实际应调用后端 POST /api/admin/ai/test-connection）
  setTimeout(() => {
    provider.status = 'connected'
    ElMessage.success(`${provider.name} 连接测试成功`)
  }, 1500)
}

function saveConfig(provider: ModelProvider) {
  // TODO: PUT /api/admin/ai/config
  ElMessage.success(`${provider.name} 配置已保存`)
}

async function addProvider() {
  const { value } = await ElMessageBox.prompt('请输入模型提供商名称', '添加提供商', {
    confirmButtonText: '添加',
    cancelButtonText: '取消',
    inputPattern: /\S+/,
    inputErrorMessage: '名称不能为空',
  }).catch(() => ({ value: '' }))
  if (!value) return
  providers.value.push({
    id: value.toLowerCase().replace(/\s+/g, '-'),
    name: value,
    enabled: false,
    apiKey: '',
    baseUrl: '',
    defaultModel: '',
    models: [],
    temperature: 0.7,
    maxTokens: 4096,
    status: 'unknown',
    showKey: false,
  })
  ElMessage.success(`已添加「${value}」`)
}

async function deleteProvider(provider: ModelProvider) {
  try {
    await ElMessageBox.confirm(`确认删除提供商「${provider.name}」？`, '删除确认', { type: 'warning' })
    providers.value = providers.value.filter(p => p.id !== provider.id)
    if (activeProviderId.value === provider.id) activeProviderId.value = providers.value[0]?.id || ''
    ElMessage.success('已删除')
  } catch { /* cancelled */ }
}

function statusLabel(s: string) {
  return s === 'connected' ? '已连接' : s === 'disconnected' ? '未连接' : s === 'testing' ? '测试中...' : '未测试'
}
function statusClass(s: string) {
  return s === 'connected' ? 'st-ok' : s === 'disconnected' ? 'st-err' : s === 'testing' ? 'st-testing' : 'st-unknown'
}
</script>

<template>
  <div class="ai-config-page">
    <div class="page-header fade-up">
      <div>
        <h1>大模型配置</h1>
        <p>管理云端 AI 模型提供商、API Key 和模型参数</p>
      </div>
      <button class="add-btn" @click="addProvider"><Plus :size="15" /> 添加提供商</button>
    </div>

    <div class="config-layout">
      <!-- 左侧：提供商列表 -->
      <div class="provider-list fade-up d1">
        <div
          v-for="p in providers" :key="p.id"
          class="provider-item"
          :class="{ active: activeProviderId === p.id }"
          @click="activeProviderId = p.id"
        >
          <div class="pi-left">
            <div class="pi-icon" :class="{ enabled: p.enabled }"><Brain :size="18" /></div>
            <div class="pi-info">
              <h3>{{ p.name }}</h3>
              <span class="pi-status" :class="statusClass(p.status)">{{ statusLabel(p.status) }}</span>
            </div>
          </div>
          <el-switch v-model="p.enabled" size="small" @click.stop />
        </div>
      </div>

      <!-- 右侧：配置表单 -->
      <div v-if="activeProvider" class="config-form fade-up d2" :key="activeProvider.id">
        <div class="form-header">
          <h2>{{ activeProvider.name }} 配置</h2>
          <div class="form-header-actions">
            <button class="test-btn" :disabled="activeProvider.status === 'testing'" @click="testConnection(activeProvider)">
              <RefreshCw :size="14" :class="{ spinning: activeProvider.status === 'testing' }" />
              {{ activeProvider.status === 'testing' ? '测试中...' : '测试连接' }}
            </button>
            <button class="save-btn" @click="saveConfig(activeProvider)"><Save :size="14" /> 保存</button>
          </div>
        </div>

        <!-- API Key -->
        <div class="form-section">
          <h3><Key :size="16" /> API Key</h3>
          <div class="key-row">
            <input
              :type="activeProvider.showKey ? 'text' : 'password'"
              v-model="activeProvider.apiKey"
              placeholder="sk-..."
              class="key-input"
            />
            <button class="eye-btn" @click="activeProvider.showKey = !activeProvider.showKey">
              <component :is="activeProvider.showKey ? EyeOff : Eye" :size="16" />
            </button>
          </div>
          <p class="form-hint">API Key 将加密存储，仅用于服务端调用</p>
        </div>

        <!-- 基础配置 -->
        <div class="form-section">
          <h3><Server :size="16" /> 基础配置</h3>
          <div class="form-grid">
            <label>
              <span>Base URL</span>
              <input v-model="activeProvider.baseUrl" placeholder="https://api.example.com/v1" />
            </label>
            <label>
              <span>默认模型</span>
              <select v-model="activeProvider.defaultModel">
                <option v-for="m in activeProvider.models" :key="m" :value="m">{{ m }}</option>
              </select>
            </label>
          </div>
        </div>

        <!-- 可用模型 -->
        <div class="form-section">
          <h3><Zap :size="16" /> 可用模型</h3>
          <div class="model-tags">
            <span v-for="m in activeProvider.models" :key="m" class="model-tag" :class="{ default: m === activeProvider.defaultModel }">
              {{ m }}
              <span v-if="m === activeProvider.defaultModel" class="default-badge">默认</span>
            </span>
          </div>
        </div>

        <!-- 生成参数 -->
        <div class="form-section">
          <h3><Gauge :size="16" /> 生成参数</h3>
          <div class="form-grid">
            <label>
              <span>Temperature: {{ activeProvider.temperature }}</span>
              <input type="range" v-model.number="activeProvider.temperature" min="0" max="2" step="0.1" class="range-input" />
              <div class="range-labels"><span>精确</span><span>随机</span></div>
            </label>
            <label>
              <span>Max Tokens</span>
              <input v-model.number="activeProvider.maxTokens" type="number" min="256" max="128000" />
            </label>
          </div>
        </div>

        <!-- 危险操作 -->
        <div class="form-section danger-section">
          <button class="delete-btn" @click="deleteProvider(activeProvider)"><Trash2 :size="14" /> 删除此提供商</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
@keyframes fadeUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
.fade-up { opacity: 0; animation: fadeUp 0.5s cubic-bezier(0.22,1,0.36,1) forwards; }
.d1 { animation-delay: 0.08s; } .d2 { animation-delay: 0.15s; }
@keyframes spin { to { transform: rotate(360deg); } }
.spinning { animation: spin 1s linear infinite; }

.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 24px; h1 { font-size: 28px; font-weight: 700; color: #303133; margin-bottom: 4px; } p { font-size: 14px; color: #909399; } }
.add-btn { display: flex; align-items: center; gap: 6px; padding: 10px 22px; border-radius: 999px; background: #1a3a5c; color: #fff; font-size: 14px; font-weight: 600; border: none; cursor: pointer; &:hover { background: #24507a; } }

/* 布局 */
.config-layout { display: grid; grid-template-columns: 280px 1fr; gap: 20px; }

/* 左侧列表 */
.provider-list { display: flex; flex-direction: column; gap: 8px; }
.provider-item {
  display: flex; align-items: center; justify-content: space-between; padding: 14px 16px;
  background: #fff; border-radius: 10px; border: 2px solid #e5e7eb; cursor: pointer; transition: all 0.25s;
  &:hover { border-color: #c0c4cc; }
  &.active { border-color: #1a3a5c; box-shadow: 0 4px 12px rgba(26,58,92,0.08); }
}
.pi-left { display: flex; align-items: center; gap: 10px; }
.pi-icon { width: 38px; height: 38px; border-radius: 10px; background: #f3f4f5; color: #909399; display: flex; align-items: center; justify-content: center; transition: all 0.2s; &.enabled { background: rgba(14,165,233,0.1); color: #0ea5e9; } }
.pi-info h3 { font-size: 14px; font-weight: 600; color: #303133; margin-bottom: 2px; }
.pi-status { font-size: 11px; font-weight: 600; &.st-ok { color: #198754; } &.st-err { color: #dc3545; } &.st-testing { color: #b8860b; } &.st-unknown { color: #c0c4cc; } }

/* 右侧表单 */
.config-form { background: #fff; border-radius: 12px; padding: 28px; border: 1px solid #e5e7eb; }
.form-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 24px; h2 { font-size: 20px; font-weight: 700; color: #303133; } }
.form-header-actions { display: flex; gap: 8px; }
.test-btn { display: flex; align-items: center; gap: 5px; padding: 8px 16px; border-radius: 8px; border: 1px solid #dcdfe6; background: #fff; color: #606266; font-size: 13px; font-weight: 600; cursor: pointer; &:hover:not(:disabled) { border-color: #1a3a5c; color: #1a3a5c; } &:disabled { opacity: 0.5; } }
.save-btn { display: flex; align-items: center; gap: 5px; padding: 8px 18px; border-radius: 999px; background: #1a3a5c; color: #fff; font-size: 13px; font-weight: 600; border: none; cursor: pointer; &:hover { background: #24507a; } }

.form-section { margin-bottom: 24px; h3 { display: flex; align-items: center; gap: 8px; font-size: 15px; font-weight: 600; color: #303133; margin-bottom: 12px; svg { color: #1a3a5c; } } }

/* API Key */
.key-row { display: flex; gap: 8px; }
.key-input { flex: 1; padding: 10px 14px; border: 1px solid #dcdfe6; border-radius: 8px; font-size: 14px; font-family: 'Courier New', monospace; outline: none; &:focus { border-color: #1a3a5c; box-shadow: 0 0 0 2px rgba(26,58,92,0.06); } }
.eye-btn { width: 40px; height: 40px; border-radius: 8px; border: 1px solid #dcdfe6; background: #fff; color: #909399; display: flex; align-items: center; justify-content: center; cursor: pointer; &:hover { color: #1a3a5c; border-color: #1a3a5c; } }
.form-hint { font-size: 12px; color: #c0c4cc; margin-top: 6px; }

/* 表单网格 */
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.form-grid label { display: flex; flex-direction: column; gap: 6px; span { font-size: 13px; color: #606266; font-weight: 500; } input, select { padding: 10px 12px; border: 1px solid #dcdfe6; border-radius: 8px; font-size: 14px; outline: none; &:focus { border-color: #1a3a5c; } } }

/* 模型标签 */
.model-tags { display: flex; flex-wrap: wrap; gap: 8px; }
.model-tag { font-size: 13px; padding: 6px 14px; border-radius: 6px; background: #f3f4f5; color: #606266; font-weight: 500; display: flex; align-items: center; gap: 6px; &.default { background: #dbeafe; color: #1e3a8a; } }
.default-badge { font-size: 10px; padding: 1px 6px; border-radius: 3px; background: #1a3a5c; color: #fff; font-weight: 700; }

/* Range input */
.range-input { width: 100%; accent-color: #1a3a5c; }
.range-labels { display: flex; justify-content: space-between; font-size: 11px; color: #c0c4cc; margin-top: 4px; }

/* 危险区 */
.danger-section { padding-top: 16px; border-top: 1px solid #f0f0f0; }
.delete-btn { display: flex; align-items: center; gap: 5px; padding: 8px 16px; border-radius: 8px; background: #fff; color: #dc3545; border: 1px solid #dc3545; font-size: 13px; font-weight: 600; cursor: pointer; &:hover { background: #dc3545; color: #fff; } }

@media (max-width: 768px) { .config-layout { grid-template-columns: 1fr; } .form-grid { grid-template-columns: 1fr; } }
</style>
