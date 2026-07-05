package com.zhihire.starmap.module.interview.controller;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.zhihire.starmap.module.common.result.Result;
import com.zhihire.starmap.module.interview.dto.InterviewAnswerRequest;
import com.zhihire.starmap.module.interview.dto.InterviewStartRequest;
import com.zhihire.starmap.module.interview.dto.ResumeOptimizeRequest;
import com.zhihire.starmap.module.interview.entity.*;
import com.zhihire.starmap.module.interview.service.InterviewService;
import jakarta.validation.Valid;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

/**
 * 面试控制器
 *
 * 职责：模拟面试全链路 + 简历优化
 */
@RestController
@RequestMapping("/api/interview")
public class InterviewController {

    private final InterviewService interviewService;

    public InterviewController(InterviewService interviewService) {
        this.interviewService = interviewService;
    }

    /** 开始模拟面试 */
    @PostMapping("/start")
    public Result<InterviewSession> startSession(
            @RequestBody(required = false) InterviewStartRequest request,
            Authentication authentication) {
        Long userId = (Long) authentication.getPrincipal();
        if (request == null) request = new InterviewStartRequest();
        return Result.ok(interviewService.startSession(userId, request));
    }

    /** 生成面试题 */
    @PostMapping("/questions")
    public Result<List<InterviewQuestion>> generateQuestions(@RequestParam Long sessionId) {
        return Result.ok(interviewService.generateQuestions(sessionId));
    }

    /** 提交回答 + AI 评分 */
    @PostMapping("/answer")
    public Result<InterviewAnswer> submitAnswer(
            @Valid @RequestBody InterviewAnswerRequest request,
            Authentication authentication) {
        Long userId = (Long) authentication.getPrincipal();
        return Result.ok(interviewService.submitAnswer(userId, request));
    }

    /** 生成面试报告 */
    @PostMapping("/report")
    public Result<InterviewReport> generateReport(@RequestParam Long sessionId) {
        return Result.ok(interviewService.generateReport(sessionId));
    }

    /** 面试记录列表 */
    @GetMapping("/list")
    public Result<Page<InterviewSession>> listSessions(
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "20") int size,
            Authentication authentication) {
        Long userId = (Long) authentication.getPrincipal();
        return Result.ok(interviewService.listSessions(userId, page, size));
    }

    /** 面试详情（含问题 + 报告） */
    @GetMapping("/{sessionId}")
    public Result<Map<String, Object>> getSessionDetail(
            @PathVariable Long sessionId,
            Authentication authentication) {
        Long userId = (Long) authentication.getPrincipal();
        return Result.ok(interviewService.getSessionDetail(sessionId, userId));
    }

    /** 题库列表 */
    @GetMapping("/question-bank")
    public Result<Page<InterviewQuestion>> listQuestionBank(
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "20") int size) {
        return Result.ok(interviewService.listQuestionBank(page, size));
    }
}
