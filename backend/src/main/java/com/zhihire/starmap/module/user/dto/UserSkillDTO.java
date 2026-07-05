package com.zhihire.starmap.module.user.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * 用户技能响应 DTO
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class UserSkillDTO {

    /** 技能 ID */
    private Long skillId;

    /** 技能名称 */
    private String name;

    /** 技能领域 */
    private String category;

    /** 熟练度 0~5 */
    private Double proficiencyLevel;
}
