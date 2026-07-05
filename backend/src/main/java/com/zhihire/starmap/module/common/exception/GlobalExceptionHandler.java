package com.zhihire.starmap.module.common.exception;

import com.zhihire.starmap.module.common.result.Result;
import jakarta.validation.ConstraintViolationException;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.validation.BindException;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestControllerAdvice;

import java.util.stream.Collectors;

/**
 * 全局异常处理器
 *
 * 统一捕获 Controller 层抛出的异常，转换为 Result 格式返回
 * 避免前端看到 Spring 默认的白页或 StackTrace
 */
@Slf4j
@RestControllerAdvice
public class GlobalExceptionHandler {

    /**
     * 处理业务异常
     *
     * @param e 业务异常
     * @return 标准错误结果
     */
    @ExceptionHandler(BusinessException.class)
    public Result<Void> handleBusinessException(BusinessException e) {
        // 记录业务异常日志（WARN 级别，非系统错误）
        log.warn("业务异常：code={}, message={}", e.getCode(), e.getMessage());
        return Result.error(e.getCode(), e.getMessage());
    }

    /**
     * 处理 @RequestBody 参数校验异常（@Valid 校验失败）
     *
     * @param e 方法参数校验异常
     * @return 标准错误结果，包含字段级错误描述
     */
    @ExceptionHandler(MethodArgumentNotValidException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public Result<Void> handleValidationException(MethodArgumentNotValidException e) {
        // 拼接所有字段校验错误信息
        String message = e.getBindingResult().getFieldErrors().stream()
                .map(fieldError -> fieldError.getField() + ": " + fieldError.getDefaultMessage())
                .collect(Collectors.joining("; "));
        log.warn("参数校验失败：{}", message);
        return Result.error(400, message);
    }

    /**
     * 处理 @RequestParam / @PathVariable 参数校验异常
     *
     * @param e 约束违反异常
     * @return 标准错误结果
     */
    @ExceptionHandler(ConstraintViolationException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public Result<Void> handleConstraintViolation(ConstraintViolationException e) {
        log.warn("约束违反：{}", e.getMessage());
        return Result.error(400, e.getMessage());
    }

    /**
     * 处理绑定异常（表单参数绑定失败）
     *
     * @param e 绑定异常
     * @return 标准错误结果
     */
    @ExceptionHandler(BindException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public Result<Void> handleBindException(BindException e) {
        String message = e.getBindingResult().getFieldErrors().stream()
                .map(fieldError -> fieldError.getField() + ": " + fieldError.getDefaultMessage())
                .collect(Collectors.joining("; "));
        log.warn("参数绑定失败：{}", message);
        return Result.error(400, message);
    }

    /**
     * 兜底处理所有未预期异常（500）
     *
     * @param e 未知异常
     * @return 标准错误结果
     */
    @ExceptionHandler(Exception.class)
    @ResponseStatus(HttpStatus.INTERNAL_SERVER_ERROR)
    public Result<Void> handleException(Exception e) {
        // 未知异常记录 ERROR 级别日志，含完整堆栈
        log.error("系统异常：{}", e.getMessage(), e);
        return Result.error(500, "系统内部错误，请联系管理员");
    }
}
