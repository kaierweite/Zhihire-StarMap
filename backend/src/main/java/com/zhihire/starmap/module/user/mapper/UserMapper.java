package com.zhihire.starmap.module.user.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.zhihire.starmap.module.user.entity.User;
import org.apache.ibatis.annotations.Mapper;

/**
 * 用户 Mapper
 *
 * 继承 BaseMapper 提供基础 CRUD，MyBatis-Plus 自动实现
 */
@Mapper
public interface UserMapper extends BaseMapper<User> {
}
