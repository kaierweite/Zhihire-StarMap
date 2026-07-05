package com.zhihire.starmap.module.system.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;

import java.time.LocalDateTime;

/**
 * 文件本体实体（单一事实源）
 *
 * 对应数据库表 upload_file
 * 所有文件引用（resume.file_id, parse_task.file_id）均指向此表
 */
@Data
@TableName("upload_file")
public class UploadFile {

    @TableId(type = IdType.AUTO)
    private Long id;

    /** 原始文件名 */
    private String originalName;

    /** UUID 存储文件名 */
    private String storedName;

    /** 存储路径 */
    private String path;

    /** 文件大小（字节） */
    private Long size;

    /** MIME 类型 */
    private String mimeType;

    /** 上传者用户 ID */
    private Long uploaderId;

    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createdAt;

    @TableLogic
    private String deletedAt;
}
