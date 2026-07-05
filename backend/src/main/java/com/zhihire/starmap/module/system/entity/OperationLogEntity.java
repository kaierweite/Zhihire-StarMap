package com.zhihire.starmap.module.system.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;

import java.time.LocalDateTime;

/**
 * 操作日志实体（append-only）
 *
 * 对应数据库表 operation_log
 * 仅 created_at + deleted_at，无 updated_at
 */
@Data
@TableName("operation_log")
public class OperationLogEntity {

    @TableId(type = IdType.AUTO)
    private Long id;

    /** 操作人用户 ID */
    private Long userId;

    /** 操作模块 */
    private String module;

    /** 操作动作 */
    private String action;

    /** 操作详情（JSON） */
    private String detail;

    /** 操作人 IP */
    private String ip;

    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createdAt;

    @TableLogic
    private String deletedAt;
}
