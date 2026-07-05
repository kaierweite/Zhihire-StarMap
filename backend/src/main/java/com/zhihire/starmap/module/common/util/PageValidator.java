package com.zhihire.starmap.module.common.util;

import com.zhihire.starmap.module.common.constant.CommonConstants;
import com.zhihire.starmap.module.common.exception.BusinessException;

/**
 * 分页参数校验工具
 */
public final class PageValidator {

    private PageValidator() {}

    /**
     * 校验并修正分页参数
     * page 最小 1，size 最小 1 最大 100
     *
     * @param page 页码
     * @param size 每页条数
     * @return 修正后的 size
     */
    public static int validateSize(int size) {
        if (size < 1) return CommonConstants.DEFAULT_PAGE_SIZE;
        if (size > CommonConstants.MAX_PAGE_SIZE) {
            throw new BusinessException(400, "每页条数不能超过 " + CommonConstants.MAX_PAGE_SIZE);
        }
        return size;
    }

    public static int validatePage(int page) {
        return Math.max(page, 1);
    }
}
