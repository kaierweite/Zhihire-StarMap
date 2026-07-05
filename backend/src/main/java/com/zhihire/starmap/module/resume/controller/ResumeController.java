package com.zhihire.starmap.module.resume.controller;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.zhihire.starmap.module.common.result.Result;
import com.zhihire.starmap.module.resume.dto.ResumeUploadResponse;
import com.zhihire.starmap.module.resume.entity.ParseTask;
import com.zhihire.starmap.module.resume.entity.Resume;
import com.zhihire.starmap.module.resume.mapper.ParseTaskMapper;
import com.zhihire.starmap.module.resume.service.ResumeService;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

/**
 * 简历控制器
 *
 * 职责：简历文件上传、简历列表、解析任务状态查询
 */
@RestController
@RequestMapping("/api/resume")
public class ResumeController {

    private final ResumeService resumeService;
    private final ParseTaskMapper parseTaskMapper;

    public ResumeController(ResumeService resumeService,
                            ParseTaskMapper parseTaskMapper) {
        this.resumeService = resumeService;
        this.parseTaskMapper = parseTaskMapper;
    }

    /**
     * 上传简历文件
     *
     * 流程：
     * 1. SystemFileService 存储文件 + 创建 upload_file 记录
     * 2. 创建 resume 记录（file_id 引用 upload_file）
     * 3. 创建 parse_task 记录（status=WAITING）
     * 4. 异步触发 AI 解析（day04 搭建链路）
     *
     * @param file           上传的文件
     * @param authentication 认证对象
     * @return 上传响应（resumeId, parseTaskId, status）
     */
    @PostMapping("/upload")
    public Result<ResumeUploadResponse> uploadResume(
            @RequestParam("file") MultipartFile file,
            Authentication authentication) {
        Long userId = (Long) authentication.getPrincipal();
        ResumeUploadResponse response = resumeService.uploadResume(file, userId);
        return Result.ok(response);
    }

    /**
     * 获取当前用户简历列表（分页）
     *
     * @param page           页码（默认 1）
     * @param size           每页条数（默认 20）
     * @param authentication 认证对象
     * @return 简历分页列表
     */
    @GetMapping("/list")
    public Result<Page<Resume>> listResumes(
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "20") int size,
            Authentication authentication) {
        Long userId = (Long) authentication.getPrincipal();
        Page<Resume> pageParam = new Page<>(page, size);
        Page<Resume> result = resumeService.listUserResumes(pageParam, userId);
        return Result.ok(result);
    }

    /**
     * 获取简历详情
     *
     * @param id             简历 ID
     * @param authentication 认证对象
     * @return 简历详情
     */
    @GetMapping("/{id}")
    public Result<Resume> getResume(@PathVariable Long id,
                                    Authentication authentication) {
        Long userId = (Long) authentication.getPrincipal();
        return Result.ok(resumeService.getResumeDetail(id, userId));
    }

    /**
     * 查询解析任务状态（轮询接口）
     *
     * @param taskId 解析任务 ID
     * @return 解析任务信息
     */
    @GetMapping("/parse/task/{taskId}")
    public Result<ParseTask> getParseTask(@PathVariable Long taskId) {
        ParseTask task = parseTaskMapper.selectById(taskId);
        if (task == null) {
            return Result.error(404, "解析任务不存在");
        }
        return Result.ok(task);
    }
}
