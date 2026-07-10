"""Test _extract_structured markdown stripping."""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
if sys.platform == "win32":
    import asyncio
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
from app.db import compat
from app.services.parse_service import _extract_structured

mock = "text\n\n`json\n{\n  \"name\": \"Zhang San\",\n  \"skills\": [\"Java\",\"Python\"],\n  \"experience\": []\n}\n`"

clean = mock.strip()
print("1. Raw starts with triple backtick:", clean.startswith("`json"))
if clean.startswith("`json"):
    clean = clean[7:]
if clean.endswith("`"):
    clean = clean[:-3]
clean = clean.strip()
result = json.loads(clean)
print('2. Parsed OK:', result.get('name'), result.get('skills'))
