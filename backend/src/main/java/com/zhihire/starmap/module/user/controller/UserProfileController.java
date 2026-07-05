package com.zhihire.starmap.module.user.controller;

import com.zhihire.starmap.module.common.result.Result;
import com.zhihire.starmap.module.user.dto.CompanyProfileDTO;
import com.zhihire.starmap.module.user.dto.UserProfileDTO;
import com.zhihire.starmap.module.user.service.UserProfileService;
import jakarta.validation.Valid;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

/**
 * 用户档案控制器
 *
 * 职责：求职者档案 + 企业档案的 CRUD
 * 路径前缀 /api/user，需认证
 */
@RestController
@RequestMapping("/api")
public class UserProfileController {

    private final UserProfileService userProfileService;

    public UserProfileController(UserProfileService userProfileService) {
        this.userProfileService = userProfileService;
    }

    /**
     * 获取当前求职者档案
     *
     * @param authentication Spring Security 认证对象（principal=userId）
     * @return 档案 DTO
     */
    @GetMapping("/user/profile")
    public Result<UserProfileDTO> getUserProfile(Authentication authentication) {
        Long userId = (Long) authentication.getPrincipal();
        return Result.ok(userProfileService.getUserProfile(userId));
    }

    /**
     * 更新求职者档案
     *
     * @param dto            档案数据
     * @param authentication 认证对象
     * @return 统一结果
     */
    @PutMapping("/user/profile")
    public Result<Void> updateUserProfile(@Valid @RequestBody UserProfileDTO dto,
                                          Authentication authentication) {
        Long userId = (Long) authentication.getPrincipal();
        userProfileService.updateUserProfile(userId, dto);
        return Result.ok();
    }

    /**
     * 获取企业档案
     *
     * @param authentication 认证对象
     * @return 企业档案 DTO
     */
    @GetMapping("/company/profile")
    public Result<CompanyProfileDTO> getCompanyProfile(Authentication authentication) {
        Long userId = (Long) authentication.getPrincipal();
        return Result.ok(userProfileService.getCompanyProfile(userId));
    }

    /**
     * 更新企业档案
     *
     * @param dto            企业档案数据
     * @param authentication 认证对象
     * @return 统一结果
     */
    @PutMapping("/company/profile")
    public Result<Void> updateCompanyProfile(@Valid @RequestBody CompanyProfileDTO dto,
                                             Authentication authentication) {
        Long userId = (Long) authentication.getPrincipal();
        userProfileService.updateCompanyProfile(userId, dto);
        return Result.ok();
    }
}
