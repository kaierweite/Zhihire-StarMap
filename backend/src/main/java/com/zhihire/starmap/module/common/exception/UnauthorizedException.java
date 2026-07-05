package com.zhihire.starmap.module.common.exception;

/**
 * 未认证异常（401）
 */
public class UnauthorizedException extends BusinessException {
    public UnauthorizedException(String message) {
        super(401, message);
    }
}
