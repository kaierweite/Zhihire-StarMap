package com.zhihire.starmap.module.admin.controller;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.core.conditions.update.LambdaUpdateWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.zhihire.starmap.module.common.exception.BusinessException;
import com.zhihire.starmap.module.common.result.Result;
import com.zhihire.starmap.module.system.annotation.OperationLog;
import com.zhihire.starmap.module.user.entity.User;
import com.zhihire.starmap.module.user.mapper.UserMapper;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.util.StringUtils;
import org.springframework.web.bind.annotation.*;

/**
 * 管理后台 — 用户管理
 */
@Slf4j
@RestController
@RequestMapping("/api/admin/user")
@PreAuthorize("hasRole('ADMIN')")
public class AdminUserController {

    private final UserMapper userMapper;

    public AdminUserController(UserMapper userMapper) {
        this.userMapper = userMapper;
    }

    /** 用户列表（支持 role/status 筛选，分页） */
    @GetMapping("/list")
    public Result<Page<User>> listUsers(
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "20") int size,
            @RequestParam(required = false) String role,
            @RequestParam(required = false) String status) {
        Page<User> pageParam = new Page<>(page, size);
        LambdaQueryWrapper<User> wrapper = new LambdaQueryWrapper<>();
        if (StringUtils.hasText(role)) wrapper.eq(User::getRole, role);
        if (StringUtils.hasText(status)) wrapper.eq(User::getStatus, status);
        wrapper.orderByDesc(User::getCreatedAt);
        return Result.ok(userMapper.selectPage(pageParam, wrapper));
    }

    /** 封禁用户 */
    @PutMapping("/{id}/ban")
    @OperationLog("用户管理/封禁用户")
    public Result<Void> banUser(@PathVariable Long id) {
        User user = userMapper.selectById(id);
        if (user == null) throw new BusinessException(404, "用户不存在");
        user.setStatus("BANNED");
        userMapper.updateById(user);
        log.info("用户封禁：userId={}", id);
        return Result.ok();
    }

    /** 解封用户 */
    @PutMapping("/{id}/unban")
    @OperationLog("用户管理/解封用户")
    public Result<Void> unbanUser(@PathVariable Long id) {
        User user = userMapper.selectById(id);
        if (user == null) throw new BusinessException(404, "用户不存在");
        user.setStatus("NORMAL");
        userMapper.updateById(user);
        log.info("用户解封：userId={}", id);
        return Result.ok();
    }
}
