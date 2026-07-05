package com.zhihire.starmap.module.graph.controller;

import com.zhihire.starmap.module.common.result.Result;
import com.zhihire.starmap.module.graph.service.GraphService;
import com.zhihire.starmap.module.system.service.SkillNormalizationService;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;

import java.util.Map;

/**
 * 能力图谱控制器
 *
 * 职责：个人/岗位图谱、缺口分析、图谱重建触发
 */
@RestController
@RequestMapping("/api/graph")
public class GraphController {

    private final GraphService graphService;

    @Value("${ai.service.url:http://localhost:8000}")
    private String aiServiceUrl;

    public GraphController(GraphService graphService) {
        this.graphService = graphService;
    }

    /** 个人能力图谱（ECharts 格式） */
    @GetMapping("/user/{userId}")
    public Result<Map<String, Object>> getUserGraph(@PathVariable Long userId) {
        return Result.ok(graphService.getUserGraph(userId));
    }

    /** 岗位能力图谱 */
    @GetMapping("/job/{jobId}")
    public Result<Map<String, Object>> getJobGraph(@PathVariable Long jobId) {
        return Result.ok(graphService.getJobGraph(jobId));
    }

    /** 缺口分析：用户技能 vs 岗位要求 */
    @GetMapping("/gap/{userId}/{jobId}")
    public Result<Map<String, Object>> getGapAnalysis(@PathVariable Long userId,
                                                      @PathVariable Long jobId) {
        return Result.ok(graphService.getGapAnalysis(userId, jobId));
    }

    /** 触发图谱重建（通知 AI 服务） */
    @PostMapping("/reload")
    @PreAuthorize("hasRole('ADMIN')")
    public Result<Void> reloadGraph() {
        try {
            RestTemplate restTemplate = new RestTemplate();
            restTemplate.postForEntity(aiServiceUrl + "/ai/graph/reload", null, String.class);
        } catch (Exception e) {
            // AI 服务不可用不阻断
        }
        return Result.ok();
    }
}
