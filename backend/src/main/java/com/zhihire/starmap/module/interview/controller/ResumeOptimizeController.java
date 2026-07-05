package com.zhihire.starmap.module.interview.controller;

import com.zhihire.starmap.module.common.result.Result;
import com.zhihire.starmap.module.interview.dto.ResumeOptimizeRequest;
import com.zhihire.starmap.module.interview.entity.ResumeOptimization;
import com.zhihire.starmap.module.interview.service.InterviewService;
import jakarta.validation.Valid;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * 简历优化控制器
 */
@RestController
@RequestMapping("/api/resume")
public class ResumeOptimizeController {

    private final InterviewService interviewService;

    public ResumeOptimizeController(InterviewService interviewService) {
        this.interviewService = interviewService;
    }

    /** 生成简历优化建议 */
    @PostMapping("/optimize")
    public Result<ResumeOptimization> optimizeResume(
            @Valid @RequestBody ResumeOptimizeRequest request,
            Authentication authentication) {
        Long userId = (Long) authentication.getPrincipal();
        return Result.ok(interviewService.optimizeResume(userId, request));
    }

    /** 获取简历优化建议 */
    @GetMapping("/{resumeId}/optimization")
    public Result<List<ResumeOptimization>> getOptimizations(
            @PathVariable Long resumeId,
            Authentication authentication) {
        Long userId = (Long) authentication.getPrincipal();
        return Result.ok(interviewService.getOptimizations(resumeId, userId));
    }
}
