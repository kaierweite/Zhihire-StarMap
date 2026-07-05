package com.zhihire.starmap.module.user.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.zhihire.starmap.module.common.exception.BusinessException;
import com.zhihire.starmap.module.user.dto.CompanyProfileDTO;
import com.zhihire.starmap.module.user.dto.UserProfileDTO;
import com.zhihire.starmap.module.user.entity.Company;
import com.zhihire.starmap.module.user.entity.UserProfile;
import com.zhihire.starmap.module.user.entity.UserSkill;
import com.zhihire.starmap.module.user.mapper.CompanyMapper;
import com.zhihire.starmap.module.user.mapper.UserProfileMapper;
import com.zhihire.starmap.module.user.mapper.UserSkillMapper;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.BeanUtils;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Slf4j
@Service
public class UserProfileService {

    private final UserProfileMapper userProfileMapper;
    private final CompanyMapper companyMapper;
    private final UserSkillMapper userSkillMapper;

    public UserProfileService(UserProfileMapper userProfileMapper,
                              CompanyMapper companyMapper,
                              UserSkillMapper userSkillMapper) {
        this.userProfileMapper = userProfileMapper;
        this.companyMapper = companyMapper;
        this.userSkillMapper = userSkillMapper;
    }

    public UserProfileDTO getUserProfile(Long userId) {
        UserProfile profile = getOrCreateProfile(userId);
        UserProfileDTO dto = new UserProfileDTO();
        BeanUtils.copyProperties(profile, dto);
        return dto;
    }

    @Transactional(rollbackFor = Exception.class)
    public void updateUserProfile(Long userId, UserProfileDTO dto) {
        UserProfile profile = getOrCreateProfile(userId);
        BeanUtils.copyProperties(dto, profile, "id", "userId", "createdAt", "updatedAt", "deletedAt");
        profile.setProfileCompleteness(calculateCompleteness(profile, userId));
        userProfileMapper.updateById(profile);
        log.info("求职者档案更新：userId={}, completeness={}", userId, profile.getProfileCompleteness());
    }

    /**
     * 重新计算并更新档案完成度（含技能数）
     */
    public void recalculateCompleteness(Long userId) {
        UserProfile profile = getOrCreateProfile(userId);
        int score = calculateCompleteness(profile, userId);
        profile.setProfileCompleteness(score);
        userProfileMapper.updateById(profile);
        log.info("档案完成度重算：userId={}, completeness={}", userId, score);
    }

    public CompanyProfileDTO getCompanyProfile(Long userId) {
        Company company = companyMapper.selectOne(
                new LambdaQueryWrapper<Company>().eq(Company::getUserId, userId));
        if (company == null) throw new BusinessException(404, "企业档案不存在");
        CompanyProfileDTO dto = new CompanyProfileDTO();
        BeanUtils.copyProperties(company, dto);
        return dto;
    }

    @Transactional(rollbackFor = Exception.class)
    public void updateCompanyProfile(Long userId, CompanyProfileDTO dto) {
        Company company = companyMapper.selectOne(
                new LambdaQueryWrapper<Company>().eq(Company::getUserId, userId));
        if (company == null) throw new BusinessException(404, "企业档案不存在");
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

    private int calculateCompleteness(UserProfile p, Long userId) {
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
        long skillCount = userSkillMapper.selectCount(
                new LambdaQueryWrapper<UserSkill>().eq(UserSkill::getUserId, userId));
        if (skillCount >= 3) score += 10;
        else if (skillCount >= 1) score += 5;
        return Math.min(score, 100);
    }
}
