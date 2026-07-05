package com.zhihire.starmap.module.common.constant;

/**
 * 公共常量
 *
 * 跨模块共享的常量定义，避免魔法值散布在各模块中
 * 状态枚举值在此定义引用，确保全项目一致性
 */
public final class CommonConstants {

    /** 私有构造，防止实例化工具类 */
    private CommonConstants() {}

    // ==================== 分页默认值 ====================

    /** 默认页码：第 1 页 */
    public static final int DEFAULT_PAGE = 1;

    /** 默认每页条数：20 */
    public static final int DEFAULT_PAGE_SIZE = 20;

    /** 每页最大条数：100 */
    public static final int MAX_PAGE_SIZE = 100;

    // ==================== 通用状态枚举 ====================

    /** 正常状态 */
    public static final String STATUS_NORMAL = "NORMAL";

    /** 禁用状态 */
    public static final String STATUS_DISABLED = "DISABLED";

    /** 封禁状态 */
    public static final String STATUS_BANNED = "BANNED";

    // ==================== 用户角色枚举 ====================

    /** 管理员角色 */
    public static final String ROLE_ADMIN = "ADMIN";

    /** 求职者角色 */
    public static final String ROLE_USER = "USER";

    /** 企业角色 */
    public static final String ROLE_COMPANY = "COMPANY";

    // ==================== 删除标记 ====================

    /** 未删除 */
    public static final String NOT_DELETED = "0";

    /** 已删除（逻辑删除） */
    public static final String DELETED = "1";
}
