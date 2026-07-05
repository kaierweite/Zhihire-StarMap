package com.zhihire.starmap.module.user.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.zhihire.starmap.module.common.exception.BusinessException;
import com.zhihire.starmap.module.user.dto.CompanyProfileDTO;
import com.zhihire.starmap.module.user.dto.UserProfileDTO;
import com.zhihire.starmap.module.user.entity.Company;
import com.zhihire.starmap.module.user.entity.UserProfile;
import com.zhihire.starmap.module.user.mapper.CompanyMapper;
import com.zhihire.starmap.module.user.mapper.UserProfileMapper;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.BeanUtils;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 * 用户档案服务
 *
 * 职责：求职者档案 + 企业档案的查询与更新
 */
@Slf4j
@Service
public class UserProfileService {

    private final UserProfileMapper userProfileMapper;
    private final CompanyMapper companyMapper;

    public UserProfileService(UserProfileMapper userProfileMapper,
                              CompanyMapper companyMapper) {
        this.userProfileMapper = userProfileMapper;
        this.companyMapper = companyMapper;
    }

    /**
     * 获取求职者档案
     * 若不存在则自动创建空档案
     */
    public UserProfileDTO getUserProfile(Long userId) {
        UserProfile profile = getOrCreateProfile(userId);
        UserProfileDTO dto = new UserProfileDTO();
        BeanUtils.copyProperties(profile, dto);
        return dto;
    }

    /**
     * 更新求职者档案
     */
    @Transactional(rollbackFor = Exception.class)
    public void updateUserProfile(Long userId, UserProfileDTO dto) {
        UserProfile profile = getOrCreateProfile(userId);
        BeanUtils.copyProperties(dto, profile, "id", "userId", "createdAt", "updatedAt", "deletedAt");
        // 计算完成度
        profile.setProfileCompleteness(calculateCompleteness(profile));
        userProfileMapper.updateById(profile);
        log.info("求职者档案更新：userId={}, completeness={}", userId, profile.getProfileCompleteness());
    }

    /**
     * 获取企业档案
     */
    public CompanyProfileDTO getCompanyProfile(Long userId) {
        Company company = companyMapper.selectOne(
                new LambdaQueryWrapper<Company>().eq(Company::getUserId, userId));
        if (company == null) {
            throw new BusinessException(404, "企业档案不存在");
        }
        CompanyProfileDTO dto = new CompanyProfileDTO();
        BeanUtils.copyProperties(company, dto);
        return dto;
    }

    /**
     * 更新企业档案
     * 审核状态和审核原因不允许前端修改
     */
    @Transactional(rollbackFor = Exception.class)
    public void updateCompanyProfile(Long userId, CompanyProfileDTO dto) {
        Company company = companyMapper.selectOne(
                new LambdaQueryWrapper<Company>().eq(Company::getUserId, userId));
        if (company == null) {
            throw new BusinessException(404, "企业档案不存在");
        }
        // 只更新允许修改的字段
        company.setCompanyName(dto.getCompanyName());
        company.setIndustry(dto.getIndustry());
        company.setScale(dto.getScale());
        company.setWebsite(dto.getWebsite());
        company.setLogoUrl(dto.getLogoUrl());
        company.setDescription(dto.getDescription());
        company.setAddress(dto.getAddress());
        company.setContactName(dto.getContactName());
        company.setContactPhone(dto.getContactPhone());
        company.setContactEmail(dto.getContactEmail());
        companyMapper.updateById(company);
        log.info("企业档案更新：userId={}", userId);
    }

    /**
     * 获取或创建求职者档案
     */
    private UserProfile getOrCreateProfile(Long userId) {
        UserProfile profile = userProfileMapper.selectOne(
                new LambdaQueryWrapper<UserProfile>().eq(UserProfile::getUserId, userId));
        if (profile == null) {
            profile = new UserProfile();
            profile.setUserId(userId);
            profile.setProfileCompleteness(0);
            userProfileMapper.insert(profile);
        }
        return profile;
    }

    /**
     * 计算简历完成度（0~100）
     * 每个关键字段占一定权重
     */
    private int calculateCompleteness(UserProfile p) {
        int score = 0;
        if (p.getRealName() != null && !p.getRealName().isEmpty()) score += 15;
        if (p.getGender() != null) score += 5;
        if (p.getEducation() != null) score += 10;
        if (p.getSchool() != null && !p.getSchool().isEmpty()) score += 10;
        if (p.getMajor() != null && !p.getMajor().isEmpty()) score += 10;
        if (p.getWorkYears() != null) score += 10;
        if (p.getCurrentCity() != null && !p.getCurrentCity().isEmpty()) score += 10;
        if (p.getExpectedCity() != null && !p.getExpectedCity().isEmpty()) score += 10;
        if (p.getExpectedSalaryMin() != null) score += 10;
        if (p.getBio() != null && !p.getBio().isEmpty()) score += 10;
        return Math.min(score, 100);
    }
}
