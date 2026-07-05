package com.zhihire.starmap.module.system.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.zhihire.starmap.module.system.entity.Skill;
import com.zhihire.starmap.module.system.entity.SkillSynonym;
import com.zhihire.starmap.module.system.mapper.SkillMapper;
import com.zhihire.starmap.module.system.mapper.SkillSynonymMapper;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;

/**
 * 技能归一服务
 *
 * 职责：将原始技能名归一到标准技能 ID
 * 流程：canonicalName 查 skill → synonym 兜底 → 未命中则创建 CANDIDATE
 */
@Slf4j
@Service
public class SkillNormalizationService {

    private final SkillMapper skillMapper;
    private final SkillSynonymMapper skillSynonymMapper;

    public SkillNormalizationService(SkillMapper skillMapper,
                                     SkillSynonymMapper skillSynonymMapper) {
        this.skillMapper = skillMapper;
        this.skillSynonymMapper = skillSynonymMapper;
    }

    /**
     * 单个技能归一
     *
     * @param raw           原始技能名（简历/JD 中提取的原始文本）
     * @param canonicalName 标准化后的技能名
     * @param confidence    置信度 0~1
     * @return 归一结果
     */
    public NormalizeResult normalizeSkill(String raw, String canonicalName, Double confidence) {
        // 1. 按 canonicalName 查 skill 唯一索引
        Skill skill = skillMapper.selectOne(
                new LambdaQueryWrapper<Skill>()
                        .eq(Skill::getName, canonicalName)
                        .eq(Skill::getStatus, "ACTIVE"));
        if (skill != null) {
            log.debug("技能归一命中（直接）：{} → skillId={}", canonicalName, skill.getId());
            return new NormalizeResult(raw, skill.getId(), confidence);
        }

        // 2. 查 skill_synonym 表（同义兜底）
        SkillSynonym synonym = skillSynonymMapper.selectOne(
                new LambdaQueryWrapper<SkillSynonym>()
                        .eq(SkillSynonym::getSynonym, canonicalName));
        if (synonym != null) {
            // 找到同义词，取对应 skill
            Skill targetSkill = skillMapper.selectById(synonym.getSkillId());
            if (targetSkill != null && "ACTIVE".equals(targetSkill.getStatus())) {
                log.debug("技能归一命中（同义）：{} → synonym → skillId={}", canonicalName, targetSkill.getId());
                return new NormalizeResult(raw, targetSkill.getId(), confidence);
            }
            // 若目标技能是 MERGED，继续找 mergeTarget
            if (targetSkill != null && "MERGED".equals(targetSkill.getStatus())
                    && targetSkill.getMergeTargetId() != null) {
                Skill mergedTarget = skillMapper.selectById(targetSkill.getMergeTargetId());
                if (mergedTarget != null && "ACTIVE".equals(mergedTarget.getStatus())) {
                    log.debug("技能归一命中（同义+合并）：{} → skillId={}", canonicalName, mergedTarget.getId());
                    return new NormalizeResult(raw, mergedTarget.getId(), confidence);
                }
            }
        }

        // 3. 全未命中 → 创建 CANDIDATE 技能
        Skill newSkill = new Skill();
        newSkill.setName(canonicalName);
        newSkill.setStatus("CANDIDATE");
        skillMapper.insert(newSkill);
        log.info("新技能入库（CANDIDATE）：name={}, skillId={}", canonicalName, newSkill.getId());
        return new NormalizeResult(raw, newSkill.getId(), confidence);
    }

    /**
     * 批量技能归一
     *
     * @param skills 待归一技能列表
     * @return 归一结果列表
     */
    public List<NormalizeResult> batchNormalize(List<NormalizeInput> skills) {
        List<NormalizeResult> results = new ArrayList<>();
        for (NormalizeInput input : skills) {
            results.add(normalizeSkill(input.getRaw(), input.getCanonicalName(), input.getConfidence()));
        }
        return results;
    }

    /**
     * 归一输入
     */
    @Data
    @AllArgsConstructor
    public static class NormalizeInput {
        private String raw;
        private String canonicalName;
        private Double confidence;
    }

    /**
     * 归一结果
     */
    @Data
    @AllArgsConstructor
    public static class NormalizeResult {
        private String raw;
        private Long skillId;
        private Double confidence;
    }
}
