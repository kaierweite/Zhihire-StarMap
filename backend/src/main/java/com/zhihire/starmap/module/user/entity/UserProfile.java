package com.zhihire.starmap.module.user.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;

/**
 * 求职者档案实体
 *
 * 对应数据库表 user_profile
 * 与 user 一对一关联（user_id）
 */
@Data
@TableName("user_profile")
public class UserProfile {

    @TableId(type = IdType.AUTO)
    private Long id;

    /** 关联用户 ID */
    private Long userId;

    /** 真实姓名 */
    private String realName;

    /** 性别：MALE/FEMALE/OTHER */
    private String gender;

    /** 出生日期 */
    private LocalDate birthDate;

    /** 学历：高中/专科/本科/硕士/博士 */
    private String education;

    /** 毕业院校 */
    private String school;

    /** 专业 */
    private String major;

    /** 工作年限 */
    private Integer workYears;

    /** 期望薪资下限 */
    private BigDecimal expectedSalaryMin;

    /** 期望薪资上限 */
    private BigDecimal expectedSalaryMax;

    /** 期望工作城市 */
    private String expectedCity;

    /** 当前居住城市 */
    private String currentCity;

    /** 个人简介 */
    private String bio;

    /** 简历完成度 0~100 */
    private Integer profileCompleteness;

    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createdAt;

    @TableField(fill = FieldFill.INSERT_UPDATE)
    private LocalDateTime updatedAt;

    @TableLogic
    private String deletedAt;
}
