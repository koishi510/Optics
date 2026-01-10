#!/usr/bin/env python3
"""
改进的截图工具 - 使用本地HTML文件
"""

from ray_optics_controller import RayOpticsScene, Point, PointSource, FlatMirror
import os
import json
import subprocess


def compress_scene_for_url(scene_json: str) -> str:
    """
    使用json-url('lzma')压缩场景JSON
    这与ray-optics仿真器使用的格式完全一致
    通过Node.js调用json-url库实现
    """
    try:
        # 调用Node.js脚本进行压缩
        script_path = os.path.join(os.path.dirname(__file__), 'compress_json.js')
        result = subprocess.run(
            ['node', script_path],
            input=scene_json.encode('utf-8'),
            capture_output=True,
            check=True
        )
        compressed = result.stdout.decode('utf-8')
        return compressed
    except subprocess.CalledProcessError as e:
        print(f"❌ JSON压缩失败: {e.stderr.decode('utf-8')}")
        raise
    except FileNotFoundError:
        print("❌ 未找到Node.js或compress_json.js脚本")
        print("   请确保已安装Node.js并运行 'npm install json-url'")
        raise


def create_local_html(scene: RayOpticsScene, output_html: str):
    """创建本地HTML文件来显示场景 - 使用LZMA压缩的URL hash方式"""

    json_data = scene.to_json(indent=None)  # 不需要缩进，减少大小

    # 使用LZMA压缩场景数据
    compressed_scene = compress_scene_for_url(json_data)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ray Optics - {scene.name}</title>
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
        <strong>{scene.name}</strong><br>
        {scene.width}x{scene.height} | {len(scene.objects)} objects
    </div>

    <div id="loading">
        <div class="spinner"></div>
        <div>Loading simulator...</div>
    </div>

    <iframe id="simulator"></iframe>

    <script>
        // 使用LZMA压缩的场景数据（已在Python中压缩）
        const compressedScene = '{compressed_scene}';

        // 直接使用压缩后的hash加载场景（ray-optics官方格式）
        const simulatorURL = 'https://phydemo.app/ray-optics/simulator/#' + compressedScene;

        const iframe = document.getElementById('simulator');
        const loading = document.getElementById('loading');

        console.log('Compressed scene length:', compressedScene.length);
        console.log('Loading URL:', simulatorURL);

        // 加载仿真器
        iframe.src = simulatorURL;

        // 监听iframe加载
        iframe.onload = function() {{
            // 给ray-optics足够时间来解压和加载场景
            setTimeout(function() {{
                loading.style.display = 'none';
                console.log('✓ Scene loaded via LZMA compressed hash');
            }}, 3000);
        }};
    </script>
</body>
</html>
"""

    with open(output_html, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"✓ HTML文件已创建: {output_html}")
    print(f"  场景数据已使用LZMA压缩（压缩后长度: {len(compressed_scene)} 字符）")
    print(f"  在浏览器中打开此文件即可查看场景")

    return output_html


def screenshot_with_selenium(html_file: str, output_image: str, wait_time: int = 5, crop_top: int = 75):
    """
    使用Selenium截图HTML文件

    参数:
        html_file: HTML文件路径
        output_image: 输出图片路径
        wait_time: 等待时间（秒）
        crop_top: 裁剪顶部像素数（默认：75）
    """
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        import time

        options = Options()
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920,1080')

        driver = webdriver.Chrome(options=options)

        # 使用file:// URL打开本地文件
        abs_path = os.path.abspath(html_file)
        file_url = f'file://{abs_path}'

        print(f"正在打开: {file_url}")
        driver.get(file_url)

        # 等待iframe加载
        print(f"等待 {wait_time} 秒...")
        time.sleep(wait_time)

        # 切换到iframe
        try:
            iframe = driver.find_element("id", "simulator")
            driver.switch_to.frame(iframe)
            print("✓ 已切换到iframe")
        except:
            print("⚠ 无法切换到iframe，使用主页面截图")

        # 截图
        driver.save_screenshot(output_image)
        print(f"✓ 截图已保存: {output_image}")

        driver.quit()

        # 裁剪顶部（如果需要）
        if crop_top > 0:
            try:
                from PIL import Image
                img = Image.open(output_image)
                width, height = img.size

                # 裁剪：从crop_top像素开始到底部
                cropped = img.crop((0, crop_top, width, height))
                cropped.save(output_image)
                print(f"✓ 已裁剪顶部 {crop_top}px")

                # 更新文件大小
                size = os.path.getsize(output_image)
                print(f"  裁剪后大小: {size / 1024:.1f} KB")
            except ImportError:
                print("⚠ 未安装PIL/Pillow，跳过裁剪")
                print("  安装: pip install pillow")
            except Exception as e:
                print(f"⚠ 裁剪失败: {e}")
        else:
            # 检查文件大小
            size = os.path.getsize(output_image)
            print(f"  文件大小: {size / 1024:.1f} KB")

        return True

    except ImportError:
        print("❌ 未安装selenium")
        print("   运行: pip install selenium")
        return False
    except Exception as e:
        print(f"❌ 截图失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("=" * 60)
    print("Ray-Optics 本地HTML截图工具")
    print("=" * 60)

    os.makedirs("output", exist_ok=True)

    # 创建测试场景
    scene = RayOpticsScene("本地HTML测试", width=1200, height=700)

    scene.add_object(PointSource(Point(200, 350), wavelength=550, brightness=0.9))
    scene.add_object(FlatMirror(Point(500, 250), Point(700, 450)))

    # 生成本地HTML
    html_file = "output/viewer.html"
    create_local_html(scene, html_file)

    # 尝试自动截图
    print("\n尝试自动截图...")
    output_image = "output/viewer_screenshot.png"
    success = screenshot_with_selenium(html_file, output_image, wait_time=10)

    if not success:
        print("\n" + "=" * 60)
        print("自动截图失败，请使用以下方法手动截图:")
        print("=" * 60)
        print(f"\n1. 在浏览器中打开: {os.path.abspath(html_file)}")
        print("2. 等待场景加载完成")
        print("3. 手动截图保存")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
