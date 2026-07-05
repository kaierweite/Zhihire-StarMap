package com.zhihire.starmap.module.common.exception;

/**
 * 文件上传异常（400）
 */
public class FileUploadException extends BusinessException {
    public FileUploadException(String message) {
        super(400, message);
    }
}
