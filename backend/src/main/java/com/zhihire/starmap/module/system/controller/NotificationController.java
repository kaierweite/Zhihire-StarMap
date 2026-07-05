package com.zhihire.starmap.module.system.controller;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.zhihire.starmap.module.common.result.Result;
import com.zhihire.starmap.module.system.entity.Notification;
import com.zhihire.starmap.module.system.service.NotificationService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

/**
 * 通知控制器
 *
 * 职责：通知列表、未读数、标记已读
 */
@Tag(name = "通知接口", description = "通知列表/已读")
@RestController
@RequestMapping("/api/notification")
public class NotificationController {

    private final NotificationService notificationService;

    public NotificationController(NotificationService notificationService) {
        this.notificationService = notificationService;
    }

    /** 通知列表（分页） */
    @GetMapping("/list")
    public Result<Page<Notification>> listNotifications(
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "20") int size,
            Authentication authentication) {
        Long userId = (Long) authentication.getPrincipal();
        return Result.ok(notificationService.listNotifications(userId, page, size));
    }

    /** 未读通知数 */
    @GetMapping("/unread-count")
    public Result<Long> getUnreadCount(Authentication authentication) {
        Long userId = (Long) authentication.getPrincipal();
        return Result.ok(notificationService.getUnreadCount(userId));
    }

    /** 标记单条已读 */
    @PutMapping("/{id}/read")
    public Result<Void> markAsRead(@PathVariable Long id,
                                   Authentication authentication) {
        Long userId = (Long) authentication.getPrincipal();
        notificationService.markAsRead(id, userId);
        return Result.ok();
    }

    /** 全部已读 */
    @PutMapping("/read-all")
    public Result<Void> markAllAsRead(Authentication authentication) {
        Long userId = (Long) authentication.getPrincipal();
        notificationService.markAllAsRead(userId);
        return Result.ok();
    }
}
