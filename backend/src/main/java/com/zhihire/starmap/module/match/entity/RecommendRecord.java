package com.zhihire.starmap.module.match.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;

import java.time.LocalDateTime;

/**
 * 推荐记录实体
 *
 * 对应数据库表 recommend_record
 * 记录推荐交互状态：点击、投递、邀请
 */
@Data
@TableName("recommend_record")
public class RecommendRecord {

    @TableId(type = IdType.AUTO)
    private Long id;

    /** 用户 ID */
    private Long userId;

    /** 岗位 ID */
    private Long jobId;

    /** 匹配分 */
    private Double score;

    /** 是否点击 */
    private Boolean isClicked;

    /** 是否投递 */
    private Boolean isApplied;

    /** 是否被邀请 */
    private Boolean isInvited;

    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createdAt;

    @TableField(fill = FieldFill.INSERT_UPDATE)
    private LocalDateTime updatedAt;

    @TableLogic
    private String deletedAt;
}
