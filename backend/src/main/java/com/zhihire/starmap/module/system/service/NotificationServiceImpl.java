package com.zhihire.starmap.module.system.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.core.conditions.update.LambdaUpdateWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.zhihire.starmap.module.system.entity.Notification;
import com.zhihire.starmap.module.system.mapper.NotificationMapper;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

@Slf4j
@Service
public class NotificationServiceImpl implements NotificationService {

    private final NotificationMapper notificationMapper;

    public NotificationServiceImpl(NotificationMapper notificationMapper) { this.notificationMapper = notificationMapper; }

    @Override
    public void createNotification(Long userId, String title, String content, String type) {
        Notification n = new Notification(); n.setUserId(userId); n.setTitle(title); n.setContent(content);
        n.setType(type); n.setIsRead(false); notificationMapper.insert(n);
    }

    @Override
    public Page<Notification> listNotifications(Long userId, int page, int size) {
        return notificationMapper.selectPage(new Page<>(page, size), new LambdaQueryWrapper<Notification>()
                .eq(Notification::getUserId, userId).orderByDesc(Notification::getCreatedAt));
    }

    @Override
    public long getUnreadCount(Long userId) {
        return notificationMapper.selectCount(new LambdaQueryWrapper<Notification>()
                .eq(Notification::getUserId, userId).eq(Notification::getIsRead, false));
    }

    @Override
    public void markAsRead(Long id, Long userId) {
        notificationMapper.update(null, new LambdaUpdateWrapper<Notification>()
                .eq(Notification::getId, id).eq(Notification::getUserId, userId).set(Notification::getIsRead, true));
    }

    @Override
    public void markAllAsRead(Long userId) {
        notificationMapper.update(null, new LambdaUpdateWrapper<Notification>()
                .eq(Notification::getUserId, userId).eq(Notification::getIsRead, false).set(Notification::getIsRead, true));
    }
}