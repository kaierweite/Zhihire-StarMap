"""数据库连接测试脚本。"""
import asyncio
import sys
sys.path.insert(0, r"C:\Users\Administrator\Desktop\Zhihire-StarMap\backend")

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def test_connection():
    """测试数据库连接。"""
    DATABASE_URL = "postgresql+asyncpg://system:123456@localhost:54321/zhihire"
    print(f"正在连接数据库...")
    print(f"URL: {DATABASE_URL}")
    
    try:
        engine = create_async_engine(DATABASE_URL, echo=False)
        
        async with engine.connect() as conn:
            # 执行 SELECT 1 测试连接
            result = await conn.execute(text("SELECT 1"))
            print(f"✅ 连接成功! SELECT 1 返回: {result.scalar()}")
            
            # 列出所有表
            result = await conn.execute(text(
                "SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename"
            ))
            tables = [row[0] for row in result]
            print(f"\n📊 已创建的表 ({len(tables)} 张):")
            for i, table in enumerate(tables, 1):
                print(f"  {i}. {table}")
            
            await conn.commit()
        
        await engine.dispose()
        print(f"\n✅ 测试完成，所有检查通过!")
        return True
        
    except Exception as e:
        print(f"\n❌ 连接失败: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_connection())
    sys.exit(0 if success else 1)
