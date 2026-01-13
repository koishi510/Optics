import json
import os

def batch_generate_json_files():
    """
    根据捕获的绿点坐标批量生成JSON文件
    坐标转换规则：
    - 横坐标不变
    - 纵坐标加上偏移量（test_00中光源y坐标 - 第一个捕获的y坐标）
    """

    # 读取模板文件
    template_path = "output/json/test_00.json"
    with open(template_path, 'r', encoding='utf-8') as f:
        template = json.load(f)

    # 读取捕获的坐标数据
    coordinates_path = "output/json/green_dot_coordinates.json"
    with open(coordinates_path, 'r', encoding='utf-8') as f:
        coord_data = json.load(f)

    coordinates = coord_data['coordinates']

    # 获取test_00中光源的坐标
    light_source = template['objs'][0]
    template_y = light_source['y']  # 625

    # 获取第一个捕获的纵坐标
    first_captured_y = coordinates[0]['y']  # 556

    # 计算纵坐标偏移量
    y_offset = template_y - first_captured_y  # 625 - 556 = 69

    print(f"模板光源坐标: ({light_source['x']}, {template_y})")
    print(f"第一个捕获坐标: ({coordinates[0]['x']}, {first_captured_y})")
    print(f"纵坐标偏移量: {y_offset}")
    print(f"\n开始生成文件...\n")

    # 确保输出目录存在
    output_dir = "output/json"
    os.makedirs(output_dir, exist_ok=True)

    # 为每个坐标生成对应的JSON文件
    for i, coord in enumerate(coordinates, start=1):
        # 创建新的JSON对象（深拷贝模板）
        new_json = json.loads(json.dumps(template))

        # 更新光源坐标
        new_x = coord['x']
        new_y = coord['y'] + y_offset

        new_json['objs'][0]['x'] = new_x
        new_json['objs'][0]['y'] = new_y

        # 生成文件名
        output_filename = f"test_{i:02d}.json"
        output_path = os.path.join(output_dir, output_filename)

        # 保存文件
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(new_json, f, indent=4, ensure_ascii=False)

        print(f"生成 {output_filename}: 帧 {coord['frame']}, 坐标 ({new_x}, {new_y}), 原始 ({coord['x']}, {coord['y']})")

    print(f"\n完成! 共生成 {len(coordinates)} 个文件 (test_01.json ~ test_{len(coordinates):02d}.json)")


if __name__ == "__main__":
    batch_generate_json_files()
