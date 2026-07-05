package com.zhihire.starmap.config;

import com.baomidou.mybatisplus.annotation.DbType;
import com.baomidou.mybatisplus.core.handlers.MetaObjectHandler;
import com.baomidou.mybatisplus.extension.plugins.MybatisPlusInterceptor;
import com.baomidou.mybatisplus.extension.plugins.inner.PaginationInnerInterceptor;
import lombok.extern.slf4j.Slf4j;
import org.apache.ibatis.reflection.MetaObject;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.stereotype.Component;

import java.time.LocalDateTime;

/**
 * MyBatis-Plus 配置
 *
 * 注册分页插件 + 自动填充处理器
 */
@Slf4j
@Configuration
public class MybatisPlusConfig {

    /**
     * 分页插件
     * 使用 PostgreSQL 方言（KingbaseES 兼容 PostgreSQL）
     *
     * @return MybatisPlusInterceptor
     */
    @Bean
    public MybatisPlusInterceptor mybatisPlusInterceptor() {
        MybatisPlusInterceptor interceptor = new MybatisPlusInterceptor();
        // 使用 PostgreSQL 方言，KingbaseES 与 PostgreSQL 兼容
        PaginationInnerInterceptor paginationInterceptor = new PaginationInnerInterceptor(DbType.POSTGRE_SQL);
        // 超过最大页数后自动调整到第一页
        paginationInterceptor.setOverflow(true);
        interceptor.addInnerInterceptor(paginationInterceptor);
        return interceptor;
    }

    /**
     * 自动填充处理器
     * 插入时自动填充 created_at / updated_at
     * 更新时自动填充 updated_at
     */
    @Component
    public static class AutoFillHandler implements MetaObjectHandler {

        /**
         * 插入时自动填充
         *
         * @param metaObject 元对象
         */
        @Override
        public void insertFill(MetaObject metaObject) {
            LocalDateTime now = LocalDateTime.now();
            // 自动填充创建时间
            this.strictInsertFill(metaObject, "createdAt", LocalDateTime.class, now);
            // 自动填充更新时间
            this.strictInsertFill(metaObject, "updatedAt", LocalDateTime.class, now);
        }

        /**
         * 更新时自动填充
         *
         * @param metaObject 元对象
         */
        @Override
        public void updateFill(MetaObject metaObject) {
            // 自动填充更新时间
            this.strictUpdateFill(metaObject, "updatedAt", LocalDateTime.class, LocalDateTime.now());
        }
    }
}
