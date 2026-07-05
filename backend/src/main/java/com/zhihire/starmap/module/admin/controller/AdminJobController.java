package com.zhihire.starmap.module.admin.controller;

import com.zhihire.starmap.module.common.exception.BusinessException;
import com.zhihire.starmap.module.common.result.Result;
import com.zhihire.starmap.module.job.entity.Job;
import com.zhihire.starmap.module.job.mapper.JobMapper;
import com.zhihire.starmap.module.system.annotation.OperationLog;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

/**
 * 管理后台 — 岗位管理
 */
@Slf4j
@RestController
@RequestMapping("/api/admin/job")
@PreAuthorize("hasRole('ADMIN')")
public class AdminJobController {

    private final JobMapper jobMapper;

    public AdminJobController(JobMapper jobMapper) {
        this.jobMapper = jobMapper;
    }

    /** 强制下架岗位 */
    @PutMapping("/{id}/close")
    @OperationLog("岗位管理/强制下架")
    public Result<Void> closeJob(@PathVariable Long id) {
        Job job = jobMapper.selectById(id);
        if (job == null) throw new BusinessException(404, "岗位不存在");
        job.setStatus("CLOSED");
        jobMapper.updateById(job);
        log.info("岗位强制下架：jobId={}", id);
        return Result.ok();
    }
}
