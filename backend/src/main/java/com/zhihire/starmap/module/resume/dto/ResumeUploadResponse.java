package com.zhihire.starmap.module.resume.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * 简历上传响应 DTO
 *
 * 返回上传结果和解析任务信息
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ResumeUploadResponse {

    /** 简历 ID */
    private Long resumeId;

    /** 解析任务 ID（前端轮询用） */
    private Long parseTaskId;

    /** 解析任务状态（初始为 WAITING） */
    private String parseStatus;

    /** 文件原始名 */
    private String fileName;
}
