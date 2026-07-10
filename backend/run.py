"""本地开发启动脚本。

Windows + psycopg 异步驱动必须使用 SelectorEventLoop，而 uvicorn 通过
`asyncio.run()` 创建事件循环的时机早于 `app.main` 模块导入——因此直接使用
`python -m uvicorn app.main:app` 时，`app.main` 顶部设置的事件循环策略为时已晚，
psycopg 会在 ProactorEventLoop 下报错无法连接数据库。

本脚本在调用 `uvicorn.run` 之前就设置 `WindowsSelectorEventLoopPolicy`，
从而保证 uvicorn 创建的事件循环即 SelectorEventLoop。

请使用：
    python run.py
而不要直接使用 `python -m uvicorn app.main:app`（在 Windows + psycopg 下会因
事件循环策略问题导致数据库接口报 500）。

注意：reload 模式会派生全新解释器子进程，无法继承此处设置的事件循环策略，
因此在 Windows + psycopg 环境下默认关闭 reload。如需热重载，可在类 Unix
环境或重启脚本中自行启用。
"""
import asyncio  # 事件循环策略
import os  # 环境变量读取
import sys  # 平台检测

# Windows + psycopg async 必须使用 SelectorEventLoop
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import uvicorn  # noqa: E402  ASGI 服务器


def main() -> None:
    """启动 uvicorn 服务。"""
    # 从环境变量读取主机/端口，便于灵活部署，默认本机 8000
    host = os.getenv("APP_HOST", "127.0.0.1")  # 监听地址
    port = int(os.getenv("APP_PORT", "8000"))  # 监听端口
    # reload：默认关闭（见模块 docstring 说明）。可通过 env APP_RELOAD=1 开启。
    reload = os.getenv("APP_RELOAD", "0") == "1"  # 是否热重载
    # 启动 uvicorn，加载 app.main:app
    uvicorn.run(
        "app.main:app",  # ASGI 应用定位
        host=host,  # 监听地址
        port=port,  # 监听端口
        reload=reload,  # 热重载开关
    )


if __name__ == "__main__":
    main()
