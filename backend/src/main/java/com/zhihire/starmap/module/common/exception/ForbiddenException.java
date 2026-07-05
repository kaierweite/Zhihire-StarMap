package com.zhihire.starmap.module.common.exception;

/**
 * 无权限异常（403）
 */
public class ForbiddenException extends BusinessException {
    public ForbiddenException(String message) {
        super(403, message);
    }
}
