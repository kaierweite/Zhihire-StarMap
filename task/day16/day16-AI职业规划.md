# 第16天开发任务（详细版）

# 项目：智聘星图——基于银河麒麟操作系统的AI智能匹配与能力图谱平台

## 今日目标

实现AI职业规划功能，根据用户技能分析技能缺口，推荐学习路线和职业发展路径。

## 今日能力要求

- Prompt工程（熟练）
- AI聊天交互（基础）
- ECharts流程图（基础）

**最终产出：**

```text
ai-service/app/
├──api/
│   └──career_plan_api.py       # 职业规划API
├──services/
│   ├──career_planner.py        # 职业规划核心服务
│   └──prompt_templates.py      # 补充职业规划Prompt

backend/.../module/career/
├──controller/CareerController.java
├──service/CareerPlanService.java
└──service/CareerPlanServiceImpl.java

frontend/src/views/user/
├──CareerPlan.vue               # 职业规划主页
├──components/
│   ├──SkillGapAnalysis.vue     # 技能缺口分析
│   ├──LearningRoadmap.vue      # 学习路线图
│   ├──CareerPath.vue           # 职业发展路径
│   └──PlanHistory.vue          # 规划历史
```

---

# 第一阶段：AI职业规划Prompt（1小时）

## 任务1：职业规划Prompt

```python
# prompt_templates.py 补充

CAREER_PLAN_PROMPT = """
你是一名资深的IT职业规划顾问。请根据用户的现有技能，生成个性化的职业发展规划。

## 用户当前技能
---
{user_skills}
---

## 用户当前岗位（如有）
Current Position: {current_position}

## 用户目标岗位（如有）
Target Position: {target_position}

## 输出格式

请分析用户现有技能与目标岗位的差距，输出以下JSON：

```json
{{
    "current_analysis": {{
        "current_level": "初级/中级/高级/专家",
        "strengths": ["核心优势1", "核心优势2"],
        "weaknesses": ["待提升领域1"]
    }},
    "skill_gap": {{
        "immediate_skills": [
            {{
                "name": "急需技能名称",
                "priority": 1,
                "reason": "为什么需要这个技能",
                "estimated_time": "预计学习时间（月）"
            }}
        ],
        "recommended_skills": [
            {{
                "name": "推荐学习技能",
                "priority": 2,
                "reason": "推荐理由"
            }}
        ]
    }},
    "learning_roadmap": [
        {{
            "phase": "第一阶段",
            "title": "阶段名称",
            "duration": "持续时间（月）",
            "skills": ["学习的技能"],
            "resources": [
                {{
                    "type": "书籍/课程/文档/项目实践",
                    "name": "资源名称",
                    "description": "资源说明"
                }}
            ],
            "milestone": "阶段目标/产出"
        }}
    ],
    "career_paths": [
        {{
            "direction": "发展方向（如：技术专家/架构师/技术管理）",
            "description": "方向说明",
            "required_skills": ["所需技能"],
            "timeline": "预计3-5年",
            "potential_roles": ["可能的职位"]
        }}
    ],
    "summary": {{
        "overall_assessment": "综合评估",
        "key_recommendations": ["最重要建议1", "最重要建议2", "最重要建议3"],
        "estimated_growth_time": "预计达到目标需要的时间（月）"
    }}
}}
```

注意：
1. 分析要具体，不要泛泛而谈
2. 学习资源推荐要真实存在
3. 时间规划要切合实际
4. 技能缺口要基于用户现有技能合理推演
5. 回应只输出JSON，不要其他内容
"""
```

---

# 第二阶段：AI职业规划服务（1.5小时）

## 任务1：职业规划服务

```python
# services/career_planner.py
import json
import logging
from typing import Optional, List
from services.llm_service import llm_service
from services.prompt_templates import CAREER_PLAN_PROMPT

logger = logging.getLogger(__name__)

class CareerPlanner:
    async def generate_plan(
        self,
        skills: List[str],
        current_position: Optional[str] = None,
        target_position: Optional[str] = None
    ) -> dict:
        """生成职业规划"""
        if not skills:
            raise ValueError("用户技能列表不能为空")

        # 构建Prompt
        prompt = CAREER_PLAN_PROMPT.format(
            user_skills="、".join(skills),
            current_position=current_position or "未填写",
            target_position=target_position or "未填写"
        )

        # 调用LLM（使用稍高温度，允许一定的创造性）
        logger.info(f"开始生成职业规划: skills={skills}")
        response = await llm_service.generate(prompt, temperature=0.3)

        # 解析JSON
        try:
            result = await llm_service.parse_json_response(response)
        except ValueError:
            logger.warning("首次JSON解析失败，重试中...")
            response = await llm_service.generate(prompt, temperature=0.2)
            result = await llm_service.parse_json_response(response)

        # 验证必需字段
        self._validate_result(result)
        return result

    def _validate_result(self, data: dict):
        """验证规划结果是否完整"""
        required_sections = ["current_analysis", "skill_gap", "learning_roadmap", "career_paths", "summary"]
        for section in required_sections:
            if section not in data:
                data[section] = {}
                logger.warning(f"缺少规划章节: {section}")
```

---

# 第三阶段：后端职业规划接口（1.5小时）

## 任务1：Controller

```java
@RestController
@RequestMapping("/api/career")
public class CareerController {
    @Autowired
    private CareerPlanService careerPlanService;

    /**
     * 获取/生成职业规划
     */
    @PostMapping("/plan")
    public Result<CareerPlanResponse> generatePlan(
        @UserId Long userId,
        @RequestBody(required = false) CareerPlanRequest request) {
        return Result.success(careerPlanService.getOrGeneratePlan(userId, request));
    }

    /**
     * 获取规划历史列表
     */
    @GetMapping("/history")
    public Result<List<CareerPlanResponse>> getHistory(@UserId Long userId) {
        return Result.success(careerPlanService.getHistory(userId));
    }

    /**
     * 删除规划记录
     */
    @DeleteMapping("/{id}")
    public Result<Void> deletePlan(@UserId Long userId, @PathVariable Long id) {
        careerPlanService.delete(userId, id);
        return Result.success(null);
    }
}
```

## 任务2：Service

```java
@Service
public class CareerPlanServiceImpl implements CareerPlanService {
    @Autowired
    private ResumeMapper resumeMapper;
    @Autowired
    private CareerPlanMapper careerPlanMapper;
    @Autowired
    private AiServiceClient aiServiceClient;

    @Override
    public CareerPlanResponse getOrGeneratePlan(Long userId, CareerPlanRequest request) {
        // 1. 获取用户技能
        Resume defaultResume = resumeMapper.findDefaultByUserId(userId);
        List<String> skills = defaultResume != null
            ? Arrays.asList(defaultResume.getSkillTags())
            : List.of();

        // 2. 调用AI生成规划
        Map<String, Object> planData = aiServiceClient.generateCareerPlan(
            skills,
            request != null ? request.getCurrentPosition() : null,
            request != null ? request.getTargetPosition() : null
        );

        // 3. 保存规划到数据库
        CareerPlan careerPlan = new CareerPlan();
        careerPlan.setUserId(userId);
        careerPlan.setPlanTitle(
            (request != null && request.getTargetPosition() != null)
                ? "通往" + request.getTargetPosition() + "的职业规划"
                : "个人职业发展规划"
        );
        careerPlan.setPlanContent(new JSONObject(planData));
        careerPlan.setCurrentSkills(skills.toArray(new String[0]));

        // 提取缺失技能
        List<String> missingSkills = extractMissingSkills(planData);
        careerPlan.setMissingSkills(missingSkills.toArray(new String[0]));

        careerPlanMapper.insert(careerPlan);

        return toResponse(careerPlan);
    }

    private List<String> extractMissingSkills(Map<String, Object> planData) {
        List<String> missing = new ArrayList<>();
        try {
            Map<String, Object> skillGap = (Map<String, Object>) planData.get("skill_gap");
            if (skillGap != null) {
                List<Map<String, Object>> immediate = (List<Map<String, Object>>) skillGap.get("immediate_skills");
                if (immediate != null) {
                    immediate.forEach(s -> missing.add((String) s.get("name")));
                }
                List<Map<String, Object>> recommended = (List<Map<String, Object>>) skillGap.get("recommended_skills");
                if (recommended != null) {
                    recommended.forEach(s -> missing.add((String) s.get("name")));
                }
            }
        } catch (Exception e) {
            log.warn("提取缺失技能失败", e);
        }
        return missing;
    }
}
```

---

# 第四阶段：前端职业规划页面（2小时）

## 核心页面功能

**职业规划主页面包含：**

1. **目标设定区**
   - 当前职位输入
   - 目标职位输入（可选）
   - "生成规划"按钮

2. **技能缺口分析**
   - 急需技能列表（带优先级标签）
   - 推荐技能列表
   - 每个技能显示：名称、优先级、理由、预计学习时间

3. **学习路线图**
   - 分阶段展示（阶段卡片）
   - 每个阶段包含：技能、学习资源、里程碑
   - 使用时间线组件展示

4. **职业发展路径**
   - 多个发展方向（选项卡切换）
   - 每个方向：描述、所需技能、时间线、潜在职位

5. **综合评估**
   - 整体评估文字
   - 关键建议列表（带重要性标识）
   - 预计成长时间

---

# 第16天验收标准

必须完成：

✅ AI职业规划Prompt设计

✅ 技能缺口分析

✅ 学习路线生成（分阶段）

✅ 职业路径推荐（多方向）

✅ 规划结果保存到数据库

✅ 规划历史查看

✅ 规划结果展示页面

✅ 美观的时间线组件

✅ 空状态处理

✅ Git已提交
