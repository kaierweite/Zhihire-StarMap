package com.zhihire.starmap.module.interview.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.core.conditions.update.LambdaUpdateWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.zhihire.starmap.module.common.exception.BusinessException;
import com.zhihire.starmap.module.interview.dto.InterviewAnswerRequest;
import com.zhihire.starmap.module.interview.dto.InterviewStartRequest;
import com.zhihire.starmap.module.interview.dto.ResumeOptimizeRequest;
import com.zhihire.starmap.module.interview.entity.*;
import com.zhihire.starmap.module.interview.mapper.*;
import com.zhihire.starmap.module.resume.entity.Resume;
import com.zhihire.starmap.module.resume.mapper.ResumeMapper;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.time.LocalDateTime;
import java.util.*;

@Slf4j
@Service
public class InterviewServiceImpl implements InterviewService {

    private final InterviewSessionMapper sessionMapper;
    private final InterviewQuestionMapper questionMapper;
    private final InterviewAnswerMapper answerMapper;
    private final InterviewReportMapper reportMapper;
    private final ResumeOptimizationMapper optimizationMapper;
    private final ResumeMapper resumeMapper;
    private final ObjectMapper objectMapper;

    public InterviewServiceImpl(InterviewSessionMapper sessionMapper, InterviewQuestionMapper questionMapper,
                                InterviewAnswerMapper answerMapper, InterviewReportMapper reportMapper,
                                ResumeOptimizationMapper optimizationMapper, ResumeMapper resumeMapper, ObjectMapper objectMapper) {
        this.sessionMapper = sessionMapper; this.questionMapper = questionMapper; this.answerMapper = answerMapper;
        this.reportMapper = reportMapper; this.optimizationMapper = optimizationMapper; this.resumeMapper = resumeMapper;
        this.objectMapper = objectMapper;
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public InterviewSession startSession(Long userId, InterviewStartRequest request) {
        InterviewSession session = new InterviewSession();
        session.setUserId(userId); session.setJobId(request.getJobId()); session.setOccupationRoleId(request.getOccupationRoleId());
        session.setStatus("PENDING"); session.setStartedAt(LocalDateTime.now()); sessionMapper.insert(session);
        log.info("面试会话创建：sessionId={}", session.getId()); return session;
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public List<InterviewQuestion> generateQuestions(Long sessionId) {
        InterviewSession session = sessionMapper.selectById(sessionId);
        if (session == null) throw new BusinessException(404, "面试会话不存在");
        String[] types = {"TECHNICAL", "BEHAVIORAL", "TECHNICAL", "SITUATIONAL", "RESUME_BASED"};
        String[] contents = {"请介绍一下 Java 中的多态机制", "描述一次你解决复杂技术问题的经历", "Spring Boot 自动配置的原理是什么？", "如果项目 deadline 紧张，你会如何安排优先级？", "请根据你的简历，介绍一个你参与的项目"};
        List<InterviewQuestion> questions = new ArrayList<>();
        for (int i = 0; i < 5; i++) {
            InterviewQuestion q = new InterviewQuestion(); q.setSessionId(sessionId); q.setQuestionType(types[i]); q.setContent(contents[i]); q.setOrderNo(i + 1); q.setIsBankVisible(false);
            try { q.setExpectedPoints(objectMapper.writeValueAsString(List.of("要点1：概念清晰", "要点2：有实际案例"))); } catch (Exception e) { q.setExpectedPoints("[]"); }
            questionMapper.insert(q); questions.add(q);
        }
        session.setStatus("IN_PROGRESS"); sessionMapper.updateById(session);
        log.info("面试题生成：sessionId={}, count={}", sessionId, questions.size()); return questions;
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public InterviewAnswer submitAnswer(Long userId, InterviewAnswerRequest request) {
        InterviewQuestion question = questionMapper.selectById(request.getQuestionId());
        if (question == null) throw new BusinessException(404, "问题不存在");
        double score = 60 + Math.random() * 30;
        InterviewAnswer answer = new InterviewAnswer(); answer.setQuestionId(request.getQuestionId()); answer.setContent(request.getContent());
        answer.setAiScore(Math.round(score * 10.0) / 10.0); answer.setAiFeedback("回答基本到位，建议补充具体案例和技术细节"); answer.setAnsweredAt(LocalDateTime.now());
        try { answer.setMatchedPoints(objectMapper.writeValueAsString(List.of("概念正确"))); answer.setMissedPoints(objectMapper.writeValueAsString(List.of("缺少实例"))); } catch (Exception e) { answer.setMatchedPoints("[]"); answer.setMissedPoints("[]"); }
        answerMapper.insert(answer); log.info("回答评分：questionId={}, score={}", request.getQuestionId(), answer.getAiScore()); return answer;
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public InterviewReport generateReport(Long sessionId) {
        InterviewSession session = sessionMapper.selectById(sessionId);
        if (session == null) throw new BusinessException(404, "面试会话不存在");
        List<InterviewAnswer> answers = answerMapper.selectList(new LambdaQueryWrapper<InterviewAnswer>()
                .inSql(InterviewAnswer::getQuestionId, "SELECT id FROM interview_question WHERE session_id = " + sessionId));
        double avgScore = answers.stream().mapToDouble(a -> a.getAiScore() != null ? a.getAiScore() : 0).average().orElse(0);
        Map<String, Double> radar = new LinkedHashMap<>();
        radar.put("technical", Math.round(avgScore * 10.0) / 10.0); radar.put("communication", Math.round((avgScore + 5) * 10.0) / 10.0);
        radar.put("problem_solving", Math.round((avgScore - 3) * 10.0) / 10.0); radar.put("culture_fit", Math.round((avgScore + 2) * 10.0) / 10.0); radar.put("depth", Math.round((avgScore - 5) * 10.0) / 10.0);
        List<Map<String, Object>> feedback = new ArrayList<>();
        for (Map.Entry<String, Double> entry : radar.entrySet()) { Map<String, Object> f = new LinkedHashMap<>(); f.put("dimension", entry.getKey()); f.put("score", entry.getValue()); f.put("advice", "建议在 " + entry.getKey() + " 方面继续提升"); feedback.add(f); }
        InterviewReport report = new InterviewReport(); report.setSessionId(sessionId); report.setOverallScore(Math.round(avgScore * 10.0) / 10.0);
        try { report.setRadar(objectMapper.writeValueAsString(radar)); report.setFeedback(objectMapper.writeValueAsString(feedback)); } catch (Exception e) { report.setRadar("{}"); report.setFeedback("[]"); }
        reportMapper.insert(report);
        questionMapper.update(null, new LambdaUpdateWrapper<InterviewQuestion>().eq(InterviewQuestion::getSessionId, sessionId).set(InterviewQuestion::getIsBankVisible, true));
        session.setStatus("COMPLETED"); session.setFinishedAt(LocalDateTime.now()); sessionMapper.updateById(session);
        log.info("面试报告生成：sessionId={}, score={}", sessionId, report.getOverallScore()); return report;
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public ResumeOptimization optimizeResume(Long userId, ResumeOptimizeRequest request) {
        Resume resume = resumeMapper.selectById(request.getResumeId());
        if (resume == null || !resume.getUserId().equals(userId)) throw new BusinessException(404, "简历不存在");
        List<Map<String, Object>> suggestions = new ArrayList<>();
        suggestions.add(new LinkedHashMap<>() {{ put("section", "专业技能"); put("current", "技能描述较笼统"); put("suggestion", "建议量化技能熟练度"); put("relates_to_skill", "Java"); }});
        suggestions.add(new LinkedHashMap<>() {{ put("section", "项目经验"); put("current", "缺少技术栈描述"); put("suggestion", "建议列出使用的技术栈和架构方案"); put("relates_to_skill", "系统设计"); }});
        ResumeOptimization opt = new ResumeOptimization(); opt.setResumeId(request.getResumeId()); opt.setJobId(request.getJobId());
        try { opt.setSuggestions(objectMapper.writeValueAsString(suggestions)); } catch (Exception e) { opt.setSuggestions("[]"); }
        optimizationMapper.insert(opt); log.info("简历优化建议生成：resumeId={}", request.getResumeId()); return opt;
    }

    @Override public Page<InterviewSession> listSessions(Long userId, int page, int size) { return sessionMapper.selectPage(new Page<>(page, size), new LambdaQueryWrapper<InterviewSession>().eq(InterviewSession::getUserId, userId).orderByDesc(InterviewSession::getCreatedAt)); }
    @Override public Map<String, Object> getSessionDetail(Long sessionId, Long userId) {
        InterviewSession session = sessionMapper.selectById(sessionId);
        if (session == null || !session.getUserId().equals(userId)) throw new BusinessException(404, "面试会话不存在");
        Map<String, Object> detail = new LinkedHashMap<>(); detail.put("session", session);
        detail.put("questions", questionMapper.selectList(new LambdaQueryWrapper<InterviewQuestion>().eq(InterviewQuestion::getSessionId, sessionId)));
        detail.put("report", reportMapper.selectOne(new LambdaQueryWrapper<InterviewReport>().eq(InterviewReport::getSessionId, sessionId)));
        return detail;
    }
    @Override public Page<InterviewQuestion> listQuestionBank(int page, int size) { return questionMapper.selectPage(new Page<>(page, size), new LambdaQueryWrapper<InterviewQuestion>().eq(InterviewQuestion::getIsBankVisible, true).orderByDesc(InterviewQuestion::getCreatedAt)); }
    @Override public List<ResumeOptimization> getOptimizations(Long resumeId, Long userId) {
        Resume resume = resumeMapper.selectById(resumeId);
        if (resume == null || !resume.getUserId().equals(userId)) throw new BusinessException(404, "简历不存在");
        return optimizationMapper.selectList(new LambdaQueryWrapper<ResumeOptimization>().eq(ResumeOptimization::getResumeId, resumeId).orderByDesc(ResumeOptimization::getCreatedAt));
    }
}