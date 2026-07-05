package com.zhihire.starmap.module.interview.dto;

import lombok.Data;

/**
 * 提交回答请求
 */
@Data
public class InterviewAnswerRequest {
    /** 问题 ID */
    private Long questionId;
    /** 用户回答内容 */
    private String content;
}
