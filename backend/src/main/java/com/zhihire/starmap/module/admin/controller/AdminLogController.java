package com.zhihire.starmap.module.admin.controller;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.zhihire.starmap.module.common.result.Result;
import com.zhihire.starmap.module.system.entity.LoginLog;
import com.zhihire.starmap.module.system.entity.OperationLogEntity;
import com.zhihire.starmap.module.system.mapper.LoginLogMapper;
import com.zhihire.starmap.module.system.mapper.OperationLogMapper;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.util.StringUtils;
import org.springframework.web.bind.annotation.*;

/**
 * 管理后台 — 日志查询
 */
@RestController
@RequestMapping("/api/admin")
@PreAuthorize("hasRole('ADMIN')")
public class AdminLogController {

    private final OperationLogMapper operationLogMapper;
    private final LoginLogMapper loginLogMapper;

    public AdminLogController(OperationLogMapper operationLogMapper,
                              LoginLogMapper loginLogMapper) {
        this.operationLogMapper = operationLogMapper;
        this.loginLogMapper = loginLogMapper;
    }

    /** 操作日志列表 */
    @GetMapping("/logs")
    public Result<Page<OperationLogEntity>> listLogs(
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "20") int size,
            @RequestParam(required = false) String module) {
        Page<OperationLogEntity> pageParam = new Page<>(page, size);
        LambdaQueryWrapper<OperationLogEntity> wrapper = new LambdaQueryWrapper<>();
        if (StringUtils.hasText(module)) {
            wrapper.eq(OperationLogEntity::getModule, module);
        }
        wrapper.orderByDesc(OperationLogEntity::getCreatedAt);
        return Result.ok(operationLogMapper.selectPage(pageParam, wrapper));
    }

    /** 操作日志详情 */
    @GetMapping("/logs/{id}")
    public Result<OperationLogEntity> getLogDetail(@PathVariable Long id) {
        return Result.ok(operationLogMapper.selectById(id));
    }

    /** 登录日志列表 */
    @GetMapping("/login-logs")
    public Result<Page<LoginLog>> listLoginLogs(
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "20") int size) {
        Page<LoginLog> pageParam = new Page<>(page, size);
        return Result.ok(loginLogMapper.selectPage(pageParam,
                new LambdaQueryWrapper<LoginLog>().orderByDesc(LoginLog::getCreatedAt)));
    }
}
