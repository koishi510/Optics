#!/usr/bin/env python3
"""
使用示例 - process_video_to_scenes 函数

这个脚本展示了如何使用 process_video_to_scenes 函数
从视频中提取绿点坐标并生成光学场景
"""

from process_video_to_scenes import process_video_to_scenes

# ==================== 示例 1: 基本使用 ====================
print("示例 1: 基本使用")
print("-" * 50)

result = process_video_to_scenes(
    json_template="output/json/test_00.json",  # 模板JSON文件
    video_path="video/test.mp4",                # 视频文件
    num_samples=20,                             # 生成20个场景
    output_prefix="test"                        # 输出文件前缀
)

print(f"生成了 {len(result['json_files'])} 个场景\n")


# ==================== 示例 2: 自定义参数 ====================
print("\n示例 2: 自定义参数")
print("-" * 50)

result = process_video_to_scenes(
    json_template="output/json/test_00.json",
    video_path="video/test.mp4",
    num_samples=10,                              # 只生成10个场景
    output_prefix="custom",                      # 自定义前缀
    generate_images=False,                       # 不生成图片（加快速度）
    verbose=True                                 # 显示详细信息
)


# ==================== 示例 3: 批量处理多个视频 ====================
print("\n示例 3: 批量处理多个视频")
print("-" * 50)

videos = [
    ("output/json/scene_a.json", "video/video1.mp4", "scene_a"),
    ("output/json/scene_b.json", "video/video2.mp4", "scene_b"),
    ("output/json/scene_c.json", "video/video3.mp4", "scene_c"),
]

for template, video, prefix in videos:
    try:
        result = process_video_to_scenes(
            json_template=template,
            video_path=video,
            num_samples=20,
            output_prefix=prefix,
            verbose=False  # 关闭详细输出
        )
        print(f"✓ {prefix}: 生成 {len(result['json_files'])} 个场景")
    except FileNotFoundError as e:
        print(f"✗ {prefix}: {e}")


# ==================== 示例 4: 只检测坐标，不生成图片 ====================
print("\n示例 4: 快速模式（不生成图片）")
print("-" * 50)

result = process_video_to_scenes(
    json_template="output/json/test_00.json",
    video_path="video/test.mp4",
    num_samples=5,
    output_prefix="quick",
    generate_images=False,  # 跳过图片生成以加快速度
    verbose=True
)


# ==================== 函数说明 ====================
print("\n" + "=" * 70)
print("函数参数说明")
print("=" * 70)
print("""
process_video_to_scenes(
    json_template,      # 必需: 模板JSON文件路径
    video_path,         # 必需: 视频文件路径
    num_samples=20,     # 可选: 采样数量（默认20）
    output_prefix="scene",  # 可选: 输出文件前缀（默认"scene"）
    generate_images=True,   # 可选: 是否生成图片（默认True）
    crop_top=75,        # 可选: 截图裁剪顶部像素（默认75）
    verbose=True        # 可选: 是否显示详细信息（默认True）
)

返回值:
{
    "json_files": [...],   # 生成的JSON文件列表
    "html_files": [...],   # 生成的HTML文件列表
    "image_files": [...]   # 生成的图片文件列表
}

坐标转换规则:
- 横坐标: 保持不变
- 纵坐标: 加上偏移量（模板光源y - 第一个捕获的y）
  例如: 模板(400, 625), 捕获(398, 556)
       偏移量 = 625 - 556 = 69
       最终坐标 = (398, 556 + 69) = (398, 625)
""")
print("=" * 70)
