package com.zhihire.starmap.module.admin.controller;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.zhihire.starmap.module.admin.dto.AiModelConfigVO;
import com.zhihire.starmap.module.admin.dto.TestConnectionRequest;
import com.zhihire.starmap.module.admin.dto.TestConnectionResponse;
import com.zhihire.starmap.module.admin.entity.AiModelConfig;
import com.zhihire.starmap.module.admin.mapper.AiModelConfigMapper;
import com.zhihire.starmap.module.common.exception.BusinessException;
import com.zhihire.starmap.module.common.result.Result;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;

@Slf4j
@RestController
@RequestMapping("/api/admin/ai")
@PreAuthorize("hasRole('ADMIN')")
public class AdminAIConfigController {

    private final AiModelConfigMapper configMapper;
    private final ObjectMapper objectMapper;

    public AdminAIConfigController(AiModelConfigMapper configMapper, ObjectMapper objectMapper) {
        this.configMapper = configMapper;
        this.objectMapper = objectMapper;
    }

    /** GET /api/admin/ai/config — list all provider configs */
    @GetMapping("/config")
    public Result<List<AiModelConfigVO>> listConfigs() {
        List<AiModelConfig> list = configMapper.selectList(
                new LambdaQueryWrapper<AiModelConfig>().orderByAsc(AiModelConfig::getId)
        );
        return Result.ok(list.stream().map(this::toVO).collect(Collectors.toList()));
    }

    /** POST /api/admin/ai/config — create new provider */
    @PostMapping("/config")
    public Result<AiModelConfigVO> createConfig(@RequestBody AiModelConfigVO vo) {
        AiModelConfig entity = fromVO(vo);
        configMapper.insert(entity);
        log.info("AI config created: providerId={}", entity.getProviderId());
        return Result.ok(toVO(entity));
    }

    /** PUT /api/admin/ai/config/{id} — update existing provider */
    @PutMapping("/config/{id}")
    public Result<AiModelConfigVO> updateConfig(@PathVariable Long id,
                                                 @RequestBody AiModelConfigVO vo) {
        AiModelConfig existing = configMapper.selectById(id);
        if (existing == null) throw new BusinessException(404, "配置不存在");
        AiModelConfig entity = fromVO(vo);
        entity.setId(id);
        configMapper.updateById(entity);
        log.info("AI config updated: id={}", id);
        return Result.ok(toVO(configMapper.selectById(id)));
    }

    /** DELETE /api/admin/ai/config/{id} */
    @DeleteMapping("/config/{id}")
    public Result<Void> deleteConfig(@PathVariable Long id) {
        AiModelConfig existing = configMapper.selectById(id);
        if (existing == null) throw new BusinessException(404, "配置不存在");
        configMapper.deleteById(id);
        log.info("AI config deleted: id={}", id);
        return Result.ok();
    }

    /** POST /api/admin/ai/test-connection — probe LLM endpoint */
    @PostMapping("/test-connection")
    public Result<TestConnectionResponse> testConnection(@RequestBody TestConnectionRequest req) {
        long start = System.currentTimeMillis();
        try {
            HttpClient client = HttpClient.newBuilder()
                    .connectTimeout(Duration.ofSeconds(10))
                    .build();
            String url = req.getBaseUrl().replaceAll("/+$", "") + "/chat/completions";
            String body = objectMapper.writeValueAsString(java.util.Map.of(
                    "model", req.getModel(),
                    "messages", List.of(java.util.Map.of("role", "user", "content", "Hi")),
                    "max_tokens", 5
            ));
            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create(url))
                    .header("Authorization", "Bearer " + req.getApiKey())
                    .header("Content-Type", "application/json")
                    .POST(HttpRequest.BodyPublishers.ofString(body))
                    .timeout(Duration.ofSeconds(15))
                    .build();
            HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());
            long latency = System.currentTimeMillis() - start;
            if (response.statusCode() >= 200 && response.statusCode() < 300) {
                log.info("AI test-connection OK: url={}, latency={}ms", url, latency);
                return Result.ok(new TestConnectionResponse(true, latency, "连接成功"));
            }
            log.warn("AI test-connection failed: url={}, status={}", url, response.statusCode());
            return Result.ok(new TestConnectionResponse(false, latency,
                    "HTTP " + response.statusCode() + ": " + response.body()));
        } catch (Exception e) {
            long latency = System.currentTimeMillis() - start;
            log.warn("AI test-connection error: {}", e.getMessage());
            return Result.ok(new TestConnectionResponse(false, latency, e.getMessage()));
        }
    }

    // ── helpers ──────────────────────────────────────────────
    private AiModelConfigVO toVO(AiModelConfig e) {
        AiModelConfigVO vo = new AiModelConfigVO();
        vo.setId(e.getId());
        vo.setProviderId(e.getProviderId());
        vo.setName(e.getName());
        vo.setEnabled(e.getEnabled());
        vo.setApiKey(e.getApiKey());
        vo.setBaseUrl(e.getBaseUrl());
        vo.setDefaultModel(e.getDefaultModel());
        vo.setModels(parseModels(e.getModelsJson()));
        vo.setTemperature(e.getTemperature());
        vo.setMaxTokens(e.getMaxTokens());
        vo.setStatus(e.getTestStatus() == null ? "unknown" : e.getTestStatus().toLowerCase());
        return vo;
    }

    private AiModelConfig fromVO(AiModelConfigVO vo) {
        AiModelConfig e = new AiModelConfig();
        e.setId(vo.getId());
        e.setProviderId(vo.getProviderId());
        e.setName(vo.getName());
        e.setEnabled(vo.getEnabled());
        e.setApiKey(vo.getApiKey());
        e.setBaseUrl(vo.getBaseUrl());
        e.setDefaultModel(vo.getDefaultModel());
        e.setModelsJson(serializeModels(vo.getModels()));
        e.setTemperature(vo.getTemperature());
        e.setMaxTokens(vo.getMaxTokens());
        e.setTestStatus(vo.getStatus() == null ? "UNKNOWN" : vo.getStatus().toUpperCase());
        return e;
    }

    private List<String> parseModels(String json) {
        if (json == null || json.isBlank()) return new ArrayList<>();
        try {
            return objectMapper.readValue(json, new TypeReference<>() {});
        } catch (JsonProcessingException e) {
            return new ArrayList<>();
        }
    }

    private String serializeModels(List<String> models) {
        if (models == null || models.isEmpty()) return "[]";
        try {
            return objectMapper.writeValueAsString(models);
        } catch (JsonProcessingException e) {
            return "[]";
        }
    }
}
