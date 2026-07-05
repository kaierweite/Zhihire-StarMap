package com.zhihire.starmap.module.interview.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;

import java.time.LocalDateTime;

/**
 * 面试报告实体
 * radar: {communication, technical, problem_solving, culture_fit, depth}
 * feedback: [{dimension, score, advice}]
 */
@Data
@TableName("interview_report")
public class InterviewReport {
    @TableId(type = IdType.AUTO)
    private Long id;
    private Long sessionId;
    private Double overallScore;
    private String radar;
    private String feedback;
    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createdAt;
    @TableField(fill = FieldFill.INSERT_UPDATE)
    private LocalDateTime updatedAt;
    @TableLogic
    private String deletedAt;
}
