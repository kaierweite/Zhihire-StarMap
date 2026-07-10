"""
配置管理 — 从环境变量 / .env 加载配置
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置，优先读取环境变量，其次 .env 文件"""

    # DeepSeek LLM 配置
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com/v1"
    deepseek_model: str = "deepseek-chat"

    # 数据库配置（KingbaseES / PostgreSQL 兼容）
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "zhihire"
    db_user: str = "postgres"
    db_password: str = "postgres"

    # 服务配置
    ai_service_port: int = 8000
    ai_service_host: str = "0.0.0.0"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


# 全局单例
settings = Settings()
