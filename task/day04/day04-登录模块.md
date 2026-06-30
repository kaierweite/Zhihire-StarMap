# 第4天开发任务（详细版）

# 项目：智聘星图——基于银河麒麟操作系统的AI智能匹配与能力图谱平台

## 今日目标

完成用户注册、登录功能，实现JWT认证和权限控制。

## 今日能力要求

- Spring Security/JWT（熟练）
- Vue3表单处理（熟练）
- BCrypt加密（了解）

**最终产出：**

```text
frontend/src/views/login/
├──LoginPage.vue          # 登录页
├──RegisterPage.vue       # 注册页
└──ForgetPassword.vue     # 忘记密码（可选）

backend/src/main/java/.../module/auth/
├──controller/AuthController.java
├──service/AuthService.java
├──service/AuthServiceImpl.java
├──dto/LoginRequest.java
├──dto/LoginResponse.java
├──dto/RegisterRequest.java
└──entity/SysUser.java

backend/.../config/security/
├──JwtAuthenticationFilter.java
├──JwtTokenProvider.java
└──SecurityConfig.java
```

---

# 第一阶段：后端JWT工具类（1小时）

## 任务1：JWT工具类

```java
@Component
public class JwtTokenProvider {
    @Value("${jwt.secret}")
    private String secret;

    @Value("${jwt.expiration}")
    private long expiration;

    public String generateToken(Long userId, String username, String role) {
        Date now = new Date();
        Date expiryDate = new Date(now.getTime() + expiration);

        return Jwts.builder()
            .setSubject(userId.toString())
            .claim("username", username)
            .claim("role", role)
            .setIssuedAt(now)
            .setExpiration(expiryDate)
            .signWith(SignatureAlgorithm.HS512, secret)
            .compact();
    }

    public Long getUserIdFromToken(String token) {
        Claims claims = Jwts.parser()
            .setSigningKey(secret)
            .parseClaimsJws(token)
            .getBody();
        return Long.parseLong(claims.getSubject());
    }

    public String getRoleFromToken(String token) {
        Claims claims = Jwts.parser()
            .setSigningKey(secret)
            .parseClaimsJws(token)
            .getBody();
        return claims.get("role", String.class);
    }

    public boolean validateToken(String token) {
        try {
            Jwts.parser().setSigningKey(secret).parseClaimsJws(token);
            return true;
        } catch (JwtException | IllegalArgumentException e) {
            return false;
        }
    }
}
```

## 任务2：JWT认证过滤器

```java
@Component
public class JwtAuthenticationFilter extends OncePerRequestFilter {
    @Autowired
    private JwtTokenProvider jwtTokenProvider;

    @Override
    protected void doFilterInternal(HttpServletRequest request,
                                   HttpServletResponse response,
                                   FilterChain filterChain) throws IOException, ServletException {
        String token = getTokenFromRequest(request);

        if (token != null && jwtTokenProvider.validateToken(token)) {
            Long userId = jwtTokenProvider.getUserIdFromToken(token);
            String role = jwtTokenProvider.getRoleFromToken(token);

            UsernamePasswordAuthenticationToken authentication =
                new UsernamePasswordAuthenticationToken(userId, null, List.of(new SimpleGrantedAuthority("ROLE_" + role)));
            authentication.setDetails(new WebAuthenticationDetailsSource().buildDetails(request));
            SecurityContextHolder.getContext().setAuthentication(authentication);
        }

        filterChain.doFilter(request, response);
    }

    private String getTokenFromRequest(HttpServletRequest request) {
        String bearerToken = request.getHeader("Authorization");
        if (bearerToken != null && bearerToken.startsWith("Bearer ")) {
            return bearerToken.substring(7);
        }
        return null;
    }
}
```

## 任务3：Spring Security配置

```java
@Configuration
@EnableWebSecurity
@EnableMethodSecurity
public class SecurityConfig {
    @Autowired
    private JwtAuthenticationFilter jwtAuthenticationFilter;

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .csrf(AbstractHttpConfigurer::disable)
            .sessionManagement(session -> session.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/api/auth/**").permitAll()
                .requestMatchers("/api/admin/**").hasRole("admin")
                .requestMatchers("/api/company/**").hasAnyRole("company", "admin")
                .anyRequest().authenticated()
            )
            .addFilterBefore(jwtAuthenticationFilter, UsernamePasswordAuthenticationFilter.class);

        return http.build();
    }

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }
}
```

---

# 第二阶段：后端认证接口（2小时）

## 任务1：Controller

```java
@RestController
@RequestMapping("/api/auth")
public class AuthController {
    @Autowired
    private AuthService authService;

    @PostMapping("/register")
    public Result<LoginResponse> register(@Valid @RequestBody RegisterRequest request) {
        return Result.success(authService.register(request));
    }

    @PostMapping("/login")
    public Result<LoginResponse> login(@Valid @RequestBody LoginRequest request) {
        return Result.success(authService.login(request));
    }

    @PostMapping("/refresh")
    public Result<LoginResponse> refreshToken(@RequestHeader("Authorization") String token) {
        return Result.success(authService.refreshToken(token));
    }

    @PostMapping("/logout")
    public Result<Void> logout(@RequestHeader("Authorization") String token) {
        authService.logout(token);
        return Result.success(null);
    }
}
```

## 任务2：Service实现

```java
@Service
public class AuthServiceImpl implements AuthService {
    @Autowired
    private SysUserMapper userMapper;
    @Autowired
    private PasswordEncoder passwordEncoder;
    @Autowired
    private JwtTokenProvider jwtTokenProvider;
    @Autowired
    private RedisTemplate<String, String> redisTemplate;

    @Override
    public LoginResponse register(RegisterRequest request) {
        // 检查用户名是否已存在
        if (userMapper.findByUsername(request.getUsername()) != null) {
            throw new BusinessException(400, "用户名已存在");
        }

        // 创建用户
        SysUser user = new SysUser();
        user.setUsername(request.getUsername());
        user.setPassword(passwordEncoder.encode(request.getPassword()));
        user.setRealName(request.getRealName());
        user.setPhone(request.getPhone());
        user.setEmail(request.getEmail());
        user.setRole(request.getRole() != null ? request.getRole() : "user");
        user.setStatus(1);
        userMapper.insert(user);

        // 如果是企业角色，同时创建企业信息
        if ("company".equals(request.getRole())) {
            SysCompany company = new SysCompany();
            company.setUserId(user.getId());
            company.setCompanyName(request.getCompanyName());
            companyMapper.insert(company);
        }

        // 生成token
        String token = jwtTokenProvider.generateToken(user.getId(), user.getUsername(), user.getRole());

        return LoginResponse.builder()
            .token(token)
            .userId(user.getId())
            .username(user.getUsername())
            .role(user.getRole())
            .build();
    }

    @Override
    public LoginResponse login(LoginRequest request) {
        SysUser user = userMapper.findByUsername(request.getUsername());
        if (user == null) {
            throw new BusinessException(400, "用户名或密码错误");
        }

        if (user.getStatus() == 0) {
            throw new BusinessException(400, "账号已被禁用");
        }

        if (!passwordEncoder.matches(request.getPassword(), user.getPassword())) {
            throw new BusinessException(400, "用户名或密码错误");
        }

        String token = jwtTokenProvider.generateToken(user.getId(), user.getUsername(), user.getRole());

        // token存入Redis（用于后续主动失效）
        redisTemplate.opsForValue().set("token:" + user.getId(), token, 24, TimeUnit.HOURS);

        return LoginResponse.builder()
            .token(token)
            .userId(user.getId())
            .username(user.getUsername())
            .role(user.getRole())
            .realName(user.getRealName())
            .build();
    }
}
```

---

# 第三阶段：前端登录注册页面（2小时）

## 任务1：登录页面

```vue
<template>
  <div class="login-container">
    <div class="login-card">
      <h2 class="login-title">智聘星图</h2>
      <p class="login-subtitle">AI智能匹配与能力图谱平台</p>

      <el-form ref="formRef" :model="loginForm" :rules="rules" size="large">
        <el-form-item prop="username">
          <el-input v-model="loginForm.username" placeholder="请输入用户名" :prefix-icon="User" />
        </el-form-item>

        <el-form-item prop="password">
          <el-input v-model="loginForm.password" type="password" placeholder="请输入密码" :prefix-icon="Lock" show-password />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" size="large" :loading="loading" class="login-btn" @click="handleLogin">
            登 录
          </el-button>
        </el-form-item>
      </el-form>

      <div class="login-footer">
        <span>还没有账号？</span>
        <el-link type="primary" @click="$router.push('/register')">立即注册</el-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import { login } from '@/api/user'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()
const loading = ref(false)

const loginForm = reactive({
  username: '',
  password: ''
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const handleLogin = async () => {
  loading.value = true
  try {
    const res = await login(loginForm)
    userStore.setUserInfo(res.data)
    ElMessage.success('登录成功')

    // 根据角色跳转
    const role = res.data.role
    if (role === 'admin') router.push('/admin/dashboard')
    else if (role === 'company') router.push('/company/dashboard')
    else router.push('/user/dashboard')
  } catch (e) {
    // 错误已在拦截器中处理
  } finally {
    loading.value = false
  }
}
</script>

<style scoped lang="scss">
.login-container {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
  width: 420px;
  padding: 40px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
}

.login-title {
  text-align: center;
  font-size: 28px;
  color: #333;
  margin-bottom: 8px;
}

.login-subtitle {
  text-align: center;
  color: #999;
  margin-bottom: 32px;
  font-size: 14px;
}

.login-btn {
  width: 100%;
}

.login-footer {
  text-align: center;
  margin-top: 16px;
  font-size: 14px;
  color: #666;
}
</style>
```

## 任务2：注册页面

注册页面包含角色选择（个人用户/企业用户），企业用户需填写公司名称。

**功能要点：**

- 用户名唯一性校验（失焦时异步校验）
- 密码强度校验（至少8位，含字母和数字）
- 确认密码校验
- 角色切换（个人/企业）
- 企业注册需填写公司基本信息

## 任务3：路由守卫

```typescript
// 路由守卫补充
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const userStore = useUserStore()

  if (token) {
    // 已登录，但访问登录页则重定向
    if (to.path === '/login' || to.path === '/register') {
      next('/dashboard')
      return
    }

    // 权限校验
    const role = userStore.role
    const requiredRole = to.meta.role
    if (requiredRole && role !== requiredRole && role !== 'admin') {
      ElMessage.warning('无权限访问')
      next('/dashboard')
      return
    }
  } else {
    if (to.path !== '/login' && to.path !== '/register') {
      next('/login')
      return
    }
  }

  next()
})
```

---

# 第四阶段：Pinia用户状态管理（30分钟）

```typescript
// stores/user.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const userInfo = ref({
    userId: 0,
    username: '',
    realName: '',
    role: '',
    avatar: ''
  })

  const isLoggedIn = computed(() => !!token.value)
  const role = computed(() => userInfo.value.role)

  function setUserInfo(info: any) {
    userInfo.value = info
    token.value = info.token
    localStorage.setItem('token', info.token)
  }

  function logout() {
    token.value = ''
    userInfo.value = { userId: 0, username: '', realName: '', role: '', avatar: '' }
    localStorage.removeItem('token')
  }

  return { token, userInfo, isLoggedIn, role, setUserInfo, logout }
})
```

---

# 第4天验收标准

必须完成：

✅ 后端注册接口可调用

✅ 后端登录接口可返回JWT Token

✅ 前端登录页可正常登录

✅ 前端注册页可正常注册

✅ JWT鉴权生效（无token无法访问）

✅ 路由守卫生效

✅ 角色区分（个人/企业）

✅ Git已提交

---

# 常见问题

**Q：跨域问题怎么解决？**

A：后端已配置CorsConfig，前端vite配置了proxy代理。

**Q：密码存储安全吗？**

A：使用BCrypt加密，不可逆，即使数据库泄露也无法还原密码。

**Q：Token过期了怎么办？**

A：前端拦截401状态码，跳转到登录页重新登录。

**Q：企业注册和个人注册有什么区别？**

A：企业注册额外需要填写公司名称，注册成功后自动创建企业信息。
