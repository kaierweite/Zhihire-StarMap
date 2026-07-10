package com.zhihire.starmap.module.admin.service;

import com.github.benmanes.caffeine.cache.Cache;
import com.github.benmanes.caffeine.cache.Caffeine;
import com.zhihire.starmap.module.admin.dto.AdminStatDTO;
import com.zhihire.starmap.module.job.mapper.JobMapper;
import com.zhihire.starmap.module.resume.mapper.ParseTaskMapper;
import com.zhihire.starmap.module.user.mapper.CompanyMapper;
import com.zhihire.starmap.module.user.mapper.UserMapper;
import org.springframework.stereotype.Service;
import java.util.concurrent.TimeUnit;

@Service
public class StatServiceImpl implements StatService {

    private final UserMapper userMapper;
    private final CompanyMapper companyMapper;
    private final JobMapper jobMapper;
    private final ParseTaskMapper parseTaskMapper;
    private final Cache<String, AdminStatDTO> statCache = Caffeine.newBuilder()
            .expireAfterWrite(5, TimeUnit.MINUTES).maximumSize(1).build();

    public StatServiceImpl(UserMapper userMapper, CompanyMapper companyMapper,
                           JobMapper jobMapper, ParseTaskMapper parseTaskMapper) {
        this.userMapper = userMapper;
        this.companyMapper = companyMapper;
        this.jobMapper = jobMapper;
        this.parseTaskMapper = parseTaskMapper;
    }

    @Override
    public AdminStatDTO getStats() {
        AdminStatDTO cached = statCache.getIfPresent("stats");
        if (cached != null) return cached;
        AdminStatDTO stats = AdminStatDTO.builder()
                .userCount(userMapper.selectCount(null))
                .companyCount(companyMapper.selectCount(null))
                .jobCount(jobMapper.selectCount(null))
                .matchCount(0L)
                .parseCount(parseTaskMapper.selectCount(null))
                .build();
        statCache.put("stats", stats);
        return stats;
    }
}