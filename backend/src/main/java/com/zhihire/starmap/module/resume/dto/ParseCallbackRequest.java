package com.zhihire.starmap.module.resume.dto;

import lombok.Data;

import java.util.List;

/**
 * AI 解析回调请求 DTO
 *
 * AI 服务解析完成后回调后端，传入解析结果
 */
@Data
public class ParseCallbackRequest {

    /** 解析任务 ID */
    private Long parseTaskId;

    /** 解析状态：SUCCESS / FAILED / REJECTED */
    private String status;

    /** 原始提取的文本 */
    private String rawData;

    /** 结构化解析结果（JSON） */
    private String parsedData;

    /** 错误信息（status=FAILED 时） */
    private String errorMessage;

    /** 解析出的技能列表 */
    private List<SkillExtract> skills;

    /**
     * AI 提取的技能
     */
    @Data
    public static class SkillExtract {
        /** 原始文本 */
        private String raw;
        /** 标准化技能名 */
        private String canonicalName;
        /** 置信度 0~1 */
        private Double confidence;
    }
}
