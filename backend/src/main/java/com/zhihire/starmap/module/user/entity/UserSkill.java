package com.zhihire.starmap.module.user.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;

import java.time.LocalDateTime;

/**
 * 用户技能关联实体
 *
 * 对应数据库表 user_skill
 * 来源：简历解析（AI 回调）或用户手动添加
 */
@Data
@TableName("user_skill")
public class UserSkill {

    @TableId(type = IdType.AUTO)
    private Long id;

    /** 用户 ID */
    private Long userId;

    /** 技能 ID（FK → skill.id，ACTIVE 状态） */
    private Long skillId;

    /** 熟练度 0~5（AI 解析时用 confidence 映射） */
    private Double proficiencyLevel;

    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createdAt;

    @TableField(fill = FieldFill.INSERT_UPDATE)
    private LocalDateTime updatedAt;

    @TableLogic
    private String deletedAt;
}
