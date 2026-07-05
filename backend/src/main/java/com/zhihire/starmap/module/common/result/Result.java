package com.zhihire.starmap.module.common.result;

import lombok.Data;

import java.io.Serializable;

/**
 * 统一 API 返回封装
 *
 * 所有 REST 接口统一使用此结构返回，前端按 code 判断成功/失败
 *
 * @param <T> 业务数据类型
 */
@Data
public class Result<T> implements Serializable {

    /** 状态码：200 成功，其他为业务错误 */
    private int code;

    /** 提示信息：成功时为 "success"，失败时为错误描述 */
    private String message;

    /** 业务数据：成功时返回，失败时为 null */
    private T data;

    /**
     * 私有构造，通过静态工厂方法创建
     */
    private Result() {}

    /**
     * 私有构造，带参初始化
     *
     * @param code    状态码
     * @param message 提示信息
     * @param data    业务数据
     */
    private Result(int code, String message, T data) {
        this.code = code;
        this.message = message;
        this.data = data;
    }

    /**
     * 成功返回（无数据）
     *
     * @param <T> 数据类型
     * @return 成功结果
     */
    public static <T> Result<T> ok() {
        return new Result<>(200, "success", null);
    }

    /**
     * 成功返回（带数据）
     *
     * @param data 业务数据
     * @param <T>  数据类型
     * @return 成功结果
     */
    public static <T> Result<T> ok(T data) {
        return new Result<>(200, "success", data);
    }

    /**
     * 成功返回（自定义消息 + 数据）
     *
     * @param message 提示信息
     * @param data    业务数据
     * @param <T>     数据类型
     * @return 成功结果
     */
    public static <T> Result<T> ok(String message, T data) {
        return new Result<>(200, message, data);
    }

    /**
     * 失败返回（自定义错误码 + 消息）
     *
     * @param code    错误码
     * @param message 错误描述
     * @param <T>     数据类型
     * @return 失败结果
     */
    public static <T> Result<T> error(int code, String message) {
        return new Result<>(code, message, null);
    }

    /**
     * 失败返回（默认 500 错误码）
     *
     * @param message 错误描述
     * @param <T>     数据类型
     * @return 失败结果
     */
    public static <T> Result<T> error(String message) {
        return new Result<>(500, message, null);
    }
}
