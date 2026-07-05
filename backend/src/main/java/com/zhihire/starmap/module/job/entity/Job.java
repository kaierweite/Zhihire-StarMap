package com.zhihire.starmap.module.job.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDateTime;

/**
 * 岗位实体
 *
 * 对应数据库表 job
 * source 双模式：MANUAL（手动填写）/ UPLOAD（JD 文件上传）
 */
@Data
@TableName("job")
public class Job {

    @TableId(type = IdType.AUTO)
    private Long id;

    /** 关联企业 ID（FK → company.id） */
    private Long companyId;

    /** 关联职业角色 ID（FK → occupation_role.id） */
    private Long occupationRoleId;

    /** 岗位标题 */
    private String title;

    /** 岗位描述 */
    private String description;

    /** 岗位要求 */
    private String requirements;

    /** 薪资下限 */
    private BigDecimal salaryMin;

    /** 薪资上限 */
    private BigDecimal salaryMax;

    /** 工作城市 */
    private String city;

    /** 最低工作年限 */
    private Integer experienceMin;

    /** 学历要求 */
    private String educationRequirement;

    /** 岗位类型：FULL_TIME/PART_TIME/INTERN */
    private String jobType;

    /** 岗位状态：OPEN/CLOSED/DRAFT */
    private String status;

    /** 岗位来源：MANUAL/UPLOAD */
    private String source;

    /** embedding 向量缓存 */
    private String embeddingCache;

    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createdAt;

    @TableField(fill = FieldFill.INSERT_UPDATE)
    private LocalDateTime updatedAt;

    @TableLogic
    private String deletedAt;
}
