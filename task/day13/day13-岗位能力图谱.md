# 第13天开发任务（详细版）

# 项目：智聘星图——基于银河麒麟操作系统的AI智能匹配与能力图谱平台

## 今日目标

实现岗位能力图谱，展示岗位技能要求的关系图，将JD技能要求可视化。

## 今日能力要求

- ECharts Graph配置（熟练）
- 数据转换处理（熟练）

**最终产出：**

```text
backend/.../module/graph/
├──controller/JobGraphController.java
├──service/JobGraphService.java
└──service/JobGraphServiceImpl.java

frontend/src/views/company/
├──JobSkillGraph.vue            # 岗位技能图谱页
└──components/
    └──JobGraphCard.vue          # 岗位图谱卡片

frontend/src/views/user/
├──JobCompareGraph.vue          # 岗位对比图（可选）
└──components/
    └──JobRequirementChart.vue   # 岗位要求分布图
```

---

# 第一阶段：后端岗位图谱接口（1.5小时）

## 任务1：岗位技能关系图

```java
@RestController
@RequestMapping("/api/graph/job")
public class JobGraphController {
    @Autowired
    private JobGraphService jobGraphService;

    /**
     * 获取岗位技能要求图谱
     * 展示该岗位所有技能要求的关系网络
     */
    @GetMapping("/{jobId}/skill-graph")
    public Result<RelationGraphResponse> getJobSkillGraph(@PathVariable Long jobId) {
        return Result.success(jobGraphService.getJobSkillGraph(jobId));
    }

    /**
     * 获取岗位技能要求分布（按类别统计）
     */
    @GetMapping("/{jobId}/skill-distribution")
    public Result<DistributionResponse> getSkillDistribution(@PathVariable Long jobId) {
        return Result.success(jobGraphService.getSkillDistribution(jobId));
    }

    /**
     * 获取岗位匹配度分布
     * 展示该岗位与所有候选人的匹配度统计
     */
    @GetMapping("/{jobId}/match-distribution")
    public Result<List<MatchDistribution>> getMatchDistribution(@PathVariable Long jobId) {
        return Result.success(jobGraphService.getMatchDistribution(jobId));
    }
}
```

## 任务2：Service实现

```java
@Service
public class JobGraphServiceImpl implements JobGraphService {
    @Autowired
    private JobSkillMapper jobSkillMapper;
    @Autowired
    private SkillMapper skillMapper;

    @Override
    public RelationGraphResponse getJobSkillGraph(Long jobId) {
        List<JobSkill> jobSkills = jobSkillMapper.findByJobId(jobId);

        List<GraphNode> nodes = new ArrayList<>();
        List<GraphEdge> edges = new ArrayList<>();

        // 岗位中心节点
        Job job = jobMapper.selectById(jobId);
        nodes.add(GraphNode.builder()
            .id("job_" + jobId)
            .name(job.getTitle())
            .category("岗位")
            .symbolSize(60)
            .itemStyle(ColorStyle.primary())
            .build());

        // 技能节点
        for (JobSkill js : jobSkills) {
            String nodeId = "skill_" + js.getSkillName();
            nodes.add(GraphNode.builder()
                .id(nodeId)
                .name(js.getSkillName())
                .category(js.getRequired() ? "必备技能" : "加分技能")
                .symbolSize(js.getRequired() ? 40 : 25)
                .itemStyle(js.getRequired() ? ColorStyle.danger() : ColorStyle.warning())
                .build());

            // 岗位到技能的连接
            edges.add(GraphEdge.builder()
                .source("job_" + jobId)
                .target(nodeId)
                .value(js.getImportance())
                .build());
        }

        // 技能之间的关联（共现关系）
        for (int i = 0; i < jobSkills.size(); i++) {
            for (int j = i + 1; j < jobSkills.size(); j++) {
                if (hasRelation(jobSkills.get(i).getSkillName(), jobSkills.get(j).getSkillName())) {
                    edges.add(GraphEdge.builder()
                        .source("skill_" + jobSkills.get(i).getSkillName())
                        .target("skill_" + jobSkills.get(j).getSkillName())
                        .value(1)
                        .lineStyle(LineStyle.dashed())
                        .build());
                }
            }
        }

        return RelationGraphResponse.builder()
            .categories(List.of("岗位", "必备技能", "加分技能"))
            .nodes(nodes)
            .edges(edges)
            .build();
    }

    /**
     * 判断两个技能是否有关联
     * 如：Spring Boot 和 Spring Cloud 关联
     */
    private boolean hasRelation(String skill1, String skill2) {
        // 同生态的技能关联
        Map<String, List<String>> relations = Map.of(
            "Java", List.of("Spring Boot", "MyBatis", "Maven"),
            "Spring Boot", List.of("Spring Cloud", "Spring Security"),
            "Vue.js", List.of("ElementPlus", "Vite", "Axios"),
            "Python", List.of("FastAPI", "LangChain", "PyTorch"),
            "Docker", List.of("Kubernetes", "Jenkins")
        );

        return relations.getOrDefault(skill1, List.of()).contains(skill2)
            || relations.getOrDefault(skill2, List.of()).contains(skill1);
    }
}
```

---

# 第二阶段：前端岗位图谱页面（2小时）

## 任务1：岗位技能关系图

```vue
<template>
  <div class="job-graph-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>岗位技能要求图谱</span>
          <span class="job-title">{{ jobInfo.title }}</span>
        </div>
      </template>

      <!-- 图例 -->
      <div class="graph-legend">
        <span><span class="dot primary"></span> 岗位</span>
        <span><span class="dot danger"></span> 必备技能</span>
        <span><span class="dot warning"></span> 加分技能</span>
      </div>

      <!-- 图谱 -->
      <div ref="chartRef" style="width: 100%; height: 500px"></div>
    </el-card>

    <!-- 技能分布饼图 -->
    <el-card class="distribution-card">
      <template #header>
        <span>技能分类分布</span>
      </template>
      <div ref="pieChartRef" style="width: 100%; height: 300px"></div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'

const chartRef = ref<HTMLElement>()

const renderGraph = (data: any) => {
  const chart = echarts.init(chartRef.value!)
  chart.setOption({
    tooltip: {
      formatter: (params: any) => `${params.data.name}<br/>类别: ${params.data.category}`
    },
    series: [{
      type: 'graph',
      layout: 'force',
      force: {
        repulsion: 500,
        edgeLength: [100, 200],
        friction: 0.1
      },
      roam: true,
      draggable: true,
      data: data.nodes,
      edges: data.edges,
      categories: data.categories.map((c: string) => ({ name: c })),
      label: {
        show: true,
        position: 'right',
        fontSize: 12
      },
      emphasis: {
        focus: 'adjacency',
        lineStyle: {
          width: 3
        }
      },
      lineStyle: {
        curveness: 0.3,
        opacity: 0.7
      }
    }]
  })
}
</script>
```

## 任务2：岗位匹配度分布图

```vue
<template>
  <div class="match-distribution">
    <h4>候选人匹配度分布</h4>
    <div ref="chartRef" style="width: 100%; height: 250px"></div>
  </div>
</template>

<script setup lang="ts">
// ECharts 柱状图展示匹配度区间分布
// X轴: 匹配度区间 0-20, 20-40, 40-60, 60-80, 80-100
// Y轴: 人数
// 颜色渐变: 低匹配度(灰色) → 高匹配度(绿色)
</script>
```

---

# 第13天验收标准

必须完成：

✅ 岗位技能关系图展示

✅ 必备技能/加分技能区分

✅ 技能节点可拖拽

✅ 悬停高亮关联节点

✅ 技能分类分布图表

✅ 岗位匹配度分布统计

✅ 无技能时显示友好提示

✅ Git已提交
