package com.zhihire.starmap.module.admin.controller;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.core.conditions.update.LambdaUpdateWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.zhihire.starmap.module.admin.dto.CompanyAuditRequest;
import com.zhihire.starmap.module.common.exception.BusinessException;
import com.zhihire.starmap.module.common.result.Result;
import com.zhihire.starmap.module.job.entity.Job;
import com.zhihire.starmap.module.job.mapper.JobMapper;
import com.zhihire.starmap.module.system.annotation.OperationLog;
import com.zhihire.starmap.module.user.entity.Company;
import com.zhihire.starmap.module.user.mapper.CompanyMapper;
import jakarta.validation.Valid;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.util.StringUtils;
import org.springframework.web.bind.annotation.*;

/**
 * 管理后台 — 企业审核
 */
@Slf4j
@RestController
@RequestMapping("/api/admin/company")
@PreAuthorize("hasRole('ADMIN')")
public class AdminCompanyController {

    private final CompanyMapper companyMapper;
    private final JobMapper jobMapper;

    public AdminCompanyController(CompanyMapper companyMapper, JobMapper jobMapper) {
        this.companyMapper = companyMapper;
        this.jobMapper = jobMapper;
    }

    /** 企业列表（按审核状态筛选，分页） */
    @GetMapping("/list")
    public Result<Page<Company>> listCompanies(
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "20") int size,
            @RequestParam(required = false) String auditStatus) {
        Page<Company> pageParam = new Page<>(page, size);
        LambdaQueryWrapper<Company> wrapper = new LambdaQueryWrapper<>();
        if (StringUtils.hasText(auditStatus)) {
            wrapper.eq(Company::getAuditStatus, auditStatus);
        }
        wrapper.orderByDesc(Company::getCreatedAt);
        return Result.ok(companyMapper.selectPage(pageParam, wrapper));
    }

    /** 审核企业 */
    @PutMapping("/{id}/audit")
    @OperationLog("企业管理/审核企业")
    public Result<Void> auditCompany(@PathVariable Long id,
                                     @Valid @RequestBody CompanyAuditRequest request) {
        Company company = companyMapper.selectById(id);
        if (company == null) throw new BusinessException(404, "企业不存在");

        // REJECTED 必须传原因
        if ("REJECTED".equals(request.getAuditStatus())
                && !StringUtils.hasText(request.getAuditReason())) {
            throw new BusinessException(400, "拒绝审核必须填写原因");
        }

        company.setAuditStatus(request.getAuditStatus());
        company.setAuditReason(request.getAuditReason());
        companyMapper.updateById(company);
        log.info("企业审核：companyId={}, status={}", id, request.getAuditStatus());

        // 审核通过：将企业 DRAFT 岗位自动 OPEN
        if ("VERIFIED".equals(request.getAuditStatus())) {
            int updated = jobMapper.update(null,
                    new LambdaUpdateWrapper<Job>()
                            .eq(Job::getCompanyId, id)
                            .eq(Job::getStatus, "DRAFT")
                            .set(Job::getStatus, "OPEN"));
            log.info("审核通过自动开放岗位：companyId={}, 开放 {} 个岗位", id, updated);
        }
        return Result.ok();
    }
}
