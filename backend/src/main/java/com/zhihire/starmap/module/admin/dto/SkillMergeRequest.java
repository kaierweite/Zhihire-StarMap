package com.zhihire.starmap.module.admin.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.Data;

/**
 * 技能合并请求
 */
@Data
public class SkillMergeRequest {

    /** 合并目标技能 ID（原技能将指向此目标） */
    @NotNull(message = "合并目标 ID 不能为空")
    private Long mergeTargetId;
}
