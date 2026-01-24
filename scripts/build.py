#!/usr/bin/env python3
# scripts/build.py
import os
import sys  # 新增：导入sys模块
import shutil
import yaml
import markdown

# ========== 新增：补全路径处理（解决config导入问题） ==========
# 获取当前脚本所在目录（scripts/）
scripts_dir = os.path.dirname(os.path.abspath(__file__))
# 获取工程根目录（scripts/的上层目录）
project_root = os.path.dirname(scripts_dir)
# 将根目录加入sys.path，让Python能找到config.py
sys.path.append(project_root)

from config import CONFIG  # 导入全局配置

# 工具函数：创建目录（不存在则创建）
def create_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

# 工具函数：读取文件内容
def read_file(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return ""

# 工具函数：写入文件内容
def write_file(path, content):
    create_dir(os.path.dirname(path))  # 自动创建父目录
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

# 步骤1：复制静态资源（CSS）到输出目录
def copy_static_files():
    static_src = CONFIG["static_dir"]
    static_dest = os.path.join(CONFIG["output_dir"], "static")
    if os.path.exists(static_src):
        shutil.copytree(static_src, static_dest, dirs_exist_ok=True)
    print("✅ 静态资源复制完成")

# 步骤2：遍历所有Markdown文章，生成文章页 + 收集文章元信息
def process_all_posts():
    all_posts = []  # 存储所有文章的元信息（用于生成首页）
    posts_dir = CONFIG["posts_dir"]

    # 遍历posts目录下所有.md文件（包括子目录，若有）
    for root, _, files in os.walk(posts_dir):
        for file in files:
            if file.endswith(".md"):
                # 1. 读取并解析Markdown文件
                md_path = os.path.join(root, file)
                md_content = read_file(md_path)
                
                # 分割YAML元信息和文章正文
                try:
                    meta_str, md_body = md_content.split("---", 2)[1], md_content.split("---", 2)[2].strip()
                    meta = yaml.safe_load(meta_str)
                except IndexError:
                    print(f"⚠️ 文章 {file} 缺少YAML元信息，跳过")
                    continue
                
                # 补全默认值（避免元信息缺失报错）
                meta["title"] = meta.get("title", "无标题")
                meta["date"] = str(meta.get("date", "无日期"))  # 强制转字符串
                meta["slug"] = meta.get("slug", file.replace(".md", ""))  # 文章唯一标识
                
                # 2. Markdown转HTML（========== 核心修改：强化代码块解析 ==========）
                html_content = markdown.markdown(
                    md_body,
                    extensions=[
                        "fenced_code",  # 解析```包裹的代码块（核心）
                        "codehilite",   # 新增：代码语法高亮（依赖pygments）
                        "tables",       # 表格支持
                        "toc",          # 目录（可选）
                        "md_in_html"    # HTML混合MD
                    ],
                    # 新增：codehilite配置（适配你的样式风格）
                    extension_configs={
                        "codehilite": {
                            "linenums": False,  # 不显示行号（和你的极简风格一致）
                            "guess_lang": True, # 自动识别代码语言（bash/python等）
                            "css_class": "highlight" # 统一高亮样式类名
                        }
                    }
                )
                
                # 3. 生成文章页输出路径（保持原文件名，改后缀为.html）
                rel_path = os.path.relpath(md_path, posts_dir)  # 相对路径
                html_filename = rel_path.replace(".md", ".html")
                post_output_path = os.path.join(CONFIG["output_dir"], "posts", html_filename)
                
                # 4. 读取文章模板，替换变量
                post_template = read_file(os.path.join(CONFIG["templates_dir"], "post.html"))
                final_html = post_template.replace("{{ site_name }}", CONFIG["site_name"]) \
                                          .replace("{{ site_title }}", CONFIG["site_title"]) \
                                          .replace("{{ author }}", CONFIG["author"]) \
                                          .replace("{{ footer_text }}", CONFIG["footer_text"]) \
                                          .replace("{{ title }}", meta["title"]) \
                                          .replace("{{ date }}", meta["date"]) \
                                          .replace("{{ content }}", html_content)
                
                # 5. 写入文章页HTML文件
                write_file(post_output_path, final_html)
                print(f"✅ 生成文章页：{meta['title']}")
                
                # 6. 收集文章元信息（用于首页）
                post_url = f"/posts/{html_filename}"  # 文章访问路径
                all_posts.append({
                    "title": meta["title"],
                    "date": meta["date"],
                    "url": post_url
                })
    
    # 按日期倒序排序（最新文章在前）
    all_posts.sort(key=lambda x: x["date"], reverse=True)
    return all_posts

# 步骤3：生成首页（自动列出所有文章）
def generate_index(all_posts):
    index_template = read_file(os.path.join(CONFIG["templates_dir"], "index.html"))
    
    # 自动生成文章列表HTML
    post_list_html = ""
    for post in all_posts:
        post_list_html += f"""
        <li class="post-item">
            <a href="{post['url']}" class="post-link">{post['title']}</a>
            <span class="post-date">{post['date']}</span>
        </li>
        """
    
    # 替换首页模板变量
    final_html = index_template.replace("{{ site_name }}", CONFIG["site_name"]) \
                              .replace("{{ site_title }}", CONFIG["site_title"]) \
                              .replace("{{ author }}", CONFIG["author"]) \
                              .replace("{{ footer_text }}", CONFIG["footer_text"]) \
                              .replace("{{ post_list }}", post_list_html)
    
    # 写入首页HTML文件
    index_output_path = os.path.join(CONFIG["output_dir"], "index.html")
    write_file(index_output_path, final_html)
    print("✅ 首页生成完成")

# 主函数：执行所有构建步骤
if __name__ == "__main__":
    try:
        copy_static_files()
        all_posts = process_all_posts()
        generate_index(all_posts)
        print("\n🎉 博客构建完成！所有页面已生成至 docs/ 目录")
    except Exception as e:
        print(f"\n❌ 构建失败：{e}")