package com.zhihire.starmap.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.annotation.web.configurers.AbstractHttpConfigurer;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;

/**
 * Spring Security 配置
 *
 * 职责：定义安全过滤链规则，配置公开/受保护端点，注册 JWT 过滤器
 * 当前阶段为骨架配置，day03 会补充完整 JWT 鉴权逻辑
 */
@Configuration
@EnableWebSecurity
public class SecurityConfig {

    /** JWT 认证过滤器（构造注入） */
    private final JwtAuthenticationFilter jwtAuthenticationFilter;

    /**
     * 构造注入 JWT 过滤器
     *
     * @param jwtAuthenticationFilter JWT 认证过滤器
     */
    public SecurityConfig(JwtAuthenticationFilter jwtAuthenticationFilter) {
        this.jwtAuthenticationFilter = jwtAuthenticationFilter;
    }

    /**
     * 安全过滤链配置
     *
     * - 禁用 CSRF（REST API 无需 CSRF）
     * - 无状态 session（JWT 鉴权，不依赖服务端 session）
     * - 公开端点：/api/ping、/api/auth/**、Swagger 文档
     * - 其余端点需认证
     *
     * @param http HttpSecurity 配置对象
     * @return SecurityFilterChain
     * @throws Exception 配置异常
     */
    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
                // 禁用 CSRF（REST API 使用 JWT，无需 CSRF 保护）
                .csrf(AbstractHttpConfigurer::disable)
                // 无状态 session（不创建 HttpSession）
                .sessionManagement(session ->
                        session.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
                // 请求授权规则
                .authorizeHttpRequests(auth -> auth
                        // 冒烟验证端点：完全公开
                        .requestMatchers("/api/ping").permitAll()
                        // 认证相关端点：登录/注册/刷新 Token 公开
                        .requestMatchers("/api/auth/**").permitAll()
                        // Swagger/Knife4j 文档端点公开
                        .requestMatchers("/swagger-ui/**", "/v3/api-docs/**",
                                "/doc.html/**", "/webjars/**").permitAll()
                        // H2 Console（仅 dev 环境）
                        .requestMatchers("/h2-console/**").permitAll()
                        // 其余所有请求需认证
                        .anyRequest().authenticated()
                )
                // 在 UsernamePasswordAuthenticationFilter 之前插入 JWT 过滤器
                .addFilterBefore(jwtAuthenticationFilter,
                        UsernamePasswordAuthenticationFilter.class);

        return http.build();
    }

    /**
     * BCrypt 密码编码器
     * 用于密码加密存储和校验
     *
     * @return PasswordEncoder
     */
    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }
}
