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

@Slf4j
@Service
public class ResumeServiceImpl implements ResumeService {

    private final SystemFileService systemFileService;
    private final ResumeMapper resumeMapper;
    private final ParseTaskMapper parseTaskMapper;

    public ResumeServiceImpl(SystemFileService systemFileService, ResumeMapper resumeMapper, ParseTaskMapper parseTaskMapper) {
        this.systemFileService = systemFileService;
        this.resumeMapper = resumeMapper;
        this.parseTaskMapper = parseTaskMapper;
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public ResumeUploadResponse uploadResume(MultipartFile file, Long userId) {
        UploadFile uploadFile = systemFileService.store(file, userId);
        Resume resume = new Resume();
        resume.setUserId(userId);
        resume.setFileId(uploadFile.getId());
        resume.setTitle(uploadFile.getOriginalName());
        resume.setStatus("NORMAL");
        resumeMapper.insert(resume);
        ParseTask parseTask = new ParseTask();
        parseTask.setFileId(uploadFile.getId());
        parseTask.setUserId(userId);
        parseTask.setStatus("WAITING");
        parseTaskMapper.insert(parseTask);
        triggerAsyncParse(parseTask.getId());
        log.info("简历创建成功：resumeId={}", resume.getId());
        return ResumeUploadResponse.builder().resumeId(resume.getId()).parseTaskId(parseTask.getId())
                .parseStatus("WAITING").fileName(uploadFile.getOriginalName()).build();
    }

    @Override
    public Page<Resume> listUserResumes(Page<Resume> page, Long userId) {
        return resumeMapper.selectPage(page, new LambdaQueryWrapper<Resume>()
                .eq(Resume::getUserId, userId).orderByDesc(Resume::getCreatedAt));
    }

    @Override
    public Resume getResumeDetail(Long resumeId, Long userId) {
        Resume resume = resumeMapper.selectById(resumeId);
        if (resume == null || !resume.getUserId().equals(userId)) throw new BusinessException(404, "简历不存在");
        return resume;
    }

    @Override
    @Async
    public void triggerAsyncParse(Long parseTaskId) {
        log.info("异步解析触发（桩实现）：parseTaskId={}", parseTaskId);
    }
}