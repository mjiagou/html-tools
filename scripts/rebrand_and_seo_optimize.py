#!/usr/bin/env python3
"""
SEO Overhaul & Rebranding Script for 微工坊 TinyTools (html.tpsh.cc)
"""

import os
import json
import re
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
TOOLS_DIR = BASE_DIR / 'tools'
INDEX_JSON_PATH = BASE_DIR / 'index.json'

BRAND_NAME = "微工坊 TinyTools"
BRAND_SHORT = "微工坊"
BRAND_URL = "https://html.tpsh.cc/"

# 1. Update index.json
with open(INDEX_JSON_PATH, 'r', encoding='utf-8') as f:
    index_data = json.load(f)

tool_map = {}
category_tag_defaults = {
    "converter": ["在线转换", "格式转换", "纯前端免安装"],
    "developer": ["开发者工具", "编程辅助", "纯前端免安装"],
    "text": ["文本处理", "在线排版", "纯前端免安装"],
    "image": ["图片处理", "图像工具", "纯前端免安装"],
    "utility": ["日常实用", "便民工具", "纯前端免安装"]
}

for tool in index_data.get('tools', []):
    tool_id = tool.get('id', '')
    tool_map[tool_id] = tool
    
    # Author & Repo
    tool['author'] = BRAND_NAME
    tool['authorUrl'] = BRAND_URL
    tool['repo'] = BRAND_URL
    
    # Text replacements in descriptions
    if 'JustHTMLs' in tool.get('description', ''):
        tool['description'] = tool['description'].replace('JustHTMLs', BRAND_SHORT)
    if 'JustHTMLs' in tool.get('longDescription', ''):
        tool['longDescription'] = tool['longDescription'].replace('JustHTMLs', BRAND_SHORT)
        
    # Enrich tags for SEO
    category = tool.get('category', 'utility')
    extra_tags = category_tag_defaults.get(category, ["纯前端免安装"])
    existing_tags = tool.get('tags', [])
    for t in extra_tags:
        if t not in existing_tags:
            existing_tags.append(t)
    tool['tags'] = existing_tags

with open(INDEX_JSON_PATH, 'w', encoding='utf-8') as f:
    json.dump(index_data, f, ensure_ascii=False, indent=2)

print(f"Updated index.json for {len(index_data.get('tools', []))} tools.")

# 2. Update tools/*/index.html and tools/*/app.html
updated_index_count = 0
updated_app_count = 0

for tool_folder in TOOLS_DIR.iterdir():
    if not tool_folder.is_dir():
        continue
    
    slug = tool_folder.name
    tool_info = tool_map.get(slug, {})
    tool_name = tool_info.get('name', slug)
    tool_desc = tool_info.get('description', f'{tool_name} 在线工具')
    tool_tags = ", ".join(tool_info.get('tags', [tool_name, "在线工具", "微工坊"]))
    
    # Update index.html
    index_file = tool_folder / 'index.html'
    if index_file.exists():
        content = index_file.read_text(encoding='utf-8')
        orig_content = content
        
        # 1. Update title
        content = re.sub(
            r'<title>(.*?)(?: - JustHTMLs)?</title>',
            rf'<title>\1 - {BRAND_NAME} | 纯前端在线工具</title>',
            content,
            count=1
        )
        
        # 2. Add or update meta description & keywords if missing
        if '<meta name="description"' not in content:
            meta_seo = (
                f'\n    <meta name="description" content="{tool_desc}。微工坊提供纯前端本地安全运算，无需安装，打开即用。">\n'
                f'    <meta name="keywords" content="{tool_tags}, 微工坊, TinyTools">\n'
            )
            content = re.sub(r'(<title>.*?</title>)', rf'\1{meta_seo}', content, count=1)
            
        # 3. Replace author / brand spans
        content = re.sub(r'<span>JustHTMLs</span>', rf'<span>{BRAND_NAME}</span>', content)
        
        # 4. Replace footer copyright
        content = re.sub(
            r'<p>&copy;\s*\d+\s*JustHTMLs.*?</p>',
            rf'<p>&copy; 2026 {BRAND_NAME} (html.tpsh.cc) · 纯前端轻量工具平台</p>',
            content
        )
        
        # 5. Clean external links
        content = content.replace('https://github.com/justhtmls/html-tools', BRAND_URL)
        content = content.replace('https://github.com/justhtmls', BRAND_URL)
        content = content.replace('JustHTMLs', BRAND_NAME)
        
        if content != orig_content:
            index_file.write_text(content, encoding='utf-8')
            updated_index_count += 1

    # Update app.html
    app_file = tool_folder / 'app.html'
    if app_file.exists():
        content = app_file.read_text(encoding='utf-8')
        orig_content = content
        
        # 1. Update title if needed
        content = re.sub(
            r'<title>(.*?)(?: - JustHTMLs)?</title>',
            rf'<title>\1 - {BRAND_NAME}</title>',
            content,
            count=1
        )
        
        # 2. Update return button text
        content = re.sub(
            r'<span>←</span>\s*返回\s*JustHTMLs',
            r'<span>←</span> 返回首页',
            content
        )
        content = content.replace('返回 JustHTMLs', '返回首页')
        
        # 3. Replace sample placeholder 'JustHTMLs'
        content = content.replace('"name": "JustHTMLs"', '"name": "TinyTools"')
        content = content.replace('name: JustHTMLs', 'name: TinyTools')
        content = content.replace('https://github.com/justhtmls/html-tools', BRAND_URL)
        content = content.replace('https://github.com/justhtmls', BRAND_URL)
        
        if content != orig_content:
            app_file.write_text(content, encoding='utf-8')
            updated_app_count += 1

print(f"Updated {updated_index_count} tool index.html files.")
print(f"Updated {updated_app_count} tool app.html files.")
