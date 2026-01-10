#!/usr/bin/env python3
"""
Ray-Optics 控制器使用示例
演示如何创建自定义光学场景
"""

from ray_optics_controller import (
    RayOpticsScene, Point, PointSource, ParallelLight,
    FlatMirror, CurvedMirror, IdealLens, GlassRefractor,
    Blocker
)


def example1_simple_mirror():
    """示例1：简单的镜面反射"""
    scene = RayOpticsScene("镜面反射实验", width=1000, height=600)

    # 添加点光源
    light = PointSource(
        position=Point(200, 200),
        wavelength=650,  # 红光
        brightness=0.8
    )
    scene.add_object(light)

    # 添加45度平面镜
    mirror = FlatMirror(
        p1=Point(400, 150),
        p2=Point(550, 300)
    )
    scene.add_object(mirror)

    # 保存
    scene.save("output/json/simple_mirror.json")

    return scene


def example2_concave_mirror():
    """示例2：凹面镜聚焦"""
    scene = RayOpticsScene("凹面镜聚焦", width=1200, height=600)

    # 添加平行光
    for y in range(200, 401, 20):
        light = ParallelLight(
            position=Point(100, y),
            direction=Point(100, 0),
            wavelength=550,
            brightness=0.5
        )
        scene.add_object(light)

    # 添加凹面镜
    mirror = CurvedMirror(
        p1=Point(600, 150),
        p2=Point(600, 450),
        p3=Point(500, 300)  # 控制点决定曲率
    )
    scene.add_object(mirror)

    scene.save("output/json/concave_mirror.json")
    return scene


def example3_glass_prism():
    """示例3：玻璃三角柱"""
    scene = RayOpticsScene("玻璃三角柱折射", width=1200, height=600)

    # 单色光源
    light = ParallelLight(
        position=Point(100, 300),
        direction=Point(100, 10),
        wavelength=532,  # 绿光
        brightness=0.8
    )
    scene.add_object(light)

    # 直角三角柱
    prism = GlassRefractor(
        points=[
            Point(400, 450),
            Point(700, 450),
            Point(400, 150),
        ],
        refractive_index=1.52  # 普通玻璃
    )
    scene.add_object(prism)

    scene.save("output/json/glass_prism.json")
    return scene


def example4_compound_lens():
    """示例4：复合透镜系统"""
    scene = RayOpticsScene("复合透镜系统", width=1400, height=600)

    # 点光源
    source = PointSource(
        position=Point(150, 300),
        wavelength=550,
        brightness=0.8
    )
    scene.add_object(source)

    # 第一个透镜（会聚）
    lens1 = IdealLens(
        p1=Point(500, 200),
        p2=Point(500, 400),
        focal_length=200
    )
    scene.add_object(lens1)

    # 第二个透镜（发散）
    lens2 = IdealLens(
        p1=Point(900, 200),
        p2=Point(900, 400),
        focal_length=-150  # 负焦距表示发散
    )
    scene.add_object(lens2)

    # 观测屏
    screen = Blocker(Point(1300, 100), Point(1300, 500))
    scene.add_object(screen)

    scene.save("output/json/compound_lens.json")
    return scene


def example5_rainbow_colors():
    """示例5：彩虹光谱"""
    scene = RayOpticsScene("光谱色散", width=1400, height=600)

    # 多种波长的光
    wavelengths = [700, 650, 600, 550, 500, 450, 400]  # 红到紫
    colors = ["红", "橙", "黄", "绿", "青", "蓝", "紫"]

    for i, (wavelength, color) in enumerate(zip(wavelengths, colors)):
        light = ParallelLight(
            position=Point(100, 300 + i * 0.5),  # 略微错开
            direction=Point(100, 0),
            wavelength=wavelength,
            brightness=0.6
        )
        scene.add_object(light)

    # 三棱镜
    prism = GlassRefractor(
        points=[
            Point(500, 450),
            Point(700, 300),
            Point(500, 150),
        ],
        refractive_index=1.5
    )
    scene.add_object(prism)

    # 观测屏
    screen = Blocker(Point(1100, 0), Point(1100, 600))
    scene.add_object(screen)

    scene.save("output/json/rainbow.json")
    return scene


def example6_custom_scene():
    """示例6：完全自定义场景"""
    scene = RayOpticsScene("自定义光学实验")

    # 你可以在这里添加任意光源和光学元件
    # 例如：创建一个激光迷宫

    # 激光源
    laser = PointSource(Point(100, 300), wavelength=650, brightness=1.0)
    scene.add_object(laser)

    # 多个镜子形成迷宫路径
    mirrors = [
        FlatMirror(Point(300, 200), Point(350, 250)),
        FlatMirror(Point(450, 350), Point(500, 300)),
        FlatMirror(Point(600, 200), Point(650, 250)),
    ]

    for mirror in mirrors:
        scene.add_object(mirror)

    # 目标点（用blocker模拟）
    target = Blocker(Point(800, 300), Point(810, 310))
    scene.add_object(target)

    scene.save("output/json/laser_maze.json")
    return scene


if __name__ == "__main__":
    import os

    # 创建输出目录
    os.makedirs("output/json", exist_ok=True)

    print("生成光学仿真场景示例...")
    print("=" * 60)

    # 运行所有示例
    print("\n[1/6] 镜面反射实验")
    example1_simple_mirror()

    print("\n[2/6] 凹面镜聚焦")
    example2_concave_mirror()

    print("\n[3/6] 玻璃三角柱折射")
    example3_glass_prism()

    print("\n[4/6] 复合透镜系统")
    example4_compound_lens()

    print("\n[5/6] 光谱色散")
    example5_rainbow_colors()

    print("\n[6/6] 激光迷宫")
    example6_custom_scene()

    print("\n" + "=" * 60)
    print("✓ 所有场景JSON文件已生成到 output/json/ 目录")
    print("\n查看方法:")
    print("1. 运行: python json_to_image.py")
    print("   (一键生成HTML和图片)")
    print("2. 或访问 https://phydemo.app/ray-optics/simulator/")
    print("   点击菜单 -> Open -> 选择生成的JSON文件")
    print("=" * 60)
