#!/usr/bin/env python3
"""
快速演示：光源轨迹功能
生成一个简单的示例，展示如何使用轨迹功能
"""

from ray_optics_controller import (
    RayOpticsScene, Point, PointSource,
    FlatMirror, Blocker,
    generate_light_trajectory
)

# 创建基础场景（只有镜子和屏幕，无光源）
print("创建基础场景...")
scene = RayOpticsScene("激光反射轨迹", width=1000, height=600)

# 添加45度镜子
mirror = FlatMirror(Point(500, 200), Point(600, 300))
scene.add_object(mirror)

# 添加观测屏
screen = Blocker(Point(900, 100), Point(900, 500))
scene.add_object(screen)

print("✓ 基础场景创建完成\n")

# 定义光源轨迹：水平移动
print("定义光源轨迹: 10个位置")
trajectory = [Point(100 + i * 30, 250) for i in range(10)]

# 显示轨迹坐标
print("轨迹点:")
for i, point in enumerate(trajectory, 1):
    print(f"  Frame {i:2d}: ({point.x}, {point.y})")

print("\n生成场景序列...")

# 生成轨迹场景
json_files = generate_light_trajectory(
    base_scene=scene,
    trajectory=trajectory,
    light_type=PointSource,
    light_params={"wavelength": 650, "brightness": 0.9},
    output_prefix="demo_trajectory"
)

print("\n" + "=" * 60)
print("✓ 完成！")
print("=" * 60)
print(f"\n已生成 {len(json_files)} 个JSON场景文件")
print("\n查看方法:")
print("1. 运行: python json_to_image.py")
print("   (转换为HTML和图片)")
print("2. 打开: output/index.html")
print("   (查看所有场景)")
print("3. 在图片查看器中连续查看 demo_trajectory_*.png 查看动画效果")
print("\n" + "=" * 60)
