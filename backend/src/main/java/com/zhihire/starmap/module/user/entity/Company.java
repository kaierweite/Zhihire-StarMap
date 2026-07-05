package com.zhihire.starmap.module.user.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;

import java.time.LocalDateTime;

/**
 * 企业档案实体
 *
 * 对应数据库表 company
 * 注册时自动创建，audit_status 初始为 UNVERIFIED
 */
@Data
@TableName("company")
public class Company {

    /** 主键 */
    @TableId(type = IdType.AUTO)
    private Long id;

    /** 关联用户 ID（FK → user.id） */
    private Long userId;

    /** 企业名称 */
    private String companyName;

    /** 所属行业 */
    private String industry;

    /** 企业规模 */
    private String scale;

    /** 企业官网 */
    private String website;

    /** 企业 Logo URL */
    private String logoUrl;

    /** 企业简介 */
    private String description;

    /** 企业地址 */
    private String address;

    /** 联系人姓名 */
    private String contactName;

    /** 联系人电话 */
    private String contactPhone;

    /** 联系人邮箱 */
    private String contactEmail;

    /**
     * 审核状态（VARCHAR 大写枚举）
     * UNVERIFIED - 未认证（注册默认）
     * PENDING    - 待审核
     * VERIFIED   - 已认证
     * REJECTED   - 已拒绝
     */
    private String auditStatus;

    /** 审核备注/拒绝原因 */
    private String auditReason;

    /** 创建时间 */
    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createdAt;

    /** 更新时间 */
    @TableField(fill = FieldFill.INSERT_UPDATE)
    private LocalDateTime updatedAt;

    /** 逻辑删除 */
    @TableLogic
    private String deletedAt;
}
