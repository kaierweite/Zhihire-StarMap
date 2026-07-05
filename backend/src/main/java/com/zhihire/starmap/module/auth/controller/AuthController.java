package com.zhihire.starmap.module.auth.controller;

import com.zhihire.starmap.module.auth.dto.LoginRequest;
import com.zhihire.starmap.module.auth.dto.LoginResponse;
import com.zhihire.starmap.module.auth.dto.RegisterRequest;
import com.zhihire.starmap.module.auth.service.AuthService;
import com.zhihire.starmap.module.common.result.Result;
import jakarta.validation.Valid;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * 认证控制器
 *
 * 职责：处理注册、登录请求
 * 路径前缀 /api/auth/，公开访问（SecurityConfig 已放行）
 */
@Slf4j
@RestController
@RequestMapping("/api/auth")
public class AuthController {

    private final AuthService authService;

    /**
     * 构造注入
     *
     * @param authService 认证服务
     */
    public AuthController(AuthService authService) {
        this.authService = authService;
    }

    /**
     * 用户注册
     *
     * @param request 注册请求（username, password, role）
     * @return 统一结果
     */
    @PostMapping("/register")
    public Result<Void> register(@Valid @RequestBody RegisterRequest request) {
        authService.register(request);
        return Result.ok();
    }

    /**
     * 用户登录
     *
     * @param request 登录请求（username, password）
     * @return 包含 JWT Token 的登录响应
     */
    @PostMapping("/login")
    public Result<LoginResponse> login(@Valid @RequestBody LoginRequest request) {
        LoginResponse response = authService.login(request);
        return Result.ok(response);
    }
}
