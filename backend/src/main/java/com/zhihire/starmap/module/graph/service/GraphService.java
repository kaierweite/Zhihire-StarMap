package com.zhihire.starmap.module.graph.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.zhihire.starmap.module.job.entity.JobSkill;
import com.zhihire.starmap.module.job.mapper.JobSkillMapper;
import com.zhihire.starmap.module.system.entity.Skill;
import com.zhihire.starmap.module.system.entity.SkillRelation;
import com.zhihire.starmap.module.system.mapper.SkillMapper;
import com.zhihire.starmap.module.system.mapper.SkillRelationMapper;
import com.zhihire.starmap.module.user.entity.UserSkill;
import com.zhihire.starmap.module.user.mapper.UserSkillMapper;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.*;
import java.util.stream.Collectors;

/**
 * 能力图谱服务
 *
 * 职责：组装 ECharts 格式的图谱数据（节点 + 边 + category）
 */
@Slf4j
@Service
public class GraphService {

    private final UserSkillMapper userSkillMapper;
    private final JobSkillMapper jobSkillMapper;
    private final SkillMapper skillMapper;
    private final SkillRelationMapper skillRelationMapper;
    private final ObjectMapper objectMapper;

    /** 节点类别颜色映射 */
    private static final Map<String, String> CATEGORY_COLORS = Map.of(
            "后端", "#5470c6", "前端", "#91cc75", "测试", "#fac858",
            "运维", "#ee6666", "数据", "#73c0de", "通用", "#3ba272");

    public GraphService(UserSkillMapper userSkillMapper, JobSkillMapper jobSkillMapper,
                        SkillMapper skillMapper, SkillRelationMapper skillRelationMapper,
                        ObjectMapper objectMapper) {
        this.userSkillMapper = userSkillMapper;
        this.jobSkillMapper = jobSkillMapper;
        this.skillMapper = skillMapper;
        this.skillRelationMapper = skillRelationMapper;
        this.objectMapper = objectMapper;
    }

    /**
     * 个人能力图谱
     * 节点：用户拥有的技能 + 一跳关联技能
     * 边：skill_relation 中涉及这些技能的关系
     */
    public Map<String, Object> getUserGraph(Long userId) {
        Set<Long> userSkillIds = userSkillMapper.selectList(
                new LambdaQueryWrapper<UserSkill>().eq(UserSkill::getUserId, userId))
                .stream().map(UserSkill::getSkillId).collect(Collectors.toSet());

        // 收集一跳关联技能
        Set<Long> allSkillIds = new HashSet<>(userSkillIds);
        List<SkillRelation> relations = skillRelationMapper.selectList(
                new LambdaQueryWrapper<SkillRelation>()
                        .in(SkillRelation::getSkillId, userSkillIds)
                        .or().in(SkillRelation::getRelatedSkillId, userSkillIds));
        for (SkillRelation r : relations) {
            allSkillIds.add(r.getSkillId());
            allSkillIds.add(r.getRelatedSkillId());
        }

        return buildGraphData(allSkillIds, userSkillIds, relations);
    }

    /**
     * 岗位能力图谱
     */
    public Map<String, Object> getJobGraph(Long jobId) {
        Set<Long> jobSkillIds = jobSkillMapper.selectList(
                new LambdaQueryWrapper<JobSkill>().eq(JobSkill::getJobId, jobId))
                .stream().map(JobSkill::getSkillId).collect(Collectors.toSet());

        Set<Long> allSkillIds = new HashSet<>(jobSkillIds);
        List<SkillRelation> relations = skillRelationMapper.selectList(
                new LambdaQueryWrapper<SkillRelation>()
                        .in(SkillRelation::getSkillId, jobSkillIds)
                        .or().in(SkillRelation::getRelatedSkillId, jobSkillIds));
        for (SkillRelation r : relations) {
            allSkillIds.add(r.getSkillId());
            allSkillIds.add(r.getRelatedSkillId());
        }

        return buildGraphData(allSkillIds, jobSkillIds, relations);
    }

    /**
     * 缺口分析：用户技能 vs 岗位要求
     * 返回：匹配技能、缺口技能、缺口技能的前置链
     */
    public Map<String, Object> getGapAnalysis(Long userId, Long jobId) {
        Set<Long> userSkillIds = userSkillMapper.selectList(
                new LambdaQueryWrapper<UserSkill>().eq(UserSkill::getUserId, userId))
                .stream().map(UserSkill::getSkillId).collect(Collectors.toSet());

        Set<Long> jobSkillIds = jobSkillMapper.selectList(
                new LambdaQueryWrapper<JobSkill>().eq(JobSkill::getJobId, jobId))
                .stream().map(JobSkill::getSkillId).collect(Collectors.toSet());

        // 匹配 vs 缺口
        Set<Long> hitIds = new HashSet<>(userSkillIds);
        hitIds.retainAll(jobSkillIds);
        Set<Long> missIds = new HashSet<>(jobSkillIds);
        missIds.removeAll(userSkillIds);

        // 缺口技能的前置链（沿 PREREQUISITE 边反推）
        List<Map<String, Object>> prereqChain = new ArrayList<>();
        if (!missIds.isEmpty()) {
            List<SkillRelation> prereqs = skillRelationMapper.selectList(
                    new LambdaQueryWrapper<SkillRelation>()
                            .in(SkillRelation::getRelatedSkillId, missIds)
                            .eq(SkillRelation::getRelationType, "PREREQUISITE"));
            for (SkillRelation r : prereqs) {
                Skill from = skillMapper.selectById(r.getSkillId());
                Skill to = skillMapper.selectById(r.getRelatedSkillId());
                if (from != null && to != null) {
                    prereqChain.add(Map.of("from", from.getName(), "to", to.getName(), "weight", r.getWeight()));
                }
            }
        }

        Map<String, Object> result = new LinkedHashMap<>();
        result.put("hit", hitIds.stream().map(id -> skillMapper.selectById(id))
                .filter(Objects::nonNull).map(Skill::getName).collect(Collectors.toList()));
        result.put("miss", missIds.stream().map(id -> skillMapper.selectById(id))
                .filter(Objects::nonNull).map(Skill::getName).collect(Collectors.toList()));
        result.put("prereqChain", prereqChain);
        result.put("matchRate", jobSkillIds.isEmpty() ? 0 : Math.round(hitIds.size() * 100.0 / jobSkillIds.size()));
        return result;
    }

    /**
     * 构建 ECharts 图谱数据
     *
     * @param allSkillIds 所有相关技能 ID
     * @param ownedSkillIds 用户/岗位拥有的技能 ID（高亮）
     * @param relations 技能关系列表
     * @return ECharts 格式 {nodes, edges, categories}
     */
    private Map<String, Object> buildGraphData(Set<Long> allSkillIds,
                                               Set<Long> ownedSkillIds,
                                               List<SkillRelation> relations) {
        // 构建 category 列表
        Set<String> categories = new LinkedHashSet<>();
        Map<Long, Skill> skillMap = new HashMap<>();
        for (Long id : allSkillIds) {
            Skill s = skillMapper.selectById(id);
            if (s != null) {
                skillMap.put(id, s);
                if (s.getCategory() != null) categories.add(s.getCategory());
            }
        }
        List<String> categoryList = new ArrayList<>(categories);

        // 构建节点
        List<Map<String, Object>> nodes = new ArrayList<>();
        for (Map.Entry<Long, Skill> entry : skillMap.entrySet()) {
            Skill s = entry.getValue();
            Map<String, Object> node = new LinkedHashMap<>();
            node.put("id", s.getId().toString());
            node.put("name", s.getName());
            node.put("category", categoryList.indexOf(s.getCategory() != null ? s.getCategory() : "通用"));
            node.put("symbolSize", ownedSkillIds.contains(s.getId()) ? 40 : 20);
            node.put("itemStyle", Map.of("color",
                    ownedSkillIds.contains(s.getId()) ? "#c23531" : "#999"));
            nodes.add(node);
        }

        // 构建边
        List<Map<String, Object>> edges = new ArrayList<>();
        Set<Long> validIds = skillMap.keySet();
        for (SkillRelation r : relations) {
            if (!validIds.contains(r.getSkillId()) || !validIds.contains(r.getRelatedSkillId())) continue;
            Map<String, Object> edge = new LinkedHashMap<>();
            edge.put("source", r.getSkillId().toString());
            edge.put("target", r.getRelatedSkillId().toString());
            edge.put("relationType", r.getRelationType());
            // 不同关系类型不同线型
            String lineStyle = "solid";
            if ("PREREQUISITE".equals(r.getRelationType())) lineStyle = "dashed";
            edge.put("lineStyle", Map.of("type", lineStyle));
            edges.add(edge);
        }

        // categories
        List<Map<String, Object>> catList = categoryList.stream()
                .map(c -> Map.of("name", c, "itemStyle", Map.of("color",
                        CATEGORY_COLORS.getOrDefault(c, "#999"))))
                .collect(Collectors.toList());

        Map<String, Object> result = new LinkedHashMap<>();
        result.put("nodes", nodes);
        result.put("edges", edges);
        result.put("categories", catList);
        return result;
    }
}
