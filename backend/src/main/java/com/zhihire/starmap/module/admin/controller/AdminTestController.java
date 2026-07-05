package com.zhihire.starmap.module.admin.controller;

import com.zhihire.starmap.module.common.result.Result;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * 管理后台测试控制器
 *
 * 职责：验证 ADMIN 角色权限控制是否生效
 * 仅 ADMIN 角色可访问 /api/admin/** 路径
 */
@RestController
@RequestMapping("/api/admin")
public class AdminTestController {

    /**
     * 管理后台测试端点
     * 仅 ADMIN 角色可访问
     *
     * @return 测试结果
     */
    @GetMapping("/test")
    @PreAuthorize("hasRole('ADMIN')")
    public Result<String> adminTest() {
        return Result.ok("admin access granted");
    }
}
