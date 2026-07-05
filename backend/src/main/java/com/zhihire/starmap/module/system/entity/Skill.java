package com.zhihire.starmap.module.system.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;

import java.time.LocalDateTime;

/**
 * 技能字典实体
 *
 * 对应数据库表 skill
 * 状态三态：ACTIVE（已激活）/ CANDIDATE（待审核）/ MERGED（已合并）
 */
@Data
@TableName("skill")
public class Skill {

    @TableId(type = IdType.AUTO)
    private Long id;

    /** 技能名称（唯一索引） */
    private String name;

    /** 技能领域：后端/前端/测试/运维/数据/通用 */
    private String category;

    /** 技能描述 */
    private String description;

    /**
     * 技能状态（VARCHAR 大写枚举）
     * ACTIVE    - 已激活（可被匹配/推荐使用）
     * CANDIDATE - 待审核（新入库等待管理员确认）
     * MERGED    - 已合并（指向 mergeTargetId 对应的技能）
     */
    private String status;

    /** MERGED 时指向的目标技能 ID */
    private Long mergeTargetId;

    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createdAt;

    @TableField(fill = FieldFill.INSERT_UPDATE)
    private LocalDateTime updatedAt;

    @TableLogic
    private String deletedAt;
}
