package com.zhihire.starmap.module.auth.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;
import lombok.Data;

/**
 * 注册请求 DTO
 */
@Data
public class RegisterRequest {

    /** 登录用户名（3~50 字符，字母数字下划线） */
    @NotBlank(message = "用户名不能为空")
    @Size(min = 3, max = 50, message = "用户名长度 3~50 字符")
    private String username;

    /** 登录密码（6~100 字符） */
    @NotBlank(message = "密码不能为空")
    @Size(min = 6, max = 100, message = "密码长度 6~100 字符")
    private String password;

    /**
     * 用户角色
     * 只允许注册 USER（求职者）或 COMPANY（企业）
     * ADMIN 由种子数据创建，不开放注册
     */
    @NotBlank(message = "角色不能为空")
    @Pattern(regexp = "USER|COMPANY", message = "角色只能是 USER 或 COMPANY")
    private String role;
}
