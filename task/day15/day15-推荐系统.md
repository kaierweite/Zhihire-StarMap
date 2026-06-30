# 第15天开发任务（详细版）

# 项目：智聘星图——基于银河麒麟操作系统的AI智能匹配与能力图谱平台

## 今日目标

实现完整的推荐系统，为用户推荐岗位，为企业推荐人才，展示推荐结果页面。

## 今日能力要求

- 推荐系统集成（熟练）
- 缓存优化（基础）
- 前端推荐列表展示（熟练）

**最终产出：**

```text
backend/.../module/recommend/
├──controller/RecommendController.java
├──service/
│   ├──JobRecommendService.java       # 岗位推荐服务
│   ├──JobRecommendServiceImpl.java
│   ├──CandidateRecommendService.java # 人才推荐服务
│   └──impl/CandidateRecommendServiceImpl.java
├──dto/
│   ├──JobRecommendResponse.java
│   └──CandidateRecommendResponse.java
└──client/RecommendAiClient.java

frontend/src/views/user/
├──JobRecommend.vue           # 岗位推荐页
└──components/
    ├──RecommendCard.vue      # 推荐卡片组件
    ├──MatchScore.vue         # 匹配度分数组件
    └──MatchDetail.vue        # 匹配详情弹窗

frontend/src/views/company/
└──CandidateRecommend.vue     # 人才推荐页
```

---

# 第一阶段：后端推荐接口（2.5小时）

## 任务1：岗位推荐（给用户推岗位）

```java
@RestController
@RequestMapping("/api/recommend")
public class RecommendController {
    @Autowired
    private JobRecommendService jobRecommendService;
    @Autowired
    private CandidateRecommendService candidateRecommendService;

    /**
     * 为用户推荐岗位（Top-N）
     */
    @GetMapping("/jobs")
    public Result<List<JobRecommendResponse>> recommendJobs(
        @UserId Long userId,
        @RequestParam(defaultValue = "10") int limit) {
        return Result.success(jobRecommendService.recommendJobs(userId, limit));
    }

    /**
     * 为企业推荐候选人（Top-N）
     */
    @GetMapping("/candidates")
    public Result<List<CandidateRecommendResponse>> recommendCandidates(
        @UserId Long userId,
        @RequestParam Long jobId,
        @RequestParam(defaultValue = "10") int limit) {
        return Result.success(candidateRecommendService.recommendCandidates(userId, jobId, limit));
    }

    /**
     * 重新计算推荐（清除缓存后重算）
     */
    @PostMapping("/refresh")
    public Result<Void> refreshRecommend(@UserId Long userId) {
        jobRecommendService.refreshCache(userId);
        return Result.success(null);
    }
}
```

## 任务2：岗位推荐服务

```java
@Service
public class JobRecommendServiceImpl implements JobRecommendService {
    @Autowired
    private ResumeMapper resumeMapper;
    @Autowired
    private JobMapper jobMapper;
    @Autowired
    private MatchResultMapper matchResultMapper;
    @Autowired
    private RecommendAiClient recommendAiClient;
    @Autowired
    private RedisTemplate<String, Object> redisTemplate;

    private static final String CACHE_KEY = "recommend:jobs:";

    @Override
    public List<JobRecommendResponse> recommendJobs(Long userId, int limit) {
        // 1. 尝试从缓存获取
        String cacheKey = CACHE_KEY + userId;
        List<JobRecommendResponse> cached = (List<JobRecommendResponse>)
            redisTemplate.opsForValue().get(cacheKey);
        if (cached != null) {
            return cached;
        }

        // 2. 获取用户画像
        UserProfile profile = buildUserProfile(userId);
        if (profile == null) {
            return List.of();  // 用户没有简历，无法推荐
        }

        // 3. 获取所有活跃岗位
        List<Job> activeJobs = jobMapper.findActiveJobs();

        // 4. 批量调用AI推荐服务
        List<Map<String, Object>> jobProfiles = activeJobs.stream()
            .map(this::buildJobProfile)
            .toList();

        List<Map<String, Object>> results =
            recommendAiClient.batchRecommend(profile.toMap(), jobProfiles);

        // 5. 转换为响应并保存匹配结果
        List<JobRecommendResponse> recommendations = results.stream()
            .map(r -> {
                JobRecommendResponse response = convertToResponse(r, activeJobs);
                saveMatchResult(userId, response);
                return response;
            })
            .limit(limit)
            .toList();

        // 6. 缓存结果（30分钟过期）
        redisTemplate.opsForValue().set(cacheKey, recommendations, 30, TimeUnit.MINUTES);

        return recommendations;
    }

    private UserProfile buildUserProfile(Long userId) {
        // 获取用户默认简历
        Resume defaultResume = resumeMapper.findDefaultByUserId(userId);
        if (defaultResume == null) return null;

        return UserProfile.builder()
            .userId(userId)
            .skills(Arrays.asList(defaultResume.getSkillTags()))
            .experienceYears(defaultResume.getExperienceYears())
            .education(defaultResume.getEducation())
            .city(extractCity(defaultResume))
            .build();
    }

    private void saveMatchResult(Long userId, JobRecommendResponse response) {
        MatchResult matchResult = new MatchResult();
        matchResult.setUserId(userId);
        matchResult.setJobId(response.getJobId());
        matchResult.setMatchScore(response.getMatchScore());
        matchResult.setSkillScore(response.getSkillScore());
        matchResult.setExperienceScore(response.getExperienceScore());
        matchResult.setEducationScore(response.getEducationScore());
        matchResult.setCityScore(response.getCityScore());
        matchResult.setMatchType("auto");
        matchResultMapper.insert(matchResult);
    }
}
```

## 任务3：人才推荐Service（为企业推荐候选人）

```java
@Service
public class CandidateRecommendServiceImpl implements CandidateRecommendService {
    @Override
    public List<CandidateRecommendResponse> recommendCandidates(
        Long userId, Long jobId, int limit) {

        // 1. 获取岗位要求
        Job job = jobMapper.selectById(jobId);
        Map<String, Object> jobProfile = buildJobProfile(job);

        // 2. 获取所有有简历的用户
        List<Resume> allResumes = resumeMapper.findParsedResumes();

        // 3. 计算匹配度（可并行处理）
        List<CandidateRecommendResponse> candidates = allResumes.parallelStream()
            .map(resume -> {
                UserProfile profile = buildUserProfileFromResume(resume);
                Map<String, Object> matchResult =
                    recommendAiClient.calculateMatch(profile.toMap(), jobProfile);

                return CandidateRecommendResponse.builder()
                    .userId(resume.getUserId())
                    .realName(resume.getRealName())
                    .matchScore((BigDecimal) matchResult.get("total_score"))
                    .matchedSkills((List<String>) matchResult.get("matched_skills"))
                    .missingSkills((List<String>) matchResult.get("missing_skills"))
                    .resumeId(resume.getId())
                    .build();
            })
            .sorted((a, b) -> b.getMatchScore().compareTo(a.getMatchScore()))
            .limit(limit)
            .toList();

        return candidates;
    }
}
```

---

# 第二阶段：前端推荐页面（2.5小时）

## 任务1：岗位推荐页面

```vue
<template>
  <div class="recommend-container">
    <!-- 匹配概览 -->
    <el-card class="overview-card">
      <div class="overview-content">
        <div class="overview-left">
          <h3>智能岗位推荐</h3>
          <p>基于你的技能和经验，为你推荐以下岗位</p>
        </div>
        <div class="overview-right">
          <div class="stat-item">
            <span class="stat-value">{{ recommendations.length }}</span>
            <span class="stat-label">推荐岗位</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">{{ highMatchCount }}</span>
            <span class="stat-label">高度匹配</span>
          </div>
          <el-button @click="refreshRecommend" :loading="refreshing">刷新推荐</el-button>
        </div>
      </div>
    </el-card>

    <!-- 推荐列表 -->
    <div class="recommend-list">
      <el-card
        v-for="(item, index) in recommendations"
        :key="item.jobId"
        class="recommend-card"
        :class="{ 'high-match': item.matchScore >= 80 }"
      >
        <div class="card-content">
          <!-- 排名 -->
          <div class="rank-badge" :class="getRankClass(index)">
            {{ index + 1 }}
          </div>

          <!-- 岗位信息 -->
          <div class="job-info">
            <h4>{{ item.jobTitle }}</h4>
            <p class="company-name">{{ item.companyName }}</p>
            <div class="job-tags">
              <el-tag>{{ item.city }}</el-tag>
              <el-tag type="success">{{ item.salaryRange }}</el-tag>
              <el-tag type="info">{{ item.experienceMin }}年以上</el-tag>
              <el-tag type="warning">{{ item.education }}</el-tag>
            </div>
          </div>

          <!-- 匹配度 -->
          <div class="match-section">
            <MatchScore :score="item.matchScore" :size="80" />
            <el-button type="primary" @click="showMatchDetail(item)">查看详情</el-button>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 空状态 -->
    <el-empty v-if="!loading && recommendations.length === 0" description="暂无推荐岗位">
      <el-button type="primary" @click="goToResume">先去上传简历</el-button>
    </el-empty>
  </div>
</template>
```

## 任务2：匹配详情弹窗

```vue
<template>
  <el-dialog v-model="visible" title="匹配详情" width="600px">
    <!-- 总分展示 -->
    <div class="total-score-section">
      <MatchScore :score="detail.matchScore" :size="100" />
      <div class="score-text">
        <h3>{{ detail.jobTitle }}</h3>
        <p>匹配度 {{ detail.matchScore }}%</p>
      </div>
    </div>

    <!-- 四维评分 -->
    <el-descriptions title="各维度评分" :column="2" border>
      <el-descriptions-item label="技能匹配" :span="2">
        <div class="dimension-score">
          <el-progress :percentage="detail.skillScore" :color="scoreColor(detail.skillScore)" />
        </div>
      </el-descriptions-item>
      <el-descriptions-item label="经验匹配" :span="2">
        <div class="dimension-score">
          <el-progress :percentage="detail.experienceScore" :color="scoreColor(detail.experienceScore)" />
        </div>
      </el-descriptions-item>
      <el-descriptions-item label="学历匹配" :span="2">
        <div class="dimension-score">
          <el-progress :percentage="detail.educationScore" :color="scoreColor(detail.educationScore)" />
        </div>
      </el-descriptions-item>
      <el-descriptions-item label="城市匹配" :span="2">
        <div class="dimension-score">
          <el-progress :percentage="detail.cityScore" :color="scoreColor(detail.cityScore)" />
        </div>
      </el-descriptions-item>
    </el-descriptions>

    <!-- 技能对比 -->
    <div class="skill-comparison">
      <h4>技能对比</h4>
      <div class="skill-section">
        <span class="section-label">已匹配技能：</span>
        <el-tag v-for="skill in detail.matchedSkills" :key="skill" type="success" class="skill-tag">
          {{ skill }}
        </el-tag>
      </div>
      <div class="skill-section">
        <span class="section-label">缺失技能：</span>
        <el-tag v-for="skill in detail.missingSkills" :key="skill" type="danger" class="skill-tag">
          {{ skill }}
        </el-tag>
      </div>
    </div>
  </el-dialog>
</template>
<script setup lang="ts">
const scoreColor = (score: number) => {
  if (score >= 80) return '#67c23a'  // 绿色
  if (score >= 60) return '#e6a23c'  // 黄色
  return '#f56c6c'  // 红色
}
</script>
```

---

# 第15天验收标准

必须完成：

✅ 为用户推荐岗位（Top-10）

✅ 为企业推荐候选人（Top-10）

✅ 推荐结果按匹配度排序

✅ 匹配详情展示（四维评分）

✅ 技能对比展示（匹配/缺失）

✅ Redis缓存加速

✅ 空状态处理（无简历/无岗位）

✅ 推荐结果保存到数据库

✅ Git已提交
