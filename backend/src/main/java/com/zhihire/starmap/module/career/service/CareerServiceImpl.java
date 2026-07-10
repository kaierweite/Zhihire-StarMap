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
import com.zhihire.starmap.module.system.entity.Skill;
import com.zhihire.starmap.module.system.mapper.SkillMapper;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import java.util.*;
import java.util.stream.Collectors;

@Slf4j
@Service
public class CareerServiceImpl implements CareerService {

    private final CareerPlanMapper careerPlanMapper;
    private final OccupationRoleMapper occupationRoleMapper;
    private final UserSkillMapper userSkillMapper;
    private final SkillMapper skillMapper;
    private final ObjectMapper objectMapper;

    @Value("")
    private String aiServiceUrl;

    public CareerServiceImpl(CareerPlanMapper careerPlanMapper, OccupationRoleMapper occupationRoleMapper,
                             UserSkillMapper userSkillMapper, SkillMapper skillMapper, ObjectMapper objectMapper) {
        this.careerPlanMapper = careerPlanMapper;
        this.occupationRoleMapper = occupationRoleMapper;
        this.userSkillMapper = userSkillMapper;
        this.skillMapper = skillMapper;
        this.objectMapper = objectMapper;
    }

    @Override
    public CareerPlan getLatestPlan(Long userId) {
        return careerPlanMapper.selectOne(new LambdaQueryWrapper<CareerPlan>()
                .eq(CareerPlan::getUserId, userId).orderByDesc(CareerPlan::getCreatedAt).last("LIMIT 1"));
    }

    @Override
    public CareerPlan generatePlan(Long userId, CareerPlanRequest request) {
        OccupationRole targetRole;
        if (request.getTargetRoleId() != null) {
            targetRole = occupationRoleMapper.selectById(request.getTargetRoleId());
            if (targetRole == null) throw new BusinessException(404, "目标角色不存在");
        } else {
            targetRole = occupationRoleMapper.selectOne(new LambdaQueryWrapper<OccupationRole>().last("LIMIT 1"));
            if (targetRole == null) throw new BusinessException(404, "暂无职业角色");
        }
        Set<Long> userSkillIds = userSkillMapper.selectList(
                new LambdaQueryWrapper<UserSkill>().eq(UserSkill::getUserId, userId))
                .stream().map(UserSkill::getSkillId).collect(Collectors.toSet());
        List<Skill> allSkills = skillMapper.selectList(new LambdaQueryWrapper<Skill>().eq(Skill::getStatus, "ACTIVE"));
        List<Map<String, Object>> gapSkills = new ArrayList<>();
        List<String> learningPath = new ArrayList<>();
        int step = 1;
        for (Skill skill : allSkills) {
            if (!userSkillIds.contains(skill.getId()) && gapSkills.size() < 5) {
                gapSkills.add(new LinkedHashMap<>() {{ put("skillId", skill.getId()); put("name", skill.getName()); put("category", skill.getCategory()); put("priority", gapSkills.size() + 1); }});
                learningPath.add("Step " + step + ": 学习 " + skill.getName());
                step++;
            }
        }
        Map<String, Object> planContent = new LinkedHashMap<>();
        planContent.put("target_role", targetRole.getName());
        planContent.put("gap_skills", gapSkills);
        planContent.put("learning_path", learningPath);
        planContent.put("graph_hints", List.of("建议关注 " + targetRole.getName() + " 核心技能栈"));
        planContent.put("rationale", String.format("目标「%s」，您目前缺少 %d 项关键技能", targetRole.getName(), gapSkills.size()));
        CareerPlan plan = new CareerPlan();
        plan.setUserId(userId);
        plan.setTargetRole(targetRole.getName());
        plan.setSource("PROACTIVE");
        try { plan.setPlanContent(objectMapper.writeValueAsString(planContent)); } catch (Exception e) { plan.setPlanContent("{}"); }
        careerPlanMapper.insert(plan);
        log.info("职业规划生成：userId={}, targetRole={}", userId, targetRole.getName());
        return plan;
    }

    @Override
    public List<OccupationRole> listRoles() {
        return occupationRoleMapper.selectList(new LambdaQueryWrapper<OccupationRole>().orderByAsc(OccupationRole::getId));
    }

    @Override
    public List<CareerPlan> getPlanHistory(Long userId) {
        return careerPlanMapper.selectList(new LambdaQueryWrapper<CareerPlan>()
                .eq(CareerPlan::getUserId, userId).orderByDesc(CareerPlan::getCreatedAt));
    }
}