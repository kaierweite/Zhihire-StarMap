package com.zhihire.starmap.module.interview.dto;

import lombok.Data;

/**
 * 开始面试请求
 */
@Data
public class InterviewStartRequest {
    /** 岗位 ID（可选，针对特定岗位） */
    private Long jobId;
    /** 职业角色 ID（可选） */
    private Long occupationRoleId;
}
