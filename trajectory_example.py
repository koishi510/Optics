#!/usr/bin/env python3
"""
光源轨迹示例 - 演示如何为移动的光源生成一系列图片
"""

from ray_optics_controller import (
    RayOpticsScene, Point, PointSource, ParallelLight,
    FlatMirror, IdealLens, GlassRefractor, Blocker,
    generate_light_trajectory
)
import math


def example1_horizontal_movement():
    """示例1：光源水平移动经过透镜"""
    print("\n示例1: 光源水平移动")
    print("-" * 60)

    # 创建基础场景（只有光学元件，无光源）
    scene = RayOpticsScene("光源水平移动", width=1200, height=600)

    # 添加透镜
    lens = IdealLens(
        p1=Point(600, 200),
        p2=Point(600, 400),
        focal_length=150
    )
    scene.add_object(lens)

    # 添加观测屏
    screen = Blocker(Point(1000, 100), Point(1000, 500))
    scene.add_object(screen)

    # 定义光源轨迹：从左到右移动
    trajectory = [Point(100 + i * 30, 300) for i in range(15)]

    # 生成轨迹图片
    generate_light_trajectory(
        base_scene=scene,
        trajectory=trajectory,
        light_type=PointSource,
        light_params={"wavelength": 550, "brightness": 0.8},
        output_prefix="h_move"
    )

    print(f"✓ 已生成 {len(trajectory)} 帧")


def example2_circular_movement():
    """示例2：光源绕圆周运动"""
    print("\n示例2: 光源圆周运动")
    print("-" * 60)

    # 创建基础场景
    scene = RayOpticsScene("光源圆周运动", width=1000, height=800)

    # 添加中央镜子
    mirror = FlatMirror(
        p1=Point(450, 350),
        p2=Point(550, 450)
    )
    scene.add_object(mirror)

    # 添加观测屏
    screen = Blocker(Point(50, 0), Point(50, 800))
    scene.add_object(screen)

    # 定义圆周轨迹
    center_x, center_y = 500, 250
    radius = 150
    n_frames = 24

    trajectory = []
    for i in range(n_frames):
        angle = 2 * math.pi * i / n_frames
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        trajectory.append(Point(x, y))

    # 生成轨迹图片
    generate_light_trajectory(
        base_scene=scene,
        trajectory=trajectory,
        light_type=PointSource,
        light_params={"wavelength": 650, "brightness": 0.9},
        output_prefix="circle_move"
    )

    print(f"✓ 已生成 {len(trajectory)} 帧")


def example3_prism_scan():
    """示例3：光源扫描三棱镜"""
    print("\n示例3: 光源扫描三棱镜")
    print("-" * 60)

    # 创建基础场景
    scene = RayOpticsScene("光源扫描三棱镜", width=1200, height=700)

    # 添加三棱镜
    prism = GlassRefractor(
        points=[
            Point(500, 550),
            Point(700, 350),
            Point(500, 150),
        ],
        refractive_index=1.5
    )
    scene.add_object(prism)

    # 添加观测屏
    screen = Blocker(Point(1100, 0), Point(1100, 700))
    scene.add_object(screen)

    # 定义扫描轨迹：垂直扫描
    trajectory = [Point(100, 150 + i * 25) for i in range(17)]

    # 生成轨迹图片
    generate_light_trajectory(
        base_scene=scene,
        trajectory=trajectory,
        light_type=PointSource,
        light_params={"wavelength": 650, "brightness": 0.8},
        output_prefix="prism_scan"
    )

    print(f"✓ 已生成 {len(trajectory)} 帧")


def example4_mirror_maze():
    """示例4：光源在镜子迷宫中移动"""
    print("\n示例4: 镜子迷宫中的移动光源")
    print("-" * 60)

    # 创建基础场景
    scene = RayOpticsScene("镜子迷宫", width=1200, height=800)

    # 添加多个镜子
    mirrors = [
        FlatMirror(Point(300, 200), Point(350, 300)),
        FlatMirror(Point(500, 100), Point(550, 200)),
        FlatMirror(Point(700, 300), Point(750, 400)),
        FlatMirror(Point(500, 500), Point(550, 600)),
    ]

    for mirror in mirrors:
        scene.add_object(mirror)

    # 添加目标屏
    target = Blocker(Point(1100, 300), Point(1100, 500))
    scene.add_object(target)

    # 定义Z字形移动轨迹
    trajectory = []
    # 第一段：向右
    for i in range(8):
        trajectory.append(Point(100 + i * 20, 250))
    # 第二段：向右下
    for i in range(8):
        trajectory.append(Point(240 + i * 20, 250 + i * 20))
    # 第三段：向右
    for i in range(8):
        trajectory.append(Point(380 + i * 20, 390))

    # 生成轨迹图片
    generate_light_trajectory(
        base_scene=scene,
        trajectory=trajectory,
        light_type=PointSource,
        light_params={"wavelength": 532, "brightness": 1.0},
        output_prefix="maze_move"
    )

    print(f"✓ 已生成 {len(trajectory)} 帧")


def example5_parallel_light_rotation():
    """示例5：平行光旋转扫描"""
    print("\n示例5: 平行光旋转扫描")
    print("-" * 60)

    # 创建基础场景
    scene = RayOpticsScene("平行光旋转", width=1000, height=800)

    # 添加透镜
    lens = IdealLens(
        p1=Point(500, 300),
        p2=Point(500, 500),
        focal_length=200
    )
    scene.add_object(lens)

    # 添加屏幕
    screen = Blocker(Point(900, 200), Point(900, 600))
    scene.add_object(screen)

    # 定义弧形轨迹（模拟旋转）
    center_x, center_y = 200, 400
    radius = 200
    n_frames = 16

    trajectory = []
    for i in range(n_frames):
        angle = -math.pi/3 + (2*math.pi/3) * i / (n_frames - 1)
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        trajectory.append(Point(x, y))

    # 平行光参数包含方向
    generate_light_trajectory(
        base_scene=scene,
        trajectory=trajectory,
        light_type=ParallelLight,
        light_params={
            "direction": Point(100, 0),
            "wavelength": 450,
            "brightness": 0.7,
            "width": 80
        },
        output_prefix="parallel_rotate"
    )

    print(f"✓ 已生成 {len(trajectory)} 帧")


if __name__ == "__main__":
    print("=" * 60)
    print("光源轨迹生成示例")
    print("=" * 60)

    # 运行所有示例
    example1_horizontal_movement()
    example2_circular_movement()
    example3_prism_scan()
    example4_mirror_maze()
    example5_parallel_light_rotation()

    print("\n" + "=" * 60)
    print("✓ 完成！所有轨迹JSON已生成")
    print("=" * 60)
    print("\n下一步：")
    print("1. 运行: python json_to_image.py")
    print("   (一键生成所有HTML和图片)")
    print("2. 打开: output/index.html")
    print("   (查看所有场景，包括轨迹动画)")
    print("\n提示: 可以使用图片查看器的幻灯片模式查看动画效果")
    print("=" * 60)
