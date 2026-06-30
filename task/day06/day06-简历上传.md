# 第6天开发任务（详细版）

# 项目：智聘星图——基于银河麒麟操作系统的AI智能匹配与能力图谱平台

## 今日目标

完成简历上传功能，支持PDF/DOC/DOCX格式上传，实现文件管理和删除。

## 今日能力要求

- 文件上传处理（熟练）
- ElementPlus Upload组件（熟练）
- MIME类型校验（基础）

**最终产出：**

```text
backend/.../module/resume/
├──controller/ResumeController.java
├──service/ResumeService.java
├──service/ResumeServiceImpl.java
├──mapper/ResumeMapper.java
├──entity/Resume.java
└──dto/
    ├──ResumeUploadRequest.java
    └──ResumeResponse.java

frontend/src/views/user/
├──ResumeUpload.vue        # 简历上传页
├──ResumeList.vue          # 简历列表/管理
└──ResumeDetail.vue        # 简历详情

frontend/src/api/
└──resume.ts               # 简历API
```

---

# 第一阶段：后端文件上传配置（1小时）

## 任务1：文件上传配置

```yaml
# application.yml 补充
spring:
  servlet:
    multipart:
      enabled: true
      max-file-size: 20MB
      max-request-size: 50MB

file:
  upload:
    path: /data/upload
    allowed-types:
      - application/pdf
      - application/msword
      - application/vnd.openxmlformats-officedocument.wordprocessingml.document
```

## 任务2：静态资源映射

```java
@Configuration
public class WebMvcConfig implements WebMvcConfigurer {
    @Value("${file.upload.path:/data/upload}")
    private String uploadPath;

    @Override
    public void addResourceHandlers(ResourceHandlerRegistry registry) {
        // 映射上传文件访问路径
        registry.addResourceHandler("/api/files/**")
            .addResourceLocations("file:" + uploadPath + "/");
    }
}
```

---

# 第二阶段：后端简历接口（2小时）

## 任务1：简历上传

```java
@RestController
@RequestMapping("/api/resume")
public class ResumeController {
    @Autowired
    private ResumeService resumeService;

    @PostMapping("/upload")
    public Result<ResumeResponse> upload(
        @UserId Long userId,
        @RequestParam("file") MultipartFile file,
        @RequestParam(value = "title", required = false) String title) {

        return Result.success(resumeService.upload(userId, file, title));
    }

    @GetMapping("/list")
    public Result<List<ResumeResponse>> getList(@UserId Long userId) {
        return Result.success(resumeService.getUserResumes(userId));
    }

    @GetMapping("/{id}")
    public Result<ResumeResponse> getDetail(@UserId Long userId, @PathVariable Long id) {
        return Result.success(resumeService.getDetail(userId, id));
    }

    @DeleteMapping("/{id}")
    public Result<Void> delete(@UserId Long userId, @PathVariable Long id) {
        resumeService.delete(userId, id);
        return Result.success(null);
    }

    @PostMapping("/{id}/set-default")
    public Result<Void> setDefault(@UserId Long userId, @PathVariable Long id) {
        resumeService.setDefault(userId, id);
        return Result.success(null);
    }
}
```

## 任务2：Service实现

```java
@Service
public class ResumeServiceImpl implements ResumeService {
    @Autowired
    private ResumeMapper resumeMapper;
    @Value("${file.upload.path:/data/upload}")
    private String uploadPath;

    @Override
    public ResumeResponse upload(Long userId, MultipartFile file, String title) {
        // 校验文件类型
        String contentType = file.getContentType();
        if (!isAllowedFileType(contentType)) {
            throw new BusinessException(400, "仅支持PDF、DOC、DOCX格式");
        }

        // 校验文件大小（20MB）
        if (file.getSize() > 20 * 1024 * 1024) {
            throw new BusinessException(400, "文件大小不能超过20MB");
        }

        try {
            // 生成存储路径
            String originalName = file.getOriginalFilename();
            String suffix = originalName.substring(originalName.lastIndexOf("."));
            String fileName = "resume_" + userId + "_" + System.currentTimeMillis() + suffix;

            // 按日期分目录存储
            String dateDir = LocalDate.now().format(DateTimeFormatter.ofPattern("yyyy/MM/dd"));
            File dir = new File(uploadPath + "/resume/" + dateDir);
            if (!dir.exists()) dir.mkdirs();

            File dest = new File(dir, fileName);
            file.transferTo(dest);

            // 保存数据库
            Resume resume = new Resume();
            resume.setUserId(userId);
            resume.setTitle(title != null ? title : originalName);
            resume.setFileName(originalName);
            resume.setFilePath("/api/files/resume/" + dateDir + "/" + fileName);
            resume.setFileType(suffix.replace(".", ""));
            resume.setFileSize(file.getSize());
            resume.setParseStatus(0); // 未解析
            resumeMapper.insert(resume);

            // 如果用户没有其他默认简历，设置为默认
            // TODO: 默认简历逻辑

            return toResponse(resume);
        } catch (IOException e) {
            throw new BusinessException(500, "文件上传失败");
        }
    }

    private boolean isAllowedFileType(String contentType) {
        return "application/pdf".equals(contentType)
            || "application/msword".equals(contentType)
            || "application/vnd.openxmlformats-officedocument.wordprocessingml.document".equals(contentType);
    }

    @Override
    public void delete(Long userId, Long id) {
        Resume resume = resumeMapper.selectById(id);
        if (resume == null || !resume.getUserId().equals(userId)) {
            throw new BusinessException(404, "简历不存在");
        }

        // 删除物理文件
        String filePath = uploadPath + resume.getFilePath().replace("/api/files", "");
        File file = new File(filePath);
        if (file.exists()) file.delete();

        // 删除数据库记录（级联删除教育经历、工作经历、项目经历）
        resumeMapper.deleteById(id);
    }
}
```

---

# 第三阶段：前端简历上传页面（2小时）

## 任务1：简历上传组件

```vue
<template>
  <div class="resume-upload-container">
    <el-card>
      <template #header>
        <span class="card-title">上传简历</span>
      </template>

      <!-- 拖拽上传区域 -->
      <el-upload
        class="resume-uploader"
        drag
        action="/api/resume/upload"
        :headers="uploadHeaders"
        :multiple="false"
        :limit="10"
        :on-success="handleUploadSuccess"
        :on-error="handleUploadError"
        :before-upload="beforeUpload"
        accept=".pdf,.doc,.docx"
      >
        <el-icon class="upload-icon" :size="60">
          <UploadFilled />
        </el-icon>
        <div class="upload-text">
          <span>拖拽简历文件到此处，或<em>点击上传</em></span>
        </div>
        <template #tip>
          <div class="upload-tip">
            支持 PDF、DOC、DOCX 格式，单个文件不超过20MB
          </div>
        </template>
      </el-upload>
    </el-card>

    <!-- 简历列表 -->
    <el-card class="resume-list-card">
      <template #header>
        <span class="card-title">我的简历（{{ resumeList.length }}）</span>
      </template>

      <el-table :data="resumeList" stripe v-loading="loading">
        <el-table-column prop="title" label="简历名称" min-width="180">
          <template #default="{ row }">
            <div class="resume-name">
              <el-icon :size="20">
                <Document />
              </el-icon>
              <span>{{ row.title }}</span>
              <el-tag v-if="row.isDefault" type="success" size="small">默认</el-tag>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="fileType" label="格式" width="80">
          <template #default="{ row }">
            <el-tag>{{ row.fileType.toUpperCase() }}</el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="fileSize" label="大小" width="100">
          <template #default="{ row }">
            {{ formatSize(row.fileSize) }}
          </template>
        </el-table-column>

        <el-table-column prop="parseStatus" label="解析状态" width="120">
          <template #default="{ row }">
            <el-tag :type="parseStatusType(row.parseStatus)">
              {{ parseStatusText(row.parseStatus) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="createTime" label="上传时间" width="180" />

        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{ row }">
            <el-button text type="primary" @click="viewDetail(row)">查看</el-button>
            <el-button
              v-if="!row.isDefault"
              text
              type="warning"
              @click="setDefault(row)"
            >设为默认</el-button>
            <el-popconfirm title="确定删除该简历？" @confirm="handleDelete(row)">
              <template #reference>
                <el-button text type="danger">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { UploadFilled, Document } from '@element-plus/icons-vue'
import { getResumeList, deleteResume, setDefaultResume } from '@/api/resume'

const loading = ref(false)
const resumeList = ref([])

const uploadHeaders = {
  Authorization: `Bearer ${localStorage.getItem('token')}`
}

onMounted(async () => {
  await loadResumeList()
})

const loadResumeList = async () => {
  loading.value = true
  try {
    const res = await getResumeList()
    resumeList.value = res.data
  } finally {
    loading.value = false
  }
}

const beforeUpload = (file: File) => {
  const validTypes = ['application/pdf', 'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
  if (!validTypes.includes(file.type)) {
    ElMessage.error('仅支持 PDF、DOC、DOCX 格式')
    return false
  }
  if (file.size > 20 * 1024 * 1024) {
    ElMessage.error('文件大小不能超过20MB')
    return false
  }
  return true
}

const handleUploadSuccess = () => {
  ElMessage.success('上传成功，等待解析')
  loadResumeList()
}

const formatSize = (bytes: number) => {
  if (bytes < 1024) return bytes + 'B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + 'KB'
  return (bytes / 1024 / 1024).toFixed(1) + 'MB'
}

const parseStatusType = (status: number) => {
  const map: Record<number, string> = { 0: 'info', 1: 'warning', 2: 'success', 3: 'danger' }
  return map[status] || 'info'
}

const parseStatusText = (status: number) => {
  const map: Record<number, string> = { 0: '未解析', 1: '解析中', 2: '已解析', 3: '解析失败' }
  return map[status] || '未知'
}
</script>
```

---

# 第6天验收标准

必须完成：

✅ PDF文件上传功能

✅ DOC/DOCX文件上传功能

✅ 文件类型校验

✅ 文件大小限制（20MB）

✅ 简历列表展示

✅ 简历删除（包含物理文件）

✅ 默认简历设置

✅ 上传进度条展示

✅ 文件大小友好显示

✅ Git已提交

---

# 常见问题

**Q：上传大文件超时怎么办？**

A：后端已配置50MB请求限制，前端axios超时设为了30秒，如果文件较大建议等待。

**Q：文件存储路径如何组织？**

A：按 yyyy/MM/dd 分日期目录存储，避免单目录文件过多。

**Q：删除简历时物理文件不删除怎么办？**

A：确保文件路径拼接正确，先打印日志确认路径是否存在。

**Q：同一个用户可以上传多个简历吗？**

A：支持多个简历，但只能设置一个为默认简历。
