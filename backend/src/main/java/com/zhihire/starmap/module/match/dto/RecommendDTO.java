package com.zhihire.starmap.module.match.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * 推荐结果 DTO
 *
 * 包含匹配分 + 岗位/简历/用户信息
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class RecommendDTO {

    /** 匹配结果 ID */
    private Long matchId;

    /** 匹配分 0~100 */
    private Double score;

    /** 岗位 ID（求职者推荐时） */
    private Long jobId;

    /** 岗位标题 */
    private String jobTitle;

    /** 岗位城市 */
    private String jobCity;

    /** 企业名称 */
    private String companyName;

    /** 简历 ID（企业推荐时） */
    private Long resumeId;

    /** 用户 ID（企业推荐时） */
    private Long userId;

    /** 用户名 */
    private String username;

    /** 匹配明细 JSON */
    private String matchDetail;
}
