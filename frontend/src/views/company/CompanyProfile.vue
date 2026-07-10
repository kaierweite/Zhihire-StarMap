<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Building2, Save, Globe, MapPin, Phone, Mail, User, AlertTriangle, CheckCircle, Clock } from 'lucide-vue-next'
import { getCompanyProfile, updateCompanyProfile, type CompanyProfile, type CompanyUpdateData } from '@/api/company'

const loading = ref(true)
const saving = ref(false)
const profile = ref<CompanyProfile | null>(null)

const form = reactive<CompanyUpdateData>({
  company_name: '',
  industry: '',
  company_type: '',
  scale: '',
  website: '',
  logo_url: '',
  description: '',
  address: '',
  contact_name: '',
  contact_phone: '',
  contact_email: '',
})

const auditStatusLabels: Record<string, string> = {
  PENDING: '审核中',
  VERIFIED: '已通过',
  REJECTED: '未通过',
  UNVERIFIED: '未提交',
}
const auditStatusType: Record<string, string> = {
  PENDING: 'warning',
  VERIFIED: 'success',
  REJECTED: 'danger',
  UNVERIFIED: 'info',
}

const scaleOptions = ['1-50人', '50-150人', '150-500人', '500-1000人', '1000人以上']
const industryOptions = ['互联网/IT', '金融', '教育', '医疗', '制造业', '房地产', '零售', '文化传媒', '其他']
const companyTypeOptions = ['国企', '事业单位', '上市公司', '其他']

async function loadProfile() {
  loading.value = true
  try {
    const res = await getCompanyProfile()
    if (res.data.code === 200 && res.data.data) {
      profile.value = res.data.data
      const p = res.data.data
      form.company_name = p.company_name || ''
      form.industry = p.industry || ''
      form.company_type = p.company_type || ''
      form.scale = p.scale || ''
      form.website = p.website || ''
      form.logo_url = p.logo_url || ''
      form.description = p.description || ''
      form.address = p.address || ''
      form.contact_name = p.contact_name || ''
      form.contact_phone = p.contact_phone || ''
      form.contact_email = p.contact_email || ''
    } else {
      ElMessage.error(res.data.message || '加载企业信息失败')
    }
  } catch {
    ElMessage.error('网络异常')
  } finally {
    loading.value = false
  }
}

async function handleSave() {
  if (!form.company_name.trim()) {
    ElMessage.warning('企业名称不能为空')
    return
  }
  saving.value = true
  try {
    const body: CompanyUpdateData = {}
    for (const [k, v] of Object.entries(form)) {
      if (v !== '' && v !== null && v !== undefined) {
        (body as any)[k] = v
      }
    }
    const res = await updateCompanyProfile(body)
    if (res.data.code === 200 && res.data.data) {
      profile.value = res.data.data
      ElMessage.success('企业信息已更新，需重新审核')
    } else {
      ElMessage.error(res.data.message || '保存失败')
    }
  } catch {
    ElMessage.error('网络异常')
  } finally {
    saving.value = false
  }
}

onMounted(loadProfile)
</script>

<template>
  <div class="page">
    <div class="page-header fade-up">
      <div class="header-left">
        <Building2 :size="28" class="header-icon" />
        <div>
          <h1>企业信息</h1>
          <span class="subtitle">管理企业基本资料与联系方式</span>
        </div>
      </div>
      <el-button type="primary" size="large" :loading="saving" @click="handleSave">
        <Save :size="16" style="margin-right:4px" /> {{ saving ? '保存中...' : '保存信息' }}
      </el-button>
    </div>

    <div v-if="loading" class="loading-hint">加载中...</div>

    <template v-else-if="profile">
      <div class="content-grid fade-up d1">
        <!-- Left: Form -->
        <div class="form-card">
          <el-form :model="form" label-width="120px" size="large">
            <el-form-item label="企业名称" required>
              <el-input v-model="form.company_name" placeholder="请输入企业全称" maxlength="100" />
            </el-form-item>

            <el-row :gutter="16">
              <el-col :span="12">
                <el-form-item label="所属行业">
                  <el-select v-model="form.industry" placeholder="请选择" clearable style="width:100%">
                    <el-option v-for="o in industryOptions" :key="o" :label="o" :value="o" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="公司规模">
                  <el-select v-model="form.scale" placeholder="请选择" clearable style="width:100%">
                    <el-option v-for="o in scaleOptions" :key="o" :label="o" :value="o" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="16">
              <el-col :span="12">
                <el-form-item label="企业类型">
                  <el-select v-model="form.company_type" placeholder="请选择" clearable style="width:100%">
                    <el-option v-for="o in companyTypeOptions" :key="o" :label="o" :value="o" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="企业官网">
                  <el-input v-model="form.website" placeholder="https://www.example.com">
                    <template #prefix><Globe :size="16" /></template>
                  </el-input>
                </el-form-item>
              </el-col>
            </el-row>

            <el-form-item label="公司地址">
              <el-input v-model="form.address" placeholder="如：北京市海淀区">
                <template #prefix><MapPin :size="16" /></template>
              </el-input>
            </el-form-item>

            <el-form-item label="企业介绍">
              <el-input v-model="form.description" type="textarea" :rows="5" placeholder="请介绍企业背景、主营业务、团队优势等..." maxlength="2000" show-word-limit />
            </el-form-item>

            <el-divider content-position="left">联系人信息</el-divider>

            <el-row :gutter="16">
              <el-col :span="12">
                <el-form-item label="联系人姓名">
                  <el-input v-model="form.contact_name" placeholder="HR 姓名">
                    <template #prefix><User :size="16" /></template>
                  </el-input>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="联系电话">
                  <el-input v-model="form.contact_phone" placeholder="手机号">
                    <template #prefix><Phone :size="16" /></template>
                  </el-input>
                </el-form-item>
              </el-col>
            </el-row>

            <el-form-item label="联系邮箱">
              <el-input v-model="form.contact_email" placeholder="hr@company.com">
                <template #prefix><Mail :size="16" /></template>
              </el-input>
            </el-form-item>
          </el-form>
        </div>

        <!-- Right: Audit status + Info -->
        <div class="side-card">
          <div class="audit-card">
            <h3>审核状态</h3>
            <div class="audit-status">
              <el-tag :type="auditStatusType[profile.audit_status] || 'info'" size="large" effect="dark">
                {{ auditStatusLabels[profile.audit_status] || profile.audit_status }}
              </el-tag>
            </div>
            <div v-if="profile.audit_status === 'REJECTED' && profile.audit_reason" class="audit-reason">
              <AlertTriangle :size="16" />
              <span>{{ profile.audit_reason }}</span>
            </div>
            <div v-if="profile.audit_status === 'VERIFIED'" class="audit-ok">
              <CheckCircle :size="16" />
              <span>企业信息已通过审核，岗位可正常展示</span>
            </div>
            <div v-if="profile.audit_status === 'PENDING'" class="audit-pending">
              <Clock :size="16" />
              <span>审核中，请耐心等待</span>
            </div>
            <p class="audit-hint">修改企业信息后，审核状态将重置为「审核中」，需管理员重新审核。</p>
          </div>

          <div class="info-card">
            <h3>信息概览</h3>
            <el-descriptions :column="1" size="small" border>
              <el-descriptions-item label="企业ID">{{ profile.id }}</el-descriptions-item>
              <el-descriptions-item label="注册时间">{{ profile.created_at?.slice(0, 10) || '-' }}</el-descriptions-item>
              <el-descriptions-item label="最后更新">{{ profile.updated_at?.slice(0, 10) || '-' }}</el-descriptions-item>
            </el-descriptions>
          </div>
        </div>
      </div>
    </template>

    <el-empty v-else description="无法加载企业信息" :image-size="80" />
  </div>
</template>

<style scoped lang="scss">
.page { max-width: 1100px; margin: 0 auto; }

@keyframes fadeUp {
  from { opacity: 0; transform: translateY(16px); }
  to { opacity: 1; transform: translateY(0); }
}
.fade-up { opacity: 0; animation: fadeUp 0.4s cubic-bezier(0.22,1,0.36,1) forwards; }
.d1 { animation-delay: 0.08s; }

.page-header {
  display: flex; align-items: center; justify-content: space-between; margin-bottom: 24px;
}
.header-left { display: flex; align-items: center; gap: 14px; }
.header-icon { color: #1a3a5c; }
h1 { font-size: 28px; font-weight: 700; color: #303133; margin: 0 0 2px 0; }
.subtitle { font-size: 14px; color: #909399; }
.loading-hint { text-align: center; padding: 60px; color: #909399; font-size: 14px; }

.content-grid { display: grid; grid-template-columns: 1fr 320px; gap: 20px; align-items: start; }

.form-card {
  background: #fff; border-radius: 12px; padding: 28px; border: 1px solid #e5e7eb;
}

.side-card { display: flex; flex-direction: column; gap: 16px; }

.audit-card, .info-card {
  background: #fff; border-radius: 12px; padding: 20px; border: 1px solid #e5e7eb;
  h3 { font-size: 15px; font-weight: 700; color: #303133; margin: 0 0 12px 0; }
}

.audit-status { margin-bottom: 12px; }
.audit-reason, .audit-ok, .audit-pending {
  display: flex; align-items: flex-start; gap: 8px;
  font-size: 13px; line-height: 1.5; margin-bottom: 10px; padding: 10px; border-radius: 8px;
}
.audit-reason { background: #fff2f0; color: #cf1322; }
.audit-ok { background: #f6ffed; color: #389e0d; }
.audit-pending { background: #fffbe6; color: #d48806; }
.audit-hint { font-size: 12px; color: #909399; line-height: 1.5; margin: 0; }

@media (max-width: 860px) { .content-grid { grid-template-columns: 1fr; } }
</style>
