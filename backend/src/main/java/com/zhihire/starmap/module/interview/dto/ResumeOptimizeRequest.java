package com.zhihire.starmap.module.interview.dto;

import lombok.Data;

/**
 * 简历优化请求
 */
@Data
public class ResumeOptimizeRequest {
    /** 简历 ID */
    private Long resumeId;
    /** 岗位 ID（可选，针对特定岗位优化） */
    private Long jobId;
}
