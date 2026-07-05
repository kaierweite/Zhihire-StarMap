package com.zhihire.starmap.module.graph.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;

import java.time.LocalDateTime;

/**
 * 能力图谱缓存实体
 * 对应数据库表 ability_graph
 */
@Data
@TableName("ability_graph")
public class AbilityGraph {
    @TableId(type = IdType.AUTO)
    private Long id;
    private Long userId;
    private String graphData;
    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createdAt;
    @TableField(fill = FieldFill.INSERT_UPDATE)
    private LocalDateTime updatedAt;
    @TableLogic
    private String deletedAt;
}
