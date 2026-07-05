package com.zhihire.starmap.module.interview.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;

import java.time.LocalDateTime;

/**
 * 简历优化建议实体
 * suggestions: [{section, current, suggestion, relates_to_skill}]
 */
@Data
@TableName("resume_optimization")
public class ResumeOptimization {
    @TableId(type = IdType.AUTO)
    private Long id;
    private Long resumeId;
    private Long jobId;
    private String suggestions;
    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createdAt;
    @TableField(fill = FieldFill.INSERT_UPDATE)
    private LocalDateTime updatedAt;
    @TableLogic
    private String deletedAt;
}
