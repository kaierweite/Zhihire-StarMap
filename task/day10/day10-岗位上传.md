# 第10天开发任务（详细版）

# 项目：智聘星图——基于银河麒麟操作系统的AI智能匹配与能力图谱平台

## 今日目标

完成企业端岗位上传功能，支持JD文档上传、岗位管理（增删改查）。

## 今日能力要求

- CRUD开发（熟练）
- 企业端权限控制（基础）
- ElementPlus表格/表单（熟练）

**最终产出：**

```text
backend/.../module/job/
├──controller/JobController.java
├──service/JobService.java
├──service/JobServiceImpl.java
├──mapper/JobMapper.java
├──entity/Job.java
├──dto/
│   ├──JobCreateRequest.java
│   ├──JobUpdateRequest.java
│   └──JobResponse.java
└──mapper/JobMapper.xml

frontend/src/views/company/
├──JobUpload.vue              # 岗位上传页
├──JobList.vue                # 岗位列表
├──JobEdit.vue                # 岗位编辑
└──JobDetail.vue              # 岗位详情

frontend/src/api/
└──job.ts                     # 岗位API
```

---

# 第一阶段：后端岗位接口（2小时）

## 任务1：岗位Controller

```java
@RestController
@RequestMapping("/api/company/job")
public class JobController {
    @Autowired
    private JobService jobService;

    @PostMapping("/create")
    public Result<JobResponse> create(@UserId Long userId,
                                       @Valid @RequestBody JobCreateRequest request) {
        return Result.success(jobService.create(userId, request));
    }

    @PostMapping("/upload")
    public Result<JobResponse> uploadJob(
        @UserId Long userId,
        @RequestParam("file") MultipartFile file) {
        return Result.success(jobService.uploadJobDoc(userId, file));
    }

    @PutMapping("/{id}")
    public Result<Void> update(@UserId Long userId,
                                @PathVariable Long id,
                                @Valid @RequestBody JobUpdateRequest request) {
        jobService.update(userId, id, request);
        return Result.success(null);
    }

    @DeleteMapping("/{id}")
    public Result<Void> delete(@UserId Long userId, @PathVariable Long id) {
        jobService.delete(userId, id);
        return Result.success(null);
    }

    @GetMapping("/list")
    public Result<PageResult<JobResponse>> list(
        @UserId Long userId,
        @RequestParam(defaultValue = "1") int page,
        @RequestParam(defaultValue = "10") int size) {
        return Result.success(jobService.getCompanyJobs(userId, page, size));
    }

    @GetMapping("/{id}")
    public Result<JobResponse> detail(@PathVariable Long id) {
        return Result.success(jobService.getDetail(id));
    }

    @PostMapping("/{id}/toggle-status")
    public Result<Void> toggleStatus(@UserId Long userId, @PathVariable Long id) {
        jobService.toggleStatus(userId, id);
        return Result.success(null);
    }
}
```

## 任务2：岗位Service

```java
@Service
public class JobServiceImpl implements JobService {
    @Autowired
    private JobMapper jobMapper;
    @Autowired
    private CompanyMapper companyMapper;
    @Autowired
    private DocumentParserFactory parserFactory;

    @Override
    public JobResponse create(Long userId, JobCreateRequest request) {
        SysCompany company = companyMapper.findByUserId(userId);
        if (company == null) {
            throw new BusinessException(400, "请先完善企业信息");
        }

        Job job = new Job();
        job.setCompanyId(company.getId());
        job.setTitle(request.getTitle());
        job.setDepartment(request.getDepartment());
        job.setDescription(request.getDescription());
        job.setRequirement(request.getRequirement());
        job.setSalaryMin(request.getSalaryMin());
        job.setSalaryMax(request.getSalaryMax());
        job.setCity(request.getCity());
        job.setExperienceMin(request.getExperienceMin());
        job.setEducation(request.getEducation());
        job.setStatus(1);  // 已发布
        jobMapper.insert(job);

        return toResponse(job);
    }

    @Override
    public JobResponse uploadJobDoc(Long userId, MultipartFile file) {
        // 1. 解析文档内容
        String fileName = file.getOriginalFilename();
        DocumentParser parser = parserFactory.getParser(fileName);
        String text;
        try {
            text = parser.parse(file.getInputStream(), fileName);
        } catch (IOException e) {
            throw new BusinessException(500, "文档解析失败");
        }

        // 2. 创建岗位（使用文件名作为标题）
        SysCompany company = companyMapper.findByUserId(userId);
        Job job = new Job();
        job.setCompanyId(company.getId());
        job.setTitle(fileName.replaceAll("\\.(pdf|doc|docx)$", ""));
        job.setDescription(text);
        job.setParseStatus(0);  // 等待AI解析
        job.setStatus(1);
        jobMapper.insert(job);

        // 3. 触发AI解析（异步）
        // TODO: 调用AI解析岗位需求

        return toResponse(job);
    }
}
```

---

# 第二阶段：前端岗位管理页面（2.5小时）

## 任务1：岗位上传页面

```vue
<template>
  <div class="job-upload-container">
    <el-row :gutter="20">
      <!-- 手动填写 -->
      <el-col :span="14">
        <el-card>
          <template #header>
            <span class="card-title">发布新岗位</span>
          </template>

          <el-form :model="jobForm" :rules="rules" label-width="100px" ref="formRef">
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="岗位名称" prop="title">
                  <el-input v-model="jobForm.title" placeholder="如：高级Java开发工程师" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="所属部门" prop="department">
                  <el-input v-model="jobForm.department" placeholder="如：技术研发部" />
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="20">
              <el-col :span="8">
                <el-form-item label="最低薪资" prop="salaryMin">
                  <el-input-number v-model="jobForm.salaryMin" :min="0" :step="1" />
                  <span class="unit">K/月</span>
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="最高薪资" prop="salaryMax">
                  <el-input-number v-model="jobForm.salaryMax" :min="0" :step="1" />
                  <span class="unit">K/月</span>
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="工作城市" prop="city">
                  <el-select v-model="jobForm.city" filterable placeholder="请选择城市">
                    <el-option v-for="city in cities" :key="city" :label="city" :value="city" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="学历要求" prop="education">
                  <el-select v-model="jobForm.education" placeholder="请选择">
                    <el-option label="不限" value="" />
                    <el-option label="大专" value="大专" />
                    <el-option label="本科" value="本科" />
                    <el-option label="硕士" value="硕士" />
                    <el-option label="博士" value="博士" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="工作经验" prop="experienceMin">
                  <el-select v-model="jobForm.experienceMin" placeholder="请选择">
                    <el-option label="不限" :value="0" />
                    <el-option label="1年以下" :value="0" />
                    <el-option label="1-3年" :value="1" />
                    <el-option label="3-5年" :value="3" />
                    <el-option label="5-10年" :value="5" />
                    <el-option label="10年以上" :value="10" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>

            <el-form-item label="岗位职责" prop="description">
              <el-input v-model="jobForm.description" type="textarea" :rows="6"
                placeholder="请描述岗位职责，每行一条" maxlength="2000" show-word-limit />
            </el-form-item>

            <el-form-item label="任职要求" prop="requirement">
              <el-input v-model="jobForm.requirement" type="textarea" :rows="6"
                placeholder="请描述任职要求，每行一条" maxlength="2000" show-word-limit />
            </el-form-item>

            <el-form-item>
              <el-button type="primary" size="large" :loading="submitting" @click="handleCreate">
                发布岗位
              </el-button>
              <el-button size="large" @click="resetForm">重置</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <!-- 文档上传 -->
      <el-col :span="10">
        <el-card>
          <template #header>
            <span class="card-title">上传JD文档</span>
          </template>

          <el-upload
            class="jd-uploader"
            drag
            action="/api/company/job/upload"
            :headers="uploadHeaders"
            :on-success="handleUploadSuccess"
            multiple
          >
            <el-icon class="upload-icon" :size="50"><UploadFilled /></el-icon>
            <div class="upload-text">
              <span>拖拽JD文档到此处，或<em>点击上传</em></span>
            </div>
            <template #tip>
              <div class="upload-tip">
                支持 PDF、DOC、DOCX 格式<br/>
                系统将自动解析岗位信息
              </div>
            </template>
          </el-upload>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>
```

## 任务2：岗位列表页面

```vue
<template>
  <div class="job-list-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span class="card-title">岗位管理</span>
          <el-button type="primary" @click="$router.push('/company/job/upload')">
            发布新岗位
          </el-button>
        </div>
      </template>

      <!-- 搜索筛选 -->
      <div class="filter-bar">
        <el-input v-model="searchKey" placeholder="搜索岗位名称" clearable style="width: 200px" />
        <el-select v-model="statusFilter" placeholder="状态" clearable style="width: 120px">
          <el-option label="发布中" :value="1" />
          <el-option label="已下架" :value="0" />
        </el-select>
        <el-button @click="loadJobs">搜索</el-button>
      </div>

      <!-- 岗位列表 -->
      <el-table :data="jobList" v-loading="loading" stripe>
        <el-table-column prop="title" label="岗位名称" min-width="160" />
        <el-table-column prop="department" label="部门" width="120" />
        <el-table-column label="薪资范围" width="150">
          <template #default="{ row }">
            {{ row.salaryMin }}-{{ row.salaryMax }}K/月
          </template>
        </el-table-column>
        <el-table-column prop="city" label="城市" width="100" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-switch
              :model-value="row.status === 1"
              @change="toggleStatus(row)"
              active-text="发布中"
              inactive-text="已下架"
            />
          </template>
        </el-table-column>
        <el-table-column prop="viewCount" label="浏览次数" width="100" />
        <el-table-column prop="createTime" label="发布时间" width="180" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button text type="primary" @click="viewDetail(row)">查看</el-button>
            <el-button text type="primary" @click="editJob(row)">编辑</el-button>
            <el-popconfirm title="确定删除该岗位？" @confirm="handleDelete(row)">
              <template #reference>
                <el-button text type="danger">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="size"
          :total="total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          @change="loadJobs"
        />
      </div>
    </el-card>
  </div>
</template>
```

---

# 第10天验收标准

必须完成：

✅ 手动发布岗位（含表单校验）

✅ 上传JD文档发布岗位

✅ 岗位列表展示（分页）

✅ 岗位编辑功能

✅ 岗位下架/发布切换

✅ 岗位删除（含确认弹窗）

✅ 搜索筛选功能

✅ 岗位详情页

✅ 企业权限控制（只能管理自己的岗位）

✅ Git已提交
