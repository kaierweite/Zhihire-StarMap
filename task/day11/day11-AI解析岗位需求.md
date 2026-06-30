# 第11天开发任务（详细版）

# 项目：智聘星图——基于银河麒麟操作系统的AI智能匹配与能力图谱平台

## 今日目标

实现AI解析岗位需求，从JD文本中提取技能要求、学历要求、工作经验、城市等信息并保存数据库。

## 今日能力要求

- FastAPI接口开发（熟练）
- JSON数据处理（熟练）
- 企业端业务流程理解（基础）

**最终产出：**

```text
ai-service/app/
├──api/
│   └──job_parser_api.py        # 岗位解析API
├──services/
│   └──job_parser.py            # 岗位解析业务逻辑

backend/.../module/job/
├──service/JobParseService.java
├──service/JobParseServiceImpl.java
└──mapper/JobSkillMapper.java

database/
└──seed_job_test.sql            # 岗位测试数据
```

---

# 第一阶段：AI服务岗位解析（1.5小时）

## 任务1：岗位解析API

```python
# api/job_parser_api.py
from fastapi import APIRouter, HTTPException
from models.schemas import JobParseRequest, JobParseResponse
from services.job_parser import JobParser
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/parse", tags=["岗位解析"])
parser = JobParser()

@router.post("/job", response_model=JobParseResponse)
async def parse_job(request: JobParseRequest):
    """解析岗位JD，提取结构化需求信息"""
    logger.info(f"收到岗位解析请求: job_id={request.job_id}")
    try:
        result = await parser.parse(request.text, request.job_id)
        return JobParseResponse(
            code=200,
            message="解析成功",
            job_id=request.job_id,
            data=result
        )
    except Exception as e:
        logger.error(f"岗位解析失败: job_id={request.job_id}", exc_info=e)
        raise HTTPException(status_code=500, detail=str(e))
```

## 任务2：岗位解析服务

```python
# services/job_parser.py
import json
import logging
from typing import Optional
from services.llm_service import llm_service
from services.prompt_templates import JOB_PARSE_PROMPT

logger = logging.getLogger(__name__)

class JobParser:
    async def parse(self, text: str, job_id: Optional[int] = None) -> dict:
        """解析岗位JD"""
        if not text or len(text.strip()) < 20:
            raise ValueError("JD文本太短，无法解析")

        # 1. 构建Prompt
        prompt = JOB_PARSE_PROMPT.format(job_text=text[:3000])

        # 2. 调用LLM
        logger.info(f"开始调用LLM解析岗位: job_id={job_id}")
        response = await llm_service.generate(prompt)

        # 3. 解析JSON
        result = await llm_service.parse_json_response(response)

        # 4. 数据清洗
        result = self._clean_result(result)

        logger.info(
            f"岗位解析完成: job_id={job_id}, "
            f"skills_must={len(result.get('requirements', {}).get('skills_must', []))}"
        )
        return result

    def _clean_result(self, data: dict) -> dict:
        """清洗解析结果"""
        if "requirements" not in data:
            data["requirements"] = {}
        if "responsibilities" not in data:
            data["responsibilities"] = []
        if "benefits" not in data:
            data["benefits"] = []

        req = data["requirements"]
        if "skills_must" not in req:
            req["skills_must"] = []
        if "skills_plus" not in req:
            req["skills_plus"] = []

        # 去重并去除空值
        req["skills_must"] = list(set(s.strip() for s in req["skills_must"] if s.strip()))
        req["skills_plus"] = list(set(s.strip() for s in req["skills_plus"] if s.strip()))

        return data
```

---

# 第二阶段：后端岗位解析集成（2小时）

## 任务1：岗位解析Service

```java
@Service
public class JobParseServiceImpl implements JobParseService {
    @Autowired
    private JobMapper jobMapper;
    @Autowired
    private JobSkillMapper jobSkillMapper;
    @Autowired
    private AiServiceClient aiServiceClient;

    @Override
    @Async("taskExecutor")
    public void parseJob(Long jobId) {
        Job job = jobMapper.selectById(jobId);
        job.setParseStatus(1);  // 解析中
        jobMapper.updateById(job);

        try {
            // 1. 获取JD文本
            String text = job.getDescription() + "\n" +
                (job.getRequirement() != null ? job.getRequirement() : "");

            // 2. 调用AI解析
            AiJobParseResult result = aiServiceClient.parseJob(text, jobId);

            // 3. 保存解析结果
            saveParseResult(job, result);

            job.setParseStatus(2);  // 解析成功
            jobMapper.updateById(job);

        } catch (Exception e) {
            log.error("岗位解析失败: jobId={}", jobId, e);
            job.setParseStatus(3);  // 解析失败
            jobMapper.updateById(job);
        }
    }

    private void saveParseResult(Job job, AiJobParseResult result) {
        // 保存技能要求到 job_skill 表
        jobSkillMapper.deleteByJobId(job.getId());

        // 必备技能
        List<String> mustSkills = result.getRequirements().getSkillsMust();
        for (String skillName : mustSkills) {
            JobSkill jobSkill = new JobSkill();
            jobSkill.setJobId(job.getId());
            jobSkill.setSkillName(skillName);
            jobSkill.setRequired(true);
            jobSkill.setImportance(5);
            jobSkillMapper.insert(jobSkill);
        }

        // 加分技能
        List<String> plusSkills = result.getRequirements().getSkillsPlus();
        for (String skillName : plusSkills) {
            JobSkill jobSkill = new JobSkill();
            jobSkill.setJobId(job.getId());
            jobSkill.setSkillName(skillName);
            jobSkill.setRequired(false);
            jobSkill.setImportance(3);
            jobSkillMapper.insert(jobSkill);
        }

        // 更新岗位的学历要求和工作经验
        String education = result.getRequirements().getEducation();
        if (education != null && !education.isEmpty()) {
            job.setEducation(education);
        }

        Integer experienceMin = result.getRequirements().getExperienceMin();
        if (experienceMin != null) {
            job.setExperienceMin(experienceMin);
        }

        // 更新技能标签数组
        List<String> allSkills = new ArrayList<>();
        allSkills.addAll(mustSkills);
        allSkills.addAll(plusSkills);
        job.setSkillTags(allSkills.toArray(new String[0]));

        // 更新城市
        String location = result.getPositionInfo().getLocation();
        if (location != null && !location.isEmpty()) {
            job.setCity(location);
        }

        jobMapper.updateById(job);
    }
}
```

## 任务2：AI客户端补充

```java
// AiServiceClient 补充岗位解析方法
public AiJobParseResult parseJob(String text, Long jobId) {
    String url = aiServiceUrl + "/api/v1/parse/job";

    Map<String, Object> request = new HashMap<>();
    request.put("text", text);
    request.put("job_id", jobId);

    ResponseEntity<AiResponse> response = restTemplate.postForEntity(
        url, request, AiResponse.class);

    if (response.getBody() == null || response.getBody().getCode() != 200) {
        throw new BusinessException(500, "AI岗位解析服务调用失败");
    }

    ObjectMapper mapper = new ObjectMapper();
    return mapper.convertValue(response.getBody().getData(), AiJobParseResult.class);
}

// 岗位解析结果DTO
@Data
public class AiJobParseResult {
    private PositionInfo positionInfo;
    private JobRequirements requirements;
    private List<String> responsibilities;
    private SalaryRange salaryRange;
    private List<String> benefits;
    private JobSummary summary;

    @Data
    public static class PositionInfo {
        private String title;
        private String department;
        private String location;
    }

    @Data
    public static class JobRequirements {
        private String education;
        private Integer experienceMin;
        private List<String> skillsMust;
        private List<String> skillsPlus;
        private List<String> otherRequirements;
    }

    @Data
    public static class SalaryRange {
        private BigDecimal min;
        private BigDecimal max;
    }

    @Data
    public static class JobSummary {
        private Integer keySkillsCount;
        private String experienceLevel;
        private String workType;
    }
}
```

---

# 第三阶段：解析结果展示页面（1小时）

## 任务1：岗位详情展示解析结果

在岗位详情页，展示AI解析出的技能要求和岗位画像：

```vue
<template>
  <!-- 岗位画像卡片 -->
  <el-card class="job-profile-card">
    <template #header>
      <div class="card-header">
        <span>岗位画像（AI解析）</span>
        <el-tag v-if="parseStatus === 2" type="success">已解析</el-tag>
        <el-tag v-else-if="parseStatus === 1" type="warning">解析中</el-tag>
        <el-tag v-else type="info">未解析</el-tag>
      </div>
    </template>

    <div v-if="parseStatus === 2" class="profile-content">
      <!-- 必备技能标签云 -->
      <div class="skill-section">
        <h4>必备技能</h4>
        <div class="skill-tags">
          <el-tag
            v-for="skill in requiredSkills"
            :key="skill"
            type="danger"
            class="skill-tag"
          >
            {{ skill }}
          </el-tag>
        </div>
      </div>

      <!-- 加分技能 -->
      <div class="skill-section">
        <h4>加分技能</h4>
        <div class="skill-tags">
          <el-tag
            v-for="skill in plusSkills"
            :key="skill"
            type="warning"
            class="skill-tag"
          >
            {{ skill }}
          </el-tag>
        </div>
      </div>

      <!-- 岗位要求概览 -->
      <el-descriptions title="硬性要求" :column="3" border>
        <el-descriptions-item label="学历要求">{{ education }}</el-descriptions-item>
        <el-descriptions-item label="工作经验">{{ experienceMin }}年以上</el-descriptions-item>
        <el-descriptions-item label="工作城市">{{ city }}</el-descriptions-item>
      </el-descriptions>
    </div>
  </el-card>
</template>
```

---

# 第11天验收标准

必须完成：

✅ AI岗位解析全流程跑通

✅ 必备技能正确提取

✅ 加分技能正确提取

✅ 学历要求正确提取

✅ 工作经验要求正确提取

✅ 城市信息正确提取

✅ 解析结果保存到job_skill表

✅ 解析状态实时更新

✅ 岗位画像页面展示

✅ Git已提交
