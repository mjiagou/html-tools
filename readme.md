# 微工坊 TinyTools

<div align="center">

[![TinyTools Logo](https://img.shields.io/badge/TinyTools-微工坊-6366f1?style=for-the-badge)](https://html.tpsh.cc/)
[![License](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)](LICENSE)

**轻量纯前端在线工具箱 - 隐私零上传·即开即用**

[在线体验](https://html.tpsh.cc/)

</div>

---

## 项目简介

微工坊（TinyTools）是一个面向开发者、设计师与日常办公用户的轻量级在线工具箱平台。汇集 120+ 款开箱即用的前端小工具，所有计算均在浏览器本地安全沙箱处理，绝不上传服务器，全面守护用户隐私。

致力于打造最完整的中文 HTML 工具集合。

### 特点

- **单文件设计** - 所有工具都是独立的 HTML 文件，内联 CSS 和 JavaScript
- **无需构建** - 不使用 React/JSX，直接从浏览器打开
- **隐私优先** - 数据在本地处理，不发送到服务器
- **本地依赖** - 第三方库放入 assets/vendor，离线可用
- **可选 CDN** - CDN 优先，失败自动回退到本地资源
- **开源免费** - MIT 许可证，欢迎贡献

---

## 工具分类

| 分类 | 描述 | 工具数量 |
|------|------|----------|
| 格式转换 | 各种文件和数据格式之间的转换工具 | - |
| 开发者工具 | 面向开发者的实用工具集合 | - |
| 文本处理 | 文本编辑、格式化和处理工具 | - |
| 图片处理 | 图片编辑、转换和优化工具 | - |
| 实用工具 | 日常生活中的实用小工具 | - |

---

## 工具清单

### 格式转换
- Base32 编码
- Base32 解码
- Base36 编码
- Base36 解码
- Base58 编码
- Base58 解码
- Base64 URL 安全编码
- Base64 URL 安全解码
- Base64 编码解码
- CSV 转 JSON
- CSV 转 TSV
- CSV 转 YAML
- HEX 编码
- HEX 解码
- HTML 实体编码/解码
- JSON 字符串转义
- JSON 格式化工具
- JSON 转 CSV
- JSON 转 TSV
- JSON 转 XML
- JSON 转 YAML
- JSONL 转换器
- TSV 转 CSV
- TSV 转 JSON
- URL 编码解码
- Unix 时间戳转换
- XML 转 JSON
- XML 转 YAML
- YAML 转 CSV
- YAML 转 JSON
- YAML 转 XML
- YAML 验证器
- 进制转换工具

### 开发者工具
- CSS 压缩/格式化工具
- Cron 表达式生成器
- CURL 转代码工具
- Gitignore 生成器
- HTML 压缩器
- HTML 格式化工具
- HTTP 状态码查询
- JSON 压缩器
- JSON 键名排序
- JWT 生成器
- JWT 解码器
- JavaScript 压缩器
- JavaScript 格式化工具
- Meta 标签生成器
- NanoID 生成器
- Robots.txt 生成器
- SQL 压缩器
- SQL 格式化工具
- Sitemap 生成器
- ULID 生成器
- URL 参数生成器
- URL 解析器
- UUID 生成器
- XML 压缩器
- XML 格式化工具
- YAML 压缩器
- YAML 格式化工具
- 哈希生成器
- 正则表达式测试器
- 渐变色生成器
- 颜色对比度检测
- 颜色选择器

### 文本处理
- Emoji 清理器
- 每日一言
- HTML 转 Markdown
- HTML 转纯文本
- JSON 转 Markdown 表格
- Lorem Ipsum 生成器
- Markdown 表格生成器
- Markdown 转 HTML
- Markdown 转纯文本
- ROT13 编码
- URL Slug 生成器
- Unicode 反转义
- Unicode 转义
- 二进制转文本
- 凯撒密码
- 大小写转换工具
- 字数统计工具
- 摩斯电码编码
- 摩斯电码解码
- 文本分割器
- 文本去重工具
- 文本反转工具
- 文本合并器
- 文本对比工具
- 文本换行器
- 文本排序工具
- 文本查找替换
- 文本清理器
- 文本缩进工具
- 文本转 HTML
- 文本转二进制
- 行号添加器
- 行尾符转换器

### 图片处理
- 图片加水印
- 图片压缩工具
- 图片尺寸调整
- 图片拼接
- 图片旋转翻转
- 图片滤镜
- 图片裁剪
- 图片转 Base64
- 图片转 WebP

### 实用工具
- BMI 计算器
- 倒计时器
- 二维码生成器
- 单位换算器
- 字节大小转换器
- 抽签工具
- 掷骰子工具
- 石头剪刀布
- 安全密码生成器
- 密码强度检测
- 日期差值计算器
- 百分比计算器
- 随机抽取器
- 随机数生成器

---

## 快速开始

### 在线使用

直接访问 [微工坊 TinyTools 网站](https://html.tpsh.cc/) 即可使用所有工具。

### 本地运行

```bash
# 启动本地开发服务
python3 -m http.server 8000
# 或
npx serve .
```

然后在浏览器中访问 `http://localhost:8000`

![](https://piggo5.oss-cn-shenzhen.aliyuncs.com/2026/iShot_2025-12-23_16.06.50.png)

---

## 贡献工具

我们欢迎社区贡献！提交新工具的流程非常简单：

### 添加新工具流程

1. 在 `tools/` 目录下创建你的工具文件夹
2. 按规范创建单文件工具（`app.html` 和 `index.html`）
3. 在 `index.json` 中注册工具元数据
4. 运行 `python3 scripts/update_sitemap.py` 生成站点地图
5. 运行 `node scripts/check-filter.js` 验证索引检索通过

### 工具规范

每个工具必须包含：

```
tools/
  └── your-tool/
      ├── index.html    # 工具详情页（介绍页面）
      └── app.html      # 工具实体页（实际运行的工具）
```

**设计原则：**

- 单文件 HTML，内联 CSS/JS
- 不使用 React 或需要构建的技术
- 从本地 assets/vendor 加载第三方库
- 保持精简（建议 500 行以内）
- 详细内容请查看 [贡献指南](CONTRIBUTING.md)。

---

## 📝 发布技术博客（SEO推广）

本项目内置了纯静态预渲染博客系统，用于通过高质量干货与教程内容推广站内工具：

1. 在 `blog/posts/` 目录下新建 Markdown 文件（如 `my-post.md`）：
   ```markdown
   ---
   title: 你的文章标题
   slug: my-post
   date: 2026-09-25
   author: 微工坊 TinyTools
   description: 搜索结果中展示的简要描述（120字左右）
   keywords: 关键词1, 关键词2, 工具推荐
   tools:
     - json-formatter
     - base64-encode
   ---
   你的正文 Markdown 内容...
   ```
2. 运行一键构建脚本：
   ```bash
   python3 scripts/build_blog.py
   ```
   脚本会自动编译生成预渲染的静态 HTML 文章页、更新博客列表页 [blog/index.html](blog/index.html)，并在 [sitemap.xml](sitemap.xml) 中自动注册新增文章 URL。

---

## 项目结构

```
html-tools/
├── index.html              # 主站门户首页
├── index.json              # 工具索引文件
├── CONTRIBUTING.md          # 贡献指南
├── README.md               # 项目说明
├── tools/                  # 工具目录
│   └── tool-name/         # 单个工具文件夹
│       ├── index.html     # 工具详情页
│       └── app.html       # 工具实体页
└── .github/
    └── ISSUE_TEMPLATE/    # GitHub Issue 模板
        ├── tool-submission.md
        └── bug-report.md
```

---

## 开发路线图

- [x] 基础网站框架
- [x] 工具索引系统
- [x] 搜索和过滤功能
- [x] 工具提交流程
- [ ] 用户系统（收藏、历史记录）
- [ ] 工具评分和评论
- [ ] 私人工具侧载功能
- [ ] 移动端优化

---

## 技术栈

- **纯 HTML/CSS/JavaScript** - 无构建步骤
- **GitHub Pages** - 静态托管
- **GitHub Issues** - 工具提交流程

---

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

---

## 鸣谢

- 所有贡献者 - 感谢你们的贡献！

---

<div align="center">

**如果这个项目对你有帮助，请给它一个 Star ⭐**

</div>
