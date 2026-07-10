import os

path = os.path.join(os.path.dirname(__file__), '..', 'ai-service', 'app', 'infrastructure', 'llm_client.py')
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

# Find second occurrence of 'class LLMClient'
idx1 = text.index('class LLMClient')
idx2 = text.index('class LLMClient', idx1 + 1)

# Find the docstring that precedes the second class
# Look backwards from idx2 for the triple-quote that starts the docstring
pre = text[:idx2]
doc_start = pre.rfind('"""')
# The docstring content is the file header that was duplicated
# So the second block starts at doc_start
new_content = text[doc_start:]
print(f"Keeping content from offset {doc_start}")
print(f"First 200 chars: {new_content[:200]}")

with open(path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f"Done. New file size: {len(new_content)} bytes")
