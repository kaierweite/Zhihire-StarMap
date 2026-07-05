package com.zhihire.starmap.module.match.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;

import java.time.LocalDateTime;

/**
 * 匹配结果实体（双向共用）
 *
 * 对应数据库表 match_result
 * 懒计算 + 新鲜度缓存：首次请求调 AI 评分，后续直接返回缓存
 */
@Data
@TableName("match_result")
public class MatchResult {

    @TableId(type = IdType.AUTO)
    private Long id;

    /** 简历 ID */
    private Long resumeId;

    /** 岗位 ID */
    private Long jobId;

    /** 匹配分 0~100 */
    private Double score;

    /** 匹配明细 JSON（breakdown + rationale + graph_hints） */
    private String matchDetail;

    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createdAt;

    @TableField(fill = FieldFill.INSERT_UPDATE)
    private LocalDateTime updatedAt;

    @TableLogic
    private String deletedAt;
}
