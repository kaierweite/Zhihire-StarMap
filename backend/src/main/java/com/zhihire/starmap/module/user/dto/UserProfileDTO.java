package com.zhihire.starmap.module.user.dto;

import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDate;

/**
 * 用户档案请求/响应 DTO
 */
@Data
public class UserProfileDTO {

    private String realName;
    private String gender;
    private LocalDate birthDate;
    private String education;
    private String school;
    private String major;
    private Integer workYears;
    private BigDecimal expectedSalaryMin;
    private BigDecimal expectedSalaryMax;
    private String expectedCity;
    private String currentCity;
    private String bio;
    private Integer profileCompleteness;
}
