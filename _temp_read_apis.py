import ast, os

root = r"C:\Users\Administrator\Desktop\Zhihire-StarMap\backend\app\api\v1"
files_to_check = ["auth.py", "ping.py", "user.py", "job.py", "resume.py", "match.py", "interview.py", "graph.py", "career.py", "company.py", "skill.py", "parse.py"]

for fname in files_to_check:
    fpath = os.path.join(root, fname)
    if not os.path.exists(fpath):
        continue
    print(f"\n=== {fname} ===")
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()
    tree = ast.parse(content)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            for decorator in node.decorator_list:
                if isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Attribute):
                    if decorator.func.attr in ("get", "post", "put", "delete", "patch"):
                        method = decorator.func.attr.upper()
                        path_info = ""
                        for arg in decorator.args:
                            if isinstance(arg, ast.Constant):
                                path_info = arg.value
                        summary = ast.get_docstring(node)
                        summary_short = summary.split("\n")[0][:60] if summary else ""
                        print(f"  {method} {path_info:<35} {node.name:<25} {summary_short}")
