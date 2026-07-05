package com.zhihire.starmap.module.career.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;

import java.time.LocalDateTime;

/**
 * 职业规划实体
 *
 * 对应数据库表 career_plan
 * plan_content 存储结构化 JSON：{target_role, gap_skills[], learning_path[], graph_hints, rationale}
 */
@Data
@TableName("career_plan")
public class CareerPlan {

    @TableId(type = IdType.AUTO)
    private Long id;

    /** 用户 ID */
    private Long userId;

    /** 目标职业角色名称 */
    private String targetRole;

    /** 结构化规划内容 JSON */
    private String planContent;

    /** 规划来源：INTERVIEW/PROACTIVE/RECOMMEND */
    private String source;

    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createdAt;

    @TableField(fill = FieldFill.INSERT_UPDATE)
    private LocalDateTime updatedAt;

    @TableLogic
    private String deletedAt;
}
