package com.zhihire.starmap.module.career.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.zhihire.starmap.module.career.dto.CareerPlanRequest;
import com.zhihire.starmap.module.career.entity.CareerPlan;
import com.zhihire.starmap.module.career.mapper.CareerPlanMapper;
import com.zhihire.starmap.module.common.exception.BusinessException;
import com.zhihire.starmap.module.job.entity.OccupationRole;
import com.zhihire.starmap.module.job.mapper.OccupationRoleMapper;
import com.zhihire.starmap.module.user.entity.UserSkill;
import com.zhihire.starmap.module.user.mapper.UserSkillMapper;
import com.zhihire.starmap.module.job.entity.JobSkill;
import com.zhihire.starmap.module.job.mapper.JobSkillMapper;
import com.zhihire.starmap.module.system.entity.Skill;
import com.zhihire.starmap.module.system.mapper.SkillMapper;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.util.*;
import java.util.stream.Collectors;

/**
 * 职业规划服务
 *
 * 职责：生成职业规划（桩实现：本地计算缺口技能 + 学习路径）
 * day16 替换为真实 AI 服务 POST /ai/career/analyze
 */
@Slf4j
@Service
public class CareerService {

    private final CareerPlanMapper careerPlanMapper;
    private final OccupationRoleMapper occupationRoleMapper;
    private final UserSkillMapper userSkillMapper;
    private final JobSkillMapper jobSkillMapper;
    private final SkillMapper skillMapper;
    private final ObjectMapper objectMapper;

    @Value("${ai.service.url:http://localhost:8000}")
    private String aiServiceUrl;

    public CareerService(CareerPlanMapper careerPlanMapper,
                         OccupationRoleMapper occupationRoleMapper,
                         UserSkillMapper userSkillMapper,
                         JobSkillMapper jobSkillMapper,
                         SkillMapper skillMapper,
                         ObjectMapper objectMapper) {
        this.careerPlanMapper = careerPlanMapper;
        this.occupationRoleMapper = occupationRoleMapper;
        this.userSkillMapper = userSkillMapper;
        this.jobSkillMapper = jobSkillMapper;
        this.skillMapper = skillMapper;
        this.objectMapper = objectMapper;
    }

    /**
     * 获取用户最新的职业规划
     */
    public CareerPlan getLatestPlan(Long userId) {
        return careerPlanMapper.selectOne(
                new LambdaQueryWrapper<CareerPlan>()
                        .eq(CareerPlan::getUserId, userId)
                        .orderByDesc(CareerPlan::getCreatedAt)
                        .last("LIMIT 1"));
    }

    /**
     * 生成职业规划
     *
     * @param userId  用户 ID
     * @param request 请求（targetRoleId 可选）
     * @return 生成的规划
     */
    public CareerPlan generatePlan(Long userId, CareerPlanRequest request) {
        // 1. 确定目标角色
        OccupationRole targetRole;
        if (request.getTargetRoleId() != null) {
            targetRole = occupationRoleMapper.selectById(request.getTargetRoleId());
            if (targetRole == null) throw new BusinessException(404, "目标角色不存在");
        } else {
            // 默认取第一个角色
            targetRole = occupationRoleMapper.selectOne(
                    new LambdaQueryWrapper<OccupationRole>().last("LIMIT 1"));
            if (targetRole == null) throw new BusinessException(404, "暂无职业角色");
        }

        // 2. 获取用户现有技能
        Set<Long> userSkillIds = userSkillMapper.selectList(
                new LambdaQueryWrapper<UserSkill>().eq(UserSkill::getUserId, userId))
                .stream().map(UserSkill::getSkillId).collect(Collectors.toSet());

        // 3. 获取目标角色要求的技能
        List<JobSkill> roleSkills = jobSkillMapper.selectList(
                new LambdaQueryWrapper<JobSkill>()
                        .eq(JobSkill::getJobId, targetRole.getId())
                        .or() // occupation_role_skill 表不存在，用 job_skill 近似
        );
        // 实际应查 occupation_role_skill 表，这里用 skill 表近似
        List<Skill> allSkills = skillMapper.selectList(
                new LambdaQueryWrapper<Skill>().eq(Skill::getStatus, "ACTIVE"));

        // 4. 计算缺口技能（简化：角色要求的 MUST 技能中用户缺失的）
        List<Map<String, Object>> gapSkills = new ArrayList<>();
        List<String> learningPath = new ArrayList<>();
        int step = 1;
        for (Skill skill : allSkills) {
            if (!userSkillIds.contains(skill.getId()) && gapSkills.size() < 5) {
                Map<String, Object> gap = new LinkedHashMap<>();
                gap.put("skillId", skill.getId());
                gap.put("name", skill.getName());
                gap.put("category", skill.getCategory());
                gap.put("priority", gapSkills.size() + 1);
                gapSkills.add(gap);
                learningPath.add("Step " + step + ": 学习 " + skill.getName());
                step++;
            }
        }

        // 5. 构建 plan_content JSON
        Map<String, Object> planContent = new LinkedHashMap<>();
        planContent.put("target_role", targetRole.getName());
        planContent.put("gap_skills", gapSkills);
        planContent.put("learning_path", learningPath);
        planContent.put("graph_hints", List.of("建议关注 " + targetRole.getName() + " 核心技能栈"));
        planContent.put("rationale", String.format("目标「%s」，您目前缺少 %d 项关键技能，建议按学习路径逐步提升",
                targetRole.getName(), gapSkills.size()));

        // 6. 保存
        CareerPlan plan = new CareerPlan();
        plan.setUserId(userId);
        plan.setTargetRole(targetRole.getName());
        plan.setSource("PROACTIVE");
        try {
            plan.setPlanContent(objectMapper.writeValueAsString(planContent));
        } catch (Exception e) {
            plan.setPlanContent("{}");
        }
        careerPlanMapper.insert(plan);

        log.info("职业规划生成：userId={}, targetRole={}, gapCount={}", userId, targetRole.getName(), gapSkills.size());
        return plan;
    }

    /**
     * 获取职业角色列表
     */
    public List<OccupationRole> listRoles() {
        return occupationRoleMapper.selectList(
                new LambdaQueryWrapper<OccupationRole>().orderByAsc(OccupationRole::getId));
    }

    /**
     * 历史规划列表
     */
    public List<CareerPlan> getPlanHistory(Long userId) {
        return careerPlanMapper.selectList(
                new LambdaQueryWrapper<CareerPlan>()
                        .eq(CareerPlan::getUserId, userId)
                        .orderByDesc(CareerPlan::getCreatedAt));
    }
}
