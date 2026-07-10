package com.zhihire.starmap.module.admin.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;

import java.time.LocalDateTime;

/**
 * AI model provider config entity.
 */
@Data
@TableName("ai_model_config")
public class AiModelConfig {

    @TableId(type = IdType.AUTO)
    private Long id;

    private String providerId;

    private String name;

    private Boolean enabled;

    private String apiKey;

    private String baseUrl;

    private String defaultModel;

    /** JSON array of model names */
    private String modelsJson;

    private Double temperature;

    private Integer maxTokens;

    /** CONNECTED / DISCONNECTED / UNKNOWN */
    private String testStatus;

    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createdAt;

    @TableField(fill = FieldFill.INSERT_UPDATE)
    private LocalDateTime updatedAt;

    @TableLogic
    private String deletedAt;
}
