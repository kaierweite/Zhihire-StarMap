package com.zhihire.starmap.module.auth.util;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import javax.crypto.SecretKey;
import java.nio.charset.StandardCharsets;
import java.util.Date;
import java.util.HashMap;
import java.util.Map;

/**
 * JWT 工具类
 *
 * 职责：签发 Token、解析 Token、提取 Claims
 * Token 结构：sub=userId, role=大写角色, iat/exp=时间戳
 */
@Component
public class JwtUtils {

    /** JWT 签名密钥（从 application.yml 读取） */
    @Value("${jwt.secret}")
    private String jwtSecret;

    /** Token 有效期（毫秒，默认 24 小时） */
    @Value("${jwt.expiration}")
    private long expiration;

    /**
     * 签发 JWT Token
     *
     * @param userId 用户 ID（存入 sub claim）
     * @param username 用户名
     * @param role   用户角色（大写：ADMIN/USER/COMPANY）
     * @return JWT Token 字符串
     */
    public String generateToken(Long userId, String username, String role) {
        // 自定义 Claims：userId + role
        Map<String, Object> claims = new HashMap<>();
        claims.put("userId", userId);
        claims.put("role", role);

        Date now = new Date();
        Date expiryDate = new Date(now.getTime() + expiration);

        return Jwts.builder()
                .claims(claims)
                .subject(userId.toString())  // sub 存 userId
                .issuedAt(now)
                .expiration(expiryDate)
                .signWith(getSigningKey())
                .compact();
    }

    /**
     * 解析 Token 获取所有 Claims
     *
     * @param token JWT Token
     * @return Claims（含 userId/role/sub/iat/exp）
     */
    public Claims parseToken(String token) {
        return Jwts.parser()
                .verifyWith(getSigningKey())
                .build()
                .parseSignedClaims(token)
                .getPayload();
    }

    /**
     * 从 Token 提取用户 ID
     *
     * @param token JWT Token
     * @return 用户 ID
     */
    public Long getUserId(String token) {
        Claims claims = parseToken(token);
        return claims.get("userId", Long.class);
    }

    /**
     * 从 Token 提取角色
     *
     * @param token JWT Token
     * @return 角色字符串（大写）
     */
    public String getRole(String token) {
        Claims claims = parseToken(token);
        return claims.get("role", String.class);
    }

    /**
     * 验证 Token 是否有效（未过期 + 签名正确）
     *
     * @param token JWT Token
     * @return true 有效，false 无效或已过期
     */
    public boolean validateToken(String token) {
        try {
            Claims claims = parseToken(token);
            // 检查是否过期
            return !claims.getExpiration().before(new Date());
        } catch (Exception e) {
            return false;
        }
    }

    /**
     * 获取 HMAC 签名密钥
     *
     * @return SecretKey
     */
    private SecretKey getSigningKey() {
        return Keys.hmacShaKeyFor(jwtSecret.getBytes(StandardCharsets.UTF_8));
    }
}
