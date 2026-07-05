package com.zhihire.starmap.module.match.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.zhihire.starmap.module.user.entity.Company;
import com.zhihire.starmap.module.job.entity.Job;
import com.zhihire.starmap.module.job.entity.JobSkill;
import com.zhihire.starmap.module.user.mapper.CompanyMapper;
import com.zhihire.starmap.module.job.mapper.JobMapper;
import com.zhihire.starmap.module.job.mapper.JobSkillMapper;
import com.zhihire.starmap.module.match.dto.RecommendDTO;
import com.zhihire.starmap.module.match.entity.MatchResult;
import com.zhihire.starmap.module.match.mapper.MatchResultMapper;
import com.zhihire.starmap.module.resume.entity.Resume;
import com.zhihire.starmap.module.resume.mapper.ResumeMapper;
import com.zhihire.starmap.module.user.entity.User;
import com.zhihire.starmap.module.user.entity.UserSkill;
import com.zhihire.starmap.module.user.mapper.UserMapper;
import com.zhihire.starmap.module.user.mapper.UserSkillMapper;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.*;
import java.util.stream.Collectors;

/**
 * 推荐核心服务
 *
 * 职责：候选召回 + 懒计算 + 新鲜度缓存 + 双向推荐
 */
@Slf4j
@Service
public class RecommendService {

    private final MatchResultMapper matchResultMapper;
    private final UserSkillMapper userSkillMapper;
    private final JobSkillMapper jobSkillMapper;
    private final ResumeMapper resumeMapper;
    private final JobMapper jobMapper;
    private final CompanyMapper companyMapper;
    private final UserMapper userMapper;
    private final ObjectMapper objectMapper;

    @Value("${ai.service.url:http://localhost:8000}")
    private String aiServiceUrl;

    /** 候选集硬封顶 */
    private static final int MAX_CANDIDATES = 50;

    public RecommendService(MatchResultMapper matchResultMapper,
                            UserSkillMapper userSkillMapper,
                            JobSkillMapper jobSkillMapper,
                            ResumeMapper resumeMapper,
                            JobMapper jobMapper,
                            CompanyMapper companyMapper,
                            UserMapper userMapper,
                            ObjectMapper objectMapper) {
        this.matchResultMapper = matchResultMapper;
        this.userSkillMapper = userSkillMapper;
        this.jobSkillMapper = jobSkillMapper;
        this.resumeMapper = resumeMapper;
        this.jobMapper = jobMapper;
        this.companyMapper = companyMapper;
        this.userMapper = userMapper;
        this.objectMapper = objectMapper;
    }

    /**
     * 求职者岗位推荐（分页）
     *
     * 1. 候选召回：用户技能 → job_skill → 候选岗位（≤50）
     * 2. 对每个候选岗位触发懒计算 match_result
     * 3. 按 score 降序分页返回
     */
    public Page<RecommendDTO> recommendJobs(Long userId, int page, int size) {
        // 获取用户简历
        Resume resume = resumeMapper.selectOne(
                new LambdaQueryWrapper<Resume>()
                        .eq(Resume::getUserId, userId)
                        .eq(Resume::getStatus, "NORMAL")
                        .orderByDesc(Resume::getCreatedAt)
                        .last("LIMIT 1"));
        if (resume == null) {
            return new Page<>(page, size);
        }

        // 候选召回：用户技能 → 岗位技能 → 候选岗位
        List<Long> userSkillIds = getUserSkillIds(userId);
        List<Long> candidateJobIds = recallJobsBySkills(userSkillIds);

        // 懒计算 match_result
        List<RecommendDTO> results = new ArrayList<>();
        for (Long jobId : candidateJobIds) {
            MatchResult mr = getOrCreateMatchResult(resume.getId(), jobId);
            if (mr != null) {
                Job job = jobMapper.selectById(jobId);
                Company company = job != null ? companyMapper.selectById(job.getCompanyId()) : null;
                results.add(RecommendDTO.builder()
                        .matchId(mr.getId())
                        .score(mr.getScore())
                        .jobId(jobId)
                        .jobTitle(job != null ? job.getTitle() : "")
                        .jobCity(job != null ? job.getCity() : "")
                        .companyName(company != null ? company.getCompanyName() : "")
                        .matchDetail(mr.getMatchDetail())
                        .build());
            }
        }

        // 按分数降序排序
        results.sort((a, b) -> Double.compare(
                b.getScore() != null ? b.getScore() : 0,
                a.getScore() != null ? a.getScore() : 0));

        // 手动分页
        return paginateList(results, page, size);
    }

    /**
     * 企业人才推荐（分页）
     *
     * 1. 候选召回：岗位技能 → user_skill → 候选用户（≤50）
     * 2. 对每个候选用户的简历触发懒计算
     */
    public Page<RecommendDTO> recommendTalents(Long userId, Long jobId, int page, int size) {
        Job job = jobMapper.selectById(jobId);
        if (job == null) return new Page<>(page, size);

        List<Long> jobSkillIds = getJobSkillIds(jobId);
        List<Long> candidateUserIds = recallUsersBySkills(jobSkillIds);

        List<RecommendDTO> results = new ArrayList<>();
        for (Long candidateUserId : candidateUserIds) {
            Resume resume = resumeMapper.selectOne(
                    new LambdaQueryWrapper<Resume>()
                            .eq(Resume::getUserId, candidateUserId)
                            .eq(Resume::getStatus, "NORMAL")
                            .last("LIMIT 1"));
            if (resume == null) continue;

            MatchResult mr = getOrCreateMatchResult(resume.getId(), jobId);
            if (mr != null) {
                User user = userMapper.selectById(candidateUserId);
                results.add(RecommendDTO.builder()
                        .matchId(mr.getId())
                        .score(mr.getScore())
                        .resumeId(resume.getId())
                        .userId(candidateUserId)
                        .username(user != null ? user.getUsername() : "")
                        .matchDetail(mr.getMatchDetail())
                        .build());
            }
        }

        results.sort((a, b) -> Double.compare(
                b.getScore() != null ? b.getScore() : 0,
                a.getScore() != null ? a.getScore() : 0));

        return paginateList(results, page, size);
    }

    /**
     * 获取某岗位匹配详情（触发懒计算）
     */
    public MatchResult getMatchDetail(Long resumeId, Long jobId) {
        return getOrCreateMatchResult(resumeId, jobId);
    }

    // ==================== 内部方法 ====================

    /**
     * 懒计算 + 新鲜度缓存
     *
     * 1. 查 match_result（resume_id + job_id）
     * 2. 若命中且未过期 → 直接返回
     * 3. 若未命中或过期 → 调 AI 评分 → 写入缓存
     */
    private MatchResult getOrCreateMatchResult(Long resumeId, Long jobId) {
        // 查缓存
        MatchResult cached = matchResultMapper.selectOne(
                new LambdaQueryWrapper<MatchResult>()
                        .eq(MatchResult::getResumeId, resumeId)
                        .eq(MatchResult::getJobId, jobId));

        // 新鲜度检查：若缓存存在且近期更新过，直接返回
        if (cached != null && cached.getUpdatedAt() != null) {
            // 简化判断：缓存存在就直接返回（完整版应检查 skill 变更时间）
            log.debug("匹配缓存命中：resumeId={}, jobId={}, score={}", resumeId, jobId, cached.getScore());
            return cached;
        }

        // 调 AI 服务评分（桩实现：本地计算）
        MatchResult result = callAIMatch(resumeId, jobId);

        if (cached != null) {
            // 更新已有记录
            result.setId(cached.getId());
            matchResultMapper.updateById(result);
        } else {
            // 新增记录
            matchResultMapper.insert(result);
        }

        log.info("匹配计算完成：resumeId={}, jobId={}, score={}", resumeId, jobId, result.getScore());
        return result;
    }

    /**
     * 调 AI 匹配评分（桩实现：本地简单计算）
     *
     * day16 替换为真实 AI 服务 POST /ai/recommend/match
     */
    private MatchResult callAIMatch(Long resumeId, Long jobId) {
        // 获取用户技能
        Resume resume = resumeMapper.selectById(resumeId);
        if (resume == null) return createDefaultResult(resumeId, jobId, 0);

        List<Long> userSkillIds = getUserSkillIds(resume.getUserId());
        List<Long> jobSkillIds = getJobSkillIds(jobId);

        // 技能匹配计算
        Set<Long> userSet = new HashSet<>(userSkillIds);
        long hitCount = jobSkillIds.stream().filter(userSet::contains).count();
        double skillScore = jobSkillIds.isEmpty() ? 50 : (hitCount * 100.0 / jobSkillIds.size());

        // 综合分（技能占比 60% + 基础分 40%）
        double totalScore = Math.round(skillScore * 0.6 + 70 * 0.4);

        // 构建 match_detail
        Map<String, Object> detail = new LinkedHashMap<>();
        detail.put("score", totalScore);
        Map<String, Object> breakdown = new LinkedHashMap<>();
        breakdown.put("skill", Map.of("score", skillScore, "hit", hitCount, "miss", jobSkillIds.size() - hitCount));
        detail.put("breakdown", breakdown);
        detail.put("rationale", String.format("技能匹配 %d/%d，综合评分 %.0f", hitCount, jobSkillIds.size(), totalScore));

        MatchResult mr = new MatchResult();
        mr.setResumeId(resumeId);
        mr.setJobId(jobId);
        mr.setScore(totalScore);
        try {
            mr.setMatchDetail(objectMapper.writeValueAsString(detail));
        } catch (Exception e) {
            mr.setMatchDetail("{}");
        }
        return mr;
    }

    private MatchResult createDefaultResult(Long resumeId, Long jobId, double score) {
        MatchResult mr = new MatchResult();
        mr.setResumeId(resumeId);
        mr.setJobId(jobId);
        mr.setScore(score);
        mr.setMatchDetail("{}");
        return mr;
    }

    private List<Long> getUserSkillIds(Long userId) {
        return userSkillMapper.selectList(
                new LambdaQueryWrapper<UserSkill>().eq(UserSkill::getUserId, userId))
                .stream().map(UserSkill::getSkillId).collect(Collectors.toList());
    }

    private List<Long> getJobSkillIds(Long jobId) {
        return jobSkillMapper.selectList(
                new LambdaQueryWrapper<JobSkill>().eq(JobSkill::getJobId, jobId))
                .stream().map(JobSkill::getSkillId).collect(Collectors.toList());
    }

    /**
     * 候选岗位召回：用户技能 → 岗位技能 → 岗位 ID（去重，≤50）
     */
    private List<Long> recallJobsBySkills(List<Long> skillIds) {
        if (skillIds.isEmpty()) return Collections.emptyList();
        return jobSkillMapper.selectList(
                new LambdaQueryWrapper<JobSkill>().in(JobSkill::getSkillId, skillIds))
                .stream().map(JobSkill::getJobId).distinct().limit(MAX_CANDIDATES).collect(Collectors.toList());
    }

    /**
     * 候选人才召回：岗位技能 → 用户技能 → 用户 ID（去重，≤50）
     */
    private List<Long> recallUsersBySkills(List<Long> skillIds) {
        if (skillIds.isEmpty()) return Collections.emptyList();
        return userSkillMapper.selectList(
                new LambdaQueryWrapper<UserSkill>().in(UserSkill::getSkillId, skillIds))
                .stream().map(UserSkill::getUserId).distinct().limit(MAX_CANDIDATES).collect(Collectors.toList());
    }

    /**
     * 手动分页
     */
    private <T> Page<T> paginateList(List<T> list, int page, int size) {
        Page<T> result = new Page<>(page, size);
        result.setTotal(list.size());
        int from = (page - 1) * size;
        int to = Math.min(from + size, list.size());
        if (from < list.size()) {
            result.setRecords(list.subList(from, to));
        } else {
            result.setRecords(Collections.emptyList());
        }
        return result;
    }
}
