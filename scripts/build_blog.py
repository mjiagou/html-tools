#!/usr/bin/env python3
"""
Blog Builder for 微工坊 TinyTools (html.tpsh.cc)
Transforms markdown posts in blog/posts/*.md into pre-rendered, SEO-optimized HTML pages,
generates the blog index page blog/index.html, and automatically syncs with sitemap.xml.
Zero third-party dependencies required.
"""

import os
import re
import json
import html
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent.parent
BLOG_DIR = BASE_DIR / 'blog'
POSTS_DIR = BLOG_DIR / 'posts'
INDEX_JSON_PATH = BASE_DIR / 'index.json'
SITE_URL = "https://html.tpsh.cc"
BRAND_NAME = "微工坊 TinyTools"


def parse_frontmatter(md_text):
    """Extract YAML-like frontmatter and body from Markdown text."""
    meta = {}
    body = md_text
    
    if md_text.startswith('---'):
        parts = md_text.split('---', 2)
        if len(parts) >= 3:
            fm_text = parts[1]
            body = parts[2].strip()
            
            current_list_key = None
            for line in fm_text.strip().splitlines():
                line_str = line.strip()
                if not line_str or line_str.startswith('#'):
                    continue
                
                # Check list item
                if line_str.startswith('- ') and current_list_key:
                    item_val = line_str[2:].strip().strip('"\'')
                    meta[current_list_key].append(item_val)
                    continue
                
                if ':' in line:
                    key, val = line.split(':', 1)
                    key = key.strip()
                    val = val.strip().strip('"\'')
                    if not val:
                        meta[key] = []
                        current_list_key = key
                    else:
                        current_list_key = None
                        if val.startswith('[') and val.endswith(']'):
                            # Simple inline list like ["tag1", "tag2"]
                            raw_items = val[1:-1].split(',')
                            meta[key] = [it.strip().strip('"\'') for it in raw_items if it.strip()]
                        else:
                            meta[key] = val
    return meta, body


def markdown_to_html(md_text):
    """
    Lightweight zero-dependency Markdown to HTML converter.
    Supports code blocks, tables, blockquotes, headers, lists, links, bold, italic.
    """
    lines = md_text.splitlines()
    html_lines = []
    in_code_block = False
    code_lang = ""
    code_buffer = []
    in_ul = False
    in_ol = False
    in_table = False
    table_header = True

    def inline_formatting(text):
        # Escape HTML entities in text outside tags
        text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        
        # Inline code
        text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
        # Bold
        text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
        # Italic
        text = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', text)
        # Images
        text = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', r'<img src="\2" alt="\1" class="article-img">', text)
        # Links
        text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" target="_blank" rel="noopener">\1</a>', text)
        return text

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Code block toggle
        if stripped.startswith('```'):
            if in_code_block:
                escaped_code = html.escape("\n".join(code_buffer))
                html_lines.append(f'<div class="code-block-wrapper"><pre><code class="language-{code_lang}">{escaped_code}</code></pre></div>')
                in_code_block = False
                code_buffer = []
                code_lang = ""
            else:
                if in_ul: html_lines.append('</ul>'); in_ul = False
                if in_ol: html_lines.append('</ol>'); in_ol = False
                if in_table: html_lines.append('</tbody></table></div>'); in_table = False
                in_code_block = True
                code_lang = stripped[3:].strip()
            i += 1
            continue

        if in_code_block:
            code_buffer.append(line)
            i += 1
            continue

        # Blank line resets lists and tables
        if not stripped:
            if in_ul: html_lines.append('</ul>'); in_ul = False
            if in_ol: html_lines.append('</ol>'); in_ol = False
            if in_table: html_lines.append('</tbody></table></div>'); in_table = False
            i += 1
            continue

        # Tables (e.g. | th1 | th2 |)
        if stripped.startswith('|') and stripped.endswith('|'):
            cells = [c.strip() for c in stripped.strip('|').split('|')]
            if not in_table:
                if in_ul: html_lines.append('</ul>'); in_ul = False
                if in_ol: html_lines.append('</ol>'); in_ol = False
                html_lines.append('<div class="table-responsive"><table class="article-table">')
                html_lines.append('<thead><tr>' + ''.join(f'<th>{inline_formatting(c)}</th>' for c in cells) + '</tr></thead><tbody>')
                in_table = True
                table_header = True
            elif table_header:
                # Check if it's separator row like | --- | --- |
                if all(re.match(r'^:?-+:?$', c) for c in cells):
                    table_header = False
                else:
                    html_lines.append('<tr>' + ''.join(f'<td>{inline_formatting(c)}</td>' for c in cells) + '</tr>')
            else:
                html_lines.append('<tr>' + ''.join(f'<td>{inline_formatting(c)}</td>' for c in cells) + '</tr>')
            i += 1
            continue
        elif in_table:
            html_lines.append('</tbody></table></div>')
            in_table = False

        # Blockquote
        if stripped.startswith('> '):
            if in_ul: html_lines.append('</ul>'); in_ul = False
            if in_ol: html_lines.append('</ol>'); in_ol = False
            quote_content = inline_formatting(stripped[2:])
            html_lines.append(f'<blockquote class="article-quote"><p>{quote_content}</p></blockquote>')
            i += 1
            continue

        # Headings
        header_match = re.match(r'^(#{1,6})\s+(.*)$', stripped)
        if header_match:
            if in_ul: html_lines.append('</ul>'); in_ul = False
            if in_ol: html_lines.append('</ol>'); in_ol = False
            level = len(header_match.group(1))
            heading_text = header_match.group(2).strip()
            anchor_id = re.sub(r'[^\w\u4e00-\u9fa5]+', '-', heading_text.lower()).strip('-')
            html_lines.append(f'<h{level} id="{anchor_id}">{inline_formatting(heading_text)}</h{level}>')
            i += 1
            continue

        # Horizontal Rule
        if re.match(r'^(-{3,}|\*{3,}|_{3,})$', stripped):
            if in_ul: html_lines.append('</ul>'); in_ul = False
            if in_ol: html_lines.append('</ol>'); in_ol = False
            html_lines.append('<hr class="article-divider">')
            i += 1
            continue

        # Unordered List
        if stripped.startswith(('- ', '* ')):
            if in_ol: html_lines.append('</ol>'); in_ol = False
            if not in_ul:
                html_lines.append('<ul class="article-list">')
                in_ul = True
            item_text = stripped[2:]
            html_lines.append(f'<li>{inline_formatting(item_text)}</li>')
            i += 1
            continue

        # Ordered List
        ol_match = re.match(r'^\d+\.\s+(.*)$', stripped)
        if ol_match:
            if in_ul: html_lines.append('</ul>'); in_ul = False
            if not in_ol:
                html_lines.append('<ol class="article-list">')
                in_ol = True
            item_text = ol_match.group(1)
            html_lines.append(f'<li>{inline_formatting(item_text)}</li>')
            i += 1
            continue

        # Regular Paragraph
        if in_ul: html_lines.append('</ul>'); in_ul = False
        if in_ol: html_lines.append('</ol>'); in_ol = False
        html_lines.append(f'<p>{inline_formatting(stripped)}</p>')
        i += 1

    if in_ul: html_lines.append('</ul>')
    if in_ol: html_lines.append('</ol>')
    if in_table: html_lines.append('</tbody></table></div>')

    return "\n".join(html_lines)


def load_tools_catalog():
    """Load tools information from index.json for CTA widgets."""
    if not INDEX_JSON_PATH.exists():
        return {}
    with open(INDEX_JSON_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    catalog = {}
    for t in data.get('tools', []):
        catalog[t['id']] = t
    return catalog


def render_tool_cta_card(tool):
    """Render a high-converting embedded tool card."""
    color = tool.get('color', '#6366f1')
    return f"""
    <div class="embedded-tool-card" style="--card-accent: {color};">
        <div class="tool-card-icon" style="background: {color}20; color: {color};">
            {tool.get('icon', '⚡')}
        </div>
        <div class="tool-card-body">
            <div class="tool-card-header">
                <span class="tool-name">{html.escape(tool.get('name', ''))}</span>
                <span class="tool-badge">纯前端·免安装</span>
            </div>
            <p class="tool-desc">{html.escape(tool.get('description', ''))}</p>
        </div>
        <div class="tool-card-action">
            <a href="../{tool.get('entry', '')}" class="btn-use-tool" target="_blank" rel="noopener">
                <i class="fas fa-play"></i> 立即使用
            </a>
        </div>
    </div>
    """


def generate_article_html(meta, content_html, tools_catalog, slug):
    """Generate the full HTML document for a single blog post."""
    title = meta.get('title', '技术博客文章 - 微工坊')
    description = meta.get('description', '微工坊技术博客与开发者实用指南。')
    keywords = meta.get('keywords', '微工坊, TinyTools, 在线工具, 开发者博客')
    author = meta.get('author', BRAND_NAME)
    date = meta.get('date', datetime.now().strftime('%Y-%m-%d'))
    article_tools = meta.get('tools', [])

    # Generate Recommended Tools Section if tools are linked
    cta_html = ""
    if article_tools:
        cta_cards = []
        for tid in article_tools:
            if tid in tools_catalog:
                cta_cards.append(render_tool_cta_card(tools_catalog[tid]))
        if cta_cards:
            cta_html = f"""
            <section class="article-tools-section">
                <h3 class="tools-section-title"><i class="fas fa-magic" style="color: #6366f1;"></i> 本文提及与推荐的在线工具</h3>
                <div class="tools-cta-grid">
                    {''.join(cta_cards)}
                </div>
            </section>
            """

    # Estimated Reading Time (approx 350 chars/min for Chinese)
    char_count = len(re.sub(r'\s+', '', content_html))
    read_time = max(1, round(char_count / 350))

    page_url = f"{SITE_URL}/blog/{slug}.html"

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-DY80W2NJR4"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());

      gtag('config', 'G-DY80W2NJR4');
    </script>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(title)} - 微工坊 TinyTools 博客</title>
    <meta name="description" content="{html.escape(description)}">
    <meta name="keywords" content="{html.escape(keywords)}">
    <link rel="canonical" href="{page_url}">
    
    <!-- Open Graph -->
    <meta property="og:type" content="article">
    <meta property="og:site_name" content="{BRAND_NAME}">
    <meta property="og:url" content="{page_url}">
    <meta property="og:title" content="{html.escape(title)}">
    <meta property="og:description" content="{html.escape(description)}">
    <meta property="og:image" content="{SITE_URL}/favicon.svg">
    
    <!-- Twitter Card -->
    <meta property="twitter:card" content="summary">
    <meta property="twitter:title" content="{html.escape(title)}">
    <meta property="twitter:description" content="{html.escape(description)}">
    
    <link rel="icon" href="../favicon.svg">
    <link rel="stylesheet" href="../assets/vendor/fontawesome/css/all.min.css">
    
    <!-- Structured Data (Article Schema) -->
    <script type="application/ld+json">
    {{
      "@context": "https://schema.org",
      "@type": "BlogPosting",
      "headline": "{html.escape(title)}",
      "description": "{html.escape(description)}",
      "datePublished": "{date}",
      "dateModified": "{date}",
      "author": {{
        "@type": "Organization",
        "name": "{BRAND_NAME}",
        "url": "{SITE_URL}/"
      }},
      "publisher": {{
        "@type": "Organization",
        "name": "{BRAND_NAME}",
        "logo": {{
          "@type": "ImageObject",
          "url": "{SITE_URL}/favicon.svg"
        }}
      }},
      "mainEntityOfPage": "{page_url}"
    }}
    </script>

    <style>
        :root {{
            --primary: #6366f1;
            --primary-dark: #4f46e5;
            --secondary: #8b5cf6;
            --bg: #0f172a;
            --bg-card: #1e293b;
            --bg-hover: #334155;
            --text: #f1f5f9;
            --text-muted: #94a3b8;
            --border: #334155;
            --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
            --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.4);
            --content-width: 820px;
        }}

        [data-theme="light"] {{
            --bg: #ffffff;
            --bg-card: #f8fafc;
            --bg-hover: #e2e8f0;
            --text: #1e293b;
            --text-muted: #64748b;
            --border: #e2e8f0;
            --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.15);
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.8;
            min-height: 100vh;
        }}

        .container {{
            max-width: var(--content-width);
            margin: 0 auto;
            padding: 0 20px;
        }}

        /* Header */
        header {{
            background: var(--bg-card);
            border-bottom: 1px solid var(--border);
            padding: 16px 0;
            position: sticky;
            top: 0;
            z-index: 100;
            backdrop-filter: blur(10px);
        }}

        .header-content {{
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}

        .logo {{
            display: flex;
            align-items: center;
            gap: 12px;
            text-decoration: none;
            color: var(--text);
        }}

        .logo-text {{
            font-size: 18px;
            font-weight: 700;
        }}

        .header-nav {{
            display: flex;
            align-items: center;
            gap: 16px;
        }}

        .nav-link {{
            color: var(--text-muted);
            text-decoration: none;
            font-size: 14px;
            transition: color 0.2s;
        }}

        .nav-link:hover {{
            color: var(--primary);
        }}

        .theme-btn {{
            background: var(--bg-hover);
            border: 1px solid var(--border);
            color: var(--text);
            padding: 6px 12px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
        }}

        /* Breadcrumbs */
        .breadcrumbs {{
            padding: 24px 0 12px;
            font-size: 14px;
            color: var(--text-muted);
            display: flex;
            gap: 8px;
            align-items: center;
            flex-wrap: wrap;
        }}

        .breadcrumbs a {{
            color: var(--text-muted);
            text-decoration: none;
        }}

        .breadcrumbs a:hover {{
            color: var(--primary);
        }}

        /* Article Header */
        .article-header {{
            padding: 24px 0 32px;
            border-bottom: 1px solid var(--border);
            margin-bottom: 36px;
        }}

        .article-title {{
            font-size: 32px;
            font-weight: 800;
            line-height: 1.35;
            margin-bottom: 16px;
            color: var(--text);
        }}

        .article-meta {{
            display: flex;
            align-items: center;
            gap: 20px;
            font-size: 14px;
            color: var(--text-muted);
            flex-wrap: wrap;
        }}

        .article-meta-item {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }}

        /* Article Content */
        .article-content {{
            font-size: 16px;
            color: var(--text);
        }}

        .article-content p {{
            margin-bottom: 22px;
            font-size: 16px;
            line-height: 1.85;
        }}

        .article-content h2 {{
            font-size: 24px;
            font-weight: 700;
            margin: 40px 0 18px;
            padding-bottom: 8px;
            border-bottom: 2px solid var(--border);
            color: var(--text);
        }}

        .article-content h3 {{
            font-size: 20px;
            font-weight: 600;
            margin: 30px 0 14px;
            color: var(--text);
        }}

        .article-content ul, .article-content ol {{
            margin: 0 0 24px 28px;
            line-height: 1.8;
        }}

        .article-content li {{
            margin-bottom: 8px;
        }}

        .article-content a {{
            color: var(--primary);
            text-decoration: underline;
            text-underline-offset: 3px;
        }}

        .article-quote {{
            border-left: 4px solid var(--primary);
            background: var(--bg-card);
            padding: 16px 20px;
            border-radius: 0 12px 12px 0;
            margin: 24px 0;
            color: var(--text-muted);
            font-style: italic;
        }}

        .article-quote p {{
            margin-bottom: 0;
        }}

        .code-block-wrapper {{
            background: #1e1e2e;
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 16px 20px;
            margin: 24px 0;
            overflow-x: auto;
        }}

        code {{
            font-family: Consolas, Monaco, "Courier New", monospace;
            font-size: 14px;
            background: var(--bg-hover);
            padding: 2px 6px;
            border-radius: 4px;
            color: #ec4899;
        }}

        pre code {{
            background: transparent;
            padding: 0;
            color: #e2e8f0;
        }}

        .table-responsive {{
            overflow-x: auto;
            margin: 28px 0;
        }}

        .article-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 15px;
        }}

        .article-table th, .article-table td {{
            padding: 12px 16px;
            border: 1px solid var(--border);
            text-align: left;
        }}

        .article-table th {{
            background: var(--bg-card);
            font-weight: 600;
        }}

        .article-table tr:nth-child(even) {{
            background: var(--bg-card);
        }}

        /* Embedded Tool CTA Card */
        .article-tools-section {{
            margin: 48px 0;
            padding: 28px;
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 16px;
            box-shadow: var(--shadow);
        }}

        .tools-section-title {{
            font-size: 18px;
            font-weight: 700;
            margin-bottom: 18px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .tools-cta-grid {{
            display: grid;
            gap: 16px;
        }}

        .embedded-tool-card {{
            display: flex;
            align-items: center;
            gap: 18px;
            padding: 16px 20px;
            background: var(--bg);
            border: 1px solid var(--border);
            border-radius: 12px;
            transition: all 0.25s ease;
        }}

        .embedded-tool-card:hover {{
            transform: translateY(-2px);
            border-color: var(--card-accent);
            box-shadow: var(--shadow);
        }}

        .tool-card-icon {{
            width: 48px;
            height: 48px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 22px;
            flex-shrink: 0;
        }}

        .tool-card-body {{
            flex: 1;
            min-width: 0;
        }}

        .tool-card-header {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 4px;
        }}

        .tool-name {{
            font-size: 16px;
            font-weight: 600;
            color: var(--text);
        }}

        .tool-badge {{
            font-size: 11px;
            background: rgba(99, 102, 241, 0.15);
            color: var(--primary);
            padding: 2px 8px;
            border-radius: 20px;
            font-weight: 500;
        }}

        .tool-desc {{
            font-size: 13px;
            color: var(--text-muted);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            margin-bottom: 0 !important;
        }}

        .btn-use-tool {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 8px 16px;
            background: var(--primary);
            color: #ffffff !important;
            border-radius: 8px;
            text-decoration: none !important;
            font-size: 13px;
            font-weight: 600;
            white-space: nowrap;
            transition: background 0.2s;
        }}

        .btn-use-tool:hover {{
            background: var(--primary-dark);
        }}

        /* Article Footer */
        .article-footer {{
            margin-top: 48px;
            padding: 24px 0;
            border-top: 1px solid var(--border);
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 16px;
        }}

        .back-to-blog {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            color: var(--text-muted);
            text-decoration: none;
            font-size: 14px;
        }}

        .back-to-blog:hover {{
            color: var(--primary);
        }}

        footer {{
            background: var(--bg-card);
            border-top: 1px solid var(--border);
            padding: 40px 0;
            margin-top: 60px;
            text-align: center;
            font-size: 14px;
            color: var(--text-muted);
        }}

        @media (max-width: 640px) {{
            .article-title {{
                font-size: 24px;
            }}
            .embedded-tool-card {{
                flex-direction: column;
                align-items: flex-start;
            }}
            .tool-card-action {{
                width: 100%;
            }}
            .btn-use-tool {{
                width: 100%;
                justify-content: center;
            }}
        }}
    </style>
</head>
<body>
    <header>
        <div class="container header-content">
            <a href="../" class="logo">
                <img src="../favicon.svg" alt="微工坊 Logo" style="width:34px;height:34px;">
                <span class="logo-text">微工坊 <span style="font-size:12px;font-weight:400;opacity:0.8;">Blog</span></span>
            </a>
            <div class="header-nav">
                <a href="../" class="nav-link"><i class="fas fa-home"></i> 首页</a>
                <a href="index.html" class="nav-link active"><i class="fas fa-newspaper"></i> 博客列表</a>
                <a href="../tools-rank.html" class="nav-link"><i class="fas fa-chart-line"></i> 工具排行</a>
                <button class="theme-btn" id="theme-toggle" title="切换主题"><i class="fas fa-moon"></i></button>
            </div>
        </div>
    </header>

    <main class="container">
        <nav class="breadcrumbs" aria-label="Breadcrumb">
            <a href="../"><i class="fas fa-home"></i> 首页</a>
            <span>/</span>
            <a href="index.html">技术博客</a>
            <span>/</span>
            <span>{html.escape(title)}</span>
        </nav>

        <article>
            <header class="article-header">
                <h1 class="article-title">{html.escape(title)}</h1>
                <div class="article-meta">
                    <span class="article-meta-item"><i class="far fa-calendar"></i> {date}</span>
                    <span class="article-meta-item"><i class="far fa-user"></i> {author}</span>
                    <span class="article-meta-item"><i class="far fa-clock"></i> 约 {read_time} 分钟阅读</span>
                </div>
            </header>

            <div class="article-content">
                {content_html}
            </div>

            {cta_html}

            <div class="article-footer">
                <a href="index.html" class="back-to-blog">
                    <i class="fas fa-arrow-left"></i> 返回博客文章列表
                </a>
                <a href="../" class="btn-use-tool" style="background: var(--bg-hover); color: var(--text) !important;">
                    <i class="fas fa-th-large"></i> 浏览微工坊全部工具
                </a>
            </div>
        </article>
    </main>

    <footer>
        <div class="container">
            <p>&copy; 2026 微工坊 TinyTools (html.tpsh.cc) · 纯前端轻量工具集合平台</p>
        </div>
    </footer>

    <script>
        const currentTheme = localStorage.getItem('justhtmls-theme') || 'dark';
        document.documentElement.setAttribute('data-theme', currentTheme);
        const themeBtn = document.getElementById('theme-toggle');
        themeBtn.innerHTML = currentTheme === 'light' ? '<i class="fas fa-moon"></i>' : '<i class="fas fa-sun"></i>';
        
        themeBtn.addEventListener('click', () => {{
            const isLight = document.documentElement.getAttribute('data-theme') === 'light';
            const nextTheme = isLight ? 'dark' : 'light';
            document.documentElement.setAttribute('data-theme', nextTheme);
            localStorage.setItem('justhtmls-theme', nextTheme);
            themeBtn.innerHTML = nextTheme === 'light' ? '<i class="fas fa-moon"></i>' : '<i class="fas fa-sun"></i>';
        }});
    </script>
</body>
</html>
"""


def generate_blog_index_html(articles):
    """Generate the blog index page listing all articles."""
    articles_sorted = sorted(articles, key=lambda a: a['date'], reverse=True)
    cards_html = []

    for art in articles_sorted:
        tools_tags = "".join(f'<span class="article-badge">{html.escape(t)}</span>' for t in art.get('tools', []))
        cards_html.append(f"""
        <article class="blog-card">
            <div class="blog-card-meta">
                <span><i class="far fa-calendar"></i> {art['date']}</span>
                <span><i class="far fa-clock"></i> {art['read_time']} 分钟阅读</span>
            </div>
            <h2 class="blog-card-title">
                <a href="{art['slug']}.html">{html.escape(art['title'])}</a>
            </h2>
            <p class="blog-card-desc">{html.escape(art['description'])}</p>
            <div class="blog-card-footer">
                <div class="blog-card-tags">
                    {tools_tags}
                </div>
                <a href="{art['slug']}.html" class="read-more-link">阅读全文 <i class="fas fa-arrow-right"></i></a>
            </div>
        </article>
        """)

    cards_joined = "".join(cards_html) if cards_html else '<div class="empty-state">暂无文章</div>'

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-DY80W2NJR4"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());

      gtag('config', 'G-DY80W2NJR4');
    </script>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>技术博客与工具指南 - 微工坊 TinyTools | 开发者干货与轻量工具技巧</title>
    <meta name="description" content="微工坊技术博客为您精选前端开发技巧、纯前端数据处理方案、轻量工具使用教程与生产力效率神器解读。">
    <meta name="keywords" content="微工坊博客, 前端工具教程, 开发者指南, 在线工具箱教程, JSON格式化教程, 代码压缩技巧">
    <link rel="canonical" href="{SITE_URL}/blog/">
    
    <!-- Open Graph -->
    <meta property="og:type" content="website">
    <meta property="og:site_name" content="{BRAND_NAME}">
    <meta property="og:url" content="{SITE_URL}/blog/">
    <meta property="og:title" content="技术博客与工具指南 - 微工坊 TinyTools">
    <meta property="og:description" content="微工坊技术博客为您精选前端开发技巧、纯前端数据处理方案、轻量工具使用教程。">
    <meta property="og:image" content="{SITE_URL}/favicon.svg">
    
    <link rel="icon" href="../favicon.svg">
    <link rel="stylesheet" href="../assets/vendor/fontawesome/css/all.min.css">
    
    <style>
        :root {{
            --primary: #6366f1;
            --primary-dark: #4f46e5;
            --secondary: #8b5cf6;
            --bg: #0f172a;
            --bg-card: #1e293b;
            --bg-hover: #334155;
            --text: #f1f5f9;
            --text-muted: #94a3b8;
            --border: #334155;
            --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
            --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.4);
            --content-width: 900px;
        }}

        [data-theme="light"] {{
            --bg: #ffffff;
            --bg-card: #f8fafc;
            --bg-hover: #e2e8f0;
            --text: #1e293b;
            --text-muted: #64748b;
            --border: #e2e8f0;
            --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.15);
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "PingFang SC", sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.6;
            min-height: 100vh;
        }}

        .container {{
            max-width: var(--content-width);
            margin: 0 auto;
            padding: 0 20px;
        }}

        header {{
            background: var(--bg-card);
            border-bottom: 1px solid var(--border);
            padding: 16px 0;
            position: sticky;
            top: 0;
            z-index: 100;
            backdrop-filter: blur(10px);
        }}

        .header-content {{
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}

        .logo {{
            display: flex;
            align-items: center;
            gap: 12px;
            text-decoration: none;
            color: var(--text);
        }}

        .logo-text {{
            font-size: 18px;
            font-weight: 700;
        }}

        .header-nav {{
            display: flex;
            align-items: center;
            gap: 16px;
        }}

        .nav-link {{
            color: var(--text-muted);
            text-decoration: none;
            font-size: 14px;
            transition: color 0.2s;
        }}

        .nav-link:hover, .nav-link.active {{
            color: var(--primary);
        }}

        .theme-btn {{
            background: var(--bg-hover);
            border: 1px solid var(--border);
            color: var(--text);
            padding: 6px 12px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
        }}

        /* Hero */
        .hero {{
            text-align: center;
            padding: 50px 0 30px;
        }}

        .hero h1 {{
            font-size: 32px;
            font-weight: 800;
            margin-bottom: 12px;
            background: linear-gradient(135deg, var(--text), var(--text-muted));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}

        .hero p {{
            color: var(--text-muted);
            font-size: 16px;
            max-width: 600px;
            margin: 0 auto;
        }}

        /* Blog Grid */
        .blog-list {{
            display: grid;
            gap: 24px;
            margin: 36px 0 60px;
        }}

        .blog-card {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 28px;
            transition: all 0.3s;
        }}

        .blog-card:hover {{
            transform: translateY(-3px);
            border-color: var(--primary);
            box-shadow: var(--shadow-lg);
        }}

        .blog-card-meta {{
            display: flex;
            align-items: center;
            gap: 16px;
            font-size: 13px;
            color: var(--text-muted);
            margin-bottom: 12px;
        }}

        .blog-card-title {{
            font-size: 22px;
            font-weight: 700;
            margin-bottom: 12px;
            line-height: 1.4;
        }}

        .blog-card-title a {{
            color: var(--text);
            text-decoration: none;
            transition: color 0.2s;
        }}

        .blog-card-title a:hover {{
            color: var(--primary);
        }}

        .blog-card-desc {{
            color: var(--text-muted);
            font-size: 15px;
            line-height: 1.7;
            margin-bottom: 20px;
        }}

        .blog-card-footer {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 12px;
            padding-top: 16px;
            border-top: 1px solid var(--border);
        }}

        .blog-card-tags {{
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }}

        .article-badge {{
            font-size: 12px;
            background: var(--bg-hover);
            color: var(--text-muted);
            padding: 3px 10px;
            border-radius: 12px;
        }}

        .read-more-link {{
            color: var(--primary);
            text-decoration: none;
            font-size: 14px;
            font-weight: 600;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            transition: gap 0.2s;
        }}

        .read-more-link:hover {{
            gap: 10px;
        }}

        footer {{
            background: var(--bg-card);
            border-top: 1px solid var(--border);
            padding: 40px 0;
            margin-top: 60px;
            text-align: center;
            font-size: 14px;
            color: var(--text-muted);
        }}
    </style>
</head>
<body>
    <header>
        <div class="container header-content">
            <a href="../" class="logo">
                <img src="../favicon.svg" alt="微工坊 Logo" style="width:34px;height:34px;">
                <span class="logo-text">微工坊 <span style="font-size:12px;font-weight:400;opacity:0.8;">Blog</span></span>
            </a>
            <div class="header-nav">
                <a href="../" class="nav-link"><i class="fas fa-home"></i> 首页</a>
                <a href="index.html" class="nav-link active"><i class="fas fa-newspaper"></i> 博客列表</a>
                <a href="../tools-rank.html" class="nav-link"><i class="fas fa-chart-line"></i> 工具排行</a>
                <button class="theme-btn" id="theme-toggle" title="切换主题"><i class="fas fa-moon"></i></button>
            </div>
        </div>
    </header>

    <main class="container">
        <section class="hero">
            <h1>微工坊技术博客</h1>
            <p>探索高效纯前端工具方案、开发者踩坑实战、格式转换技巧与生产力提升秘籍。</p>
        </section>

        <section class="blog-list">
            {cards_joined}
        </section>
    </main>

    <footer>
        <div class="container">
            <p>&copy; 2026 微工坊 TinyTools (html.tpsh.cc) · 纯前端轻量工具集合平台</p>
        </div>
    </footer>

    <script>
        const currentTheme = localStorage.getItem('justhtmls-theme') || 'dark';
        document.documentElement.setAttribute('data-theme', currentTheme);
        const themeBtn = document.getElementById('theme-toggle');
        themeBtn.innerHTML = currentTheme === 'light' ? '<i class="fas fa-moon"></i>' : '<i class="fas fa-sun"></i>';
        
        themeBtn.addEventListener('click', () => {{
            const isLight = document.documentElement.getAttribute('data-theme') === 'light';
            const nextTheme = isLight ? 'dark' : 'light';
            document.documentElement.setAttribute('data-theme', nextTheme);
            localStorage.setItem('justhtmls-theme', nextTheme);
            themeBtn.innerHTML = nextTheme === 'light' ? '<i class="fas fa-moon"></i>' : '<i class="fas fa-sun"></i>';
        }});
    </script>
</body>
</html>
"""


def build_all_posts():
    """Main build entry point."""
    print("🚀 开始构建微工坊博客系统...")
    POSTS_DIR.mkdir(parents=True, exist_ok=True)
    tools_catalog = load_tools_catalog()
    
    articles = []
    
    md_files = list(POSTS_DIR.glob('*.md'))
    if not md_files:
        print("⚠️ 未在 blog/posts/ 找到任何 Markdown 文章文件。")
        return

    for md_path in md_files:
        print(f"📄 正在解析文章: {md_path.name}")
        md_text = md_path.read_text(encoding='utf-8')
        meta, body = parse_frontmatter(md_text)
        
        slug = meta.get('slug', md_path.stem)
        meta['slug'] = slug
        
        html_content = markdown_to_html(body)
        
        # Calculate reading time
        char_count = len(re.sub(r'\s+', '', html_content))
        meta['read_time'] = max(1, round(char_count / 350))
        
        full_page_html = generate_article_html(meta, html_content, tools_catalog, slug)
        
        out_html_path = BLOG_DIR / f"{slug}.html"
        out_html_path.write_text(full_page_html, encoding='utf-8')
        print(f"   ✓ 成功编译静态文章页: blog/{slug}.html")
        
        articles.append(meta)

    # Generate Blog Index
    index_html = generate_blog_index_html(articles)
    (BLOG_DIR / "index.html").write_text(index_html, encoding='utf-8')
    print("✓ 成功生成博客列表聚合页: blog/index.html")

    # Update sitemap
    sitemap_script = BASE_DIR / 'scripts' / 'update_sitemap.py'
    if sitemap_script.exists():
        os.system(f"python3 {sitemap_script}")
    
    print("🎉 博客系统构建完成！所有文章均为 100% 预渲染静态页面，SEO 就绪。")


if __name__ == '__main__':
    build_all_posts()
