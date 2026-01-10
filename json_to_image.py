#!/usr/bin/env python3
"""
JSON转图片工具 - 一键将所有JSON场景转换为HTML和图片

截图配置：
  - 默认裁剪顶部75像素以去除ray-optics工具栏
  - 可修改 SCREENSHOT_CROP_TOP 调整裁剪高度
"""

from screenshot_helper import screenshot_with_selenium, compress_scene_for_url
import os
import json
import glob
import sys

# ========== 依赖检查 ==========
# 检查Pillow是否已安装（裁剪功能必需）
try:
    from PIL import Image
except ImportError:
    print("=" * 70)
    print("❌ 错误：未安装Pillow库，无法进行图片裁剪！")
    print("=" * 70)
    print()
    print("Pillow是Python图像处理库，用于裁剪截图去除顶部工具栏。")
    print()
    print("请根据您的环境安装Pillow：")
    print()
    print("  方法1（推荐conda环境）：")
    print("    conda install pillow")
    print()
    print("  方法2（使用pip）：")
    print("    pip install pillow")
    print()
    print("安装完成后请重新运行此脚本。")
    print("=" * 70)
    sys.exit(1)
# ==============================

# ========== 截图配置 ==========
SCREENSHOT_CROP_TOP = 75  # 裁剪顶部像素（默认75px）
# ==============================


def create_html_from_json(json_data: dict, output_html: str):
    """从JSON数据创建本地HTML文件 - 使用json-url压缩"""

    # 将字典转换为JSON字符串
    json_str = json.dumps(json_data, ensure_ascii=False, separators=(",", ":"))

    # 使用json-url压缩场景数据
    compressed_scene = compress_scene_for_url(json_str)

    scene_name = json_data.get("name", "Ray Optics Scene")
    width = json_data.get("width", 1200)
    height = json_data.get("height", 600)
    obj_count = len(json_data.get("objs", []))

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ray Optics - {scene_name}</title>
    <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: Arial, sans-serif;
            background: #000;
            color: white;
            overflow: hidden;
        }}
        #info {{
            position: fixed;
            top: 10px;
            left: 10px;
            padding: 10px 15px;
            background: rgba(0, 0, 0, 0.8);
            border-radius: 5px;
            z-index: 1000;
            font-size: 12px;
        }}
        #loading {{
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            text-align: center;
        }}
        .spinner {{
            border: 4px solid rgba(255, 255, 255, 0.1);
            border-top: 4px solid white;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 10px;
        }}
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
        iframe {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            border: none;
        }}
    </style>
</head>
<body>
    <div id="info">
        <strong>{scene_name}</strong><br>
        {width}x{height} | {obj_count} objects
    </div>

    <div id="loading">
        <div class="spinner"></div>
        <div>Loading simulator...</div>
    </div>

    <iframe id="simulator"></iframe>

    <script>
        const compressedScene = '{compressed_scene}';
        const simulatorURL = 'https://phydemo.app/ray-optics/simulator/#' + compressedScene;

        const iframe = document.getElementById('simulator');
        const loading = document.getElementById('loading');

        console.log('Compressed scene length:', compressedScene.length);
        console.log('Loading URL:', simulatorURL);

        iframe.src = simulatorURL;

        iframe.onload = function() {{
            setTimeout(function() {{
                loading.style.display = 'none';
                console.log('✓ Scene loaded');
            }}, 3000);
        }};
    </script>
</body>
</html>
"""

    with open(output_html, "w", encoding="utf-8") as f:
        f.write(html_content)

    return output_html


def create_index_html(json_dir: str, html_dir: str, image_dir: str):
    """创建索引页面"""
    print("\n创建索引页面...")

    json_files = sorted(glob.glob(os.path.join(json_dir, "*.json")))

    if not json_files:
        print("没有找到JSON文件")
        return

    index_content = (
        """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ray-Optics 场景库</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            padding: 20px;
            min-height: 100vh;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
        }

        header {
            text-align: center;
            padding: 40px 0;
        }

        h1 {
            font-size: 3em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }

        .subtitle {
            font-size: 1.2em;
            opacity: 0.9;
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 25px;
            padding: 20px 0;
        }

        .card {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 20px;
            transition: all 0.3s ease;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }

        .card:hover {
            transform: translateY(-5px);
            background: rgba(255, 255, 255, 0.15);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        }

        .card h3 {
            font-size: 1.3em;
            margin-bottom: 15px;
            color: #fff;
        }

        .card-links {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }

        .btn {
            display: inline-block;
            padding: 10px 20px;
            background: rgba(255, 255, 255, 0.2);
            color: white;
            text-decoration: none;
            border-radius: 8px;
            transition: all 0.2s;
            font-size: 0.9em;
            border: 1px solid rgba(255, 255, 255, 0.3);
        }

        .btn:hover {
            background: rgba(255, 255, 255, 0.3);
            transform: scale(1.05);
        }

        .btn-primary {
            background: #4CAF50;
            border-color: #4CAF50;
        }

        .btn-primary:hover {
            background: #45a049;
        }

        .stats {
            text-align: center;
            padding: 30px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            margin: 20px 0;
        }

        .stats-number {
            font-size: 3em;
            font-weight: bold;
            color: #4CAF50;
        }

        footer {
            text-align: center;
            padding: 40px 0 20px;
            opacity: 0.8;
        }

        .preview {
            width: 100%;
            height: 200px;
            background: rgba(0, 0, 0, 0.3);
            border-radius: 10px;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
        }

        .preview img {
            max-width: 100%;
            max-height: 100%;
            object-fit: contain;
        }

        .no-image {
            color: rgba(255, 255, 255, 0.5);
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🔬 Ray-Optics 场景库</h1>
            <p class="subtitle">光学仿真场景合集</p>
        </header>

        <div class="stats">
            <div class="stats-number">"""
        + str(len(json_files))
        + """</div>
            <div>个可用场景</div>
        </div>

        <div class="grid">
"""
    )

    for json_path in json_files:
        base_name = os.path.splitext(os.path.basename(json_path))[0]
        name = base_name.replace("_", " ").replace("-", " ").title()

        html_file = f"html/{base_name}.html"
        json_file = f"json/{base_name}.json"
        png_file = f"images/{base_name}.png"

        png_path = os.path.join(image_dir, f"{base_name}.png")
        png_exists = os.path.exists(png_path)

        preview_html = (
            f'<img src="{png_file}" alt="{name}">'
            if png_exists
            else '<div class="no-image">暂无预览图</div>'
        )

        index_content += f"""
            <div class="card">
                <div class="preview">
                    {preview_html}
                </div>
                <h3>{name}</h3>
                <div class="card-links">
                    <a href="{html_file}" class="btn btn-primary" target="_blank">🔬 查看仿真</a>
                    <a href="{json_file}" class="btn" download>💾 下载JSON</a>
                    {'<a href="' + png_file + '" class="btn" download>🖼️ 下载截图</a>' if png_exists else ""}
                </div>
            </div>
"""

    index_content += """
        </div>

        <footer>
            <p>使用 <a href="https://github.com/ricktu288/ray-optics" style="color: #4CAF50;">Ray-Optics</a> 创建</p>
            <p style="margin-top: 10px; font-size: 0.9em;">
                Generated by ray_optics_controller.py
            </p>
        </footer>
    </div>
</body>
</html>
"""

    index_path = "output/index.html"
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(index_content)

    print(f"✓ 索引页面已创建: {index_path}")


def json_to_image():
    """将所有JSON文件转换为HTML和图片"""
    print("=" * 60)
    print("JSON转图片工具")
    print("=" * 60)
    print(f"裁剪配置: SCREENSHOT_CROP_TOP = {SCREENSHOT_CROP_TOP}px")
    print("=" * 60)

    # 创建输出目录
    json_dir = "output/json"
    html_dir = "output/html"
    image_dir = "output/images"

    os.makedirs(json_dir, exist_ok=True)
    os.makedirs(html_dir, exist_ok=True)
    os.makedirs(image_dir, exist_ok=True)

    # 查找所有JSON文件
    json_files = sorted(glob.glob(os.path.join(json_dir, "*.json")))

    if not json_files:
        print(f"\n❌ 在 {json_dir} 中没有找到JSON文件")
        print("\n请先运行以下命令生成场景:")
        print("  python ray_optics_controller.py")
        print("  python example_usage.py")
        print("  python quickstart.py")
        return

    print(f"\n找到 {len(json_files)} 个JSON文件\n")

    for i, json_path in enumerate(json_files, 1):
        base_name = os.path.splitext(os.path.basename(json_path))[0]

        print(f"[{i}/{len(json_files)}] 处理: {base_name}.json")

        try:
            # 读取JSON
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # 生成HTML
            html_file = os.path.join(html_dir, f"{base_name}.html")
            create_html_from_json(data, html_file)
            print(f"  ✓ HTML已生成: {base_name}.html")

            # 截图
            png_file = os.path.join(image_dir, f"{base_name}.png")

            if os.path.exists(png_file):
                print(f"  ⚠ PNG已存在，跳过截图")
            else:
                print(f"  正在截图...")
                success = screenshot_with_selenium(
                    html_file, png_file, wait_time=1, crop_top=SCREENSHOT_CROP_TOP
                )
                if success:
                    print(f"  ✓ 截图已保存: {base_name}.png")
                else:
                    print(f"  ❌ 截图失败")

        except Exception as e:
            print(f"  ❌ 处理失败: {e}")

        print()

    # 创建索引
    create_index_html(json_dir, html_dir, image_dir)

    print("\n" + "=" * 60)
    print("✓ 完成!")
    print("=" * 60)
    print(f"\n输出目录:")
    print(f"  - JSON文件:  {json_dir}/")
    print(f"  - HTML文件:  {html_dir}/")
    print(f"  - PNG图片:   {image_dir}/")
    print(f"\n查看结果:")
    print("  打开浏览器: output/index.html")
    print("=" * 60)


if __name__ == "__main__":
    json_to_image()
