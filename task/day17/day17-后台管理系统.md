# 第17天开发任务（详细版）

# 项目：智聘星图——基于银河麒麟操作系统的AI智能匹配与能力图谱平台

## 今日目标

完成后台管理系统，包括用户管理、企业管理、数据统计、日志查看四大模块。

## 今日能力要求

- 后台管理CRUD（熟练）
- ECharts数据可视化（熟练）
- 权限控制（基础）

**最终产出：**

```text
backend/.../module/admin/
├──controller/
│   ├──AdminUserController.java       # 用户管理
│   ├──AdminCompanyController.java    # 企业管理
│   ├──AdminStatsController.java      # 数据统计
│   └──AdminLogController.java        # 日志管理
├──service/
│   ├──AdminUserService.java
│   ├──AdminStatsService.java
│   └──impl/
├──dto/
│   ├──UserManageResponse.java
│   ├──CompanyManageResponse.java
│   ├──DashboardStatsResponse.java
│   └──LogResponse.java
├──mapper/
│   └──SystemLogMapper.java
└──entity/
    └──SystemLog.java

frontend/src/views/admin/
├──AdminDashboard.vue              # 管理首页/数据统计
├──UserManagement.vue              # 用户管理
├──UserDetail.vue                  # 用户详情
├──CompanyManagement.vue           # 企业管理
├──CompanyDetail.vue               # 企业详情
├──SystemLog.vue                   # 系统日志
└──components/
    ├──StatsCard.vue               # 统计卡片
    ├──UserTable.vue               # 用户表格
    └──LogFilter.vue               # 日志筛选组件
```

---

# 第一阶段：后端管理接口（3小时）

## 任务1：用户管理

```java
@RestController
@RequestMapping("/api/admin/user")
public class AdminUserController {
    @Autowired
    private AdminUserService adminUserService;

    /**
     * 用户列表（分页 + 搜索 + 筛选）
     */
    @GetMapping("/list")
    public Result<PageResult<UserManageResponse>> list(
        @RequestParam(defaultValue = "1") int page,
        @RequestParam(defaultValue = "15") int size,
        @RequestParam(required = false) String keyword,
        @RequestParam(required = false) String role,
        @RequestParam(required = false) Integer status) {

        return Result.success(adminUserService.listUsers(page, size, keyword, role, status));
    }

    /**
     * 用户详情
     */
    @GetMapping("/{id}")
    public Result<UserManageResponse> detail(@PathVariable Long id) {
        return Result.success(adminUserService.getUserDetail(id));
    }

    /**
     * 启用/禁用用户
     */
    @PutMapping("/{id}/status")
    public Result<Void> toggleStatus(@PathVariable Long id, @RequestParam Integer status) {
        adminUserService.toggleStatus(id, status);
        return Result.success(null);
    }

    /**
     * 删除用户
     */
    @DeleteMapping("/{id}")
    public Result<Void> delete(@PathVariable Long id) {
        adminUserService.deleteUser(id);
        return Result.success(null);
    }
}
```

## 任务2：数据统计接口

```java
@RestController
@RequestMapping("/api/admin/stats")
public class AdminStatsController {
    @Autowired
    private AdminStatsService statsService;

    /**
     * 首页概览数据
     */
    @GetMapping("/dashboard")
    public Result<DashboardStatsResponse> getDashboardStats() {
        return Result.success(statsService.getDashboardStats());
    }

    /**
     * 用户增长趋势（近30天）
     */
    @GetMapping("/user-trend")
    public Result<List<TrendData>> getUserTrend() {
        return Result.success(statsService.getUserTrend(30));
    }

    /**
     * 岗位发布趋势
     */
    @GetMapping("/job-trend")
    public Result<List<TrendData>> getJobTrend() {
        return Result.success(statsService.getJobTrend(30));
    }

    /**
     * 技能分布统计（Top-20技能）
     */
    @GetMapping("/skill-distribution")
    public Result<List<SkillStat>> getSkillDistribution() {
        return Result.success(statsService.getSkillDistribution(20));
    }

    /**
     * 匹配度分布统计
     */
    @GetMapping("/match-distribution")
    public Result<List<DistributionData>> getMatchDistribution() {
        return Result.success(statsService.getMatchDistribution());
    }
}
```

## 任务3：统计Service实现

```java
@Service
public class AdminStatsServiceImpl implements AdminStatsService {
    @Autowired
    private SysUserMapper userMapper;
    @Autowired
    private JobMapper jobMapper;
    @Autowired
    private ResumeMapper resumeMapper;
    @Autowired
    private MatchResultMapper matchResultMapper;

    @Override
    public DashboardStatsResponse getDashboardStats() {
        // 总计数据
        long totalUsers = userMapper.selectCount(null);
        long totalCompanies = userMapper.selectCount(Wrappers.<SysUser>lambdaQuery()
            .eq(SysUser::getRole, "company"));
        long totalJobs = jobMapper.selectCount(null);
        long totalResumes = resumeMapper.selectCount(null);
        long totalMatches = matchResultMapper.selectCount(null);
        long todayNewUsers = userMapper.countTodayNew();
        long todayNewJobs = jobMapper.countTodayNew();

        // 活跃数据（近7天有操作的用户）
        long activeUsers = userMapper.countActiveUsers(7);

        return DashboardStatsResponse.builder()
            .totalUsers(totalUsers)
            .totalCompanies(totalCompanies)
            .totalJobs(totalJobs)
            .totalResumes(totalResumes)
            .totalMatches(totalMatches)
            .todayNewUsers(todayNewUsers)
            .todayNewJobs(todayNewJobs)
            .activeUsers(activeUsers)
            .build();
    }

    @Override
    public List<TrendData> getUserTrend(int days) {
        // 按日期分组统计注册人数
        List<TrendData> trend = new ArrayList<>();
        LocalDate today = LocalDate.now();
        for (int i = days - 1; i >= 0; i--) {
            LocalDate date = today.minusDays(i);
            long count = userMapper.countByDate(date);
            trend.add(TrendData.builder()
                .date(date.toString())
                .value(count)
                .build());
        }
        return trend;
    }

    @Override
    public List<SkillStat> getSkillDistribution(int topN) {
        // 从user_skill表统计技能出现频率
        List<SkillStat> stats = userSkillMapper.countSkillFrequency();
        return stats.stream()
            .sorted((a, b) -> b.getCount().compareTo(a.getCount()))
            .limit(topN)
            .toList();
    }
}
```

---

# 第二阶段：前端管理页面（3小时）

## 任务1：管理首页（数据看板）

```vue
<template>
  <div class="admin-dashboard">
    <!-- 统计卡片 -->
    <el-row :gutter="20">
      <el-col :span="6" v-for="stat in stats" :key="stat.label">
        <StatsCard :stat="stat" />
      </el-col>
    </el-row>

    <!-- 趋势图 -->
    <el-row :gutter="20" class="chart-row">
      <el-col :span="12">
        <el-card>
          <template #header><span>用户增长趋势（近30天）</span></template>
          <div ref="userTrendChart" style="height: 300px"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header><span>岗位发布趋势（近30天）</span></template>
          <div ref="jobTrendChart" style="height: 300px"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 技能分布 -->
    <el-row :gutter="20" class="chart-row">
      <el-col :span="12">
        <el-card>
          <template #header><span>热门技能Top-20</span></template>
          <div ref="skillChart" style="height: 350px"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header><span>匹配度分布</span></template>
          <div ref="matchChart" style="height: 350px"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'
import { getDashboardStats, getUserTrend, getSkillDistribution } from '@/api/admin'

// 统计卡片
const stats = ref([
  { label: '总用户数', value: 0, icon: 'User', color: '#409eff' },
  { label: '企业用户', value: 0, icon: 'OfficeBuilding', color: '#67c23a' },
  { label: '岗位总数', value: 0, icon: 'Briefcase', color: '#e6a23c' },
  { label: '匹配次数', value: 0, icon: 'DataAnalysis', color: '#f56c6c' }
])

// 趋势图（使用ECharts折线图）
const renderTrendChart = (el: HTMLElement, data: any[], color: string) => {
  const chart = echarts.init(el)
  chart.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: data.map(d => d.date.slice(5)) },
    yAxis: { type: 'value', minInterval: 1 },
    series: [{
      type: 'line',
      data: data.map(d => d.value),
      smooth: true,
      areaStyle: { color: color + '30' },
      lineStyle: { color, width: 2 }
    }]
  })
}

// 热门技能（使用ECharts柱状图）
// 匹配度分布（使用饼图）
</script>
```

## 任务2：用户管理页面

```vue
<template>
  <div class="user-management">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>用户管理</span>
          <div class="header-right">
            <el-input v-model="searchKey" placeholder="搜索用户名/手机号" style="width: 200px" clearable />
            <el-select v-model="roleFilter" placeholder="角色" clearable style="width: 120px">
              <el-option label="求职者" value="user" />
              <el-option label="企业" value="company" />
              <el-option label="管理员" value="admin" />
            </el-select>
            <el-select v-model="statusFilter" placeholder="状态" clearable style="width: 100px">
              <el-option label="正常" :value="1" />
              <el-option label="禁用" :value="0" />
            </el-select>
            <el-button type="primary" @click="loadUsers">搜索</el-button>
          </div>
        </div>
      </template>

      <!-- 用户表格 -->
      <el-table :data="userList" v-loading="loading" stripe>
        <el-table-column type="index" label="#" width="50" />
        <el-table-column prop="username" label="用户名" min-width="120" />
        <el-table-column prop="realName" label="姓名" width="100" />
        <el-table-column prop="phone" label="手机号" width="130" />
        <el-table-column prop="email" label="邮箱" min-width="180" />
        <el-table-column label="角色" width="100">
          <template #default="{ row }">
            <el-tag :type="roleType(row.role)" size="small">{{ roleLabel(row.role) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-switch
              :model-value="row.status === 1"
              @change="toggleUserStatus(row)"
              :loading="row._loading"
            />
          </template>
        </el-table-column>
        <el-table-column prop="createTime" label="注册时间" width="180" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button text type="primary" @click="viewUser(row)">详情</el-button>
            <el-popconfirm title="确定删除该用户？" @confirm="handleDelete(row)">
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
          layout="total, sizes, prev, pager, next"
          @change="loadUsers"
        />
      </div>
    </el-card>
  </div>
</template>
```

---

# 第17天验收标准

必须完成：

✅ 用户管理列表（分页+搜索+筛选）

✅ 用户启用/禁用

✅ 用户详情查看

✅ 企业管理列表

✅ 数据看板（4个统计卡片+趋势图）

✅ 热门技能Top-20图

✅ 匹配度分布图

✅ 系统日志查看（分页+筛选）

✅ 管理员权限控制

✅ Git已提交
