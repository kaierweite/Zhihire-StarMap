package com.zhihire.starmap.module.admin.controller;

import com.zhihire.starmap.module.admin.dto.AdminStatDTO;
import com.zhihire.starmap.module.admin.service.StatService;
import com.zhihire.starmap.module.common.result.Result;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * 管理后台 — 统计数据
 */
@RestController
@RequestMapping("/api/admin/stat")
@PreAuthorize("hasRole('ADMIN')")
public class AdminStatController {

    private final StatService statService;

    public AdminStatController(StatService statService) {
        this.statService = statService;
    }

    /** 获取统计数据（Caffeine 缓存 5 分钟） */
    @GetMapping
    public Result<AdminStatDTO> getStats() {
        return Result.ok(statService.getStats());
    }
}
