package com.zhihire.starmap.module.resume.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.zhihire.starmap.module.common.exception.BusinessException;
import com.zhihire.starmap.module.resume.dto.ParseCallbackRequest;
import com.zhihire.starmap.module.resume.entity.ParseTask;
import com.zhihire.starmap.module.resume.entity.Resume;
import com.zhihire.starmap.module.resume.mapper.ParseTaskMapper;
import com.zhihire.starmap.module.resume.mapper.ResumeMapper;
import com.zhihire.starmap.module.system.service.SkillNormalizationService;
import com.zhihire.starmap.module.user.entity.UserSkill;
import com.zhihire.starmap.module.user.mapper.UserSkillMapper;
import com.zhihire.starmap.module.user.service.UserProfileService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;

/**
 * 解析回调服务
 *
 * 职责：处理 AI 服务解析完成后的回调
 * 流程：更新 parse_task → 更新 resume → 技能归一 → user_skill 入库 → 更新完成度
 */
@Slf4j
@Service
public class ParseCallbackService {

    private final ParseTaskMapper parseTaskMapper;
    private final ResumeMapper resumeMapper;
    private final UserSkillMapper userSkillMapper;
    private final SkillNormalizationService skillNormalizationService;
    private final UserProfileService userProfileService;

    public ParseCallbackService(ParseTaskMapper parseTaskMapper,
                                ResumeMapper resumeMapper,
                                UserSkillMapper userSkillMapper,
                                SkillNormalizationService skillNormalizationService,
                                UserProfileService userProfileService) {
        this.parseTaskMapper = parseTaskMapper;
        this.resumeMapper = resumeMapper;
        this.userSkillMapper = userSkillMapper;
        this.skillNormalizationService = skillNormalizationService;
        this.userProfileService = userProfileService;
    }

    /**
     * 处理解析回调
     *
     * @param request 回调请求
     */
    @Transactional(rollbackFor = Exception.class)
    public void handleCallback(ParseCallbackRequest request) {
        // 1. 查询解析任务
        ParseTask parseTask = parseTaskMapper.selectById(request.getParseTaskId());
        if (parseTask == null) {
            throw new BusinessException(404, "解析任务不存在");
        }

        // 2. 更新解析任务状态
        parseTask.setStatus(request.getStatus());
        if ("FAILED".equals(request.getStatus()) || "REJECTED".equals(request.getStatus())) {
            parseTask.setResult(request.getErrorMessage());
            parseTaskMapper.updateById(parseTask);
            log.warn("解析任务失败：taskId={}, reason={}", parseTask.getId(), request.getErrorMessage());
            return;
        }
        parseTask.setResult(request.getParsedData());
        parseTaskMapper.updateById(parseTask);

        // 3. 更新 resume 的 content_text
        Resume resume = resumeMapper.selectOne(
                new LambdaQueryWrapper<Resume>()
                        .eq(Resume::getFileId, parseTask.getFileId())
                        .eq(Resume::getUserId, parseTask.getUserId()));
        if (resume != null) {
            resume.setContentText(request.getRawData());
            resumeMapper.updateById(resume);
        }

        // 4. 技能归一入库 + user_skill 写入
        if (request.getSkills() != null && !request.getSkills().isEmpty()) {
            List<SkillNormalizationService.NormalizeInput> inputs = request.getSkills().stream()
                    .map(s -> new SkillNormalizationService.NormalizeInput(
                            s.getRaw(), s.getCanonicalName(), s.getConfidence()))
                    .collect(Collectors.toList());

            List<SkillNormalizationService.NormalizeResult> results =
                    skillNormalizationService.batchNormalize(inputs);

            // 写入 user_skill（仅 ACTIVE 技能）
            List<UserSkill> newSkills = new ArrayList<>();
            for (SkillNormalizationService.NormalizeResult r : results) {
                // 去重：如果用户已有该技能则跳过
                Long existing = userSkillMapper.selectCount(
                        new LambdaQueryWrapper<UserSkill>()
                                .eq(UserSkill::getUserId, parseTask.getUserId())
                                .eq(UserSkill::getSkillId, r.getSkillId()));
                if (existing > 0) continue;

                UserSkill us = new UserSkill();
                us.setUserId(parseTask.getUserId());
                us.setSkillId(r.getSkillId());
                // confidence 0~1 映射到 proficiency_level 0~5
                us.setProficiencyLevel(r.getConfidence() != null ? r.getConfidence() * 5.0 : 3.0);
                userSkillMapper.insert(us);
                newSkills.add(us);
            }
            log.info("用户技能入库：userId={}, 新增 {} 个技能", parseTask.getUserId(), newSkills.size());
        }

        // 5. 更新档案完成度
        userProfileService.recalculateCompleteness(parseTask.getUserId());

        log.info("解析回调处理完成：taskId={}, status={}", parseTask.getId(), request.getStatus());
    }
}
