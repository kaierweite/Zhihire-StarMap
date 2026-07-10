package com.zhihire.starmap.module.system.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.zhihire.starmap.module.system.entity.Skill;
import com.zhihire.starmap.module.system.entity.SkillSynonym;
import com.zhihire.starmap.module.system.mapper.SkillMapper;
import com.zhihire.starmap.module.system.mapper.SkillSynonymMapper;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import java.util.ArrayList;
import java.util.List;

@Slf4j
@Service
public class SkillNormalizationServiceImpl implements SkillNormalizationService {

    private final SkillMapper skillMapper;
    private final SkillSynonymMapper skillSynonymMapper;

    public SkillNormalizationServiceImpl(SkillMapper skillMapper, SkillSynonymMapper skillSynonymMapper) {
        this.skillMapper = skillMapper;
        this.skillSynonymMapper = skillSynonymMapper;
    }

    @Override
    public NormalizeResult normalizeSkill(String raw, String canonicalName, Double confidence) {
        Skill skill = skillMapper.selectOne(new LambdaQueryWrapper<Skill>()
                .eq(Skill::getName, canonicalName).eq(Skill::getStatus, "ACTIVE"));
        if (skill != null) { log.debug("技能归一命中：{} → skillId={}", canonicalName, skill.getId()); return new NormalizeResult(raw, skill.getId(), confidence); }
        SkillSynonym synonym = skillSynonymMapper.selectOne(new LambdaQueryWrapper<SkillSynonym>().eq(SkillSynonym::getSynonym, canonicalName));
        if (synonym != null) {
            Skill targetSkill = skillMapper.selectById(synonym.getSkillId());
            if (targetSkill != null && "ACTIVE".equals(targetSkill.getStatus())) return new NormalizeResult(raw, targetSkill.getId(), confidence);
            if (targetSkill != null && "MERGED".equals(targetSkill.getStatus()) && targetSkill.getMergeTargetId() != null) {
                Skill mergedTarget = skillMapper.selectById(targetSkill.getMergeTargetId());
                if (mergedTarget != null && "ACTIVE".equals(mergedTarget.getStatus())) return new NormalizeResult(raw, mergedTarget.getId(), confidence);
            }
        }
        Skill newSkill = new Skill(); newSkill.setName(canonicalName); newSkill.setStatus("CANDIDATE");
        skillMapper.insert(newSkill);
        log.info("新技能入库（CANDIDATE）：name={}, skillId={}", canonicalName, newSkill.getId());
        return new NormalizeResult(raw, newSkill.getId(), confidence);
    }

    @Override
    public List<NormalizeResult> batchNormalize(List<NormalizeInput> skills) {
        List<NormalizeResult> results = new ArrayList<>();
        for (NormalizeInput input : skills) results.add(normalizeSkill(input.getRaw(), input.getCanonicalName(), input.getConfidence()));
        return results;
    }
}