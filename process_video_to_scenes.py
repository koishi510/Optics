#!/usr/bin/env python3
"""
视频处理工具 - 从视频中提取绿点坐标并生成光学场景

主要功能：
1. 捕获视频中的绿点坐标
2. 根据坐标换算生成JSON场景文件
3. 自动生成对应的HTML和图片

使用示例：
    from process_video_to_scenes import process_video_to_scenes

    process_video_to_scenes(
        json_template="output/json/test_00.json",
        video_path="video/test.mp4",
        num_samples=20,
        output_prefix="test"
    )
"""

import cv2
import numpy as np
import json
import os
from screenshot_helper import screenshot_with_selenium, compress_scene_for_url


def detect_green_in_frame(frame):
    """检测单帧中的绿点位置"""
    # 转换到HSV色彩空间
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # 定义绿色的HSV范围
    lower_green = np.array([35, 50, 50])
    upper_green = np.array([85, 255, 255])

    # 创建掩码
    mask = cv2.inRange(hsv, lower_green, upper_green)

    # 形态学操作，去除噪点
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    # 查找轮廓
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        # 找到最大的轮廓（假设这是绿点）
        largest_contour = max(contours, key=cv2.contourArea)

        # 计算轮廓的中心点
        M = cv2.moments(largest_contour)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            return (cx, cy)
    return None


def detect_green_dots_from_video(video_path, num_samples=20, verbose=True):
    """
    从视频中检测绿点坐标

    Args:
        video_path: 视频文件路径
        num_samples: 采样数量
        verbose: 是否显示详细信息

    Returns:
        list: 坐标列表 [{"frame": 1, "x": 398, "y": 556}, ...]
    """
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise ValueError(f"无法打开视频文件: {video_path}")

    # 获取视频信息
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    if verbose:
        print(f"视频信息: {total_frames} 帧, {fps:.2f} FPS")
        print("\n第一步: 扫描所有帧，查找绿点...")

    # 找到所有有绿点的帧
    valid_frames = []
    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        if verbose and frame_count % 50 == 0:
            print(f"  扫描进度: {frame_count}/{total_frames} 帧")

        pos = detect_green_in_frame(frame)
        if pos is not None:
            valid_frames.append((frame_count, pos))

    cap.release()

    if verbose:
        print(f"\n找到 {len(valid_frames)} 帧包含绿点")

    if len(valid_frames) == 0:
        raise ValueError("警告: 没有找到绿点!")

    # 从有效帧中均匀采样
    if verbose:
        print(f"\n第二步: 从有效帧中采样 {num_samples} 个点...")

    coordinates = []

    if len(valid_frames) <= num_samples:
        # 如果有效帧数少于等于采样数，全部使用
        coordinates = [{"frame": f, "x": x, "y": y} for f, (x, y) in valid_frames]
        if verbose:
            print(f"有效帧数({len(valid_frames)})少于采样数({num_samples})，使用全部有效帧")
    else:
        # 均匀采样
        step = len(valid_frames) / num_samples
        for i in range(num_samples):
            idx = int(i * step)
            frame_num, (x, y) = valid_frames[idx]
            coordinates.append({"frame": frame_num, "x": x, "y": y})

    if verbose:
        print(f"处理完成! 共采样 {len(coordinates)} 个坐标点\n")

    return coordinates


def create_html_from_json(json_data, output_html):
    """从JSON数据创建本地HTML文件"""
    json_str = json.dumps(json_data, ensure_ascii=False, separators=(",", ":"))
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

        iframe.src = simulatorURL;

        iframe.onload = function() {{
            setTimeout(function() {{
                loading.style.display = 'none';
            }}, 3000);
        }};
    </script>
</body>
</html>
"""

    with open(output_html, "w", encoding="utf-8") as f:
        f.write(html_content)

    return output_html


def process_video_to_scenes(
    json_template,
    video_path,
    num_samples=20,
    output_prefix="scene",
    generate_images=True,
    crop_top=75,
    verbose=True
):
    """
    从视频中提取绿点坐标并生成光学场景

    Args:
        json_template: 模板JSON文件路径
        video_path: 视频文件路径
        num_samples: 采样数量（默认20）
        output_prefix: 输出文件前缀（默认"scene"）
        generate_images: 是否生成图片（默认True）
        crop_top: 截图时裁剪顶部像素（默认75）
        verbose: 是否显示详细信息（默认True）

    Returns:
        dict: 处理结果，包含生成的文件列表

    Example:
        result = process_video_to_scenes(
            json_template="output/json/test_00.json",
            video_path="video/test.mp4",
            num_samples=20,
            output_prefix="test"
        )
    """

    if verbose:
        print("=" * 70)
        print("视频处理工具 - 从视频生成光学场景")
        print("=" * 70)
        print(f"模板JSON: {json_template}")
        print(f"视频文件: {video_path}")
        print(f"采样数量: {num_samples}")
        print(f"输出前缀: {output_prefix}")
        print(f"生成图片: {generate_images}")
        print("=" * 70)
        print()

    # 检查文件是否存在
    if not os.path.exists(json_template):
        raise FileNotFoundError(f"模板JSON文件不存在: {json_template}")
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"视频文件不存在: {video_path}")

    # 读取模板JSON
    if verbose:
        print("读取模板JSON...")
    with open(json_template, 'r', encoding='utf-8') as f:
        template = json.load(f)

    # 提取光源坐标
    light_source = None
    for obj in template.get('objs', []):
        if obj.get('type') == 'PointSource':
            light_source = obj
            break

    if light_source is None:
        raise ValueError("模板JSON中未找到PointSource对象")

    template_x = light_source['x']
    template_y = light_source['y']

    if verbose:
        print(f"模板光源坐标: ({template_x}, {template_y})\n")

    # 检测视频中的绿点坐标
    if verbose:
        print("开始检测视频中的绿点...")
    coordinates = detect_green_dots_from_video(video_path, num_samples, verbose)

    # 计算坐标偏移量
    first_x = coordinates[0]['x']
    first_y = coordinates[0]['y']
    y_offset = template_y - first_y

    if verbose:
        print(f"第一个捕获坐标: ({first_x}, {first_y})")
        print(f"纵坐标偏移量: {y_offset}\n")

    # 创建输出目录
    json_dir = "output/json"
    html_dir = "output/html"
    image_dir = "output/images"

    os.makedirs(json_dir, exist_ok=True)
    os.makedirs(html_dir, exist_ok=True)
    os.makedirs(image_dir, exist_ok=True)

    # 生成文件
    result = {
        "json_files": [],
        "html_files": [],
        "image_files": []
    }

    if verbose:
        print("开始生成场景文件...\n")

    for i, coord in enumerate(coordinates, start=1):
        # 创建新的JSON对象
        new_json = json.loads(json.dumps(template))

        # 更新光源坐标
        new_x = coord['x']
        new_y = coord['y'] + y_offset

        # 找到光源对象并更新
        for obj in new_json.get('objs', []):
            if obj.get('type') == 'PointSource':
                obj['x'] = new_x
                obj['y'] = new_y
                break

        # 生成文件名
        filename = f"{output_prefix}_{i:02d}"
        json_path = os.path.join(json_dir, f"{filename}.json")
        html_path = os.path.join(html_dir, f"{filename}.html")
        image_path = os.path.join(image_dir, f"{filename}.png")

        # 保存JSON文件
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(new_json, f, indent=4, ensure_ascii=False)
        result["json_files"].append(json_path)

        if verbose:
            print(f"[{i}/{len(coordinates)}] {filename}")
            print(f"  帧 {coord['frame']}: 坐标 ({new_x}, {new_y}), 原始 ({coord['x']}, {coord['y']})")

        # 生成HTML文件
        create_html_from_json(new_json, html_path)
        result["html_files"].append(html_path)
        if verbose:
            print(f"  ✓ JSON & HTML 已生成")

        # 生成图片
        if generate_images:
            if os.path.exists(image_path):
                if verbose:
                    print(f"  ⚠ PNG已存在，跳过截图")
            else:
                if verbose:
                    print(f"  正在截图...")
                success = screenshot_with_selenium(
                    html_path, image_path, wait_time=1, crop_top=crop_top
                )
                if success:
                    result["image_files"].append(image_path)
                    if verbose:
                        print(f"  ✓ 截图已保存")
                else:
                    if verbose:
                        print(f"  ❌ 截图失败")

        if verbose:
            print()

    if verbose:
        print("=" * 70)
        print("✓ 处理完成!")
        print("=" * 70)
        print(f"生成文件统计:")
        print(f"  JSON文件: {len(result['json_files'])} 个")
        print(f"  HTML文件: {len(result['html_files'])} 个")
        print(f"  PNG图片:  {len(result['image_files'])} 个")
        print(f"\n输出目录:")
        print(f"  - JSON: {json_dir}/")
        print(f"  - HTML: {html_dir}/")
        print(f"  - 图片: {image_dir}/")
        print("=" * 70)

    return result


if __name__ == "__main__":
    # 示例用法
    result = process_video_to_scenes(
        json_template="output/json/test_00.json",
        video_path="video/test.mp4",
        num_samples=20,
        output_prefix="test"
    )

    print("\n处理结果:")
    print(f"  成功生成 {len(result['json_files'])} 个场景")
