package com.zhihire.starmap.module.common.exception;

import lombok.Getter;

/**
 * 业务异常
 *
 * 用于可预见的业务逻辑错误（如用户名已存在、权限不足等）
 * 由 GlobalExceptionHandler 统一捕获并转换为 Result 返回
 */
@Getter
public class BusinessException extends RuntimeException {

    /** 业务错误码 */
    private final int code;

    /**
     * 构造业务异常（默认错误码 500）
     *
     * @param message 错误描述
     */
    public BusinessException(String message) {
        super(message);
        this.code = 500;
    }

    /**
     * 构造业务异常（自定义错误码）
     *
     * @param code    业务错误码
     * @param message 错误描述
     */
    public BusinessException(int code, String message) {
        super(message);
        this.code = code;
    }
}
