package com.zhihire.starmap.module.system.annotation;

import java.lang.annotation.*;

/**
 * 操作日志注解
 *
 * 标注在 Controller 方法上，AOP 切面自动记录操作日志
 * 用法：@OperationLog("模块/动作")
 */
@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
@Documented
public @interface OperationLog {
    /** 操作描述，格式：模块/动作 */
    String value() default "";
}
