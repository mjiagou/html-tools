#!/usr/bin/env python3
"""
scripts/fix_seo_issues.py
批量修复微工坊全站 SEO 问题：
1. 修复 tools/*/index.html 中的 72 处 404 死链（原 github tree/main 替换为站内导流）
2. 消除 tools/*/index.html (指南意图) 与 tools/*/app.html (工具意图) 的关键词自相蚕食（Cannibalization）
3. 补齐所有 tools/*/app.html 缺失的 description、keywords、OpenGraph、TwitterCard
4. 注入 Schema.org WebApplication 与 TechArticle 结构化数据
5. 补齐缺少 clicks.js 统计代码的页面
6. 为 index.html 补充 <noscript> 语义化静态工具索引，解决爬虫冷启动渲染问题
"""

import os
import json
import re
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
BASE_URL = "https://html.tpsh.cc"

def load_data():
    with open(BASE_DIR / 'index.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    tools = data.get('tools', [])
    categories = {c['id']: c['name'] for c in data.get('categories', [])}
    return tools, categories

def clean_html(text):
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')

def fix_tool_index(tool):
    slug = tool['slug']
    file_path = BASE_DIR / 'tools' / slug / 'index.html'
    if not file_path.exists():
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. 修复 72 处 tree/main 死链
    pattern_icon = re.compile(
        r'<a\s+href="https://html\.tpsh\.cc//tree/main/tools/[^"]*"\s+target="_blank"\s+class="btn btn-secondary">\s*<i class="fab fa-github"></i>\s*查看源码\s*</a>',
        re.DOTALL
    )
    content = pattern_icon.sub(
        '<a href="../../" class="btn btn-secondary">\n                <i class="fas fa-th-large"></i>\n                更多工具\n            </a>',
        content
    )
    
    pattern_btn = re.compile(
        r'<a\s+href="https://html\.tpsh\.cc//tree/main/tools/[^"]*"\s+target="_blank"\s+class="btn btn-secondary">查看源码</a>'
    )
    content = pattern_btn.sub(
        '<a href="app.html" target="_blank" class="btn btn-secondary">全屏打开</a>',
        content
    )
    
    pattern_sec = re.compile(
        r'<a\s+href="https://html\.tpsh\.cc//tree/main/tools/[^"]*"\s+target="_blank"\s+class="btn secondary">查看源码</a>'
    )
    content = pattern_sec.sub(
        '<a href="app.html" target="_blank" class="btn secondary">全屏打开</a>',
        content
    )
    
    # 2. 优化 Title (指南使用意图)
    new_title = f"{tool['name']} 功能说明与使用指南 - 微工坊 TinyTools"
    content = re.sub(r'<title>.*?</title>', f'<title>{clean_html(new_title)}</title>', content, count=1, flags=re.DOTALL)
    
    # 3. 优化 Meta Description & Keywords
    tags_str = ", ".join(tool.get('tags', []))
    desc_text = f"{tool['name']} 在线功能介绍与使用说明。{tool['description']}。微工坊提供纯前端本地安全运算，隐私零上传，即开即用。"
    kw_text = f"{tags_str}, 使用指南, 教程, 微工坊, TinyTools"
    
    meta_desc_tag = f'<meta name="description" content="{clean_html(desc_text)}">'
    meta_kw_tag = f'<meta name="keywords" content="{clean_html(kw_text)}">'
    
    if re.search(r'<meta\s+name=[\'"]description[\'"]', content):
        content = re.sub(r'<meta\s+name=[\'"]description[\'"][^>]*>', meta_desc_tag, content, count=1)
    else:
        content = re.sub(r'(<title>.*?</title>)', rf'\1\n    {meta_desc_tag}', content, count=1)
        
    if re.search(r'<meta\s+name=[\'"]keywords[\'"]', content):
        content = re.sub(r'<meta\s+name=[\'"]keywords[\'"][^>]*>', meta_kw_tag, content, count=1)
    else:
        content = re.sub(r'(<meta\s+name=[\'"]description[\'"][^>]*>)', rf'\1\n    {meta_kw_tag}', content, count=1)
    
    # 4. OpenGraph 与 Twitter Cards
    og_block = f"""    <!-- Open Graph / Facebook -->
    <meta property="og:type" content="article">
    <meta property="og:url" content="https://html.tpsh.cc/tools/{slug}/">
    <meta property="og:site_name" content="微工坊 TinyTools">
    <meta property="og:title" content="{clean_html(new_title)}">
    <meta property="og:description" content="{clean_html(desc_text)}">
    <meta property="og:image" content="https://html.tpsh.cc/favicon.svg">
    
    <!-- Twitter -->
    <meta property="twitter:card" content="summary">
    <meta property="twitter:url" content="https://html.tpsh.cc/tools/{slug}/">
    <meta property="twitter:title" content="{clean_html(new_title)}">
    <meta property="twitter:description" content="{clean_html(desc_text)}">
    <meta property="twitter:image" content="https://html.tpsh.cc/favicon.svg">"""

    if 'og:title' not in content:
        if '<link rel="canonical"' in content:
            content = re.sub(r'(<link\s+rel=[\'"]canonical[\'"][^>]*>)', rf'\1\n\n{og_block}', content, count=1)
        else:
            content = re.sub(r'(</head>)', rf'{og_block}\n\1', content, count=1)

    # 5. Schema.org TechArticle JSON-LD
    schema_ld = {
        "@context": "https://schema.org",
        "@type": "TechArticle",
        "headline": f"{tool['name']} 功能说明与使用指南",
        "description": tool['description'],
        "url": f"https://html.tpsh.cc/tools/{slug}/",
        "inLanguage": "zh-CN",
        "author": {
            "@type": "Organization",
            "name": "微工坊 TinyTools",
            "url": "https://html.tpsh.cc/"
        },
        "datePublished": tool.get('createdAt', '2025-12-22'),
        "dateModified": tool.get('updatedAt', '2025-12-22')
    }
    schema_str = f"""    <!-- Structured Data (JSON-LD) -->
    <script type="application/ld+json">
{json.dumps(schema_ld, ensure_ascii=False, indent=4)}
    </script>"""

    if 'application/ld+json' not in content:
        content = re.sub(r'(</head>)', rf'{schema_str}\n\1', content, count=1)

    # 6. clicks.js 引入检查
    if 'clicks.js' not in content:
        content = re.sub(r'(</body>)', r'    <script src="../../assets/clicks.js"></script>\n\1', content, count=1)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    return True

def fix_tool_app(tool):
    slug = tool['slug']
    file_path = BASE_DIR / 'tools' / slug / 'app.html'
    if not file_path.exists():
        return False
        
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. 优化 Title (在线工具使用意图)
    new_title = f"{tool['name']} 在线工具 - 微工坊 TinyTools | 纯前端免安装"
    content = re.sub(r'<title>.*?</title>', f'<title>{clean_html(new_title)}</title>', content, count=1, flags=re.DOTALL)
    
    # 2. 补齐 Meta Description & Keywords
    tags_str = ", ".join(tool.get('tags', []))
    desc_text = f"{tool['description']}。微工坊纯前端工具，浏览器本地安全计算，数据隐私零上传，即开即用。"
    kw_text = f"{tags_str}, 在线工具, 免安装, 微工坊, TinyTools"
    
    meta_desc_tag = f'<meta name="description" content="{clean_html(desc_text)}">'
    meta_kw_tag = f'<meta name="keywords" content="{clean_html(kw_text)}">'
    
    if re.search(r'<meta\s+name=[\'"]description[\'"]', content):
        content = re.sub(r'<meta\s+name=[\'"]description[\'"][^>]*>', meta_desc_tag, content, count=1)
    else:
        content = re.sub(r'(<title>.*?</title>)', rf'\1\n    {meta_desc_tag}', content, count=1)
        
    if re.search(r'<meta\s+name=[\'"]keywords[\'"]', content):
        content = re.sub(r'<meta\s+name=[\'"]keywords[\'"][^>]*>', meta_kw_tag, content, count=1)
    else:
        content = re.sub(r'(<meta\s+name=[\'"]description[\'"][^>]*>)', rf'\1\n    {meta_kw_tag}', content, count=1)

    # 3. OpenGraph 与 Twitter Cards
    og_block = f"""    <!-- Open Graph / Facebook -->
    <meta property="og:type" content="website">
    <meta property="og:url" content="https://html.tpsh.cc/tools/{slug}/app.html">
    <meta property="og:site_name" content="微工坊 TinyTools">
    <meta property="og:title" content="{clean_html(new_title)}">
    <meta property="og:description" content="{clean_html(desc_text)}">
    <meta property="og:image" content="https://html.tpsh.cc/favicon.svg">
    
    <!-- Twitter -->
    <meta property="twitter:card" content="summary">
    <meta property="twitter:url" content="https://html.tpsh.cc/tools/{slug}/app.html">
    <meta property="twitter:title" content="{clean_html(new_title)}">
    <meta property="twitter:description" content="{clean_html(desc_text)}">
    <meta property="twitter:image" content="https://html.tpsh.cc/favicon.svg">"""

    if 'og:title' not in content:
        if '<link rel="canonical"' in content:
            content = re.sub(r'(<link\s+rel=[\'"]canonical[\'"][^>]*>)', rf'\1\n\n{og_block}', content, count=1)
        else:
            content = re.sub(r'(</head>)', rf'{og_block}\n\1', content, count=1)

    # 4. Schema.org WebApplication JSON-LD
    schema_ld = {
        "@context": "https://schema.org",
        "@type": "WebApplication",
        "name": tool['name'],
        "url": f"https://html.tpsh.cc/tools/{slug}/app.html",
        "description": tool['description'],
        "applicationCategory": "UtilitiesApplication",
        "operatingSystem": "All",
        "browserRequirements": "Requires JavaScript. Requires HTML5.",
        "offers": {
            "@type": "Offer",
            "price": "0",
            "priceCurrency": "CNY"
        }
    }
    schema_str = f"""    <!-- Structured Data (JSON-LD) -->
    <script type="application/ld+json">
{json.dumps(schema_ld, ensure_ascii=False, indent=4)}
    </script>"""

    if 'application/ld+json' not in content:
        content = re.sub(r'(</head>)', rf'{schema_str}\n\1', content, count=1)

    # 5. clicks.js 引入检查
    if 'clicks.js' not in content:
        if '</body>' in content:
            content = re.sub(r'(</body>)', r'    <script src="../../assets/clicks.js"></script>\n\1', content, count=1)
        else:
            content += '\n<script src="../../assets/clicks.js"></script>'

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    return True

def update_homepage_noscript(tools, categories):
    index_file = BASE_DIR / 'index.html'
    with open(index_file, 'r', encoding='utf-8') as f:
        content = f.read()

    cat_tools = {}
    for t in tools:
        cat = t.get('category', 'other')
        cat_tools.setdefault(cat, []).append(t)

    noscript_html = ['<noscript>', '    <div class="static-tools-sitemap" style="padding: 20px 0;">']
    noscript_html.append('        <h2>全部工具静态导航目录（支持无脚本环境与搜索引擎收录）</h2>')
    for cat_id, cat_name in categories.items():
        t_list = cat_tools.get(cat_id, [])
        if not t_list:
            continue
        noscript_html.append(f'        <div style="margin: 20px 0;">')
        noscript_html.append(f'            <h3>{cat_name}</h3>')
        noscript_html.append('            <ul style="display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 10px; list-style: none; padding: 0;">')
        for t in t_list:
            slug = t['slug']
            name = t['name']
            desc = t['description']
            noscript_html.append(
                f'                <li style="background: rgba(255,255,255,0.05); padding: 12px; border-radius: 8px;">'
                f'<a href="tools/{slug}/app.html" style="font-weight: 600; color: #6366f1; text-decoration: none;">{name}</a> - '
                f'<span style="font-size: 13px; color: #94a3b8;">{desc}</span> '
                f'(<a href="tools/{slug}/" style="color: #8b5cf6; font-size: 12px;">使用说明</a>)</li>'
            )
        noscript_html.append('            </ul>')
        noscript_html.append('        </div>')
    noscript_html.append('    </div>')
    noscript_html.append('</noscript>')
    
    noscript_block = '\n'.join(noscript_html)

    if '<noscript>' in content and 'static-tools-sitemap' in content:
        content = re.sub(r'<noscript>.*?static-tools-sitemap.*?</noscript>', noscript_block, content, flags=re.DOTALL)
    else:
        target = '<div class="tools-grid" id="tools-grid">'
        content = content.replace(target, f'{noscript_block}\n                {target}', 1)

    with open(index_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print("✓ 主页 index.html 成功注入 <noscript> 语义化静态工具全量目录")

def main():
    tools, categories = load_data()
    print(f"正在优化 {len(tools)} 个工具的 SEO 配置...")
    
    idx_fixed = 0
    app_fixed = 0
    for t in tools:
        if fix_tool_index(t):
            idx_fixed += 1
        if fix_tool_app(t):
            app_fixed += 1
            
    print(f"✓ 已处理工具详情页 (index.html): {idx_fixed} 个")
    print(f"✓ 已处理工具应用页 (app.html): {app_fixed} 个")
    
    update_homepage_noscript(tools, categories)
    print("SEO 批量优化完成！")

if __name__ == '__main__':
    main()
