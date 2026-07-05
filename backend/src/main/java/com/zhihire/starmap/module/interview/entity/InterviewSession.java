package com.zhihire.starmap.module.interview.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;

import java.time.LocalDateTime;

/**
 * 面试会话实体
 * status: PENDING/IN_PROGRESS/COMPLETED/ABORTED
 */
@Data
@TableName("interview_session")
public class InterviewSession {
    @TableId(type = IdType.AUTO)
    private Long id;
    private Long userId;
    private Long jobId;
    private Long occupationRoleId;
    private String status;
    private LocalDateTime startedAt;
    private LocalDateTime finishedAt;
    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createdAt;
    @TableField(fill = FieldFill.INSERT_UPDATE)
    private LocalDateTime updatedAt;
    @TableLogic
    private String deletedAt;
}
