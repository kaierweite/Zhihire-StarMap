package com.zhihire.starmap.module.job.controller;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.zhihire.starmap.module.common.result.Result;
import com.zhihire.starmap.module.job.dto.JobRequest;
import com.zhihire.starmap.module.job.dto.JobStatusRequest;
import com.zhihire.starmap.module.job.entity.Job;
import com.zhihire.starmap.module.job.entity.JobSkill;
import com.zhihire.starmap.module.job.service.JobService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.util.List;

/**
 * 岗位控制器（企业端）
 *
 * 职责：岗位 CRUD、手动/JD 双模式创建
 * 需认证，企业角色操作
 */
@Tag(name = "岗位管理", description = "企业端岗位 CRUD")
@RestController
@RequestMapping("/api/job")
public class JobController {

    private final JobService jobService;

    public JobController(JobService jobService) {
        this.jobService = jobService;
    }

    /**
     * 创建岗位（手动填写）
     *
     * @param request        岗位信息 + 技能列表
     * @param authentication 认证对象
     * @return 创建的岗位
     */
    @PostMapping("/create")
    public Result<Job> createJob(@Valid @RequestBody JobRequest request,
                                 Authentication authentication) {
        Long userId = (Long) authentication.getPrincipal();
        Job job = jobService.createJob(userId, request);
        return Result.ok(job);
    }

    /**
     * 创建岗位（JD 文件上传）
     *
     * @param file           JD 文件（PDF/DOC/DOCX）
     * @param authentication 认证对象
     * @return 创建的岗位（初始 DRAFT，待异步解析）
     */
    @PostMapping("/upload")
    public Result<Job> uploadJob(@RequestParam("file") MultipartFile file,
                                 Authentication authentication) {
        Long userId = (Long) authentication.getPrincipal();
        Job job = jobService.createJobByUpload(userId, file);
        return Result.ok(job);
    }

    /**
     * 更新岗位
     */
    @PutMapping("/{id}")
    public Result<Void> updateJob(@PathVariable Long id,
                                  @Valid @RequestBody JobRequest request,
                                  Authentication authentication) {
        Long userId = (Long) authentication.getPrincipal();
        jobService.updateJob(userId, id, request);
        return Result.ok();
    }

    /**
     * 切换岗位状态
     */
    @PutMapping("/{id}/status")
    public Result<Void> updateJobStatus(@PathVariable Long id,
                                        @Valid @RequestBody JobStatusRequest request,
                                        Authentication authentication) {
        Long userId = (Long) authentication.getPrincipal();
        jobService.updateJobStatus(userId, id, request);
        return Result.ok();
    }

    /**
     * 企业岗位列表（分页）
     */
    @GetMapping("/list")
    public Result<Page<Job>> listJobs(
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "20") int size,
            Authentication authentication) {
        Long userId = (Long) authentication.getPrincipal();
        return Result.ok(jobService.listCompanyJobs(userId, page, size));
    }

    /**
     * 岗位技能列表
     */
    @GetMapping("/{id}/skills")
    public Result<List<JobSkill>> getJobSkills(@PathVariable Long id) {
        return Result.ok(jobService.getJobSkills(id));
    }
}
