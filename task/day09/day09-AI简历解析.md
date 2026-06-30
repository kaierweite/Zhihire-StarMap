# 第9天开发任务（详细版）

# 项目：智聘星图——基于银河麒麟操作系统的AI智能匹配与能力图谱平台

## 今日目标

完成AI简历解析的全流程：上传简历→调用AI解析→提取技能标签→保存到数据库。

## 今日能力要求

- FastAPI异步处理（熟练）
- Spring Cloud Feign/HTTP调用（基础）
- JSONB数据库操作（基础）

**最终产出：**

```text
ai-service/app/
├──api/
│   └──resume_parser_api.py    # 简历解析API
├──services/
│   └──resume_parser.py        # 简历解析业务逻辑
└──models/
    └──schemas.py              # 补充请求/响应模型

backend/.../module/resume/
├──controller/ResumeParseController.java
├──service/ResumeParseService.java
├──service/ResumeParseServiceImpl.java
└──client/AiServiceClient.java    # 调用AI服务客户端

database/
└──seed_resume_test.sql           # 测试数据
```

---

# 第一阶段：AI服务简历解析API（1.5小时）

## 任务1：简历解析API

```python
# api/resume_parser_api.py
from fastapi import APIRouter, HTTPException
from models.schemas import ResumeParseRequest, ResumeParseResponse
from services.resume_parser import ResumeParser
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/parse", tags=["简历解析"])
parser = ResumeParser()

@router.post("/resume", response_model=ResumeParseResponse)
async def parse_resume(request: ResumeParseRequest):
    """
    解析简历文本，提取结构化信息
    """
    logger.info(f"收到简历解析请求: resume_id={request.resume_id}")
    try:
        result = await parser.parse(request.text, request.resume_id)
        return ResumeParseResponse(
            code=200,
            message="解析成功",
            resume_id=request.resume_id,
            data=result
        )
    except Exception as e:
        logger.error(f"简历解析失败: resume_id={request.resume_id}", exc_info=e)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/resume/batch")
async def batch_parse_resume(requests: list[ResumeParseRequest]):
    """批量解析简历"""
    results = []
    for req in requests:
        try:
            result = await parser.parse(req.text, req.resume_id)
            results.append({
                "resume_id": req.resume_id,
                "status": "success",
                "data": result
            })
        except Exception as e:
            results.append({
                "resume_id": req.resume_id,
                "status": "failed",
                "error": str(e)
            })
    return {"code": 200, "results": results}
```

## 任务2：简历解析服务

```python
# services/resume_parser.py
import json
import logging
from typing import Optional
from services.llm_service import llm_service
from services.prompt_templates import RESUME_PARSE_PROMPT

logger = logging.getLogger(__name__)

class ResumeParser:
    async def parse(self, text: str, resume_id: Optional[int] = None) -> dict:
        """解析简历文本"""
        if not text or len(text.strip()) < 20:
            raise ValueError("简历文本太短，无法解析")

        # 1. 构建Prompt
        prompt = RESUME_PARSE_PROMPT.format(resume_text=text[:3000])

        # 2. 调用LLM
        logger.info(f"开始调用LLM解析简历: resume_id={resume_id}")
        response = await llm_service.generate(prompt)

        # 3. 解析JSON
        try:
            result = await llm_service.parse_json_response(response)
        except ValueError as e:
            logger.error(f"JSON解析失败: resume_id={resume_id}")
            # 重试一次
            response = await llm_service.generate(prompt, temperature=0.3)
            result = await llm_service.parse_json_response(response)

        # 4. 数据清洗和补全
        result = self._clean_result(result)

        logger.info(f"简历解析完成: resume_id={resume_id}, skills={result.get('skills', [])}")
        return result

    def _clean_result(self, data: dict) -> dict:
        """清洗和补全解析结果"""
        # 确保必需字段存在
        if "personal_info" not in data:
            data["personal_info"] = {}
        if "skills" not in data:
            data["skills"] = []
        if "education" not in data:
            data["education"] = {}
        if "work_experience" not in data:
            data["work_experience"] = []
        if "project_experience" not in data:
            data["project_experience"] = []

        # 去除空字符串
        data["skills"] = [s for s in data.get("skills", []) if s.strip()]

        # 计算总工作年限
        total_years = 0
        for exp in data.get("work_experience", []):
            if exp.get("start_date") and exp.get("end_date"):
                # 粗略计算
                pass
        data["summary"] = data.get("summary", {})
        data["summary"]["total_experience_years"] = total_years

        return data
```

---

# 第二阶段：后端集成AI服务（2小时）

## 任务1：AI服务客户端

```java
// 使用RestTemplate或Feign调用AI服务
@Component
public class AiServiceClient {
    @Value("${ai-service.url:http://localhost:8000}")
    private String aiServiceUrl;

    private final RestTemplate restTemplate;

    public AiServiceClient() {
        this.restTemplate = new RestTemplate();
        this.restTemplate.setRequestFactory(new SimpleClientHttpRequestFactory() {{
            setConnectTimeout(5000);
            setReadTimeout(120000);  // AI解析可能较慢，设2分钟超时
        }});
    }

    public AiParseResult parseResume(String text, Long resumeId) {
        String url = aiServiceUrl + "/api/v1/parse/resume";

        Map<String, Object> request = new HashMap<>();
        request.put("text", text);
        request.put("resume_id", resumeId);

        ResponseEntity<AiResponse> response = restTemplate.postForEntity(
            url, request, AiResponse.class);

        if (response.getBody() == null || response.getBody().getCode() != 200) {
            throw new BusinessException(500, "AI解析服务调用失败");
        }

        return response.getBody().getData();
    }
}

// 响应模型
@Data
public class AiResponse {
    private Integer code;
    private String message;
    private AiParseResult data;
}

@Data
public class AiParseResult {
    private Map<String, Object> personalInfo;
    private Map<String, Object> education;
    private List<Map<String, Object>> workExperience;
    private List<Map<String, Object>> projectExperience;
    private List<String> skills;
    private List<String> certifications;
    private Map<String, Object> summary;
}
```

## 任务2：简历解析业务逻辑

```java
@Service
public class ResumeParseServiceImpl implements ResumeParseService {
    @Autowired
    private ResumeMapper resumeMapper;
    @Autowired
    private UserSkillMapper userSkillMapper;
    @Autowired
    private AiServiceClient aiServiceClient;

    @Override
    @Async  // 异步执行，不阻塞用户
    public void parseResume(Long resumeId) {
        // 1. 更新解析状态为"解析中"
        Resume resume = resumeMapper.selectById(resumeId);
        resume.setParseStatus(1);  // 解析中
        resumeMapper.updateById(resume);

        try {
            // 2. 读取文件内容
            String text = readResumeFile(resume.getFilePath());

            // 3. 调用AI服务
            AiParseResult result = aiServiceClient.parseResume(text, resumeId);

            // 4. 保存解析结果到数据库
            saveParseResult(resume, result);

            // 5. 更新解析状态为"已解析"
            resume.setParseStatus(2);
            resume.setParseResult(new JSONObject(objectMapper.writeValueAsString(result)));
            resumeMapper.updateById(resume);

        } catch (Exception e) {
            log.error("简历解析失败: resumeId={}", resumeId, e);
            resume.setParseStatus(3);  // 解析失败
            resumeMapper.updateById(resume);
        }
    }

    private void saveParseResult(Resume resume, AiParseResult result) {
        // 保存技能标签
        List<String> skills = result.getSkills();
        resume.setSkillTags(skills.toArray(new String[0]));

        // 保存学历信息
        Map<String, Object> edu = result.getEducation();
        if (edu != null) {
            resume.setEducation((String) edu.get("degree"));
            resume.setSchool((String) edu.get("school"));
            resume.setMajor((String) edu.get("major"));
        }

        // 保存工作年限
        Map<String, Object> summary = result.getSummary();
        if (summary != null && summary.get("total_experience_years") != null) {
            resume.setExperienceYears(new BigDecimal(summary.get("total_experience_years").toString()));
        }

        resumeMapper.updateById(resume);

        // 同步更新用户技能表
        syncUserSkills(resume.getUserId(), skills);
    }

    private void syncUserSkills(Long userId, List<String> skills) {
        // 先删除旧的技能记录
        userSkillMapper.deleteByUserId(userId);
        // 插入新的技能
        for (String skillName : skills) {
            UserSkill userSkill = new UserSkill();
            userSkill.setUserId(userId);
            userSkill.setSkillName(skillName);
            userSkill.setLevel(1);
            userSkill.setSource("resume");
            userSkillMapper.insert(userSkill);
        }
    }
}
```

## 任务3：异步解析配置

```java
@Configuration
@EnableAsync
public class AsyncConfig {
    @Bean("taskExecutor")
    public Executor taskExecutor() {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
        executor.setCorePoolSize(2);
        executor.setMaxPoolSize(5);
        executor.setQueueCapacity(100);
        executor.setThreadNamePrefix("resume-parse-");
        executor.initialize();
        return executor;
    }
}
```

---

# 第三阶段：前端解析状态展示（1小时）

## 任务1：解析进度展示

在简历列表页面，对正在解析的简历显示进度状态：

```vue
<!-- 解析中 - 显示旋转动画 -->
<template v-if="row.parseStatus === 1">
  <el-tag type="warning">
    <el-icon class="is-loading"><Loading /></el-icon>
    解析中
  </el-tag>
</template>

<!-- 解析完成 - 显示技能标签预览 -->
<template v-else-if="row.parseStatus === 2">
  <div class="skill-tags">
    <el-tag
      v-for="skill in row.skillTags?.slice(0, 5)"
      :key="skill"
      size="small"
      class="skill-tag"
    >
      {{ skill }}
    </el-tag>
    <el-tag v-if="row.skillTags?.length > 5" size="small" type="info">
      +{{ row.skillTags.length - 5 }}
    </el-tag>
  </div>
</template>

<!-- 解析失败 - 显示重新解析按钮 -->
<template v-else-if="row.parseStatus === 3">
  <div class="parse-failed">
    <el-tag type="danger">解析失败</el-tag>
    <el-button text type="primary" size="small" @click="retryParse(row)">
      重新解析
    </el-button>
  </div>
</template>
```

---

# 第9天验收标准

必须完成：

✅ AI简历解析全流程跑通

✅ 解析结果保存到数据库

✅ 技能标签正确提取

✅ 技能同步到用户技能表

✅ 异步解析不阻塞用户

✅ 解析状态实时更新

✅ 解析失败重试机制

✅ 批量解析支持

✅ Git已提交

---

# 常见问题

**Q：AI解析太慢怎么办？**

A：异步解析，前端轮询或WebSocket推送状态更新。

**Q：解析结果不准？**

A：优化Prompt，增加示例输出，降低temperature值。

**Q：大段文本超出LLM上下文？**

A：截取前3000字符，一般简历这个长度足够。

**Q：AI服务挂了怎么处理？**

A：解析状态标记为"解析失败"，允许用户手动重新解析。
