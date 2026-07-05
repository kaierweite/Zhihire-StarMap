package com.zhihire.starmap.module.job.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import lombok.Data;

import java.math.BigDecimal;
import java.util.List;

/**
 * 岗位创建/更新请求 DTO
 */
@Data
public class JobRequest {

    /** 岗位标题 */
    @NotBlank(message = "岗位标题不能为空")
    private String title;

    /** 岗位描述 */
    private String description;

    /** 岗位要求 */
    private String requirements;

    /** 薪资下限（元/月） */
    private BigDecimal salaryMin;

    /** 薪资上限（元/月） */
    private BigDecimal salaryMax;

    /** 工作城市 */
    private String city;

    /** 最低工作年限 */
    private Integer experienceMin;

    /** 学历要求 */
    private String educationRequirement;

    /** 岗位类型：FULL_TIME/PART_TIME/INTERN */
    @Pattern(regexp = "FULL_TIME|PART_TIME|INTERN", message = "岗位类型不合法")
    private String jobType;

    /** 职业角色 ID（可选，关联 occupation_role 表） */
    private Long occupationRoleId;

    /** 岗位来源：MANUAL/UPLOAD */
    @NotBlank(message = "岗位来源不能为空")
    @Pattern(regexp = "MANUAL|UPLOAD", message = "岗位来源只能是 MANUAL 或 UPLOAD")
    private String source;

    /** 岗位技能列表 */
    private List<JobSkillRequest> skills;

    /**
     * 岗位技能
     */
    @Data
    public static class JobSkillRequest {
        /** 技能 ID（必须为 ACTIVE 状态） */
        private Long skillId;
        /** 重要度 1~5 */
        private Double importance;
        /** 要求等级：MUST/NICE/BONUS */
        private String requiredLevel;
    }
}
