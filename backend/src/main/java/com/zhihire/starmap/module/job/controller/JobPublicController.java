package com.zhihire.starmap.module.job.controller;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.zhihire.starmap.module.common.result.Result;
import com.zhihire.starmap.module.job.entity.Job;
import com.zhihire.starmap.module.job.entity.JobSkill;
import com.zhihire.starmap.module.job.service.JobService;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * 岗位公开查询控制器（无需企业身份）
 *
 * 职责：对外岗位列表 + 岗位详情
 * 仅返回 status=OPEN 且企业已审核的岗位
 */
@RestController
@RequestMapping("/api/job/public")
public class JobPublicController {

    private final JobService jobService;

    public JobPublicController(JobService jobService) {
        this.jobService = jobService;
    }

    /**
     * 对外岗位列表（分页）
     *
     * @param page    页码
     * @param size    每页条数
     * @param city    城市筛选（可选）
     * @param keyword 关键词搜索（可选，搜标题+描述）
     * @return 岗位分页列表
     */
    @GetMapping("/list")
    public Result<Page<Job>> listPublicJobs(
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "20") int size,
            @RequestParam(required = false) String city,
            @RequestParam(required = false) String keyword) {
        return Result.ok(jobService.listPublicJobs(page, size, city, keyword));
    }

    /**
     * 岗位详情
     *
     * @param id 岗位 ID
     * @return 岗位信息
     */
    @GetMapping("/{id}")
    public Result<Job> getPublicJob(@PathVariable Long id) {
        return Result.ok(jobService.getPublicJob(id));
    }

    /**
     * 岗位技能列表
     */
    @GetMapping("/{id}/skills")
    public Result<List<JobSkill>> getJobSkills(@PathVariable Long id) {
        return Result.ok(jobService.getJobSkills(id));
    }
}
