package com.zhihire.starmap.module.interview.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;

import java.time.LocalDateTime;

/**
 * 面试问题实体
 * questionType: TECHNICAL/BEHAVIORAL/SITUATIONAL/RESUME_BASED
 */
@Data
@TableName("interview_question")
public class InterviewQuestion {
    @TableId(type = IdType.AUTO)
    private Long id;
    private Long sessionId;
    private String questionType;
    private String content;
    private String expectedPoints;
    private Integer orderNo;
    private Boolean isBankVisible;
    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createdAt;
    @TableField(fill = FieldFill.INSERT_UPDATE)
    private LocalDateTime updatedAt;
    @TableLogic
    private String deletedAt;
}
