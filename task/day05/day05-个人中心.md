# 第5天开发任务（详细版）

# 项目：智聘星图——基于银河麒麟操作系统的AI智能匹配与能力图谱平台

## 今日目标

完成个人中心功能，包括用户信息查看/修改、密码修改、头像上传。

## 今日能力要求

- Spring Boot文件上传（熟练）
- Vue3表单校验（熟练）
- Pinia状态同步（基础）

**最终产出：**

```text
backend/.../module/user/
├──controller/UserController.java
├──service/UserService.java
├──service/UserServiceImpl.java
├──dto/
│   ├──UserUpdateRequest.java
│   ├──PasswordUpdateRequest.java
│   └──UserProfileResponse.java
└──mapper/SysUserMapper.java

frontend/src/views/user/
├──UserProfile.vue           # 个人资料
├──PasswordUpdate.vue        # 修改密码
└──AvatarUpload.vue          # 上传头像

frontend/src/components/
└──AvatarUpload.vue          # 通用头像上传组件
```

---

# 第一阶段：后端用户管理接口（2小时）

## 任务1：获取用户信息

```java
@RestController
@RequestMapping("/api/user")
public class UserController {
    @Autowired
    private UserService userService;

    @GetMapping("/profile")
    public Result<UserProfileResponse> getProfile(@UserId Long userId) {
        return Result.success(userService.getProfile(userId));
    }

    @PutMapping("/profile")
    public Result<Void> updateProfile(@UserId Long userId,
                                       @Valid @RequestBody UserUpdateRequest request) {
        userService.updateProfile(userId, request);
        return Result.success(null);
    }

    @PutMapping("/password")
    public Result<Void> updatePassword(@UserId Long userId,
                                        @Valid @RequestBody PasswordUpdateRequest request) {
        userService.updatePassword(userId, request);
        return Result.success(null);
    }

    @PostMapping("/avatar")
    public Result<String> uploadAvatar(@UserId Long userId,
                                        @RequestParam("file") MultipartFile file) {
        return Result.success(userService.uploadAvatar(userId, file));
    }
}
```

## 任务2：头像上传处理

```java
@Service
public class UserServiceImpl implements UserService {
    @Autowired
    private SysUserMapper userMapper;

    @Value("${file.upload.path:/data/upload}")
    private String uploadPath;

    @Override
    public String uploadAvatar(Long userId, MultipartFile file) {
        // 检查文件类型
        String contentType = file.getContentType();
        if (contentType == null || !contentType.startsWith("image/")) {
            throw new BusinessException(400, "只支持上传图片文件");
        }

        // 检查文件大小（最大2MB）
        if (file.getSize() > 2 * 1024 * 1024) {
            throw new BusinessException(400, "图片大小不能超过2MB");
        }

        try {
            // 生成文件名
            String suffix = contentType.substring(contentType.lastIndexOf("/") + 1);
            String fileName = "avatar_" + userId + "_" + System.currentTimeMillis() + "." + suffix;

            // 保存文件
            File dir = new File(uploadPath + "/avatar");
            if (!dir.exists()) dir.mkdirs();
            File dest = new File(dir, fileName);
            file.transferTo(dest);

            // 更新数据库
            String avatarUrl = "/api/files/avatar/" + fileName;
            userMapper.updateAvatar(userId, avatarUrl);

            // 如果是企业用户且是企业LOGO，也同步更新企业头像
            // TODO: 企业LOGO同步

            return avatarUrl;
        } catch (IOException e) {
            throw new BusinessException(500, "头像上传失败");
        }
    }
}
```

## 任务3：修改密码

```java
@Override
public void updatePassword(Long userId, PasswordUpdateRequest request) {
    SysUser user = userMapper.selectById(userId);

    // 验证旧密码
    if (!passwordEncoder.matches(request.getOldPassword(), user.getPassword())) {
        throw new BusinessException(400, "原密码不正确");
    }

    // 新密码不能和旧密码相同
    if (passwordEncoder.matches(request.getNewPassword(), user.getPassword())) {
        throw new BusinessException(400, "新密码不能与原密码相同");
    }

    // 更新密码
    user.setPassword(passwordEncoder.encode(request.getNewPassword()));
    userMapper.updateById(user);

    // 清除Redis中的token（强制重新登录）
    redisTemplate.delete("token:" + userId);
}
```

---

# 第二阶段：前端个人中心页面（2.5小时）

## 任务1：个人资料页面

```vue
<template>
  <div class="profile-container">
    <el-card class="profile-card">
      <template #header>
        <span class="card-title">个人资料</span>
      </template>

      <el-form :model="profileForm" :rules="rules" label-width="100px">
        <el-form-item label="用户名">
          <el-input v-model="profileForm.username" disabled />
        </el-form-item>

        <el-form-item label="真实姓名" prop="realName">
          <el-input v-model="profileForm.realName" placeholder="请输入真实姓名" />
        </el-form-item>

        <el-form-item label="手机号" prop="phone">
          <el-input v-model="profileForm.phone" placeholder="请输入手机号" />
        </el-form-item>

        <el-form-item label="邮箱" prop="email">
          <el-input v-model="profileForm.email" placeholder="请输入邮箱" />
        </el-form-item>

        <el-form-item label="角色">
          <el-tag :type="roleTagType">{{ roleLabel }}</el-tag>
        </el-form-item>

        <el-form-item label="注册时间">
          <span>{{ profileForm.createTime }}</span>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" :loading="saving" @click="handleSave">保存修改</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="avatar-card">
      <template #header>
        <span class="card-title">头像设置</span>
      </template>

      <div class="avatar-upload">
        <el-avatar :size="120" :src="avatarUrl">
          <User />
        </el-avatar>
        <el-upload
          class="avatar-uploader"
          action="/api/user/avatar"
          :headers="uploadHeaders"
          :show-file-list="false"
          :on-success="handleAvatarSuccess"
          :before-upload="beforeAvatarUpload"
        >
          <el-button type="primary" plain>上传头像</el-button>
        </el-upload>
      </div>
    </el-card>
  </div>
</template>
```

## 任务2：修改密码页面

```vue
<template>
  <el-card>
    <template #header>
      <span class="card-title">修改密码</span>
    </template>

    <el-form :model="passwordForm" :rules="passwordRules" label-width="120px" style="max-width: 400px">
      <el-form-item label="原密码" prop="oldPassword">
        <el-input v-model="passwordForm.oldPassword" type="password" show-password />
      </el-form-item>

      <el-form-item label="新密码" prop="newPassword">
        <el-input v-model="passwordForm.newPassword" type="password" show-password />
        <div class="password-strength" v-if="passwordForm.newPassword">
          <div class="strength-bar" :class="strengthClass"></div>
          <span class="strength-text">{{ strengthText }}</span>
        </div>
      </el-form-item>

      <el-form-item label="确认密码" prop="confirmPassword">
        <el-input v-model="passwordForm.confirmPassword" type="password" show-password />
      </el-form-item>

      <el-form-item>
        <el-button type="primary" :loading="saving" @click="handleUpdatePassword">确认修改</el-button>
      </el-form-item>
    </el-form>
  </el-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { ElMessage } from 'element-plus'
import { updatePassword } from '@/api/user'

const passwordForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const validatePass = (rule: any, value: string, callback: any) => {
  if (value.length < 8) {
    callback(new Error('密码长度不能少于8位'))
  } else if (!/(?=.*[a-zA-Z])(?=.*\d)/.test(value)) {
    callback(new Error('密码必须包含字母和数字'))
  } else {
    callback()
  }
}

const validateConfirm = (rule: any, value: string, callback: any) => {
  if (value !== passwordForm.newPassword) {
    callback(new Error('两次输入密码不一致'))
  } else {
    callback()
  }
}

const passwordRules = {
  oldPassword: [{ required: true, message: '请输入原密码', trigger: 'blur' }],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { validator: validatePass, trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    { validator: validateConfirm, trigger: 'blur' }
  ]
}
</script>
```

## 任务3：密码强度指示器

```typescript
// 密码强度计算
const strengthLevel = computed(() => {
  const pwd = passwordForm.newPassword
  let score = 0
  if (pwd.length >= 8) score += 25
  if (pwd.length >= 12) score += 15
  if (/(?=.*[a-z])(?=.*[A-Z])/.test(pwd)) score += 20  // 大小写混合
  if (/(?=.*\d)/.test(pwd)) score += 20
  if (/(?=.*[!@#$%^&*])/.test(pwd)) score += 20  // 特殊字符
  return score
})

const strengthClass = computed(() => {
  if (strengthLevel.value < 40) return 'weak'
  if (strengthLevel.value < 70) return 'medium'
  return 'strong'
})

const strengthText = computed(() => {
  if (strengthLevel.value < 40) return '弱'
  if (strengthLevel.value < 70) return '中'
  return '强'
})
```

---

# 第三阶段：企业信息管理（1小时）

如果是企业用户，个人中心扩展显示企业信息编辑：

## 企业信息字段

- 企业名称（不可修改，需联系管理员）
- 企业简介
- 所属行业
- 企业规模
- 办公地址
- 企业网站
- 联系人
- 联系电话

## 后端接口

```java
@GetMapping("/company/info")
public Result<CompanyInfoResponse> getCompanyInfo(@UserId Long userId)

@PutMapping("/company/info")
public Result<Void> updateCompanyInfo(@UserId Long userId,
                                       @Valid @RequestBody CompanyUpdateRequest request)
```

---

# 第5天验收标准

必须完成：

✅ 个人资料查看和修改

✅ 密码修改（含强度校验）

✅ 头像上传（图片类型+大小限制）

✅ 企业信息管理（企业用户）

✅ 密码修改后需要重新登录

✅ 表单校验全部正常工作

✅ Git已提交

---

# 常见问题

**Q：头像上传后不显示？**

A：检查后端静态资源映射配置，确保头像目录可访问。

**Q：修改密码后为什么要重新登录？**

A：出于安全考虑，密码变更后应使旧的token失效。

**Q：上传的图片保存在哪里？**

A：本地保存在/data/upload/avatar目录，正式环境应使用OSS对象存储。
