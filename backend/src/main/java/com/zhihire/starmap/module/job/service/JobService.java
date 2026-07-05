package com.zhihire.starmap.module.job.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.zhihire.starmap.module.common.exception.BusinessException;
import com.zhihire.starmap.module.job.dto.JobRequest;
import com.zhihire.starmap.module.job.dto.JobStatusRequest;
import com.zhihire.starmap.module.job.entity.Job;
import com.zhihire.starmap.module.job.entity.JobSkill;
import com.zhihire.starmap.module.job.entity.OccupationRole;
import com.zhihire.starmap.module.job.mapper.JobMapper;
import com.zhihire.starmap.module.job.mapper.JobSkillMapper;
import com.zhihire.starmap.module.job.mapper.OccupationRoleMapper;
import com.zhihire.starmap.module.resume.entity.ParseTask;
import com.zhihire.starmap.module.resume.mapper.ParseTaskMapper;
import com.zhihire.starmap.module.system.entity.Skill;
import com.zhihire.starmap.module.system.mapper.SkillMapper;
import com.zhihire.starmap.module.system.service.SkillNormalizationService;
import com.zhihire.starmap.module.system.service.SystemFileService;
import com.zhihire.starmap.module.user.entity.Company;
import com.zhihire.starmap.module.user.mapper.CompanyMapper;
import lombok.extern.slf4j.Slf4j;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.multipart.MultipartFile;

import java.util.List;

/**
 * 岗位服务
 *
 * 职责：岗位 CRUD、双模式创建（手动/JD上传）、公开查询
 */
@Slf4j
@Service
public class JobService {

    private final JobMapper jobMapper;
    private final JobSkillMapper jobSkillMapper;
    private final CompanyMapper companyMapper;
    private final SkillMapper skillMapper;
    private final OccupationRoleMapper occupationRoleMapper;
    private final SystemFileService systemFileService;
    private final ParseTaskMapper parseTaskMapper;
    private final SkillNormalizationService skillNormalizationService;

    public JobService(JobMapper jobMapper, JobSkillMapper jobSkillMapper,
                      CompanyMapper companyMapper, SkillMapper skillMapper,
                      OccupationRoleMapper occupationRoleMapper,
                      SystemFileService systemFileService,
                      ParseTaskMapper parseTaskMapper,
                      SkillNormalizationService skillNormalizationService) {
        this.jobMapper = jobMapper;
        this.jobSkillMapper = jobSkillMapper;
        this.companyMapper = companyMapper;
        this.skillMapper = skillMapper;
        this.occupationRoleMapper = occupationRoleMapper;
        this.systemFileService = systemFileService;
        this.parseTaskMapper = parseTaskMapper;
        this.skillNormalizationService = skillNormalizationService;
    }

    /**
     * 手动创建岗位
     *
     * @param userId  企业用户 ID
     * @param request 岗位请求
     * @return 创建的岗位
     */
    @Transactional(rollbackFor = Exception.class)
    public Job createJob(Long userId, JobRequest request) {
        // 1. 获取企业档案
        Company company = getCompanyByUserId(userId);

        // 2. 校验技能全部为 ACTIVE
        validateSkills(request.getSkills());

        // 3. 创建岗位
        Job job = new Job();
        job.setCompanyId(company.getId());
        job.setTitle(request.getTitle());
        job.setDescription(request.getDescription());
        job.setRequirements(request.getRequirements());
        job.setSalaryMin(request.getSalaryMin());
        job.setSalaryMax(request.getSalaryMax());
        job.setCity(request.getCity());
        job.setExperienceMin(request.getExperienceMin());
        job.setEducationRequirement(request.getEducationRequirement());
        job.setJobType(request.getJobType() != null ? request.getJobType() : "FULL_TIME");
        job.setStatus("OPEN");
        job.setSource(request.getSource());
        job.setOccupationRoleId(request.getOccupationRoleId());
        jobMapper.insert(job);

        // 4. 写入岗位技能关联
        saveJobSkills(job.getId(), request.getSkills());

        log.info("岗位创建成功：jobId={}, title={}, source={}", job.getId(), job.getTitle(), job.getSource());
        return job;
    }

    /**
     * JD 文件上传创建岗位（异步解析）
     *
     * @param userId 企业用户 ID
     * @param file   JD 文件
     * @return 岗位（初始状态，技能待异步解析填充）
     */
    @Transactional(rollbackFor = Exception.class)
    public Job createJobByUpload(Long userId, MultipartFile file) {
        Company company = getCompanyByUserId(userId);

        // 存储 JD 文件
        var uploadFile = systemFileService.store(file, userId);

        // 创建岗位（初始状态，技能待解析）
        Job job = new Job();
        job.setCompanyId(company.getId());
        job.setTitle("待解析：" + uploadFile.getOriginalName());
        job.setStatus("DRAFT");
        job.setSource("UPLOAD");
        jobMapper.insert(job);

        // 创建解析任务
        ParseTask parseTask = new ParseTask();
        parseTask.setFileId(uploadFile.getId());
        parseTask.setUserId(userId);
        parseTask.setStatus("WAITING");
        parseTaskMapper.insert(parseTask);

        // 异步触发 AI 解析
        triggerJobParse(job.getId(), parseTask.getId());

        log.info("JD 上传岗位创建：jobId={}, parseTaskId={}", job.getId(), parseTask.getId());
        return job;
    }

    /**
     * 更新岗位
     */
    @Transactional(rollbackFor = Exception.class)
    public void updateJob(Long userId, Long jobId, JobRequest request) {
        Job job = getJobAndVerifyOwner(userId, jobId);
        job.setTitle(request.getTitle());
        job.setDescription(request.getDescription());
        job.setRequirements(request.getRequirements());
        job.setSalaryMin(request.getSalaryMin());
        job.setSalaryMax(request.getSalaryMax());
        job.setCity(request.getCity());
        job.setExperienceMin(request.getExperienceMin());
        job.setEducationRequirement(request.getEducationRequirement());
        job.setOccupationRoleId(request.getOccupationRoleId());
        jobMapper.updateById(job);

        // 更新技能关联（删旧重建）
        if (request.getSkills() != null) {
            validateSkills(request.getSkills());
            jobSkillMapper.delete(new LambdaQueryWrapper<JobSkill>()
                    .eq(JobSkill::getJobId, jobId));
            saveJobSkills(jobId, request.getSkills());
        }
        log.info("岗位更新：jobId={}", jobId);
    }

    /**
     * 切换岗位状态
     */
    public void updateJobStatus(Long userId, Long jobId, JobStatusRequest request) {
        Job job = getJobAndVerifyOwner(userId, jobId);
        job.setStatus(request.getStatus());
        jobMapper.updateById(job);
        log.info("岗位状态变更：jobId={}, status={}", jobId, request.getStatus());
    }

    /**
     * 企业岗位列表（分页）
     */
    public Page<Job> listCompanyJobs(Long userId, int page, int size) {
        Company company = getCompanyByUserId(userId);
        Page<Job> pageParam = new Page<>(page, size);
        return jobMapper.selectPage(pageParam,
                new LambdaQueryWrapper<Job>()
                        .eq(Job::getCompanyId, company.getId())
                        .orderByDesc(Job::getCreatedAt));
    }

    /**
     * 对外岗位列表（仅 OPEN + 企业已审核）
     */
    public Page<Job> listPublicJobs(int page, int size, String city, String keyword) {
        Page<Job> pageParam = new Page<>(page, size);

        // 先查已审核的企业 ID 列表
        List<Long> verifiedCompanyIds = companyMapper.selectList(
                new LambdaQueryWrapper<Company>()
                        .eq(Company::getAuditStatus, "VERIFIED"))
                .stream().map(Company::getId).toList();

        if (verifiedCompanyIds.isEmpty()) {
            return pageParam;
        }

        LambdaQueryWrapper<Job> wrapper = new LambdaQueryWrapper<Job>()
                .in(Job::getCompanyId, verifiedCompanyIds)
                .eq(Job::getStatus, "OPEN");

        if (city != null && !city.isEmpty()) {
            wrapper.eq(Job::getCity, city);
        }
        if (keyword != null && !keyword.isEmpty()) {
            wrapper.and(w -> w.like(Job::getTitle, keyword)
                    .or().like(Job::getDescription, keyword));
        }
        wrapper.orderByDesc(Job::getCreatedAt);

        return jobMapper.selectPage(pageParam, wrapper);
    }

    /**
     * 岗位详情（公开）
     */
    public Job getPublicJob(Long jobId) {
        Job job = jobMapper.selectById(jobId);
        if (job == null || !"OPEN".equals(job.getStatus())) {
            throw new BusinessException(404, "岗位不存在或未开放");
        }
        // 校验企业已审核
        Company company = companyMapper.selectById(job.getCompanyId());
        if (company == null || !"VERIFIED".equals(company.getAuditStatus())) {
            throw new BusinessException(404, "岗位不存在");
        }
        return job;
    }

    /**
     * 获取岗位技能列表
     */
    public List<JobSkill> getJobSkills(Long jobId) {
        return jobSkillMapper.selectList(
                new LambdaQueryWrapper<JobSkill>()
                        .eq(JobSkill::getJobId, jobId));
    }

    // ==================== 内部方法 ====================

    private Company getCompanyByUserId(Long userId) {
        Company company = companyMapper.selectOne(
                new LambdaQueryWrapper<Company>().eq(Company::getUserId, userId));
        if (company == null) {
            throw new BusinessException(403, "您不是企业用户");
        }
        return company;
    }

    private Job getJobAndVerifyOwner(Long userId, Long jobId) {
        Job job = jobMapper.selectById(jobId);
        if (job == null) throw new BusinessException(404, "岗位不存在");
        Company company = companyMapper.selectById(job.getCompanyId());
        if (company == null || !company.getUserId().equals(userId)) {
            throw new BusinessException(403, "无权操作此岗位");
        }
        return job;
    }

    private void validateSkills(List<JobRequest.JobSkillRequest> skills) {
        if (skills == null) return;
        for (var s : skills) {
            Skill skill = skillMapper.selectById(s.getSkillId());
            if (skill == null || !"ACTIVE".equals(skill.getStatus())) {
                throw new BusinessException(400, "技能 ID=" + s.getSkillId() + " 不存在或非 ACTIVE 状态");
            }
        }
    }

    private void saveJobSkills(Long jobId, List<JobRequest.JobSkillRequest> skills) {
        if (skills == null) return;
        for (var s : skills) {
            JobSkill js = new JobSkill();
            js.setJobId(jobId);
            js.setSkillId(s.getSkillId());
            js.setImportance(s.getImportance() != null ? s.getImportance() : 3.0);
            js.setRequiredLevel(s.getRequiredLevel() != null ? s.getRequiredLevel() : "NICE");
            jobSkillMapper.insert(js);
        }
    }

    /**
     * 异步触发 JD 解析（桩实现）
     */
    @Async
    public void triggerJobParse(Long jobId, Long parseTaskId) {
        log.info("异步 JD 解析触发（桩实现）：jobId={}, parseTaskId={}", jobId, parseTaskId);
        // day07 替换为真实 AI 服务调用
    }
}
