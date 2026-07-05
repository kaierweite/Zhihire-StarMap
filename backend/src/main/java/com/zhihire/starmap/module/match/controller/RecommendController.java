package com.zhihire.starmap.module.match.controller;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.zhihire.starmap.module.common.result.Result;
import com.zhihire.starmap.module.match.dto.RecommendDTO;
import com.zhihire.starmap.module.match.entity.MatchResult;
import com.zhihire.starmap.module.match.service.RecommendService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

/**
 * 推荐控制器
 *
 * 职责：求职者岗位推荐 + 企业人才推荐 + 匹配详情
 */
@Tag(name = "推荐接口", description = "岗位推荐/人才推荐")
@RestController
@RequestMapping("/api/recommend")
public class RecommendController {

    private final RecommendService recommendService;

    public RecommendController(RecommendService recommendService) {
        this.recommendService = recommendService;
    }

    /**
     * 求职者岗位推荐（分页）
     *
     * 基于用户技能召回候选岗位，懒计算匹配分，按分数降序返回
     */
    @GetMapping("/jobs")
    public Result<Page<RecommendDTO>> recommendJobs(
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "20") int size,
            Authentication authentication) {
        Long userId = (Long) authentication.getPrincipal();
        return Result.ok(recommendService.recommendJobs(userId, page, size));
    }

    /**
     * 企业人才推荐（分页）
     *
     * 基于岗位技能召回候选人才，懒计算匹配分
     *
     * @param jobId 岗位 ID
     */
    @GetMapping("/talents")
    public Result<Page<RecommendDTO>> recommendTalents(
            @RequestParam Long jobId,
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "20") int size,
            Authentication authentication) {
        Long userId = (Long) authentication.getPrincipal();
        return Result.ok(recommendService.recommendTalents(userId, jobId, page, size));
    }

    /**
     * 某岗位匹配详情（触发懒计算）
     *
     * @param jobId 岗位 ID
     */
    @GetMapping("/job/{jobId}/detail")
    public Result<MatchResult> getMatchDetail(@PathVariable Long jobId,
                                              Authentication authentication) {
        Long userId = (Long) authentication.getPrincipal();
        // 获取用户简历（简化：取最新简历）
        return Result.ok(recommendService.getMatchDetail(userId, jobId));
    }
}
