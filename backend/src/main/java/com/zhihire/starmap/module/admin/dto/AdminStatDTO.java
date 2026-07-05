package com.zhihire.starmap.module.admin.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * 管理后台统计数据
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class AdminStatDTO {
    private Long userCount;
    private Long companyCount;
    private Long jobCount;
    private Long matchCount;
    private Long parseCount;
}
