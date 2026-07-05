package com.zhihire.starmap.module.job.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import lombok.Data;

/**
 * 岗位状态切换请求
 */
@Data
public class JobStatusRequest {

    /** 目标状态：OPEN/CLOSED/DRAFT */
    @NotBlank(message = "状态不能为空")
    @Pattern(regexp = "OPEN|CLOSED|DRAFT", message = "状态只能是 OPEN/CLOSED/DRAFT")
    private String status;
}
