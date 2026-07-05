package com.zhihire.starmap.config;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.web.authentication.WebAuthenticationDetailsSource;
import org.springframework.stereotype.Component;
import org.springframework.util.StringUtils;
import org.springframework.web.filter.OncePerRequestFilter;

import javax.crypto.SecretKey;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.Collections;
import java.util.List;

/**
 * JWT 认证过滤器
 *
 * 职责：从请求头提取 JWT Token，解析验证后设置 Spring Security 上下文
 * 继承 OncePerRequestFilter 保证每次请求只执行一次
 *
 * 当前为骨架实现，day03 会补充完整 Token 刷新/过期处理逻辑
 */
@Slf4j
@Component
public class JwtAuthenticationFilter extends OncePerRequestFilter {

    /** JWT 密钥（从 application.yml 读取） */
    @Value("${jwt.secret}")
    private String jwtSecret;

    /** Authorization 请求头前缀 */
    private static final String BEARER_PREFIX = "Bearer ";

    /**
     * 核心过滤逻辑：提取并验证 JWT
     *
     * @param request     HTTP 请求
     * @param response    HTTP 响应
     * @param filterChain 过滤器链
     * @throws ServletException Servlet 异常
     * @throws IOException      IO 异常
     */
    @Override
    protected void doFilterInternal(HttpServletRequest request,
                                    HttpServletResponse response,
                                    FilterChain filterChain)
            throws ServletException, IOException {
        try {
            // 从 Authorization 头提取 Token
            String token = extractToken(request);

            // Token 有效则解析并设置认证上下文
            if (StringUtils.hasText(token) && validateToken(token)) {
                Claims claims = parseToken(token);

                // 从 claims 提取用户名和角色
                String username = claims.getSubject();
                String role = claims.get("role", String.class);

                // 构建 Spring Security 认证对象
                // 角色以大写存储（ADMIN/USER/COMPANY），加 ROLE_ 前缀供 Spring Security 识别
                List<SimpleGrantedAuthority> authorities = StringUtils.hasText(role)
                        ? List.of(new SimpleGrantedAuthority("ROLE_" + role))
                        : Collections.emptyList();

                UsernamePasswordAuthenticationToken authentication =
                        new UsernamePasswordAuthenticationToken(
                                username, null, authorities);
                authentication.setDetails(
                        new WebAuthenticationDetailsSource().buildDetails(request));

                // 设置到 Security 上下文，后续 Controller 可通过 @AuthenticationPrincipal 获取
                SecurityContextHolder.getContext().setAuthentication(authentication);
            }
        } catch (Exception e) {
            // Token 解析失败不阻断请求，由后续鉴权拦截器处理 401
            log.debug("JWT 认证跳过：{}", e.getMessage());
        }

        filterChain.doFilter(request, response);
    }

    /**
     * 从请求头提取 Bearer Token
     *
     * @param request HTTP 请求
     * @return Token 字符串，无 Token 时返回 null
     */
    private String extractToken(HttpServletRequest request) {
        String bearerToken = request.getHeader("Authorization");
        if (StringUtils.hasText(bearerToken) && bearerToken.startsWith(BEARER_PREFIX)) {
            return bearerToken.substring(BEARER_PREFIX.length());
        }
        return null;
    }

    /**
     * 验证 Token 有效性（签名 + 过期时间）
     *
     * @param token JWT Token
     * @return true 有效，false 无效或已过期
     */
    private boolean validateToken(String token) {
        try {
            parseToken(token);
            return true;
        } catch (Exception e) {
            log.debug("Token 验证失败：{}", e.getMessage());
            return false;
        }
    }

    /**
     * 解析 JWT Token 获取 Claims
     *
     * @param token JWT Token
     * @return Claims 声明
     */
    private Claims parseToken(String token) {
        SecretKey key = Keys.hmacShaKeyFor(jwtSecret.getBytes(StandardCharsets.UTF_8));
        return Jwts.parser()
                .verifyWith(key)
                .build()
                .parseSignedClaims(token)
                .getPayload();
    }
}
