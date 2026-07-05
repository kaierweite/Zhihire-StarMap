package com.zhihire.starmap.module.interview.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;

import java.time.LocalDateTime;

/**
 * 用户面试回答实体
 */
@Data
@TableName("interview_answer")
public class InterviewAnswer {
    @TableId(type = IdType.AUTO)
    private Long id;
    private Long questionId;
    private String content;
    private Double aiScore;
    private String aiFeedback;
    private String matchedPoints;
    private String missedPoints;
    private LocalDateTime answeredAt;
    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createdAt;
    @TableField(fill = FieldFill.INSERT_UPDATE)
    private LocalDateTime updatedAt;
    @TableLogic
    private String deletedAt;
}
