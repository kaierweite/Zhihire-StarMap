package com.zhihire.starmap.module.admin.dto;

import lombok.Data;

import java.util.List;

/**
 * VO for AI model config — matches frontend ModelProvider interface.
 */
@Data
public class AiModelConfigVO {
    private Long id;
    private String providerId;
    private String name;
    private Boolean enabled;
    private String apiKey;
    private String baseUrl;
    private String defaultModel;
    private List<String> models;
    private Double temperature;
    private Integer maxTokens;
    private String status;
}
