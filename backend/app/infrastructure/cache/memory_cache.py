"""内存缓存封装。

基于 aiocache 的 SimpleMemoryCache 提供：
- JWT 黑名单（登出令牌失效）
- 验证码缓存（短信/邮箱验证码 + 过期）
- 通用统计与键值缓存

day00 阶段使用内存后端即可满足本地开发，
后续可平滑切换至 Redis 后端，业务层调用不变。
"""
import asyncio  # 异步事件循环（用于过期任务的延时）
from typing import Any  # 任意类型

from aiocache import SimpleMemoryCache  # 内存缓存后端

from app.config.settings import settings  # 全局配置


class MemoryCache:
    """内存缓存封装。

    内部维护一个 SimpleMemoryCache 实例，并提供面向业务的语义化方法。
    所有键值均为字符串，值可为任意可 JSON 序列化的对象。

    Attributes:
        cache: aiocache SimpleMemoryCache 实例。
    """

    def __init__(self) -> None:
        # 根据配置选择后端；目前仅实现内存，预留 redis 分支
        backend = settings.cache_backend  # 读取缓存后端配置
        if backend == "memory":
            # 内存缓存：进程内单例，重启即失效
            self.cache = SimpleMemoryCache()
        else:
            # 尚未支持的后端统一回退到内存，避免启动报错
            self.cache = SimpleMemoryCache()

    # ===== 通用键值操作 =====
    async def get(self, key: str, default: Any = None) -> Any:
        """读取缓存值，缺失返回 default。"""
        # 从内存缓存取值
        value = await self.cache.get(key, default=default)
        return value

    async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """写入缓存值，可指定过期时间（秒）。"""
        # ttl 为 None 时表示不过期
        await self.cache.set(key, value, ttl=ttl)

    async def delete(self, key: str) -> None:
        """删除指定缓存键。"""
        # 不存在时忽略
        await self.cache.delete(key)

    # ===== JWT 黑名单 =====
    async def blacklist_token(self, jti: str, ttl: int | None = None) -> None:
        """将 JWT 的 jti 加入黑名单。

        Args:
            jti: 令牌唯一标识。
            ttl: 过期秒数，通常等于剩余有效期，到期自动清理。
        """
        # 以 `jwt:blacklist:<jti>` 作为键，值为 1
        await self.set(f"jwt:blacklist:{jti}", 1, ttl=ttl)

    async def is_token_blacklisted(self, jti: str) -> bool:
        """判断令牌是否已被列入黑名单。"""
        # 命中即为已失效
        value = await self.get(f"jwt:blacklist:{jti}")
        return bool(value)

    # ===== 验证码缓存 =====
    async def set_code(self, key: str, code: str, ttl: int = 300) -> None:
        """设置验证码，默认 5 分钟过期。"""
        # 以 `code:<key>` 存储验证码
        await self.set(f"code:{key}", code, ttl=ttl)

    async def get_code(self, key: str) -> str | None:
        """读取验证码，缺失返回 None。"""
        # 取值并归一为字符串或 None
        value = await self.get(f"code:{key}")
        return str(value) if value is not None else None

    async def consume_code(self, key: str) -> None:
        """验证码校验通过后清理，避免重复使用。"""
        # 删除已用验证码
        await self.delete(f"code:{key}")

    # ===== 统计缓存 =====
    async def incr_stat(self, key: str, amount: int = 1) -> int:
        """统计计数自增，键不存在时从 0 开始。"""
        # 读取当前值，缺失按 0 处理
        current = await self.get(f"stat:{key}", default=0)
        # 确保为整型
        new_value = int(current) + amount
        # 写回（统计计数通常长期保留，不过期）
        await self.set(f"stat:{key}", new_value)
        return new_value

    async def get_stat(self, key: str, default: int = 0) -> int:
        """读取统计计数。"""
        value = await self.get(f"stat:{key}", default=default)
        return int(value)


# 模块级单例，供业务层注入使用
memory_cache = MemoryCache()