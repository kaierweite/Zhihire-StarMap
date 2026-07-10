import re
path = r"C:\Users\Administrator\Desktop\Zhihire-StarMap\backend\app\db\session.py"
content = open(path, "r", encoding="utf-8").read()

old = """async def get_db() -> AsyncGenerator[AsyncSession, None]:
    \"\"\"\u83b7\u53d6\u6570\u636e\u5e93\u4f1a\u8bdd\u7684 FastAPI \u4f9d\u8d56\u3002

    \u4ee5\u751f\u6210\u5668\u5f62\u5f0f\u63d0\u4f9b\uff0c\u786e\u4fdd\u8bf7\u6c42\u7ed3\u675f\u540e\u4f1a\u8bdd\u88ab\u6b63\u786e\u5173\u95ed\uff0c
    \u5373\u4f7f\u4e2d\u9014\u629b\u51fa\u5f02\u5e38\u4e5f\u80fd\u8fdb\u5165 finally \u91ca\u653e\u8fde\u63a5\u3002

    Yields:
        AsyncSession: \u5f53\u524d\u8bf7\u6c42\u8303\u56f4\u5185\u7684\u5f02\u6b65\u6570\u636e\u5e93\u4f1a\u8bdd\u3002
    \"\"\"
    # \u4e3a\u6bcf\u4e2a\u8bf7\u6c42\u521b\u5efa\u72ec\u7acb\u4f1a\u8bdd
    async with AsyncSessionLocal() as session:
        # \u4ea4\u51fa\u4f1a\u8bdd\u4f9b\u8def\u7531\u4f7f\u7528
        yield session
        # \u4f5c\u7528\u57df\u7ed3\u675f\u65f6\u81ea\u52a8\u5173\u95ed\u5e76\u5f52\u8fd8\u8fde\u63a5"""

new = """async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()"""

if old in content:
    content = content.replace(old, new)
    open(path, "w", encoding="utf-8").write(content)
    print("SUCCESS: get_db() fixed")
else:
    print("FAIL: Could not find the old get_db() code")
    # Print a snippet of what we're looking for
    idx = content.find("async def get_db()")
    if idx >= 0:
        print(f"Found at position {idx}")
        print(content[idx:idx+600])
