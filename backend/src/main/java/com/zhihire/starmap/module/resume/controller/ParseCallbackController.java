package com.zhihire.starmap.module.resume.controller;

import com.zhihire.starmap.module.common.result.Result;
import com.zhihire.starmap.module.resume.dto.ParseCallbackRequest;
import com.zhihire.starmap.module.resume.service.ParseCallbackService;
import jakarta.validation.Valid;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * 解析回调控制器
 *
 * 职责：接收 AI 服务解析完成后的回调
 * 路径 /api/parse/callback，公开访问（AI 服务调用）
 */
@Slf4j
@RestController
@RequestMapping("/api/parse")
public class ParseCallbackController {

    private final ParseCallbackService parseCallbackService;

    public ParseCallbackController(ParseCallbackService parseCallbackService) {
        this.parseCallbackService = parseCallbackService;
    }

    /**
     * AI 解析完成回调
     *
     * AI 服务解析简历/JD 完成后调用此接口，传入解析结果
     * 后端更新 parse_task、resume、技能归一入库、user_skill 写入
     *
     * @param request 回调请求
     * @return 统一结果
     */
    @PostMapping("/callback")
    public Result<Void> handleCallback(@Valid @RequestBody ParseCallbackRequest request) {
        log.info("收到解析回调：parseTaskId={}, status={}", request.getParseTaskId(), request.getStatus());
        parseCallbackService.handleCallback(request);
        return Result.ok();
    }
}
