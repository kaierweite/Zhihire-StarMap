package com.zhihire.starmap.module.user.controller;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.zhihire.starmap.module.common.result.Result;
import com.zhihire.starmap.module.system.entity.Skill;
import com.zhihire.starmap.module.system.mapper.SkillMapper;
import com.zhihire.starmap.module.user.dto.UserSkillDTO;
import com.zhihire.starmap.module.user.entity.UserSkill;
import com.zhihire.starmap.module.user.mapper.UserSkillMapper;
import com.zhihire.starmap.module.user.service.UserProfileService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.stream.Collectors;

/**
 * 用户技能控制器
 *
 * 职责：查询/删除当前用户的技能
 */
@Slf4j
@RestController
@RequestMapping("/api/user")
public class UserSkillController {

    private final UserSkillMapper userSkillMapper;
    private final SkillMapper skillMapper;
    private final UserProfileService userProfileService;

    public UserSkillController(UserSkillMapper userSkillMapper,
                               SkillMapper skillMapper,
                               UserProfileService userProfileService) {
        this.userSkillMapper = userSkillMapper;
        this.skillMapper = skillMapper;
        this.userProfileService = userProfileService;
    }

    /**
     * 获取当前用户技能列表
     *
     * 关联查 skill 表，返回技能名 + 领域 + 熟练度
     */
    @GetMapping("/skills")
    public Result<List<UserSkillDTO>> getUserSkills(Authentication authentication) {
        Long userId = (Long) authentication.getPrincipal();

        List<UserSkill> userSkills = userSkillMapper.selectList(
                new LambdaQueryWrapper<UserSkill>()
                        .eq(UserSkill::getUserId, userId));

        List<UserSkillDTO> dtos = userSkills.stream().map(us -> {
            Skill skill = skillMapper.selectById(us.getSkillId());
            String name = skill != null ? skill.getName() : "未知";
            String category = skill != null ? skill.getCategory() : null;
            return new UserSkillDTO(us.getSkillId(), name, category, us.getProficiencyLevel());
        }).collect(Collectors.toList());

        return Result.ok(dtos);
    }

    /**
     * 删除用户技能
     *
     * @param skillId      技能 ID
     * @param authentication 认证对象
     * @return 统一结果
     */
    @DeleteMapping("/skills/{skillId}")
    public Result<Void> deleteUserSkill(@PathVariable Long skillId,
                                        Authentication authentication) {
        Long userId = (Long) authentication.getPrincipal();

        int rows = userSkillMapper.delete(
                new LambdaQueryWrapper<UserSkill>()
                        .eq(UserSkill::getUserId, userId)
                        .eq(UserSkill::getSkillId, skillId));

        if (rows == 0) {
            return Result.error(404, "技能不存在");
        }

        // 重新计算完成度
        userProfileService.recalculateCompleteness(userId);
        log.info("用户技能删除：userId={}, skillId={}", userId, skillId);
        return Result.ok();
    }
}
