package com.zhihire.starmap.module.system.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;

import java.time.LocalDateTime;

/**
 * 技能关系边实体
 *
 * 对应数据库表 skill_relation
 * 关系类型：PREREQUISITE（前置）/ SIMILAR（相似）/ INCLUDES（包含）/ COMPLEMENTARY（互补）
 */
@Data
@TableName("skill_relation")
public class SkillRelation {

    @TableId(type = IdType.AUTO)
    private Long id;

    /** 源技能 ID */
    private Long skillId;

    /** 目标技能 ID */
    private Long relatedSkillId;

    /** 关系类型：PREREQUISITE/SIMILAR/INCLUDES/COMPLEMENTARY */
    private String relationType;

    /** 关系权重 0~1 */
    private Double weight;

    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createdAt;

    @TableField(fill = FieldFill.INSERT_UPDATE)
    private LocalDateTime updatedAt;

    @TableLogic
    private String deletedAt;
}
