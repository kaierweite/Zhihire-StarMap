package com.zhihire.starmap.module.resume.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;

import java.time.LocalDateTime;

/**
 * 解析任务实体
 *
 * 对应数据库表 parse_task
 * 简历上传后创建，异步调用 AI 服务解析
 */
@Data
@TableName("parse_task")
public class ParseTask {

    @TableId(type = IdType.AUTO)
    private Long id;

    /** 关联文件 ID（FK → upload_file.id） */
    private Long fileId;

    /** 关联用户 ID */
    private Long userId;

    /**
     * 任务状态
     * WAITING → PARSING → SUCCESS/FAILED/REJECTED
     */
    private String status;

    /** 解析结果（JSONB） */
    private String result;

    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createdAt;

    @TableField(fill = FieldFill.INSERT_UPDATE)
    private LocalDateTime updatedAt;

    @TableLogic
    private String deletedAt;
}
