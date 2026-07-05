package com.zhihire.starmap.config;

import com.zhihire.starmap.module.auth.util.JwtUtils;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.web.authentication.WebAuthenticationDetailsSource;
import org.springframework.stereotype.Component;
import org.springframework.util.StringUtils;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.util.Collections;
import java.util.List;

/**
 * JWT 认证过滤器
 *
 * 职责：从请求头提取 JWT Token，解析验证后设置 Spring Security 上下文
 * 继承 OncePerRequestFilter 保证每次请求只执行一次
 * 使用 JwtUtils 统一处理 Token 解析与校验
 */
@Slf4j
@Component
public class JwtAuthenticationFilter extends OncePerRequestFilter {

    /** JWT 工具类（构造注入） */
    private final JwtUtils jwtUtils;

    /** Authorization 请求头前缀 */
    private static final String BEARER_PREFIX = "Bearer ";

    /**
     * 构造注入
     *
     * @param jwtUtils JWT 工具类
     */
    public JwtAuthenticationFilter(JwtUtils jwtUtils) {
        this.jwtUtils = jwtUtils;
    }

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
            if (StringUtils.hasText(token) && jwtUtils.validateToken(token)) {
                // 从 Token 提取 userId 和角色
                Long userId = jwtUtils.getUserId(token);
                String role = jwtUtils.getRole(token);

                // 构建 Spring Security 认证对象
                // 角色以大写存储（ADMIN/USER/COMPANY），加 ROLE_ 前缀供 Spring Security 识别
                List<SimpleGrantedAuthority> authorities = StringUtils.hasText(role)
                        ? List.of(new SimpleGrantedAuthority("ROLE_" + role))
                        : Collections.emptyList();

                // principal 存 userId，后续 Controller 可通过 @AuthenticationPrincipal 获取
                UsernamePasswordAuthenticationToken authentication =
                        new UsernamePasswordAuthenticationToken(
                                userId, null, authorities);
                authentication.setDetails(
                        new WebAuthenticationDetailsSource().buildDetails(request));

                // 设置到 Security 上下文
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
}
