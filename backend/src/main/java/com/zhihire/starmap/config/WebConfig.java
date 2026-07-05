package com.zhihire.starmap.config;

import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.CorsRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

/**
 * Web MVC 配置
 *
 * 职责：跨域（CORS）配置、静态资源映射等 Web 层通用配置
 */
@Configuration
public class WebConfig implements WebMvcConfigurer {

    /**
     * CORS 跨域配置
     *
     * 允许前端 Vue 开发服务器（默认 5173 端口）跨域访问后端 API
     * 生产环境应通过 Nginx 反向代理，此配置仅做兜底
     *
     * @param registry CORS 注册器
     */
    @Override
    public void addCorsMappings(CorsRegistry registry) {
        registry.addMapping("/api/**")
                // 允许的来源（本地开发 + 生产部署）
                .allowedOriginPatterns("*")
                // 允许的 HTTP 方法
                .allowedMethods("GET", "POST", "PUT", "DELETE", "OPTIONS")
                // 允许的请求头
                .allowedHeaders("*")
                // 允许携带 Cookie/Authorization 头
                .allowCredentials(true)
                // 预检请求缓存时间（秒）
                .maxAge(3600);
    }
}
