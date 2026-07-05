package com.zhihire.starmap.module.user.dto;

import lombok.Data;

/**
 * 企业档案请求/响应 DTO
 */
@Data
public class CompanyProfileDTO {

    private String companyName;
    private String industry;
    private String scale;
    private String website;
    private String logoUrl;
    private String description;
    private String address;
    private String contactName;
    private String contactPhone;
    private String contactEmail;
    /** 审核状态（只读） */
    private String auditStatus;
    /** 审核原因（只读） */
    private String auditReason;
}
