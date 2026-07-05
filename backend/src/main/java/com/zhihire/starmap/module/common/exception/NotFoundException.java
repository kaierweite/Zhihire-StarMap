package com.zhihire.starmap.module.common.exception;

/**
 * 资源未找到异常（404）
 */
public class NotFoundException extends BusinessException {
    public NotFoundException(String message) {
        super(404, message);
    }
}
