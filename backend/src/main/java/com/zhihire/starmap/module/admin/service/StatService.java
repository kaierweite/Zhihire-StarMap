package com.zhihire.starmap.module.admin.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.github.benmanes.caffeine.cache.Cache;
import com.github.benmanes.caffeine.cache.Caffeine;
import com.zhihire.starmap.module.admin.dto.AdminStatDTO;
import com.zhihire.starmap.module.job.entity.Job;
import com.zhihire.starmap.module.job.mapper.JobMapper;
import com.zhihire.starmap.module.resume.entity.ParseTask;
import com.zhihire.starmap.module.resume.mapper.ParseTaskMapper;
import com.zhihire.starmap.module.user.entity.Company;
import com.zhihire.starmap.module.user.entity.User;
import com.zhihire.starmap.module.user.mapper.CompanyMapper;
import com.zhihire.starmap.module.user.mapper.UserMapper;
import org.springframework.stereotype.Service;

import java.util.concurrent.TimeUnit;

/**
 * 管理后台统计服务
 *
 * SQL 实时聚合 + Caffeine 短缓存（5 分钟）
 */
@Service
public class StatService {

    private final UserMapper userMapper;
    private final CompanyMapper companyMapper;
    private final JobMapper jobMapper;
    private final ParseTaskMapper parseTaskMapper;

    /** Caffeine 缓存：5 分钟过期 */
    private final Cache<String, AdminStatDTO> statCache = Caffeine.newBuilder()
            .expireAfterWrite(5, TimeUnit.MINUTES)
            .maximumSize(1)
            .build();

    public StatService(UserMapper userMapper, CompanyMapper companyMapper,
                       JobMapper jobMapper, ParseTaskMapper parseTaskMapper) {
        this.userMapper = userMapper;
        this.companyMapper = companyMapper;
        this.jobMapper = jobMapper;
        this.parseTaskMapper = parseTaskMapper;
    }

    /**
     * 获取统计数据（缓存 5 分钟）
     */
    public AdminStatDTO getStats() {
        AdminStatDTO cached = statCache.getIfPresent("stats");
        if (cached != null) return cached;

        AdminStatDTO stats = AdminStatDTO.builder()
                .userCount(userMapper.selectCount(null))
                .companyCount(companyMapper.selectCount(null))
                .jobCount(jobMapper.selectCount(null))
                .matchCount(0L)  // day09 接入匹配模块后补充
                .parseCount(parseTaskMapper.selectCount(null))
                .build();

        statCache.put("stats", stats);
        return stats;
    }
}
