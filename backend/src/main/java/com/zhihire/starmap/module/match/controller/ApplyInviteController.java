package com.zhihire.starmap.module.match.controller;

import com.zhihire.starmap.module.common.result.Result;
import com.zhihire.starmap.module.match.entity.RecommendRecord;
import com.zhihire.starmap.module.match.service.ApplyInviteService;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * 投递/面试邀请控制器
 */
@RestController
@RequestMapping("/api/recommend")
public class ApplyInviteController {

    private final ApplyInviteService applyInviteService;

    public ApplyInviteController(ApplyInviteService applyInviteService) {
        this.applyInviteService = applyInviteService;
    }

    /** 求职者投递岗位 */
    @PostMapping("/job/{jobId}/apply")
    public Result<Void> applyJob(@PathVariable Long jobId,
                                 Authentication authentication) {
        Long userId = (Long) authentication.getPrincipal();
        applyInviteService.applyJob(userId, jobId);
        return Result.ok();
    }

    /** 企业发起面试邀请 */
    @PostMapping("/talent/{resumeId}/invite")
    public Result<Void> inviteTalent(@PathVariable Long resumeId,
                                     @RequestParam Long jobId,
                                     Authentication authentication) {
        Long userId = (Long) authentication.getPrincipal();
        applyInviteService.inviteTalent(userId, resumeId, jobId);
        return Result.ok();
    }

    /** 收到的面试邀请 */
    @GetMapping("/invitations")
    public Result<List<RecommendRecord>> getInvitations(Authentication authentication) {
        Long userId = (Long) authentication.getPrincipal();
        return Result.ok(applyInviteService.getInvitations(userId));
    }
}
