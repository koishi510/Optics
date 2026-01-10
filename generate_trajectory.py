#!/usr/bin/env python3
"""
光源轨迹生成工具 - 从外部文件读取场景和轨迹
"""

import json
import os
import sys
import argparse
from typing import List, Dict, Any


def load_scene_json(scene_path: str) -> Dict[str, Any]:
    """加载场景JSON文件"""
    with open(scene_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_trajectory_json(trajectory_path: str) -> List[Dict[str, float]]:
    """
    加载轨迹JSON文件

    支持格式:
    1. 点数组: [{"x": 100, "y": 300}, {"x": 130, "y": 300}, ...]
    2. 分离格式: {"x": [100, 130, 160], "y": [300, 300, 300]}
    """
    with open(trajectory_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 格式1: 点数组
    if isinstance(data, list):
        return data

    # 格式2: 分离的x和y数组
    if isinstance(data, dict) and 'x' in data and 'y' in data:
        x_coords = data['x']
        y_coords = data['y']
        if len(x_coords) != len(y_coords):
            raise ValueError(f"x和y坐标数量不匹配: {len(x_coords)} vs {len(y_coords)}")
        return [{"x": x, "y": y} for x, y in zip(x_coords, y_coords)]

    raise ValueError(f"不支持的轨迹格式: {type(data)}")


def create_light_source(position: Dict[str, float], light_config: Dict[str, Any]) -> Dict[str, Any]:
    """创建光源对象"""
    light_type = light_config.get("type", "PointSource")

    if light_type == "PointSource":
        return {
            "type": "PointSource",
            "x": position["x"],
            "y": position["y"],
            "wavelength": str(light_config.get("wavelength", 550)),
            "brightness": str(light_config.get("brightness", 0.8))
        }
    elif light_type == "Beam":  # ParallelLight
        p1 = position
        width = light_config.get("width", 50)
        p2 = {"x": p1["x"], "y": p1["y"] + width}
        return {
            "type": "Beam",
            "p1": p1,
            "p2": p2,
            "wavelength": str(light_config.get("wavelength", 550)),
            "brightness": str(light_config.get("brightness", 0.8))
        }
    else:
        raise ValueError(f"不支持的光源类型: {light_type}")


def generate_trajectory_scenes(
    base_scene: Dict[str, Any],
    trajectory: List[Dict[str, float]],
    light_config: Dict[str, Any],
    output_dir: str,
    output_prefix: str
) -> List[str]:
    """生成轨迹场景序列"""

    os.makedirs(output_dir, exist_ok=True)
    json_files = []

    print(f"\n生成光源轨迹: {len(trajectory)} 个位置")
    print("=" * 60)

    for i, position in enumerate(trajectory, 1):
        # 复制基础场景
        scene = {
            "version": base_scene.get("version", 5),
            "objs": base_scene.get("objs", []).copy(),
            "width": base_scene.get("width", 1200),
            "height": base_scene.get("height", 600),
            "rayModeDensity": base_scene.get("rayModeDensity", 0.1),
            "origin": base_scene.get("origin", {"x": 0, "y": 0}),
            "scale": base_scene.get("scale", 1),
            "simulateColors": base_scene.get("simulateColors", True)
        }

        # 添加光源
        light = create_light_source(position, light_config)
        scene["objs"].append(light)

        # 保存JSON
        filename = os.path.join(output_dir, f"{output_prefix}_{i:03d}.json")
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(scene, f, indent=2, ensure_ascii=False)

        json_files.append(filename)
        print(f"✓ 场景已保存: {filename}")

    print("=" * 60)
    print(f"✓ 已生成 {len(json_files)} 个场景文件\n")

    return json_files


def main():
    parser = argparse.ArgumentParser(
        description='从外部文件生成光源轨迹动画',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例用法:

  # 基本用法
  python generate_trajectory.py scene.json trajectory.json

  # 指定输出前缀
  python generate_trajectory.py scene.json trajectory.json -o my_animation

  # 指定光源参数
  python generate_trajectory.py scene.json trajectory.json -w 650 -b 0.9

  # 使用平行光
  python generate_trajectory.py scene.json trajectory.json -t Beam --width 80

  # 自动转换为图片
  python generate_trajectory.py scene.json trajectory.json --convert

轨迹文件格式 (trajectory.json):

  格式1 - 点数组:
  [
    {"x": 100, "y": 300},
    {"x": 130, "y": 300},
    {"x": 160, "y": 300}
  ]

  格式2 - 分离坐标:
  {
    "x": [100, 130, 160, 190],
    "y": [300, 300, 300, 300]
  }
        '''
    )

    parser.add_argument('scene', help='基础场景JSON文件路径（不含光源）')
    parser.add_argument('trajectory', help='轨迹数据JSON文件路径')
    parser.add_argument('-o', '--output', default='trajectory',
                        help='输出文件名前缀（默认: trajectory）')
    parser.add_argument('-d', '--dir', default='output/json',
                        help='输出目录（默认: output/json）')
    parser.add_argument('-t', '--type', choices=['PointSource', 'Beam'],
                        default='PointSource',
                        help='光源类型（默认: PointSource）')
    parser.add_argument('-w', '--wavelength', type=float, default=550,
                        help='波长(nm)（默认: 550）')
    parser.add_argument('-b', '--brightness', type=float, default=0.8,
                        help='亮度(0-1)（默认: 0.8）')
    parser.add_argument('--width', type=float, default=50,
                        help='平行光束宽度（仅用于Beam类型，默认: 50）')
    parser.add_argument('--convert', action='store_true',
                        help='自动转换为HTML和图片')

    args = parser.parse_args()

    # 检查文件存在
    if not os.path.exists(args.scene):
        print(f"❌ 错误: 场景文件不存在: {args.scene}")
        sys.exit(1)

    if not os.path.exists(args.trajectory):
        print(f"❌ 错误: 轨迹文件不存在: {args.trajectory}")
        sys.exit(1)

    print("=" * 60)
    print("光源轨迹生成工具")
    print("=" * 60)

    # 加载文件
    print(f"\n加载场景: {args.scene}")
    base_scene = load_scene_json(args.scene)
    print(f"  场景尺寸: {base_scene.get('width', '?')}x{base_scene.get('height', '?')}")
    print(f"  对象数量: {len(base_scene.get('objs', []))}")

    print(f"\n加载轨迹: {args.trajectory}")
    trajectory = load_trajectory_json(args.trajectory)
    print(f"  轨迹点数: {len(trajectory)}")
    print(f"  起点: ({trajectory[0]['x']}, {trajectory[0]['y']})")
    print(f"  终点: ({trajectory[-1]['x']}, {trajectory[-1]['y']})")

    # 光源配置
    light_config = {
        "type": args.type,
        "wavelength": args.wavelength,
        "brightness": args.brightness,
    }
    if args.type == "Beam":
        light_config["width"] = args.width

    print(f"\n光源配置:")
    print(f"  类型: {args.type}")
    print(f"  波长: {args.wavelength} nm")
    print(f"  亮度: {args.brightness}")
    if args.type == "Beam":
        print(f"  宽度: {args.width}")

    # 生成场景
    json_files = generate_trajectory_scenes(
        base_scene,
        trajectory,
        light_config,
        args.dir,
        args.output
    )

    # 自动转换
    if args.convert:
        print("正在转换为HTML和图片...")
        try:
            from json_to_image import json_to_image
            json_to_image()
        except Exception as e:
            print(f"⚠ 转换失败: {e}")
            print("提示: 手动运行 'python json_to_image.py'")
    else:
        print("提示: 运行 'python json_to_image.py' 生成HTML和图片")

    print("\n" + "=" * 60)
    print("✓ 完成!")
    print("=" * 60)


if __name__ == "__main__":
    main()
