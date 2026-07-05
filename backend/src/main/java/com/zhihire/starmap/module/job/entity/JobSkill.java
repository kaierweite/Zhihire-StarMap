package com.zhihire.starmap.module.job.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;

import java.time.LocalDateTime;

/**
 * 岗位技能关联实体
 *
 * 对应数据库表 job_skill
 */
@Data
@TableName("job_skill")
public class JobSkill {

    @TableId(type = IdType.AUTO)
    private Long id;

    /** 岗位 ID */
    private Long jobId;

    /** 技能 ID */
    private Long skillId;

    /** 重要度 1~5 */
    private Double importance;

    /** 要求等级：MUST/NICE/BONUS */
    private String requiredLevel;

    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createdAt;

    @TableField(fill = FieldFill.INSERT_UPDATE)
    private LocalDateTime updatedAt;

    @TableLogic
    private String deletedAt;
}
