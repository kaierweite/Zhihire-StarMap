package com.zhihire.starmap.module.admin.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import lombok.Data;

/**
 * 企业审核请求
 */
@Data
public class CompanyAuditRequest {

    /** 审核结果：VERIFIED / REJECTED */
    @NotBlank(message = "审核结果不能为空")
    @Pattern(regexp = "VERIFIED|REJECTED", message = "审核结果只能是 VERIFIED 或 REJECTED")
    private String auditStatus;

    /** 审核备注（REJECTED 时必填） */
    private String auditReason;
}
