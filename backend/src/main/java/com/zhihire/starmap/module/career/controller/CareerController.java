package com.zhihire.starmap.module.career.controller;

import com.zhihire.starmap.module.career.dto.CareerPlanRequest;
import com.zhihire.starmap.module.career.entity.CareerPlan;
import com.zhihire.starmap.module.career.service.CareerService;
import com.zhihire.starmap.module.common.result.Result;
import com.zhihire.starmap.module.job.entity.OccupationRole;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * 职业规划控制器
 *
 * 职责：生成/查询职业规划、职业角色列表
 */
@RestController
@RequestMapping("/api/career")
public class CareerController {

    private final CareerService careerService;

    public CareerController(CareerService careerService) {
        this.careerService = careerService;
    }

    /** 获取当前用户最新职业规划 */
    @GetMapping("/plan")
    public Result<CareerPlan> getPlan(Authentication authentication) {
        Long userId = (Long) authentication.getPrincipal();
        CareerPlan plan = careerService.getLatestPlan(userId);
        return Result.ok(plan);
    }

    /** 生成/更新职业规划 */
    @PostMapping("/plan")
    public Result<CareerPlan> generatePlan(@RequestBody(required = false) CareerPlanRequest request,
                                           Authentication authentication) {
        Long userId = (Long) authentication.getPrincipal();
        if (request == null) request = new CareerPlanRequest();
        return Result.ok(careerService.generatePlan(userId, request));
    }

    /** 职业角色列表 */
    @GetMapping("/roles")
    public Result<List<OccupationRole>> listRoles() {
        return Result.ok(careerService.listRoles());
    }

    /** 历史规划列表 */
    @GetMapping("/plan/history")
    public Result<List<CareerPlan>> getPlanHistory(Authentication authentication) {
        Long userId = (Long) authentication.getPrincipal();
        return Result.ok(careerService.getPlanHistory(userId));
    }
}
