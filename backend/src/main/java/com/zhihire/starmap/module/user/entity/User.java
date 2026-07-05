package com.zhihire.starmap.module.user.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;

import java.time.LocalDateTime;

/**
 * 用户实体
 *
 * 对应数据库表 "user"（PostgreSQL 关键字需双引号）
 * 角色与状态均为 VARCHAR 大写语义枚举（ADR-0002）
 */
@Data
@TableName("\"user\"")
public class User {

    /** 主键，自增 */
    @TableId(type = IdType.AUTO)
    private Long id;

    /** 登录用户名（唯一） */
    private String username;

    /** BCrypt 加密后的密码 */
    private String password;

    /** 邮箱 */
    private String email;

    /** 手机号 */
    private String phone;

    /**
     * 用户角色（VARCHAR 大写枚举）
     * ADMIN - 管理员
     * USER  - 求职者
     * COMPANY - 企业
     */
    private String role;

    /**
     * 账户状态（VARCHAR 大写枚举）
     * NORMAL   - 正常
     * DISABLED - 禁用
     * BANNED   - 封禁
     */
    private String status;

    /** 头像 URL */
    private String avatarUrl;

    /** 创建时间（自动填充） */
    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createdAt;

    /** 更新时间（自动填充） */
    @TableField(fill = FieldFill.INSERT_UPDATE)
    private LocalDateTime updatedAt;

    /** 逻辑删除标记（"0"未删/"1"已删） */
    @TableLogic
    private String deletedAt;
}
