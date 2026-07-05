package com.zhihire.starmap.module.admin.controller;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.zhihire.starmap.module.admin.dto.SkillMergeRequest;
import com.zhihire.starmap.module.admin.dto.SkillStatusUpdateRequest;
import com.zhihire.starmap.module.admin.dto.SynonymAddRequest;
import com.zhihire.starmap.module.common.exception.BusinessException;
import com.zhihire.starmap.module.common.result.Result;
import com.zhihire.starmap.module.system.entity.Skill;
import com.zhihire.starmap.module.system.entity.SkillSynonym;
import com.zhihire.starmap.module.system.mapper.SkillMapper;
import com.zhihire.starmap.module.system.mapper.SkillSynonymMapper;
import jakarta.validation.Valid;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.util.StringUtils;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;

/**
 * 管理后台 — 技能字典管理
 *
 * 职责：技能列表查询、状态审核、合并操作、同义词管理
 * 所有接口仅 ADMIN 角色可访问
 */
@Slf4j
@RestController
@RequestMapping("/api/admin/skill")
@PreAuthorize("hasRole('ADMIN')")
public class AdminSkillController {

    private final SkillMapper skillMapper;
    private final SkillSynonymMapper skillSynonymMapper;

    /** AI 微服务地址（用于触发图谱重建） */
    @Value("${ai.service.url:http://localhost:8000}")
    private String aiServiceUrl;

    public AdminSkillController(SkillMapper skillMapper,
                                SkillSynonymMapper skillSynonymMapper) {
        this.skillMapper = skillMapper;
        this.skillSynonymMapper = skillSynonymMapper;
    }

    /**
     * 技能列表（分页 + 状态筛选）
     *
     * @param page   页码（默认 1）
     * @param size   每页条数（默认 20）
     * @param status 状态筛选（可选：ACTIVE/CANDIDATE/MERGED）
     * @param name   名称模糊搜索（可选）
     * @return 技能分页列表
     */
    @GetMapping("/list")
    public Result<Page<Skill>> listSkills(
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "20") int size,
            @RequestParam(required = false) String status,
            @RequestParam(required = false) String name) {

        Page<Skill> pageParam = new Page<>(page, size);
        LambdaQueryWrapper<Skill> wrapper = new LambdaQueryWrapper<>();

        if (StringUtils.hasText(status)) {
            wrapper.eq(Skill::getStatus, status);
        }
        if (StringUtils.hasText(name)) {
            wrapper.like(Skill::getName, name);
        }
        wrapper.orderByDesc(Skill::getCreatedAt);

        Page<Skill> result = skillMapper.selectPage(pageParam, wrapper);
        return Result.ok(result);
    }

    /**
     * 更新技能状态（审核 CANDIDATE → ACTIVE）
     *
     * @param id      技能 ID
     * @param request 状态更新请求
     * @return 统一结果
     */
    @PutMapping("/{id}")
    public Result<Void> updateSkillStatus(@PathVariable Long id,
                                          @Valid @RequestBody SkillStatusUpdateRequest request) {
        Skill skill = skillMapper.selectById(id);
        if (skill == null) {
            throw new BusinessException(404, "技能不存在");
        }

        String oldStatus = skill.getStatus();
        skill.setStatus(request.getStatus());
        skillMapper.updateById(skill);
        log.info("技能状态变更：skillId={}, {} → {}", id, oldStatus, request.getStatus());

        // 审核后触发 AI 图谱重建
        triggerGraphReload();

        return Result.ok();
    }

    /**
     * 合并技能（原技能 → MERGED，指向目标技能）
     *
     * @param id      原技能 ID
     * @param request 合并请求（mergeTargetId）
     * @return 统一结果
     */
    @PutMapping("/{id}/merge")
    public Result<Void> mergeSkill(@PathVariable Long id,
                                   @Valid @RequestBody SkillMergeRequest request) {
        Skill skill = skillMapper.selectById(id);
        if (skill == null) {
            throw new BusinessException(404, "技能不存在");
        }
        if (id.equals(request.getMergeTargetId())) {
            throw new BusinessException(400, "不能合并到自身");
        }

        Skill target = skillMapper.selectById(request.getMergeTargetId());
        if (target == null) {
            throw new BusinessException(404, "合并目标技能不存在");
        }

        // 原技能 → MERGED
        skill.setStatus("MERGED");
        skill.setMergeTargetId(request.getMergeTargetId());
        skillMapper.updateById(skill);
        log.info("技能合并：{} (id={}) → {} (id={})", skill.getName(), id, target.getName(), request.getMergeTargetId());

        // 合并后触发 AI 图谱重建
        triggerGraphReload();

        return Result.ok();
    }

    /**
     * 同义词列表（分页 + 技能 ID 筛选）
     */
    @GetMapping("/synonym/list")
    public Result<Page<SkillSynonym>> listSynonyms(
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "20") int size,
            @RequestParam(required = false) Long skillId) {

        Page<SkillSynonym> pageParam = new Page<>(page, size);
        LambdaQueryWrapper<SkillSynonym> wrapper = new LambdaQueryWrapper<>();
        if (skillId != null) {
            wrapper.eq(SkillSynonym::getSkillId, skillId);
        }
        wrapper.orderByDesc(SkillSynonym::getCreatedAt);

        Page<SkillSynonym> result = skillSynonymMapper.selectPage(pageParam, wrapper);
        return Result.ok(result);
    }

    /**
     * 添加同义词
     */
    @PostMapping("/synonym")
    public Result<Void> addSynonym(@Valid @RequestBody SynonymAddRequest request) {
        // 校验技能存在
        Skill skill = skillMapper.selectById(request.getSkillId());
        if (skill == null) {
            throw new BusinessException(404, "技能不存在");
        }

        // 校验同义词不重复
        Long count = skillSynonymMapper.selectCount(
                new LambdaQueryWrapper<SkillSynonym>()
                        .eq(SkillSynonym::getSynonym, request.getSynonym()));
        if (count > 0) {
            throw new BusinessException(400, "同义词已存在");
        }

        SkillSynonym synonym = new SkillSynonym();
        synonym.setSkillId(request.getSkillId());
        synonym.setSynonym(request.getSynonym());
        skillSynonymMapper.insert(synonym);
        log.info("同义词添加：skillId={}, synonym={}", request.getSkillId(), request.getSynonym());
        return Result.ok();
    }

    /**
     * 删除同义词
     */
    @DeleteMapping("/synonym/{id}")
    public Result<Void> deleteSynonym(@PathVariable Long id) {
        int rows = skillSynonymMapper.deleteById(id);
        if (rows == 0) {
            throw new BusinessException(404, "同义词不存在");
        }
        log.info("同义词删除：id={}", id);
        return Result.ok();
    }

    /**
     * 触发 AI 服务图谱重建
     * 异步调用，失败不阻断主流程
     */
    private void triggerGraphReload() {
        try {
            RestTemplate restTemplate = new RestTemplate();
            restTemplate.postForEntity(aiServiceUrl + "/ai/graph/reload", null, String.class);
            log.info("AI 图谱重建触发成功");
        } catch (Exception e) {
            // AI 服务不可用时不阻断，仅记录日志
            log.warn("AI 图谱重建触发失败（AI 服务可能未启动）：{}", e.getMessage());
        }
    }
}
