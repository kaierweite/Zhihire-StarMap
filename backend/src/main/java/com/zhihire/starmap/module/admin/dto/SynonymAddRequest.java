package com.zhihire.starmap.module.admin.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.Data;

/**
 * 添加同义词请求
 */
@Data
public class SynonymAddRequest {

    /** 关联技能 ID */
    @NotNull(message = "技能 ID 不能为空")
    private Long skillId;

    /** 同义词 */
    @NotBlank(message = "同义词不能为空")
    private String synonym;
}
