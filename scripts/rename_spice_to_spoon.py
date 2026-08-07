import re
import os

replacements = {
    "pages/index.md": [
        (r"- 밋밋한 결과물에 프롬프트 조미료를 쳐서 품질 높이기", r"- 밋밋한 결과물에 프롬프트 한 스푼을 더해 품질 높이기"),
        (r"\[프롬프트 조미료\]", r"[프롬프트 한 스푼]"),
    ],
    "pages/sections/prompt-snippets.md": [
        (r"title: 프롬프트 조미료", r"title: 프롬프트 한 스푼"),
        (r"# 프롬프트 조미료", r"# 프롬프트 한 스푼"),
        (r"프롬프트 조미료는", r"프롬프트 한 스푼은"),
        (r"'사실 확인용 프롬프트\(조미료\)'를", r"'사실 확인용 프롬프트(한 스푼)'를")
    ],
    "pages/sections/prompt-snippets/summarize-core.md": [
        (r"한 줄 조미료로", r"프롬프트 한 스푼으로")
    ],
    "pages/sections/prompt-snippets/reduce-hallucination.md": [
        (r"이 조미료가 필요합니다.", r"이 프롬프트 한 스푼이 필요합니다.")
    ],
    "pages/sections/prompt-snippets/improve-results.md": [
        (r"\*\*⭐ 가장 많이 사용하는 프롬프트 \(조미료\)\*\*", r"**⭐ 가장 많이 사용하는 프롬프트 (한 스푼)**"),
        (r"이 조미료들을 번갈아 사용하며", r"이 한 스푼들을 번갈아 사용하며")
    ],
    "pages/sections/prompt-snippets/ask-better.md": [
        (r"마법의 조미료입니다.", r"마법의 한 스푼입니다.")
    ],
    "pages/sections/prompt-snippets/compare-analyze.md": [
        (r"조미료를 연달아 사용하면", r"프롬프트를 연달아 사용하면")  # '한 스푼' instead of 조미료 here
    ],
    "data/page-registry.json": [
        (r'\"title\": \"프롬프트 조미료\"', r'"title": "프롬프트 한 스푼"')
    ],
    "data/navigation.json": [
        (r'\"label\": \"프롬프트 조미료\"', r'"label": "프롬프트 한 스푼"')
    ]
}

# Apply compare-analyze.md specific fix
replacements["pages/sections/prompt-snippets/compare-analyze.md"] = [
    (r"조미료를 연달아 사용하면", r"한 스푼을 연달아 더하면")
]

for filepath, pairs in replacements.items():
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        for old, new in pairs:
            content = re.sub(old, new, content)
            
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated {filepath}")
    else:
        print(f"File not found: {filepath}")

