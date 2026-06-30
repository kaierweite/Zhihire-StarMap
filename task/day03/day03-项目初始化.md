# 第3天开发任务（详细版）

# 项目：智聘星图——基于银河麒麟操作系统的AI智能匹配与能力图谱平台

## 今日目标

完成前后端项目初始化，构建基础开发框架，打通前后端通信。

## 今日能力要求

- Vue3（熟练）
- Spring Boot（熟练）
- Maven/Gradle（基础）

**最终产出：**

```text
project/
├──frontend/             # Vue3项目（已初始化）
│   ├──src/
│   │   ├──api/          # API封装
│   │   ├──router/       # 路由配置
│   │   ├──stores/       # Pinia状态管理
│   │   ├──utils/        # 工具函数
│   │   └──App.vue
│   ├──vite.config.ts    # Vite配置
│   └──package.json
├──backend/              # SpringBoot项目（已初始化）
│   ├──src/main/java/
│   │   └──com/zhihire/
│   │       ├──common/   # 公共模块
│   │       ├──config/   # 配置类
│   │       ├──module/   # 业务模块
│   │       └──ZhihireApplication.java
│   └──pom.xml
└──ai-service/           # Python项目（目录结构）
```

---

# 第一阶段：前端初始化（2小时）

## 任务1：创建Vue3项目

```bash
npm create vite@latest frontend -- --template vue-ts
cd frontend
```

## 任务2：安装核心依赖

```bash
# UI框架
npm install element-plus
npm install @element-plus/icons-vue

# 状态管理
npm install pinia

# 路由
npm install vue-router@4

# HTTP请求
npm install axios

# 图表
npm install echarts
npm install vue-echarts

# 工具库
npm install dayjs
npm install @vueuse/core
```

## 任务3：目录结构搭建

```text
frontend/src/
├──api/
│   ├──index.ts          # axios封装
│   ├──user.ts           # 用户相关API
│   └──...
├──assets/
│   └──styles/
│       ├──global.scss   # 全局样式
│       ├──variables.scss # 变量定义
│       └──theme.scss    # 主题
├──components/           # 公共组件
│   ├──AppHeader.vue
│   ├──AppSidebar.vue
│   └──...
├──layouts/              # 布局组件
│   ├──DefaultLayout.vue
│   ├──UserLayout.vue
│   └──AdminLayout.vue
├──router/
│   └──index.ts          # 路由配置
├──stores/
│   ├──user.ts           # 用户状态
│   └──app.ts            # 应用状态
├──utils/
│   ├──auth.ts           # 鉴权工具
│   ├──format.ts         # 格式化
│   └──validate.ts       # 表单校验
├──views/                # 页面
│   ├──login/
│   ├──user/
│   └──...
├──App.vue
├──main.ts
└──env.d.ts
```

## 任务4：基础配置

### vite.config.ts

```typescript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src')
    }
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: true
      }
    }
  }
})
```

### Axios封装

```typescript
// src/api/index.ts
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'

const request = axios.create({
  baseURL: '/api',
  timeout: 30000
})

// 请求拦截器
request.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => Promise.reject(error)
)

// 响应拦截器
request.interceptors.response.use(
  response => {
    const res = response.data
    if (res.code !== 200) {
      ElMessage.error(res.message || '请求失败')
      return Promise.reject(res)
    }
    return res
  },
  error => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    ElMessage.error(error.message || '网络错误')
    return Promise.reject(error)
  }
)

export default request
```

### Router配置

```typescript
// src/router/index.ts
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/login/LoginPage.vue')
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/login/RegisterPage.vue')
  },
  {
    path: '/',
    component: () => import('@/layouts/DefaultLayout.vue'),
    children: [
      { path: '', redirect: '/dashboard' },
      { path: 'dashboard', name: 'Dashboard', component: () => import('@/views/dashboard/UserDashboard.vue') }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (to.name !== 'Login' && to.name !== 'Register' && !token) {
    next('/login')
  } else {
    next()
  }
})

export default router
```

---

# 第二阶段：后端初始化（3小时）

## 任务1：创建SpringBoot项目

使用 Spring Initializr 或手动创建。

### pom.xml（核心依赖）

```xml
<dependencies>
    <!-- Web -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
    </dependency>

    <!-- MyBatis Plus -->
    <dependency>
        <groupId>com.baomidou</groupId>
        <artifactId>mybatis-plus-boot-starter</artifactId>
        <version>3.5.5</version>
    </dependency>

    <!-- PostgreSQL -->
    <dependency>
        <groupId>org.postgresql</groupId>
        <artifactId>postgresql</artifactId>
    </dependency>

    <!-- JWT -->
    <dependency>
        <groupId>io.jsonwebtoken</groupId>
        <artifactId>jjwt</artifactId>
        <version>0.9.1</version>
    </dependency>

    <!-- Redis -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-data-redis</artifactId>
    </dependency>

    <!-- 参数校验 -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-validation</artifactId>
    </dependency>

    <!-- Knife4j (接口文档) -->
    <dependency>
        <groupId>com.github.xiaoymin</groupId>
        <artifactId>knife4j-openapi3-jakarta-spring-boot-starter</artifactId>
        <version>4.4.0</version>
    </dependency>

    <!-- Lombok -->
    <dependency>
        <groupId>org.projectlombok</groupId>
        <artifactId>lombok</artifactId>
    </dependency>

    <!-- 工具类 -->
    <dependency>
        <groupId>cn.hutool</groupId>
        <artifactId>hutool-all</artifactId>
        <version>5.8.25</version>
    </dependency>
</dependencies>
```

## 任务2：目录结构搭建

```text
backend/src/main/java/com/zhihire/
├──common/
│   ├──constant/          # 常量
│   ├──exception/         # 异常处理
│   │   ├──GlobalExceptionHandler.java
│   │   └──BusinessException.java
│   ├──result/            # 统一返回
│   │   ├──Result.java
│   │   └──PageResult.java
│   └──utils/
│       ├──JwtUtils.java
│       └──PasswordUtils.java
├──config/
│   ├──MyBatisPlusConfig.java
│   ├──RedisConfig.java
│   ├──CorsConfig.java
│   ├──Knife4jConfig.java
│   └──JacksonConfig.java
├──module/
│   ├──user/
│   │   ├──controller/
│   │   ├──service/
│   │   ├──mapper/
│   │   ├──entity/
│   │   └──dto/
│   └──...
└──ZhihireApplication.java
```

## 任务3：核心配置

### application.yml

```yaml
server:
  port: 8080

spring:
  datasource:
    url: jdbc:postgresql://localhost:5432/zhihire
    username: postgres
    password: 123456
    driver-class-name: org.postgresql.Driver

  data:
    redis:
      host: localhost
      port: 6379
      database: 0

mybatis-plus:
  mapper-locations: classpath:mapper/*.xml
  type-aliases-package: com.zhihire.module
  configuration:
    map-underscore-to-camel-case: true
    log-impl: org.apache.ibatis.logging.stdout.StdOutImpl

jwt:
  secret: zhihire-secret-key-2024
  expiration: 86400000  # 24小时

springdoc:
  api-docs:
    path: /api-docs
  swagger-ui:
    path: /swagger-ui.html
```

### MyBatisPlus配置

```java
@Configuration
@MapperScan("com.zhihire.module.*.mapper")
public class MyBatisPlusConfig {
    @Bean
    public MybatisPlusInterceptor mybatisPlusInterceptor() {
        MybatisPlusInterceptor interceptor = new MybatisPlusInterceptor();
        interceptor.addInnerInterceptor(new PaginationInnerInterceptor(DbType.POSTGRE_SQL));
        return interceptor;
    }
}
```

### 跨域配置

```java
@Configuration
public class CorsConfig implements WebMvcConfigurer {
    @Override
    public void addCorsMappings(CorsRegistry registry) {
        registry.addMapping("/**")
            .allowCredentials(true)
            .allowedOriginPatterns("*")
            .allowedMethods("*")
            .allowedHeaders("*")
            .exposedHeaders("*");
    }
}
```

### 统一结果封装

```java
@Data
public class Result<T> {
    private Integer code;
    private String message;
    private T data;

    public static <T> Result<T> success(T data) {
        Result<T> result = new Result<>();
        result.code = 200;
        result.message = "success";
        result.data = data;
        return result;
    }

    public static <T> Result<T> error(Integer code, String message) {
        Result<T> result = new Result<>();
        result.code = code;
        result.message = message;
        return result;
    }
}
```

---

# 第三阶段：AI服务目录搭建（30分钟）

## 目录结构

```text
ai-service/
├──app/
│   ├──__init__.py
│   ├──main.py              # FastAPI入口
│   ├──config.py            # 配置
│   ├──models/              # 数据模型
│   │   ├──__init__.py
│   │   └──schemas.py
│   ├──services/            # 服务层
│   │   ├──__init__.py
│   │   ├──resume_parser.py # 简历解析
│   │   ├──job_parser.py    # 岗位解析
│   │   ├──skill_extractor.py # 技能抽取
│   │   └──recommender.py   # 推荐算法
│   └──utils/               # 工具
│       ├──__init__.py
│       └──helpers.py
├──requirements.txt
├──Dockerfile
└──.env
```

### 依赖文件

```text
# requirements.txt
fastapi==0.109.0
uvicorn==0.27.0
pydantic==2.5.0
python-multipart==0.0.6
httpx==0.26.0
python-docx==1.1.0
pdfplumber==0.10.3
sentence-transformers==2.2.2
langchain==0.1.5
openai==1.12.0
redis==5.0.1
numpy==1.26.3
scikit-learn==1.4.0
```

### FastAPI入口

```python
# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="智聘星图AI服务", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "ai-service"}
```

---

# 第3天验收标准

必须完成：

✅ 前端项目可运行（npm run dev）

✅ 后端项目可编译（mvn compile）

✅ API接口可访问（Swagger页面）

✅ 前后端代理已配置

✅ AI服务目录已创建

✅ 所有依赖已安装完毕

✅ Git已提交

---

# 常见问题

**Q：端口冲突怎么办？**

A：前端3000，后端8080，AI服务8000。如果被占用可以修改配置。

**Q：PostgreSQL连不上？**

A：检查数据库是否启动，用户名密码是否正确，数据库zhihire是否已创建。

**Q：Maven下载依赖慢？**

A：配置阿里云镜像仓库。

**Q：Node版本要求？**

A：Node >= 18，推荐使用LTS版本。
