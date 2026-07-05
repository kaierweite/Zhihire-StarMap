package com.zhihire.starmap.module.system.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;

import java.time.LocalDateTime;

/**
 * 通知实体
 *
 * 对应数据库表 notification
 * 类型：APPLICATION（投递通知）/ INTERVIEW_INVITE（面试邀请）/ SYSTEM（系统通知）
 */
@Data
@TableName("notification")
public class Notification {

    @TableId(type = IdType.AUTO)
    private Long id;

    /** 接收者用户 ID */
    private Long userId;

    /** 通知标题 */
    private String title;

    /** 通知内容 */
    private String content;

    /** 通知类型：APPLICATION/INTERVIEW_INVITE/SYSTEM */
    private String type;

    /** 是否已读 */
    private Boolean isRead;

    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createdAt;

    @TableLogic
    private String deletedAt;
}
