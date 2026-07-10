"""Test DeepSeek API real call."""
import sys, os, json, asyncio
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from app.infrastructure.llm.deepseek_client import deepseek_client
from app.services.parse_service import _extract_structured
from app.db.session import AsyncSessionLocal


async def test():
    print("=== Test 1: Direct DeepSeek chat ===")
    print(f"has_key: {deepseek_client.has_key}")
    print(f"model: {deepseek_client.chat_model}")
    
    try:
        resp = await deepseek_client.chat(
            [{"role": "user", "content": 'Return ONLY valid JSON: {"name": "test"}. No other text.'}],
            temperature=0.1, max_tokens=200
        )
        print(f"Response ({len(resp)} chars):")
        print(resp[:300])
        print("---")
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}")

    print()
    print("=== Test 2: _extract_structured (resume-like text) ===")
    async with AsyncSessionLocal() as db:
        text = "Name: Zhang San\\nEmail: test@test.com\\nEducation: Bachelor\\nSkills: Java, Python, MySQL, Docker, Redis"
        result = await _extract_structured(db, text, [])
        print(f"Keys: {list(result.keys())}")
        if "raw_response" in result:
            print(f"RAW (stripped): {result['raw_response'][:200]}")
        else:
            print(f"name={result.get('name')}")
            print(f"education={result.get('education')}")
            print(f"skills={result.get('skills')}")
            print(f"experience={len(result.get('experience', []))}")


asyncio.run(test())
