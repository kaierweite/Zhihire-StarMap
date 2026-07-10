# -*- coding: utf-8 -*-
import os

path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'ai-service', 'main.py')

with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Add import after resume_optimize import
old_import = "from app.api.resume_optimize import router as resume_opt_router"
new_import = (
    "from app.api.resume_optimize import router as resume_opt_router\n"
    "from app.api.admin_config import router as admin_config_router\n"
    "from app.api.admin_config import _load_configs_into_runtime"
)
text = text.replace(old_import, new_import)

# 2. Add config loading after graph rebuild
old_graph = (
    '        logger.info(\n'
    '            f"\\u56fe\\u8c31\\u5df2\\u91cd\\u5efa: {skill_graph.get_node_count()} \\u8282\\u70b9, "\n'
    '            f"{skill_graph.get_edge_count()} \\u6761\\u8fb9"\n'
    '        )\n'
    '    except Exception as e:\n'
    '        logger.warning(f"\\u6570\\u636e\\u5e93\\u4e0d\\u53ef\\u7528\\uff0c\\u56fe\\u8c31\\u4e3a\\u7a7a: {e}")'
)
new_graph = (
    '        logger.info(\n'
    '            f"\\u56fe\\u8c31\\u5df2\\u91cd\\u5efa: {skill_graph.get_node_count()} \\u8282\\u70b9, "\n'
    '            f"{skill_graph.get_edge_count()} \\u6761\\u8fb9"\n'
    '        )\n'
    '\n'
    '        # Load AI model configs from DB into llm_client runtime\n'
    '        try:\n'
    '            count = await _load_configs_into_runtime()\n'
    '            logger.info(f"AI provider configs loaded from DB: {count}")\n'
    '        except Exception as e:\n'
    '            logger.warning(f"AI config load failed (non-fatal): {e}")\n'
    '    except Exception as e:\n'
    '        logger.warning(f"\\u6570\\u636e\\u5e93\\u4e0d\\u53ef\\u7528\\uff0c\\u56fe\\u8c31\\u4e3a\\u7a7a: {e}")'
)
text = text.replace(old_graph, new_graph)

# 3. Add admin_config router
old_router = "app.include_router(resume_opt_router)"
new_router = "app.include_router(resume_opt_router)\napp.include_router(admin_config_router)"
text = text.replace(old_router, new_router)

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)

print(f"main.py patched, {os.path.getsize(path)} bytes")
