package com.zhihire.starmap.module.match.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.zhihire.starmap.module.job.entity.Company;
import com.zhihire.starmap.module.job.entity.Job;
import com.zhihire.starmap.module.job.entity.JobSkill;
import com.zhihire.starmap.module.job.mapper.CompanyMapper;
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
import org.springframework.stereotype.Service;
import java.util.*;
import java.util.stream.Collectors;

@Slf4j
@Service
public class RecommendServiceImpl implements RecommendService {

    private final MatchResultMapper matchResultMapper;
    private final UserSkillMapper userSkillMapper;
    private final JobSkillMapper jobSkillMapper;
    private final ResumeMapper resumeMapper;
    private final JobMapper jobMapper;
    private final CompanyMapper companyMapper;
    private final UserMapper userMapper;
    private final ObjectMapper objectMapper;
    private static final int MAX_CANDIDATES = 50;

    public RecommendServiceImpl(MatchResultMapper matchResultMapper, UserSkillMapper userSkillMapper,
                                JobSkillMapper jobSkillMapper, ResumeMapper resumeMapper, JobMapper jobMapper,
                                CompanyMapper companyMapper, UserMapper userMapper, ObjectMapper objectMapper) {
        this.matchResultMapper = matchResultMapper;
        this.userSkillMapper = userSkillMapper;
        this.jobSkillMapper = jobSkillMapper;
        this.resumeMapper = resumeMapper;
        this.jobMapper = jobMapper;
        this.companyMapper = companyMapper;
        this.userMapper = userMapper;
        this.objectMapper = objectMapper;
    }

    @Override
    public Page<RecommendDTO> recommendJobs(Long userId, int page, int size) {
        Resume resume = resumeMapper.selectOne(new LambdaQueryWrapper<Resume>()
                .eq(Resume::getUserId, userId).eq(Resume::getStatus, "NORMAL").last("LIMIT 1"));
        if (resume == null) return new Page<>(page, size);
        List<Long> userSkillIds = getUserSkillIds(userId);
        List<Long> candidateJobIds = recallJobsBySkills(userSkillIds);
        List<RecommendDTO> results = new ArrayList<>();
        for (Long jobId : candidateJobIds) {
            MatchResult mr = getOrCreateMatchResult(resume.getId(), jobId);
            if (mr != null) {
                Job job = jobMapper.selectById(jobId);
                Company company = job != null ? companyMapper.selectById(job.getCompanyId()) : null;
                results.add(RecommendDTO.builder().matchId(mr.getId()).score(mr.getScore()).jobId(jobId)
                        .jobTitle(job != null ? job.getTitle() : "").jobCity(job != null ? job.getCity() : "")
                        .companyName(company != null ? company.getCompanyName() : "").matchDetail(mr.getMatchDetail()).build());
            }
        }
        results.sort((a, b) -> Double.compare(b.getScore() != null ? b.getScore() : 0, a.getScore() != null ? a.getScore() : 0));
        return paginateList(results, page, size);
    }

    @Override
    public Page<RecommendDTO> recommendTalents(Long userId, Long jobId, int page, int size) {
        Job job = jobMapper.selectById(jobId);
        if (job == null) return new Page<>(page, size);
        List<Long> jobSkillIds = getJobSkillIds(jobId);
        List<Long> candidateUserIds = recallUsersBySkills(jobSkillIds);
        List<RecommendDTO> results = new ArrayList<>();
        for (Long candidateUserId : candidateUserIds) {
            Resume resume = resumeMapper.selectOne(new LambdaQueryWrapper<Resume>()
                    .eq(Resume::getUserId, candidateUserId).eq(Resume::getStatus, "NORMAL").last("LIMIT 1"));
            if (resume == null) continue;
            MatchResult mr = getOrCreateMatchResult(resume.getId(), jobId);
            if (mr != null) {
                User user = userMapper.selectById(candidateUserId);
                results.add(RecommendDTO.builder().matchId(mr.getId()).score(mr.getScore()).resumeId(resume.getId())
                        .userId(candidateUserId).username(user != null ? user.getUsername() : "").matchDetail(mr.getMatchDetail()).build());
            }
        }
        results.sort((a, b) -> Double.compare(b.getScore() != null ? b.getScore() : 0, a.getScore() != null ? a.getScore() : 0));
        return paginateList(results, page, size);
    }

    @Override
    public MatchResult getMatchDetail(Long resumeId, Long jobId) { return getOrCreateMatchResult(resumeId, jobId); }

    private MatchResult getOrCreateMatchResult(Long resumeId, Long jobId) {
        MatchResult cached = matchResultMapper.selectOne(new LambdaQueryWrapper<MatchResult>()
                .eq(MatchResult::getResumeId, resumeId).eq(MatchResult::getJobId, jobId));
        if (cached != null && cached.getUpdatedAt() != null) return cached;
        MatchResult result = callAIMatch(resumeId, jobId);
        if (cached != null) { result.setId(cached.getId()); matchResultMapper.updateById(result); }
        else matchResultMapper.insert(result);
        return result;
    }

    private MatchResult callAIMatch(Long resumeId, Long jobId) {
        Resume resume = resumeMapper.selectById(resumeId);
        if (resume == null) return createDefaultResult(resumeId, jobId, 0);
        List<Long> userSkillIds = getUserSkillIds(resume.getUserId());
        List<Long> jobSkillIds = getJobSkillIds(jobId);
        Set<Long> userSet = new HashSet<>(userSkillIds);
        long hitCount = jobSkillIds.stream().filter(userSet::contains).count();
        double skillScore = jobSkillIds.isEmpty() ? 50 : (hitCount * 100.0 / jobSkillIds.size());
        double totalScore = Math.round(skillScore * 0.6 + 70 * 0.4);
        Map<String, Object> detail = new LinkedHashMap<>();
        detail.put("score", totalScore);
        detail.put("breakdown", Map.of("skill", Map.of("score", skillScore, "hit", hitCount, "miss", jobSkillIds.size() - hitCount)));
        detail.put("rationale", String.format("技能匹配 %d/%d，综合评分 %.0f", hitCount, jobSkillIds.size(), totalScore));
        MatchResult mr = new MatchResult();
        mr.setResumeId(resumeId); mr.setJobId(jobId); mr.setScore(totalScore);
        try { mr.setMatchDetail(objectMapper.writeValueAsString(detail)); } catch (Exception e) { mr.setMatchDetail("{}"); }
        return mr;
    }

    private MatchResult createDefaultResult(Long resumeId, Long jobId, double score) {
        MatchResult mr = new MatchResult(); mr.setResumeId(resumeId); mr.setJobId(jobId); mr.setScore(score); mr.setMatchDetail("{}"); return mr;
    }

    private List<Long> getUserSkillIds(Long userId) { return userSkillMapper.selectList(new LambdaQueryWrapper<UserSkill>().eq(UserSkill::getUserId, userId)).stream().map(UserSkill::getSkillId).collect(Collectors.toList()); }
    private List<Long> getJobSkillIds(Long jobId) { return jobSkillMapper.selectList(new LambdaQueryWrapper<JobSkill>().eq(JobSkill::getJobId, jobId)).stream().map(JobSkill::getSkillId).collect(Collectors.toList()); }
    private List<Long> recallJobsBySkills(List<Long> skillIds) { if (skillIds.isEmpty()) return Collections.emptyList(); return jobSkillMapper.selectList(new LambdaQueryWrapper<JobSkill>().in(JobSkill::getSkillId, skillIds)).stream().map(JobSkill::getJobId).distinct().limit(MAX_CANDIDATES).collect(Collectors.toList()); }
    private List<Long> recallUsersBySkills(List<Long> skillIds) { if (skillIds.isEmpty()) return Collections.emptyList(); return userSkillMapper.selectList(new LambdaQueryWrapper<UserSkill>().in(UserSkill::getSkillId, skillIds)).stream().map(UserSkill::getUserId).distinct().limit(MAX_CANDIDATES).collect(Collectors.toList()); }
    private <T> Page<T> paginateList(List<T> list, int page, int size) { Page<T> result = new Page<>(page, size); result.setTotal(list.size()); int from = (page - 1) * size; int to = Math.min(from + size, list.size()); result.setRecords(from < list.size() ? list.subList(from, to) : Collections.emptyList()); return result; }
}