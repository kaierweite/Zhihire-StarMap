package com.zhihire.starmap.module.match.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.zhihire.starmap.module.common.exception.BusinessException;
import com.zhihire.starmap.module.user.entity.Company;
import com.zhihire.starmap.module.job.entity.Job;
import com.zhihire.starmap.module.job.mapper.JobMapper;
import com.zhihire.starmap.module.match.entity.RecommendRecord;
import com.zhihire.starmap.module.match.mapper.RecommendRecordMapper;
import com.zhihire.starmap.module.resume.entity.Resume;
import com.zhihire.starmap.module.resume.mapper.ResumeMapper;
import com.zhihire.starmap.module.system.service.NotificationService;
import com.zhihire.starmap.module.user.entity.User;
import com.zhihire.starmap.module.user.mapper.CompanyMapper;
import com.zhihire.starmap.module.user.mapper.UserMapper;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Slf4j
@Service
public class ApplyInviteService {

    private final RecommendRecordMapper recommendRecordMapper;
    private final ResumeMapper resumeMapper;
    private final JobMapper jobMapper;
    private final UserMapper userMapper;
    private final CompanyMapper companyMapper;
    private final NotificationService notificationService;

    public ApplyInviteService(RecommendRecordMapper recommendRecordMapper,
                              ResumeMapper resumeMapper, JobMapper jobMapper,
                              UserMapper userMapper, CompanyMapper companyMapper,
                              NotificationService notificationService) {
        this.recommendRecordMapper = recommendRecordMapper;
        this.resumeMapper = resumeMapper;
        this.jobMapper = jobMapper;
        this.userMapper = userMapper;
        this.companyMapper = companyMapper;
        this.notificationService = notificationService;
    }

    /** 求职者投递岗位 */
    @Transactional(rollbackFor = Exception.class)
    public void applyJob(Long userId, Long jobId) {
        Resume resume = resumeMapper.selectOne(
                new LambdaQueryWrapper<Resume>().eq(Resume::getUserId, userId).last("LIMIT 1"));
        if (resume == null) throw new BusinessException(400, "请先上传简历");
        Job job = jobMapper.selectById(jobId);
        if (job == null) throw new BusinessException(404, "岗位不存在");

        RecommendRecord record = recommendRecordMapper.selectOne(
                new LambdaQueryWrapper<RecommendRecord>()
                        .eq(RecommendRecord::getUserId, userId)
                        .eq(RecommendRecord::getJobId, jobId));
        if (record == null) {
            record = new RecommendRecord();
            record.setUserId(userId);
            record.setJobId(jobId);
            record.setIsClicked(true);
            record.setIsApplied(true);
            record.setIsInvited(false);
            recommendRecordMapper.insert(record);
        } else {
            record.setIsApplied(true);
            recommendRecordMapper.updateById(record);
        }

        Company company = companyMapper.selectById(job.getCompanyId());
        if (company != null) {
            User applicant = userMapper.selectById(userId);
            String content = String.format("求职者 %s 投递了岗位「%s」",
                    applicant != null ? applicant.getUsername() : "未知", job.getTitle());
            notificationService.createNotification(company.getUserId(), "收到新投递", content, "APPLICATION");
        }
        log.info("求职者投递：userId={}, jobId={}", userId, jobId);
    }

    /** 企业发起面试邀请 */
    @Transactional(rollbackFor = Exception.class)
    public void inviteTalent(Long userId, Long resumeId, Long jobId) {
        Resume resume = resumeMapper.selectById(resumeId);
        if (resume == null) throw new BusinessException(404, "简历不存在");
        Job job = jobMapper.selectById(jobId);
        if (job == null) throw new BusinessException(404, "岗位不存在");

        Company company = companyMapper.selectOne(
                new LambdaQueryWrapper<Company>().eq(Company::getUserId, userId));
        if (company == null || !job.getCompanyId().equals(company.getId())) {
            throw new BusinessException(403, "无权操作此岗位");
        }

        RecommendRecord record = recommendRecordMapper.selectOne(
                new LambdaQueryWrapper<RecommendRecord>()
                        .eq(RecommendRecord::getUserId, resume.getUserId())
                        .eq(RecommendRecord::getJobId, jobId));
        if (record == null) {
            record = new RecommendRecord();
            record.setUserId(resume.getUserId());
            record.setJobId(jobId);
            record.setIsClicked(false);
            record.setIsApplied(false);
            record.setIsInvited(true);
            recommendRecordMapper.insert(record);
        } else {
            record.setIsInvited(true);
            recommendRecordMapper.updateById(record);
        }

        String content = String.format("企业「%s」邀请您面试岗位「%s」",
                company.getCompanyName(), job.getTitle());
        notificationService.createNotification(resume.getUserId(), "面试邀请", content, "INTERVIEW_INVITE");
        log.info("面试邀请：resumeId={}, jobId={}", resumeId, jobId);
    }

    /** 收到的面试邀请列表 */
    public List<RecommendRecord> getInvitations(Long userId) {
        return recommendRecordMapper.selectList(
                new LambdaQueryWrapper<RecommendRecord>()
                        .eq(RecommendRecord::getUserId, userId)
                        .eq(RecommendRecord::getIsInvited, true)
                        .orderByDesc(RecommendRecord::getCreatedAt));
    }
}
