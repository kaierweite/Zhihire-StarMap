# 第18天开发任务（详细版）

# 项目：智聘星图——基于银河麒麟操作系统的AI智能匹配与能力图谱平台

## 今日目标

系统优化，修复已知Bug，优化SQL性能，优化页面加载速度，增加Loading状态。

## 今日能力要求

- SQL性能优化（熟练）
- Vue3性能优化（熟练）
- Java性能分析（基础）

**最终产出：**

```text
docs/
├──性能优化报告.md          # 优化前后对比
└──Bug修复清单.md           # Bug修复记录

backend/.../
├──优化后的SQL             # 代码内已优化
├──optimizer/
│   ├──SqlOptimizer.java   # SQL优化建议工具
│   └──CacheManager.java   # 缓存管理器优化
└──common/
    └──aspect/
        └──LogAspect.java  # AOP日志切面（修复）

frontend/
├──优化后的组件            # 按需修改
├──utils/
│   ├──lazyLoad.ts         # 懒加载工具
│   └──performance.ts      # 性能监控
└──components/
    └──SkeletonLoader.vue   # 骨架屏组件
```

---

# 第一阶段：Bug修复（2小时）

## 任务1：已知Bug清单

| # | Bug描述 | 优先级 | 模块 | 修复方案 |
|---|---------|--------|------|----------|
| 1 | 上传头像后不刷新显示 | 高 | 个人中心 | 上传成功后强制刷新用户信息 |
| 2 | 简历删除后技能未同步删除 | 高 | 简历管理 | 级联删除user_skill记录 |
| 3 | 岗位切换状态后列表不更新 | 中 | 岗位管理 | 切换后重新加载列表 |
| 4 | AI解析超时导致前端一直显示"解析中" | 高 | AI解析 | 增加超时检测，超过5分钟标记为失败 |
| 5 | 手机号格式校验不严谨 | 中 | 注册 | 更严格的正则校验 |
| 6 | 密码修改后旧Token仍有效 | 高 | 安全 | 密码修改后踢出旧Token |
| 7 | 企业注册时未创建company记录 | 高 | 注册 | 修复注册逻辑 |
| 8 | 表格分页后序号不连续 | 低 | 全局 | 序号改为(page-1)*size+index |
| 9 | 城市选择器数据不全 | 中 | 岗位 | 补充城市数据 |
| 10 | 日志记录器偶发NPE | 高 | 日志 | 增加空值判断 |

## 任务2：Bug修复示例（AI解析超时检测）

```java
// 增加定时检测解析状态
@Component
public class ParseStatusMonitor {
    @Autowired
    private ResumeMapper resumeMapper;

    private static final long TIMEOUT_MINUTES = 5;

    /**
     * 每3分钟检测一次解析超时
     */
    @Scheduled(fixedRate = 180000)
    public void checkParseTimeout() {
        LocalDateTime timeoutThreshold = LocalDateTime.now().minusMinutes(TIMEOUT_MINUTES);

        // 查询所有解析中且超过5分钟的简历
        List<Resume> timedOut = resumeMapper.selectList(
            Wrappers.<Resume>lambdaQuery()
                .eq(Resume::getParseStatus, 1)  // 解析中
                .lt(Resume::getUpdateTime, timeoutThreshold)
        );

        for (Resume resume : timedOut) {
            log.warn("检测到解析超时: resumeId={}, updateTime={}",
                resume.getId(), resume.getUpdateTime());
            resume.setParseStatus(3);  // 标记为解析失败
            resumeMapper.updateById(resume);
        }
    }
}
```

---

# 第二阶段：SQL性能优化（1.5小时）

## 任务1：慢SQL分析与优化

```sql
-- 优化前：未使用索引，全表扫描
SELECT * FROM match_result ORDER BY create_time DESC;

-- 优化后：限定范围 + 索引
SELECT * FROM match_result
WHERE create_time > NOW() - INTERVAL ''30 days''
ORDER BY create_time DESC
LIMIT 100;

-- 优化前：N+1查询问题
-- 循环中逐条查询用户技能
for (UserSkill skill : userSkillList) {
    Skill dict = skillMapper.selectById(skill.getSkillId());
}

-- 优化后：一次性批量查询
List<Long> skillIds = userSkillList.stream()
    .map(UserSkill::getSkillId).toList();
List<Skill> skills = skillMapper.selectBatchIds(skillIds);
Map<Long, Skill> skillMap = skills.stream()
    .collect(Collectors.toMap(Skill::getId, Function.identity()));

-- 优化前：大表分页偏移大
SELECT * FROM system_log ORDER BY id LIMIT 10 OFFSET 100000;

-- 优化后：游标分页/子查询优化
SELECT * FROM system_log
WHERE id > (SELECT id FROM system_log ORDER BY id LIMIT 1 OFFSET 100000)
ORDER BY id LIMIT 10;
```

## 任务2：添加@Cacheable缓存

```java
@Service
@CacheConfig(cacheNames = "dictionary")
public class SkillServiceImpl implements SkillService {

    @Override
    @Cacheable(key = "'all_skills'")
    public List<Skill> getAllSkills() {
        // 技能字典变化少，适合缓存
        return skillMapper.selectList(null);
    }

    @Override
    @CacheEvict(key = "'all_skills'")
    public void addSkill(Skill skill) {
        skillMapper.insert(skill);
    }
}
```

---

# 第三阶段：前端性能优化（1.5小时）

## 任务1：代码分割和懒加载

```typescript
// router/index.ts - 路由懒加载
const routes = [
  {
    path: '/admin',
    component: () => import('@/layouts/AdminLayout.vue'),
    children: [
      {
        path: 'dashboard',
        // 按路由分割代码，减小首屏加载体积
        component: () => import(/* webpackChunkName: "admin-dashboard" */ '@/views/admin/AdminDashboard.vue')
      },
      {
        path: 'users',
        component: () => import(/* webpackChunkName: "admin-user" */ '@/views/admin/UserManagement.vue')
      }
    ]
  }
]
```

## 任务2：骨架屏组件

```vue
<template>
  <div class="skeleton-container">
    <!-- 统计卡片骨架 -->
    <div class="skeleton-row">
      <div v-for="i in 4" :key="i" class="skeleton-card">
        <div class="skeleton-title"></div>
        <div class="skeleton-value"></div>
      </div>
    </div>
    <!-- 图表骨架 -->
    <div class="skeleton-chart">
      <div class="skeleton-line"></div>
    </div>
    <!-- 表格骨架 -->
    <div class="skeleton-table">
      <div v-for="i in 5" :key="i" class="skeleton-row-item">
        <div v-for="j in 4" :key="j" class="skeleton-cell"></div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.skeleton {
  &-card, &-chart, &-table {
    background: #f0f0f0;
    border-radius: 8px;
    animation: shimmer 1.5s infinite;
    @keyframes shimmer {
      0% { opacity: 0.6; }
      50% { opacity: 1; }
      100% { opacity: 0.6; }
    }
  }
}
</style>
```

## 任务3：图片懒加载

```typescript
// 使用VueUse的懒加载
import { useIntersectionObserver } from '@vueuse/core'

const avatarRef = ref(null)
const showAvatar = ref(false)

useIntersectionObserver(avatarRef, ([{ isIntersecting }]) => {
  if (isIntersecting) {
    showAvatar.value = true
  }
})
```

---

# 第四阶段：加载状态和错误处理（1小时）

## 任务1：统一Loading封装

```typescript
// 全局Loading封装
import { ElLoading } from 'element-plus'

let loadingInstance: any = null

export const showLoading = (text = '加载中...') => {
  loadingInstance = ElLoading.service({
    lock: true,
    text,
    background: 'rgba(255, 255, 255, 0.8)',
    customClass: 'custom-loading'
  })
}

export const hideLoading = () => {
  if (loadingInstance) {
    loadingInstance.close()
    loadingInstance = null
  }
}

// 配合axios使用
request.interceptors.request.use(
  config => {
    if (!config.hideLoading) {
      showLoading()
    }
    return config
  }
)

request.interceptors.response.use(
  response => {
    hideLoading()
    return response
  },
  error => {
    hideLoading()
    return Promise.reject(error)
  }
)
```

---

# 第18天验收标准

必须完成：

✅ 所有已知Bug已修复

✅ 慢SQL已优化

✅ 热点数据已添加缓存

✅ N+1查询问题已解决

✅ 路由懒加载已配置

✅ 全局Loading已覆盖

✅ 骨架屏已添加

✅ 错误边界处理

✅ 性能优化前后对比数据

✅ Git已提交
