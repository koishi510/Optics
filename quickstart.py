#!/usr/bin/env python3
"""
快速开始：创建你的第一个光学场景
"""

from ray_optics_controller import (
    RayOpticsScene, Point,
    PointSource, ParallelLight,
    FlatMirror, IdealLens,
    GlassRefractor, Blocker
)
import os

# 确保输出目录存在
os.makedirs("output/json", exist_ok=True)

# ============================================
# 场景1: 基础激光反射
# ============================================
print("创建场景1: 激光反射...")
scene1 = RayOpticsScene("激光反射演示", width=1000, height=500)

# 添加红色激光光源
laser = PointSource(
    position=Point(150, 250),
    wavelength=650,  # 红光
    brightness=0.9
)
scene1.add_object(laser)

# 添加45度镜子
mirror = FlatMirror(
    p1=Point(400, 150),
    p2=Point(550, 300)
)
scene1.add_object(mirror)

# 添加观测屏
screen = Blocker(Point(850, 50), Point(850, 450))
scene1.add_object(screen)

scene1.save("output/quickstart_1_reflection.json")
print(f"✓ 已保存: output/quickstart_1_reflection.json")

# ============================================
# 场景2: 透镜聚焦
# ============================================
print("\n创建场景2: 透镜聚焦...")
scene2 = RayOpticsScene("透镜聚焦演示", width=1200, height=600)

# 添加绿色点光源
source = PointSource(
    position=Point(200, 300),
    wavelength=532,  # 绿光
    brightness=0.8
)
scene2.add_object(source)

# 添加会聚透镜
lens = IdealLens(
    p1=Point(600, 200),
    p2=Point(600, 400),
    focal_length=200
)
scene2.add_object(lens)

# 添加焦点屏
focal_screen = Blocker(Point(1000, 150), Point(1000, 450))
scene2.add_object(focal_screen)

scene2.save("output/quickstart_2_lens.json")
print(f"✓ 已保存: output/quickstart_2_lens.json")

# ============================================
# 场景3: 彩虹棱镜
# ============================================
print("\n创建场景3: 彩虹棱镜...")
scene3 = RayOpticsScene("彩虹棱镜演示", width=1400, height=700)

# 添加白光（多个波长模拟）
wavelengths = {
    700: "红",
    650: "橙红",
    600: "橙",
    570: "黄",
    550: "黄绿",
    500: "绿",
    470: "蓝",
    430: "紫"
}

for i, (wl, color) in enumerate(wavelengths.items()):
    light = ParallelLight(
        position=Point(100, 350 + i * 0.3),
        direction=Point(150, 0),
        wavelength=wl,
        brightness=0.5
    )
    scene3.add_object(light)

# 三棱镜
prism = GlassRefractor(
    points=[
        Point(500, 550),  # 底部左
        Point(750, 350),  # 顶部
        Point(500, 150),  # 底部右
    ],
    refractive_index=1.52
)
scene3.add_object(prism)

# 观测屏
rainbow_screen = Blocker(Point(1200, 0), Point(1200, 700))
scene3.add_object(rainbow_screen)

scene3.save("output/quickstart_3_rainbow.json")
print(f"✓ 已保存: output/quickstart_3_rainbow.json")

# ============================================
# 打印查看方式
# ============================================
print("\n" + "=" * 60)
print("🎉 完成！已创建3个场景")
print("=" * 60)
print("\n查看方式1: 在线查看")
print("1. 访问: https://phydemo.app/ray-optics/simulator/")
print("2. 点击左上角菜单 ☰")
print("3. 选择 Open")
print("4. 选择 output/json/ 目录中的 .json 文件")

print("\n查看方式2: 本地HTML查看器")
print("1. 运行: python json_to_image.py")
print("2. 打开: output/index.html")

print("\n📁 所有JSON文件位于: output/json/")
print("\n下一步：")
print("1. 打开 ray_optics_controller.py 查看完整API")
print("2. 打开 example_usage.py 查看更多示例")
print("3. 阅读 README.md 了解详细文档")
