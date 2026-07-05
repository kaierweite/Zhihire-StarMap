package com.zhihire.starmap.module.auth.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.zhihire.starmap.module.auth.dto.LoginRequest;
import com.zhihire.starmap.module.auth.dto.LoginResponse;
import com.zhihire.starmap.module.auth.dto.RegisterRequest;
import com.zhihire.starmap.module.auth.util.JwtUtils;
import com.zhihire.starmap.module.common.constant.CommonConstants;
import com.zhihire.starmap.module.common.exception.BusinessException;
import com.zhihire.starmap.module.user.entity.Company;
import com.zhihire.starmap.module.user.entity.User;
import com.zhihire.starmap.module.user.mapper.CompanyMapper;
import com.zhihire.starmap.module.user.mapper.UserMapper;
import com.zhihire.starmap.module.system.entity.LoginLog;
import com.zhihire.starmap.module.system.mapper.LoginLogMapper;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 * 认证服务
 *
 * 职责：处理注册、登录业务逻辑
 */
@Slf4j
@Service
public class AuthService {

    private final UserMapper userMapper;
    private final CompanyMapper companyMapper;
    private final LoginLogMapper loginLogMapper;
    private final PasswordEncoder passwordEncoder;
    private final JwtUtils jwtUtils;

    /**
     * 构造注入
     *
     * @param userMapper      用户 Mapper
     * @param companyMapper   企业 Mapper
     * @param passwordEncoder BCrypt 密码编码器
     * @param jwtUtils        JWT 工具类
     */
    public AuthService(UserMapper userMapper, CompanyMapper companyMapper,
                       PasswordEncoder passwordEncoder, LoginLogMapper loginLogMapper, JwtUtils jwtUtils) {
        this.userMapper = userMapper;
        this.companyMapper = companyMapper;
        this.passwordEncoder = passwordEncoder;
        this.loginLogMapper = loginLogMapper;
        this.jwtUtils = jwtUtils;
    }

    /**
     * 用户注册
     *
     * 流程：
     * 1. 校验用户名唯一
     * 2. BCrypt 加密密码
     * 3. 写入 user 表
     * 4. 若角色为 COMPANY，同步创建企业档案（audit_status=UNVERIFIED）
     *
     * @param request 注册请求（username, password, role）
     */
    @Transactional(rollbackFor = Exception.class)
    public void register(RegisterRequest request) {
        // 1. 校验用户名唯一
        Long count = userMapper.selectCount(
                new LambdaQueryWrapper<User>()
                        .eq(User::getUsername, request.getUsername()));
        if (count > 0) {
            throw new BusinessException(400, "用户名已存在");
        }

        // 2. 构建用户实体
        User user = new User();
        user.setUsername(request.getUsername());
        // BCrypt 加密密码
        user.setPassword(passwordEncoder.encode(request.getPassword()));
        user.setRole(request.getRole());
        user.setStatus(CommonConstants.STATUS_NORMAL);

        // 3. 插入用户记录
        userMapper.insert(user);
        log.info("用户注册成功：username={}, role={}", user.getUsername(), user.getRole());

        // 4. 企业角色自动创建企业档案
        if (CommonConstants.ROLE_COMPANY.equals(request.getRole())) {
            Company company = new Company();
            company.setUserId(user.getId());
            company.setCompanyName(request.getUsername() + "（待完善）");
            company.setAuditStatus("UNVERIFIED");
            companyMapper.insert(company);
            log.info("企业档案自动创建：userId={}", user.getId());
        }
    }

    /**
     * 用户登录
     *
     * 流程：
     * 1. 校验用户名存在
     * 2. BCrypt 校验密码
     * 3. 校验账户状态
     * 4. 签发 JWT Token
     *
     * @param request 登录请求（username, password）
     * @return 登录响应（token, role, userId, nickname）
     */
    public LoginResponse login(LoginRequest request) {
        // 1. 根据用户名查询用户
        User user = userMapper.selectOne(
                new LambdaQueryWrapper<User>()
                        .eq(User::getUsername, request.getUsername()));
        if (user == null) {
            throw new BusinessException(401, "用户名或密码错误");
        }

        // 2. BCrypt 校验密码
        if (!passwordEncoder.matches(request.getPassword(), user.getPassword())) {
            throw new BusinessException(401, "用户名或密码错误");
        }

        // 3. 校验账户状态（NORMAL 才允许登录）
        if (!CommonConstants.STATUS_NORMAL.equals(user.getStatus())) {
            throw new BusinessException(403, "账户已被禁用或封禁，请联系管理员");
        }

        // 4. 签发 JWT Token（sub=userId, role=大写角色）
        String token = jwtUtils.generateToken(user.getId(), user.getUsername(), user.getRole());
        log.info("用户登录成功：username={}, role={}", user.getUsername(), user.getRole());

        // 5. 记录登录日志
        LoginLog loginLog = new LoginLog();
        loginLog.setUserId(user.getId());
        loginLogMapper.insert(loginLog);

        // 6. 返回登录响应
        return LoginResponse.builder()
                .token(token)
                .role(user.getRole())
                .userId(user.getId())
                .nickname(user.getUsername())
                .build();
    }
}
