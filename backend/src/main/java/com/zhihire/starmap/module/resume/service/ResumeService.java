package com.zhihire.starmap.module.resume.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.zhihire.starmap.module.common.exception.BusinessException;
import com.zhihire.starmap.module.resume.dto.ResumeUploadResponse;
import com.zhihire.starmap.module.resume.entity.ParseTask;
import com.zhihire.starmap.module.resume.entity.Resume;
import com.zhihire.starmap.module.resume.mapper.ParseTaskMapper;
import com.zhihire.starmap.module.resume.mapper.ResumeMapper;
import com.zhihire.starmap.module.system.entity.UploadFile;
import com.zhihire.starmap.module.system.service.SystemFileService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.multipart.MultipartFile;

/**
 * 简历服务
 *
 * 职责：简历上传（文件存储 + 创建简历 + 创建解析任务 + 异步触发解析）
 */
@Slf4j
@Service
public class ResumeService {

    private final SystemFileService systemFileService;
    private final ResumeMapper resumeMapper;
    private final ParseTaskMapper parseTaskMapper;

    public ResumeService(SystemFileService systemFileService,
                         ResumeMapper resumeMapper,
                         ParseTaskMapper parseTaskMapper) {
        this.systemFileService = systemFileService;
        this.resumeMapper = resumeMapper;
        this.parseTaskMapper = parseTaskMapper;
    }

    /**
     * 上传简历
     *
     * @param file   文件
     * @param userId 用户 ID
     * @return 上传响应
     */
    @Transactional(rollbackFor = Exception.class)
    public ResumeUploadResponse uploadResume(MultipartFile file, Long userId) {
        // 1. 存储文件（大小 + 扩展名 + 魔数校验）
        UploadFile uploadFile = systemFileService.store(file, userId);

        // 2. 创建简历记录
        Resume resume = new Resume();
        resume.setUserId(userId);
        resume.setFileId(uploadFile.getId());
        resume.setTitle(uploadFile.getOriginalName());
        resume.setStatus("NORMAL");
        resumeMapper.insert(resume);
        log.info("简历创建成功：resumeId={}, userId={}", resume.getId(), userId);

        // 3. 创建解析任务（status=WAITING）
        ParseTask parseTask = new ParseTask();
        parseTask.setFileId(uploadFile.getId());
        parseTask.setUserId(userId);
        parseTask.setStatus("WAITING");
        parseTaskMapper.insert(parseTask);
        log.info("解析任务创建：parseTaskId={}, status=WAITING", parseTask.getId());

        // 4. 异步触发 AI 解析（当前为桩实现，day07 接入真实 AI 服务）
        triggerAsyncParse(parseTask.getId());

        return ResumeUploadResponse.builder()
                .resumeId(resume.getId())
                .parseTaskId(parseTask.getId())
                .parseStatus("WAITING")
                .fileName(uploadFile.getOriginalName())
                .build();
    }

    /**
     * 获取用户简历列表（分页）
     */
    public Page<Resume> listUserResumes(Page<Resume> page, Long userId) {
        return resumeMapper.selectPage(page,
                new LambdaQueryWrapper<Resume>()
                        .eq(Resume::getUserId, userId)
                        .orderByDesc(Resume::getCreatedAt));
    }

    /**
     * 获取简历详情（校验所有权）
     */
    public Resume getResumeDetail(Long resumeId, Long userId) {
        Resume resume = resumeMapper.selectById(resumeId);
        if (resume == null || !resume.getUserId().equals(userId)) {
            throw new BusinessException(404, "简历不存在");
        }
        return resume;
    }

    /**
     * 异步触发 AI 解析（桩实现）
     *
     * day07 会替换为真实 AI 服务调用：
     * 1. 调用 ai-service POST /ai/parse/resume
     * 2. 解析完成后更新 parse_task.status + resume.content_text
     *
     * @param parseTaskId 解析任务 ID
     */
    @Async
    public void triggerAsyncParse(Long parseTaskId) {
        log.info("异步解析触发（桩实现）：parseTaskId={}", parseTaskId);
        // 桩实现：直接标记为 WAITING，等待 day07 接入 AI 服务
        // 生产逻辑：
        // 1. 更新 status = PARSING
        // 2. 调用 ai-service
        // 3. 成功 → status = SUCCESS + 更新 resume.content_text
        // 4. 失败 → status = FAILED
    }
}
