package com.zhihire.starmap.module.admin.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import lombok.Data;

/**
 * 技能状态更新请求
 */
@Data
public class SkillStatusUpdateRequest {

    /** 目标状态：ACTIVE / CANDIDATE */
    @NotBlank(message = "状态不能为空")
    @Pattern(regexp = "ACTIVE|CANDIDATE", message = "状态只能是 ACTIVE 或 CANDIDATE")
    private String status;
}
