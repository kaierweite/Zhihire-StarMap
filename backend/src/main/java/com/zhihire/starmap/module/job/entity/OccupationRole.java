package com.zhihire.starmap.module.job.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;

import java.time.LocalDateTime;

/**
 * 职业角色实体
 *
 * 对应数据库表 occupation_role
 */
@Data
@TableName("occupation_role")
public class OccupationRole {

    @TableId(type = IdType.AUTO)
    private Long id;

    /** 角色名称 */
    private String name;

    /** 角色描述 */
    private String description;

    /** 角色分类 */
    private String category;

    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createdAt;

    @TableField(fill = FieldFill.INSERT_UPDATE)
    private LocalDateTime updatedAt;

    @TableLogic
    private String deletedAt;
}
