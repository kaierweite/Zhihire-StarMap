package com.zhihire.starmap.module.auth.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.zhihire.starmap.module.auth.dto.LoginRequest;
import com.zhihire.starmap.module.auth.dto.LoginResponse;
import com.zhihire.starmap.module.auth.dto.RegisterRequest;
import com.zhihire.starmap.module.auth.util.JwtUtils;
import com.zhihire.starmap.module.common.constant.CommonConstants;
import com.zhihire.starmap.module.common.exception.BusinessException;
import com.zhihire.starmap.module.system.entity.LoginLog;
import com.zhihire.starmap.module.system.mapper.LoginLogMapper;
import com.zhihire.starmap.module.user.entity.Company;
import com.zhihire.starmap.module.user.entity.User;
import com.zhihire.starmap.module.user.mapper.CompanyMapper;
import com.zhihire.starmap.module.user.mapper.UserMapper;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Slf4j
@Service
public class AuthServiceImpl implements AuthService {

    private final UserMapper userMapper;
    private final CompanyMapper companyMapper;
    private final PasswordEncoder passwordEncoder;
    private final LoginLogMapper loginLogMapper;
    private final JwtUtils jwtUtils;

    public AuthServiceImpl(UserMapper userMapper, CompanyMapper companyMapper,
                           PasswordEncoder passwordEncoder, LoginLogMapper loginLogMapper,
                           JwtUtils jwtUtils) {
        this.userMapper = userMapper;
        this.companyMapper = companyMapper;
        this.passwordEncoder = passwordEncoder;
        this.loginLogMapper = loginLogMapper;
        this.jwtUtils = jwtUtils;
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public void register(RegisterRequest request) {
        Long count = userMapper.selectCount(
                new LambdaQueryWrapper<User>().eq(User::getUsername, request.getUsername()));
        if (count > 0) throw new BusinessException(400, "用户名已存在");
        User user = new User();
        user.setUsername(request.getUsername());
        user.setPassword(passwordEncoder.encode(request.getPassword()));
        user.setRole(request.getRole());
        user.setStatus(CommonConstants.STATUS_NORMAL);
        userMapper.insert(user);
        log.info("用户注册成功：username={}, role={}", user.getUsername(), user.getRole());
        if (CommonConstants.ROLE_COMPANY.equals(request.getRole())) {
            Company company = new Company();
            company.setUserId(user.getId());
            company.setCompanyName(request.getUsername() + "（待完善）");
            company.setAuditStatus("UNVERIFIED");
            companyMapper.insert(company);
            log.info("企业档案自动创建：userId={}", user.getId());
        }
    }

    @Override
    public LoginResponse login(LoginRequest request) {
        User user = userMapper.selectOne(
                new LambdaQueryWrapper<User>().eq(User::getUsername, request.getUsername()));
        if (user == null) throw new BusinessException(401, "用户名或密码错误");
        if (!passwordEncoder.matches(request.getPassword(), user.getPassword()))
            throw new BusinessException(401, "用户名或密码错误");
        if (!CommonConstants.STATUS_NORMAL.equals(user.getStatus()))
            throw new BusinessException(403, "账户已被禁用或封禁，请联系管理员");
        String token = jwtUtils.generateToken(user.getId(), user.getUsername(), user.getRole());
        log.info("用户登录成功：username={}, role={}", user.getUsername(), user.getRole());
        LoginLog loginLog = new LoginLog();
        loginLog.setUserId(user.getId());
        loginLogMapper.insert(loginLog);
        return LoginResponse.builder().token(token).role(user.getRole())
                .userId(user.getId()).nickname(user.getUsername()).build();
    }
}