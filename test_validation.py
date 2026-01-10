#!/usr/bin/env python3
"""
测试生成的场景是否可以在ray-optics中正常工作
"""

from ray_optics_controller import *
import json
import os

def validate_json(filename):
    """验证JSON文件格式"""
    try:
        with open(filename, 'r') as f:
            data = json.load(f)

        # 检查必需字段
        required_fields = ['version', 'objs', 'width', 'height', 'origin', 'scale']
        missing = [f for f in required_fields if f not in data]

        if missing:
            print(f"❌ {filename}: 缺少字段 {missing}")
            return False

        if data['version'] != 5:
            print(f"❌ {filename}: 版本号错误 (应为5)")
            return False

        print(f"✓ {filename}: JSON格式正确")
        print(f"  - 版本: {data['version']}")
        print(f"  - 对象数: {len(data['objs'])}")
        print(f"  - 尺寸: {data['width']}x{data['height']}")

        return True
    except Exception as e:
        print(f"❌ {filename}: {e}")
        return False


def test_simple_scene():
    """创建并验证一个简单场景"""
    print("\n测试1: 创建简单场景")
    print("=" * 60)

    scene = RayOpticsScene("测试场景", width=800, height=600)

    # 添加光源和镜子
    scene.add_object(PointSource(Point(100, 300), wavelength=550))
    scene.add_object(FlatMirror(Point(300, 200), Point(400, 400)))

    # 保存
    test_file = "output/test_simple.json"
    scene.save(test_file)

    # 验证
    return validate_json(test_file)


def test_complex_scene():
    """创建并验证复杂场景"""
    print("\n测试2: 创建复杂场景")
    print("=" * 60)

    scene = RayOpticsScene("复杂测试", width=1400, height=700)

    # 多个光源
    scene.add_object(PointSource(Point(100, 350), wavelength=650))
    scene.add_object(ParallelLight(
        position=Point(100, 200),
        direction=Point(1, 0),
        wavelength=450,
        width=100
    ))

    # 光学元件
    scene.add_object(FlatMirror(Point(400, 100), Point(500, 200)))
    scene.add_object(IdealLens(Point(700, 250), Point(700, 450), focal_length=150))

    # 三棱镜
    prism = GlassRefractor(
        points=[Point(900, 500), Point(1100, 350), Point(900, 200)],
        refractive_index=1.52
    )
    scene.add_object(prism)

    # 遮挡物
    scene.add_object(Blocker(Point(1300, 100), Point(1300, 600)))

    test_file = "output/test_complex.json"
    scene.save(test_file)

    return validate_json(test_file)


def validate_all_scenes():
    """验证output目录中的所有场景"""
    print("\n测试3: 验证所有生成的场景")
    print("=" * 60)

    json_files = [f for f in os.listdir("output") if f.endswith('.json')]

    if not json_files:
        print("没有找到JSON文件")
        return False

    results = []
    for filename in sorted(json_files):
        filepath = os.path.join("output", filename)
        results.append(validate_json(filepath))
        print()

    success = sum(results)
    total = len(results)

    print("=" * 60)
    print(f"结果: {success}/{total} 个文件验证通过")

    return success == total


def print_usage_guide():
    """打印使用指南"""
    print("\n" + "=" * 60)
    print("如何在ray-optics中查看生成的场景:")
    print("=" * 60)
    print()
    print("方法1: 手动加载")
    print("1. 访问 https://phydemo.app/ray-optics/simulator/")
    print("2. 点击左上角的菜单图标 (☰)")
    print("3. 选择 'Open'")
    print("4. 选择 output/ 目录中的任意 .json 文件")
    print()
    print("方法2: 直接URL")
    print("使用 scene.get_simulator_url() 方法获取可直接访问的URL")
    print()
    print("示例:")
    scene = RayOpticsScene("示例")
    scene.add_object(PointSource(Point(200, 300)))
    scene.add_object(FlatMirror(Point(400, 200), Point(500, 400)))
    url = scene.get_simulator_url("example.json")
    print(f"URL前100字符: {url[:100]}...")
    print()


if __name__ == "__main__":
    print("Ray-Optics JSON格式验证测试")
    print("=" * 60)

    os.makedirs("output", exist_ok=True)

    # 运行测试
    test1 = test_simple_scene()
    test2 = test_complex_scene()
    test3 = validate_all_scenes()

    # 打印使用指南
    print_usage_guide()

    # 总结
    print("=" * 60)
    if test1 and test2 and test3:
        print("✓ 所有测试通过！")
        print("✓ JSON格式正确，可以在ray-optics中使用")
    else:
        print("❌ 部分测试失败")
    print("=" * 60)
