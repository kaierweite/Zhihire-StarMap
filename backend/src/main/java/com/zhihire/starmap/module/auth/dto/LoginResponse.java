package com.zhihire.starmap.module.auth.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * 登录响应 DTO
 *
 * 包含 JWT Token 和用户基本信息，前端据此存储登录态
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class LoginResponse {

    /** JWT Token（前端存 localStorage/cookie，后续请求放 Authorization 头） */
    private String token;

    /** 用户角色：ADMIN/USER/COMPANY */
    private String role;

    /** 用户 ID */
    private Long userId;

    /** 用户昵称/用户名 */
    private String nickname;
}
