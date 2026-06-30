# 第12天开发任务（详细版）

# 项目：智聘星图——基于银河麒麟操作系统的AI智能匹配与能力图谱平台

## 今日目标

实现个人能力图谱页面，包括技能树、雷达图、关系图三种可视化展示方式。

## 今日能力要求

- ECharts配置（熟练）
- networkx基础（了解）
- Vue3组件封装（熟练）

**最终产出：**

```text
backend/.../module/graph/
├──controller/GraphController.java
├──service/GraphService.java
├──service/GraphServiceImpl.java
├──dto/
│   ├──SkillGraphResponse.java
│   └──RadarDataResponse.java

ai-service/app/services/
└──graph_service.py             # 图谱计算服务

frontend/src/views/user/
├──SkillGraph.vue               # 能力图谱主页
├──components/
│   ├──SkillTree.vue            # 技能树组件
│   ├──SkillRadar.vue           # 雷达图组件
│   ├──SkillRelationGraph.vue   # 技能关系图组件
│   └──GraphLegend.vue          # 图例组件

frontend/src/api/
└──graph.ts                     # 图谱API
```

---

# 第一阶段：后端图谱接口（1.5小时）

## 任务1：技能树接口

```java
@RestController
@RequestMapping("/api/graph")
public class GraphController {
    @Autowired
    private GraphService graphService;

    /**
     * 获取用户技能树数据
     * 返回树形结构，用于展示技能层级关系
     */
    @GetMapping("/skill-tree")
    public Result<SkillTreeResponse> getSkillTree(@UserId Long userId) {
        return Result.success(graphService.getSkillTree(userId));
    }

    /**
     * 获取用户技能雷达图数据
     * 按技能分类统计，用于展示综合能力
     */
    @GetMapping("/radar")
    public Result<RadarResponse> getRadarData(@UserId Long userId) {
        return Result.success(graphService.getRadarData(userId));
    }

    /**
     * 获取技能关系图数据
     * 展示技能之间的关联关系
     */
    @GetMapping("/relation")
    public Result<RelationGraphResponse> getRelationGraph(@UserId Long userId) {
        return Result.success(graphService.getRelationGraph(userId));
    }
}
```

## 任务2：图谱Service

```java
@Service
public class GraphServiceImpl implements GraphService {
    @Autowired
    private UserSkillMapper userSkillMapper;
    @Autowired
    private SkillMapper skillMapper;

    @Override
    public SkillTreeResponse getSkillTree(Long userId) {
        // 获取用户技能
        List<UserSkill> userSkills = userSkillMapper.findByUserId(userId);

        // 构建技能树
        // Java → Spring Boot → Spring Cloud
        // Python → FastAPI → LangChain
        // 前端 → Vue.js → ElementPlus
        List<SkillTreeNode> children = new ArrayList<>();

        // 按一级分类分组
        Map<String, List<UserSkill>> grouped = userSkills.stream()
            .collect(Collectors.groupingBy(s -> getSkillCategory(s.getSkillName())));

        for (Map.Entry<String, List<UserSkill>> entry : grouped.entrySet()) {
            SkillTreeNode categoryNode = SkillTreeNode.builder()
                .name(entry.getKey())
                .children(entry.getValue().stream()
                    .map(s -> SkillTreeNode.builder()
                        .name(s.getSkillName())
                        .value(s.getLevel())
                        .build())
                    .toList())
                .build();
            children.add(categoryNode);
        }

        return SkillTreeResponse.builder()
            .name("能力图谱")
            .children(children)
            .build();
    }

    @Override
    public RadarResponse getRadarData(Long userId) {
        List<UserSkill> userSkills = userSkillMapper.findByUserId(userId);

        // 按分类计算各维度平均值
        Map<String, Double> categoryScores = new HashMap<>();
        Map<String, Integer> categoryCounts = new HashMap<>();

        for (UserSkill skill : userSkills) {
            String category = getSkillCategory(skill.getSkillName());
            categoryScores.merge(category, (double) skill.getLevel(), Double::sum);
            categoryCounts.merge(category, 1, Integer::sum);
        }

        List<RadarDimension> dimensions = categoryScores.entrySet().stream()
            .map(entry -> RadarDimension.builder()
                .name(entry.getKey())
                .score(entry.getValue() / categoryCounts.get(entry.getKey()))
                .maxScore(5)
                .build())
            .toList();

        return RadarResponse.builder()
            .dimensions(dimensions)
            .build();
    }

    /**
     * 根据技能名称判断所属分类
     */
    private String getSkillCategory(String skillName) {
        // Java生态
        if (skillName.matches("Java|Spring.*|MyBatis|Maven|Gradle")) return "后端开发";
        // 前端
        if (skillName.matches("Vue.*|React|JavaScript|TypeScript|HTML|CSS")) return "前端开发";
        // AI
        if (skillName.matches("Python|PyTorch|TensorFlow|LangChain|NLP|CV")) return "人工智能";
        // 数据库
        if (skillName.matches("MySQL|PostgreSQL|Redis|MongoDB|Elasticsearch")) return "数据库";
        // DevOps
        if (skillName.matches("Docker|K8s|Jenkins|Git|CI/CD")) return "DevOps";
        return "其他";
    }
}
```

---

# 第二阶段：AI服务图谱计算（1小时）

```python
# graph_service.py
import networkx as nx
from typing import List, Dict

class GraphService:
    def __init__(self):
        self.graph = nx.Graph()

    def build_skill_relation_graph(self, skills: List[str]) -> Dict:
        """
        构建技能关系图
        基于技能共现关系和预定义的技能层级构建
        """
        self.graph.clear()

        # 预定义的技能关系
        skill_relations = {
            "Java": ["Spring Boot", "MyBatis", "Maven", "Gradle"],
            "Spring Boot": ["Spring Cloud", "Spring Security", "JPA"],
            "Python": ["FastAPI", "Django", "LangChain", "PyTorch"],
            "Vue.js": ["ElementPlus", "Vite", "Pinia", "Vue Router"],
            "React": ["Next.js", "Ant Design", "Redux"],
            "Docker": ["Kubernetes", "Docker Compose", "Jenkins"],
            "MySQL": ["PostgreSQL", "MyBatis", "JPA"],
            "Redis": ["Spring Cache", "Session", "Redisson"],
        }

        # 添加用户技能节点
        for skill in skills:
            self.graph.add_node(skill, category=self._get_category(skill))

        # 添加关系边
        for skill in skills:
            related = skill_relations.get(skill, [])
            for rel in related:
                if rel in skills:
                    self.graph.add_edge(skill, rel, weight=2)
                else:
                    self.graph.add_edge(skill, rel, weight=1, style="dashed")

        # 转换为ECharts Graph格式
        nodes = []
        for node, data in self.graph.nodes(data=True):
            nodes.append({
                "id": node,
                "name": node,
                "category": data.get("category", "其他"),
                "symbolSize": 30 + (skills.count(node) * 10)
            })

        edges = []
        for u, v, data in self.graph.edges(data=True):
            edges.append({
                "source": u,
                "target": v,
                "value": data.get("weight", 1),
                "lineStyle": {
                    "type": "solid" if data.get("style") != "dashed" else "dashed"
                }
            })

        return {"nodes": nodes, "edges": edges}

    def _get_category(self, skill: str) -> str:
        categories = {
            "Java": "后端", "Python": "AI", "Vue.js": "前端",
            "React": "前端", "Docker": "DevOps", "MySQL": "数据库",
            "Redis": "数据库", "Spring": "后端"
        }
        for key, value in categories.items():
            if key.lower() in skill.lower():
                return value
        return "其他"
```

---

# 第三阶段：前端图谱页面（2.5小时）

## 任务1：技能树组件（ECharts Tree）

```vue
<template>
  <div ref="chartRef" :style="{ width: '100%', height: '400px' }"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import * as echarts from 'echarts'

const props = defineProps<{ data: any }>()
const chartRef = ref<HTMLElement>()

const renderChart = () => {
  const chart = echarts.init(chartRef.value!)
  chart.setOption({
    tooltip: { trigger: 'item', triggerOn: 'mousemove' },
    series: [{
      type: 'tree',
      data: [props.data],
      top: '5%',
      left: '10%',
      bottom: '5%',
      right: '20%',
      symbolSize: 10,
      label: {
        position: 'left',
        verticalAlign: 'middle',
        align: 'right',
        fontSize: 13
      },
      leaves: {
        label: {
          position: 'right',
          verticalAlign: 'middle',
          align: 'left'
        }
      },
      expandAndCollapse: true,
      animationDuration: 550,
      animationDurationUpdate: 750
    }]
  })
}

onMounted(renderChart)
watch(() => props.data, renderChart)
</script>
```

## 任务2：雷达图组件

```vue
<template>
  <div ref="chartRef" :style="{ width: '100%', height: '400px' }"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import * as echarts from 'echarts'

const props = defineProps<{
  dimensions: { name: string; score: number; maxScore: number }[]
}>()
const chartRef = ref<HTMLElement>()

const renderChart = () => {
  const chart = echarts.init(chartRef.value!)
  chart.setOption({
    radar: {
      indicator: props.dimensions.map(d => ({
        name: d.name,
        max: d.maxScore
      })),
      shape: 'circle',
      splitArea: {
        areaStyle: {
          color: ['rgba(102, 126, 234, 0.1)', 'rgba(102, 126, 234, 0.2)']
        }
      },
      axisLine: { lineStyle: { color: 'rgba(102, 126, 234, 0.5)' } }
    },
    series: [{
      type: 'radar',
      data: [{
        value: props.dimensions.map(d => d.score),
        name: '能力评估',
        areaStyle: {
          color: 'rgba(102, 126, 234, 0.4)'
        },
        lineStyle: {
          color: '#667eea',
          width: 2
        }
      }]
    }]
  })
}

onMounted(renderChart)
watch(() => props.dimensions, renderChart, { deep: true })
</script>
```

## 任务3：技能关系图组件

Vue组件使用ECharts Graph类型展示技能关系网络，支持节点拖拽、缩放等交互。

**配置要点：**

- 节点大小按重要性缩放
- 颜色按分类区分
- 实线表示强关联（同项目使用）
- 虚线表示弱关联（生态相关）
- 悬停高亮关联节点
- 自适应布局

---

# 第12天验收标准

必须完成：

✅ 技能树完整展示（含层级关系）

✅ 雷达图按分类展示能力评分

✅ 技能关系图展示技能关联

✅ 图谱数据来自用户真实技能

✅ 图表可交互（缩放/悬停/点击）

✅ 无技能时显示空状态

✅ 响应式布局

✅ Git已提交
