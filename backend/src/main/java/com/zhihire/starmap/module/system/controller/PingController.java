package com.zhihire.starmap.module.system.controller;

import com.zhihire.starmap.module.common.result.Result;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import javax.sql.DataSource;
import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.Statement;

/**
 * 冒烟验证控制器
 *
 * 职责：提供 /api/ping 端点，验证服务启动 + 数据库连通
 * 不需要认证，供部署后快速确认环境是否就绪
 */
@Slf4j
@RestController
@RequestMapping("/api")
public class PingController {

    /** 数据源（构造注入） */
    private final DataSource dataSource;

    /**
     * 构造注入数据源
     *
     * @param dataSource 数据库连接池
     */
    @Autowired
    public PingController(DataSource dataSource) {
        this.dataSource = dataSource;
    }

    /**
     * 冒烟验证端点
     *
     * 验证：
     * 1. Spring Boot 服务正常启动
     * 2. 数据库 JDBC 连接正常（SELECT 1）
     *
     * @return 包含 "pong" 的统一结果
     */
    @GetMapping("/ping")
    public Result<String> ping() {
        try (Connection conn = dataSource.getConnection();
             Statement stmt = conn.createStatement();
             ResultSet rs = stmt.executeQuery("SELECT 1")) {
            if (rs.next()) {
                log.info("数据库连通验证通过");
                return Result.ok("pong");
            }
        } catch (Exception e) {
            log.error("数据库连通验证失败：{}", e.getMessage(), e);
            return Result.error(500, "数据库连接失败：" + e.getMessage());
        }
        return Result.error(500, "数据库查询异常");
    }
}
