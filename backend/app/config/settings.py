"""应用配置模块。

基于 Pydantic Settings 从环境变量与 .env 文件读取全局配置，
集中管理数据库连接、JWT 密钥、DeepSeek API Key 与文件存储路径等参数。
"""
from functools import lru_cache  # 提供单例缓存，避免重复读取环境变量

from pydantic_settings import BaseSettings, SettingsConfigDict  # 配置基类与配置字典


class Settings(BaseSettings):
    """全局配置项。

    所有字段均可通过环境变量或 .env 文件覆盖，
    变量名大小写不敏感，未声明的环境变量将被忽略。
    """

    # Pydantic Settings 配置：从 .env 读取、UTF-8 编码、忽略多余项
    model_config = SettingsConfigDict(
        env_file=".env",  # 默认读取后端根目录下的 .env
        env_file_encoding="utf-8",  # 读取 .env 时使用 UTF-8 编码
        case_sensitive=False,  # 环境变量名不区分大小写
        extra="ignore",  # 忽略未声明的环境变量，避免启动报错
    )

    # ===== 应用基础信息 =====
    app_name: str = "智聘星图"  # 应用名称
    app_env: str = "dev"  # 运行环境：dev / prod
    api_prefix: str = "/api"  # 统一 API 路径前缀

    # ===== 数据库连接 =====
    # KingbaseES 兼容 PostgreSQL，使用 asyncpg 异步驱动
    database_url: str = (
        "postgresql+asyncpg://kingbase:kingbase@127.0.0.1:54321/starmap"
    )
    db_pool_size: int = 10  # 连接池常驻连接数
    db_max_overflow: int = 20  # 连接池允许的额外溢出连接数
    db_pool_recycle: int = 3600  # 连接回收周期（秒），避免数据库主动断开

    # ===== JWT 认证 =====
    jwt_secret: str = "change-me-in-production-please"  # JWT 签名密钥，生产环境必须替换
    jwt_algorithm: str = "HS256"  # JWT 签名算法
    access_token_expire_minutes: int = 60 * 24  # 访问令牌有效期（分钟），默认 24 小时
    refresh_token_expire_days: int = 7  # 刷新令牌有效期（天）

    # ===== DeepSeek 云端大模型 API =====
    deepseek_api_key: str = ""  # API Key，留空时客户端走 mock 逻辑，便于无网本地开发
    deepseek_base_url: str = "https://api.deepseek.com"  # DeepSeek 接口基础地址
    deepseek_chat_model: str = "deepseek-chat"  # 对话模型名称
    deepseek_vision_model: str = "deepseek-chat"  # 视觉模型名称，暂复用对话端点
    deepseek_timeout: int = 60  # DeepSeek 请求超时时间（秒）

    # ===== 文件本地存储 =====
    file_storage_dir: str = "./storage/uploads"  # 上传文件落地的物理目录
    file_base_url: str = "/files"  # 文件访问 URL 前缀

    # ===== 缓存后端 =====
    cache_backend: str = "memory"  # memory / redis，目前默认内存

    # ===== CORS 跨域允许的前端来源 =====
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:3000",
    ]


@lru_cache
def get_settings() -> Settings:
    """获取全局配置单例。

    使用 lru_cache 确保整个进程只读取一次环境变量，
    避免重复实例化带来的开销与配置漂移。

    Returns:
        Settings: 全局配置实例。
    """
    return Settings()


# 模块级单例，供其他模块直接 `from app.config.settings import settings` 使用
settings = get_settings()