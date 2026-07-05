package com.zhihire.starmap.module.career.dto;

import lombok.Data;

/**
 * 职业规划生成请求
 */
@Data
public class CareerPlanRequest {

    /** 目标职业角色 ID（可选，不传则自动推荐） */
    private Long targetRoleId;
}
