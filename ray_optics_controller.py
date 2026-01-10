#!/usr/bin/env python3
"""
Ray-Optics Simulator Controller
用于生成ray-optics仿真器的JSON场景文件
"""

import json
import os
from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class Point:
    """点坐标"""
    x: float
    y: float

    def to_dict(self):
        return {"x": self.x, "y": self.y}


class OpticalObject:
    """光学对象基类"""
    def __init__(self, obj_type: str, position: Point):
        self.type = obj_type
        self.position = position

    def to_dict(self) -> Dict[str, Any]:
        """转换为ray-optics JSON格式"""
        return {
            "type": self.type,
            "p1": self.position.to_dict()
        }


class PointSource(OpticalObject):
    """点光源"""
    def __init__(self, position: Point, wavelength: float = 550,
                 brightness: float = 0.5):
        super().__init__("PointSource", position)
        self.wavelength = wavelength  # 波长 (nm)
        self.brightness = brightness  # 亮度 0-1

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "PointSource",
            "x": self.position.x,
            "y": self.position.y,
            "wavelength": str(self.wavelength),
            "brightness": str(self.brightness),
        }


class ParallelLight(OpticalObject):
    """平行光束（Beam类型）"""
    def __init__(self, position: Point, direction: Point,
                 wavelength: float = 550, brightness: float = 0.5,
                 width: float = 50):
        super().__init__("Beam", position)
        self.direction = direction
        self.wavelength = wavelength
        self.brightness = brightness
        self.width = width

    def to_dict(self) -> Dict[str, Any]:
        # p1和p2定义光束的宽度（垂直于传播方向）
        return {
            "type": "Beam",
            "p1": self.position.to_dict(),
            "p2": Point(self.position.x, self.position.y + self.width).to_dict(),
            "wavelength": str(self.wavelength),
            "brightness": str(self.brightness),
        }


class FlatMirror(OpticalObject):
    """平面镜"""
    def __init__(self, p1: Point, p2: Point):
        super().__init__("Mirror", p1)
        self.p2 = p2

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "Mirror",
            "p1": self.position.to_dict(),
            "p2": self.p2.to_dict(),
        }


class CurvedMirror(OpticalObject):
    """曲面镜（抛物面镜）"""
    def __init__(self, p1: Point, p2: Point, p3: Point):
        super().__init__("ParabolicMirror", p1)
        self.p2 = p2
        self.p3 = p3  # 控制点

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "ParabolicMirror",
            "p1": self.position.to_dict(),
            "p2": self.p2.to_dict(),
            "p3": self.p3.to_dict(),
        }


class IdealLens(OpticalObject):
    """理想透镜"""
    def __init__(self, p1: Point, p2: Point, focal_length: float = 100):
        super().__init__("IdealLens", p1)
        self.p2 = p2
        self.focal_length = focal_length

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "IdealLens",
            "p1": self.position.to_dict(),
            "p2": self.p2.to_dict(),
            "focalLength": str(self.focal_length),
        }


class GlassRefractor(OpticalObject):
    """玻璃折射体（多边形）"""
    def __init__(self, points: List[Point], refractive_index: float = 1.5):
        super().__init__("Glass", points[0])
        self.points = points
        self.refractive_index = refractive_index

    def to_dict(self) -> Dict[str, Any]:
        # 使用path数组表示多边形顶点
        path = []
        for p in self.points:
            path.append({
                "x": p.x,
                "y": p.y,
                "arc": False
            })
        return {
            "type": "Glass",
            "path": path,
            "refIndex": self.refractive_index
        }


class Blocker(OpticalObject):
    """遮挡物"""
    def __init__(self, p1: Point, p2: Point):
        super().__init__("Blocker", p1)
        self.p2 = p2

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "Blocker",
            "p1": self.position.to_dict(),
            "p2": self.p2.to_dict(),
        }


class RayOpticsScene:
    """Ray-Optics场景"""
    def __init__(self, name: str = "Optical Simulation",
                 width: int = 1200, height: int = 600):
        self.name = name
        self.width = width
        self.height = height
        self.objects: List[OpticalObject] = []

    def add_object(self, obj: OpticalObject):
        """添加光学对象"""
        self.objects.append(obj)
        return self

    def add_objects(self, objects: List[OpticalObject]):
        """批量添加光学对象"""
        self.objects.extend(objects)
        return self

    def to_json(self, indent: int = 2) -> str:
        """生成JSON字符串"""
        scene_dict = {
            "version": 5,
            "objs": [obj.to_dict() for obj in self.objects],
            "width": self.width,
            "height": self.height,
            "rayModeDensity": 0.1,
            "origin": {
                "x": 0,
                "y": 0
            },
            "scale": 1,
            "simulateColors": True
        }
        return json.dumps(scene_dict, indent=indent, ensure_ascii=False)

    def save(self, filename: str):
        """保存JSON文件"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(self.to_json())
        print(f"✓ 场景已保存: {filename}")
        return self


def create_example_scene() -> RayOpticsScene:
    """创建示例场景：双缝干涉"""
    scene = RayOpticsScene("双缝干涉实验")

    # 添加平行光源
    light = ParallelLight(
        position=Point(100, 300),
        direction=Point(100, 0),
        wavelength=550,
        brightness=0.8
    )
    scene.add_object(light)

    # 添加双缝屏障
    scene.add_object(Blocker(Point(300, 0), Point(300, 250)))
    scene.add_object(Blocker(Point(300, 350), Point(300, 600)))
    scene.add_object(Blocker(Point(300, 280), Point(300, 320)))

    # 添加观测屏
    scene.add_object(Blocker(Point(800, 0), Point(800, 600)))

    return scene


def create_lens_system() -> RayOpticsScene:
    """创建透镜系统示例"""
    scene = RayOpticsScene("透镜成像系统")

    # 点光源
    scene.add_object(PointSource(
        position=Point(200, 300),
        wavelength=550,
        brightness=0.8
    ))

    # 会聚透镜
    scene.add_object(IdealLens(
        p1=Point(500, 200),
        p2=Point(500, 400),
        focal_length=150
    ))

    # 观测屏
    scene.add_object(Blocker(Point(900, 100), Point(900, 500)))

    return scene


def create_prism_dispersion() -> RayOpticsScene:
    """创建三棱镜色散示例"""
    scene = RayOpticsScene("三棱镜色散")

    # 白光光源（使用多个波长）
    for i, wavelength in enumerate([650, 550, 450]):  # 红绿蓝
        scene.add_object(ParallelLight(
            position=Point(100, 300 + i * 0.1),
            direction=Point(100, 0),
            wavelength=wavelength,
            brightness=0.6
        ))

    # 三棱镜
    prism = GlassRefractor(
        points=[
            Point(400, 400),
            Point(600, 300),
            Point(400, 200),
        ],
        refractive_index=1.5
    )
    scene.add_object(prism)

    return scene


def generate_light_trajectory(
    base_scene: 'RayOpticsScene',
    trajectory: List[Point],
    light_type: type = PointSource,
    light_params: Dict[str, Any] = None,
    output_prefix: str = "trajectory",
    auto_convert: bool = False
) -> List[str]:
    """
    为光源轨迹生成一系列场景图片

    参数:
        base_scene: 基础场景（包含光学元件，但无光源）
        trajectory: 光源位置数组
        light_type: 光源类型（PointSource 或 ParallelLight）
        light_params: 光源参数字典（wavelength, brightness等，不包括position）
        output_prefix: 输出文件名前缀
        auto_convert: 是否自动转换为HTML和图片

    返回:
        生成的JSON文件路径列表
    """
    if light_params is None:
        light_params = {"wavelength": 650, "brightness": 0.8}

    json_files = []

    # 确保输出目录存在
    os.makedirs("output/json", exist_ok=True)

    print(f"\n生成光源轨迹: {len(trajectory)} 个位置")
    print("=" * 60)

    for i, position in enumerate(trajectory, 1):
        # 创建新场景（复制基础场景）
        scene = RayOpticsScene(
            name=f"{base_scene.name} - Frame {i}",
            width=base_scene.width,
            height=base_scene.height
        )

        # 复制基础场景中的所有光学元件
        for obj in base_scene.objects:
            scene.add_object(obj)

        # 添加当前位置的光源
        if light_type == PointSource:
            light = PointSource(position=position, **light_params)
        elif light_type == ParallelLight:
            light = ParallelLight(position=position, **light_params)
        else:
            raise ValueError(f"不支持的光源类型: {light_type}")

        scene.add_object(light)

        # 保存JSON
        filename = f"output/json/{output_prefix}_{i:03d}.json"
        scene.save(filename)
        json_files.append(filename)

    print("=" * 60)
    print(f"✓ 已生成 {len(json_files)} 个场景文件\n")

    # 自动转换为HTML和图片
    if auto_convert:
        print("正在转换为HTML和图片...")
        from json_to_image import json_to_image
        json_to_image()
    else:
        print("提示: 运行 'python json_to_image.py' 生成HTML和图片")

    return json_files


if __name__ == "__main__":
    print("Ray-Optics 控制器示例\n")
    print("=" * 50)

    # 创建输出目录
    os.makedirs("output/json", exist_ok=True)

    # 示例1: 双缝干涉
    print("\n1. 生成双缝干涉场景...")
    scene1 = create_example_scene()
    scene1.save("output/json/double_slit.json")

    # 示例2: 透镜系统
    print("\n2. 生成透镜系统场景...")
    scene2 = create_lens_system()
    scene2.save("output/json/lens_system.json")

    # 示例3: 三棱镜色散
    print("\n3. 生成三棱镜色散场景...")
    scene3 = create_prism_dispersion()
    scene3.save("output/json/prism_dispersion.json")

    print("\n" + "=" * 50)
    print("\n查看生成的场景:")
    print("1. 运行: python json_to_image.py")
    print("   (一键生成HTML和图片)")
    print("2. 或访问 https://phydemo.app/ray-optics/simulator/")
    print("   手动加载 output/json/*.json 文件")
    print("\n" + "=" * 50)
