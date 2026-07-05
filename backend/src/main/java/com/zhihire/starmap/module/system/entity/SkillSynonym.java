package com.zhihire.starmap.module.system.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;

import java.time.LocalDateTime;

/**
 * 技能同义词实体
 *
 * 对应数据库表 skill_synonym
 * 支撑技能归一的同义兜底查询
 */
@Data
@TableName("skill_synonym")
public class SkillSynonym {

    @TableId(type = IdType.AUTO)
    private Long id;

    /** 关联技能 ID（FK → skill.id） */
    private Long skillId;

    /** 同义词（唯一索引） */
    private String synonym;

    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createdAt;

    @TableField(fill = FieldFill.INSERT_UPDATE)
    private LocalDateTime updatedAt;

    @TableLogic
    private String deletedAt;
}
