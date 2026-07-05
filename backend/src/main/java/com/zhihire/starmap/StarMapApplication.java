package com.zhihire.starmap;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * 智聘星图后端启动类
 *
 * 职责：Spring Boot 应用入口，扫描所有子模块组件
 * MapperScan 路径 com.zhihire.starmap.module.*.mapper 一行扫全模块 Mapper
 */
@SpringBootApplication
@MapperScan("com.zhihire.starmap.module.*.mapper")
public class StarMapApplication {

    /**
     * 主方法，启动 Spring Boot 应用
     *
     * @param args 命令行参数
     */
    public static void main(String[] args) {
        SpringApplication.run(StarMapApplication.class, args);
    }
}
