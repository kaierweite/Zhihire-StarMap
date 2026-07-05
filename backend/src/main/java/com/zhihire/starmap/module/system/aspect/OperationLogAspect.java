package com.zhihire.starmap.module.system.aspect;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.zhihire.starmap.module.system.annotation.OperationLog;
import com.zhihire.starmap.module.system.entity.OperationLogEntity;
import com.zhihire.starmap.module.system.mapper.OperationLogMapper;
import jakarta.servlet.http.HttpServletRequest;
import lombok.extern.slf4j.Slf4j;
import org.aspectj.lang.ProceedingJoinPoint;
import org.aspectj.lang.annotation.Around;
import org.aspectj.lang.annotation.Aspect;
import org.aspectj.lang.reflect.MethodSignature;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Component;
import org.springframework.web.context.request.RequestContextHolder;
import org.springframework.web.context.request.ServletRequestAttributes;

import java.util.HashMap;
import java.util.Map;

/**
 * 操作日志 AOP 切面
 *
 * 拦截带 @OperationLog 注解的方法，自动记录操作日志到 operation_log 表
 */
@Slf4j
@Aspect
@Component
public class OperationLogAspect {

    private final OperationLogMapper operationLogMapper;
    private final ObjectMapper objectMapper;

    public OperationLogAspect(OperationLogMapper operationLogMapper,
                              ObjectMapper objectMapper) {
        this.operationLogMapper = operationLogMapper;
        this.objectMapper = objectMapper;
    }

    /**
     * 环绕通知：拦截 @OperationLog 注解的方法
     *
     * @param joinPoint    连接点
     * @param operationLog 注解
     * @return 方法执行结果
     */
    @Around("@annotation(operationLog)")
    public Object around(ProceedingJoinPoint joinPoint, OperationLog operationLog) throws Throwable {
        long startTime = System.currentTimeMillis();
        Object result = null;
        boolean success = true;

        try {
            result = joinPoint.proceed();
            return result;
        } catch (Throwable e) {
            success = false;
            throw e;
        } finally {
            // 异步记录日志（不阻断主流程）
            try {
                recordLog(joinPoint, operationLog, result, success, startTime);
            } catch (Exception e) {
                log.warn("操作日志记录失败：{}", e.getMessage());
            }
        }
    }

    private void recordLog(ProceedingJoinPoint joinPoint, OperationLog annotation,
                           Object result, boolean success, long startTime) {
        // 获取当前用户
        Long userId = null;
        Authentication auth = SecurityContextHolder.getContext().getAuthentication();
        if (auth != null && auth.getPrincipal() instanceof Long) {
            userId = (Long) auth.getPrincipal();
        }

        // 获取请求 IP
        String ip = "";
        ServletRequestAttributes attrs =
                (ServletRequestAttributes) RequestContextHolder.getRequestAttributes();
        if (attrs != null) {
            ip = attrs.getRequest().getRemoteAddr();
        }

        // 构建详情
        Map<String, Object> detail = new HashMap<>();
        detail.put("success", success);
        detail.put("duration", System.currentTimeMillis() - startTime);
        // 记录方法参数（排除敏感字段）
        MethodSignature sig = (MethodSignature) joinPoint.getSignature();
        String[] paramNames = sig.getParameterNames();
        Object[] args = joinPoint.getArgs();
        if (paramNames != null) {
            Map<String, Object> params = new HashMap<>();
            for (int i = 0; i < paramNames.length; i++) {
                // 排除密码等敏感字段
                if (paramNames[i].toLowerCase().contains("password")) continue;
                params.put(paramNames[i], args[i]);
            }
            detail.put("params", params);
        }

        // 解析注解值（模块/动作）
        String[] parts = annotation.value().split("/", 2);
        String module = parts.length > 0 ? parts[0] : "";
        String action = parts.length > 1 ? parts[1] : "";

        OperationLogEntity logEntity = new OperationLogEntity();
        logEntity.setUserId(userId);
        logEntity.setModule(module);
        logEntity.setAction(action);
        try {
            logEntity.setDetail(objectMapper.writeValueAsString(detail));
        } catch (Exception e) {
            logEntity.setDetail("{}");
        }
        logEntity.setIp(ip);
        operationLogMapper.insert(logEntity);
    }
}
