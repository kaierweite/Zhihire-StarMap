package com.zhihire.starmap.module.resume.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;

import java.time.LocalDateTime;

/**
 * 简历实体
 *
 * 对应数据库表 resume
 * 通过 file_id 引用 upload_file（单一事实源）
 */
@Data
@TableName("resume")
public class Resume {

    @TableId(type = IdType.AUTO)
    private Long id;

    /** 关联用户 ID */
    private Long userId;

    /** 关联文件 ID（FK → upload_file.id） */
    private Long fileId;

    /** 简历标题 */
    private String title;

    /** 解析后的文本内容 */
    private String contentText;

    /** embedding 向量缓存（JSONB） */
    private String embeddingCache;

    /** 状态：NORMAL/DISABLED */
    private String status;

    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createdAt;

    @TableField(fill = FieldFill.INSERT_UPDATE)
    private LocalDateTime updatedAt;

    @TableLogic
    private String deletedAt;
}
