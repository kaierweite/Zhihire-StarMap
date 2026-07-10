import sys, subprocess, json

# Get list of all tracked .vue files in the user views
result = subprocess.run(["git", "ls-files", "frontend/src/views/user/"], capture_output=True, text=True)
vue_files = [f for f in result.stdout.strip().split("\n") if f.endswith(".vue") and "Layout" not in f and "Section" not in f and "Phone" not in f and "Video" not in f]
print(vue_files)
