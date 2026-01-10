#!/usr/bin/env python3
"""
轨迹生成辅助工具 - 快速创建轨迹JSON文件
"""

import json
import math
import argparse


def generate_linear_trajectory(start_x, start_y, end_x, end_y, n_points):
    """生成直线轨迹"""
    trajectory = []
    for i in range(n_points):
        t = i / (n_points - 1) if n_points > 1 else 0
        x = start_x + (end_x - start_x) * t
        y = start_y + (end_y - start_y) * t
        trajectory.append({"x": x, "y": y})
    return trajectory


def generate_circular_trajectory(center_x, center_y, radius, n_points, start_angle=0, end_angle=None):
    """生成圆周或圆弧轨迹"""
    if end_angle is None:
        end_angle = start_angle + 2 * math.pi

    trajectory = []
    for i in range(n_points):
        t = i / n_points
        angle = start_angle + (end_angle - start_angle) * t
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        trajectory.append({"x": x, "y": y})
    return trajectory


def generate_grid_trajectory(x_start, x_end, x_steps, y_start, y_end, y_steps, zigzag=False):
    """生成网格扫描轨迹"""
    trajectory = []

    x_values = [x_start + (x_end - x_start) * i / (x_steps - 1) for i in range(x_steps)]
    y_values = [y_start + (y_end - y_start) * i / (y_steps - 1) for i in range(y_steps)]

    for j, y in enumerate(y_values):
        xs = x_values if not zigzag or j % 2 == 0 else reversed(x_values)
        for x in xs:
            trajectory.append({"x": x, "y": y})

    return trajectory


def main():
    parser = argparse.ArgumentParser(
        description='生成轨迹JSON文件',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:

  # 水平直线（10个点）
  python create_trajectory.py -t line -o horizontal.json \\
      --start 100 300 --end 500 300 -n 10

  # 垂直直线（20个点）
  python create_trajectory.py -t line -o vertical.json \\
      --start 300 100 --end 300 500 -n 20

  # 对角线（15个点）
  python create_trajectory.py -t line -o diagonal.json \\
      --start 100 100 --end 800 500 -n 15

  # 完整圆周（36个点）
  python create_trajectory.py -t circle -o circle.json \\
      --center 500 400 --radius 150 -n 36

  # 圆弧（从-60到+60度，20个点）
  python create_trajectory.py -t circle -o arc.json \\
      --center 500 400 --radius 200 -n 20 \\
      --start-angle -60 --end-angle 60

  # 网格扫描（5x5）
  python create_trajectory.py -t grid -o grid.json \\
      --x-range 100 500 --y-range 100 500 \\
      --x-steps 5 --y-steps 5

  # Z字形网格扫描
  python create_trajectory.py -t grid -o zigzag.json \\
      --x-range 100 500 --y-range 100 500 \\
      --x-steps 10 --y-steps 5 --zigzag
        '''
    )

    parser.add_argument('-t', '--type', required=True,
                        choices=['line', 'circle', 'grid'],
                        help='轨迹类型')
    parser.add_argument('-o', '--output', required=True,
                        help='输出JSON文件路径')
    parser.add_argument('-n', '--n-points', type=int, default=20,
                        help='点数（默认: 20）')
    parser.add_argument('-f', '--format', choices=['array', 'separated'],
                        default='array',
                        help='输出格式：array=[{x,y}], separated={x:[],y:[]}（默认: array）')

    # 直线参数
    line_group = parser.add_argument_group('直线轨迹参数')
    line_group.add_argument('--start', nargs=2, type=float, metavar=('X', 'Y'),
                            help='起点坐标 (x y)')
    line_group.add_argument('--end', nargs=2, type=float, metavar=('X', 'Y'),
                            help='终点坐标 (x y)')

    # 圆周参数
    circle_group = parser.add_argument_group('圆周轨迹参数')
    circle_group.add_argument('--center', nargs=2, type=float, metavar=('X', 'Y'),
                              help='圆心坐标 (x y)')
    circle_group.add_argument('--radius', type=float,
                              help='半径')
    circle_group.add_argument('--start-angle', type=float, default=0,
                              help='起始角度（度数，0度为右侧，默认: 0）')
    circle_group.add_argument('--end-angle', type=float,
                              help='结束角度（度数，默认: 360）')

    # 网格参数
    grid_group = parser.add_argument_group('网格扫描参数')
    grid_group.add_argument('--x-range', nargs=2, type=float, metavar=('MIN', 'MAX'),
                            help='X范围 (min max)')
    grid_group.add_argument('--y-range', nargs=2, type=float, metavar=('MIN', 'MAX'),
                            help='Y范围 (min max)')
    grid_group.add_argument('--x-steps', type=int, default=5,
                            help='X方向步数（默认: 5）')
    grid_group.add_argument('--y-steps', type=int, default=5,
                            help='Y方向步数（默认: 5）')
    grid_group.add_argument('--zigzag', action='store_true',
                            help='启用Z字形扫描')

    args = parser.parse_args()

    # 生成轨迹
    trajectory = None

    if args.type == 'line':
        if not args.start or not args.end:
            parser.error("直线轨迹需要 --start 和 --end 参数")
        trajectory = generate_linear_trajectory(
            args.start[0], args.start[1],
            args.end[0], args.end[1],
            args.n_points
        )

    elif args.type == 'circle':
        if not args.center or not args.radius:
            parser.error("圆周轨迹需要 --center 和 --radius 参数")
        start_rad = math.radians(args.start_angle)
        end_rad = math.radians(args.end_angle) if args.end_angle is not None else None
        trajectory = generate_circular_trajectory(
            args.center[0], args.center[1],
            args.radius,
            args.n_points,
            start_rad, end_rad
        )

    elif args.type == 'grid':
        if not args.x_range or not args.y_range:
            parser.error("网格扫描需要 --x-range 和 --y-range 参数")
        trajectory = generate_grid_trajectory(
            args.x_range[0], args.x_range[1], args.x_steps,
            args.y_range[0], args.y_range[1], args.y_steps,
            args.zigzag
        )

    # 转换格式
    if args.format == 'separated':
        output = {
            "x": [p["x"] for p in trajectory],
            "y": [p["y"] for p in trajectory]
        }
    else:
        output = trajectory

    # 保存
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"✓ 已生成轨迹文件: {args.output}")
    print(f"  轨迹类型: {args.type}")
    print(f"  点数: {len(trajectory)}")
    print(f"  格式: {args.format}")
    print(f"  起点: ({trajectory[0]['x']:.1f}, {trajectory[0]['y']:.1f})")
    print(f"  终点: ({trajectory[-1]['x']:.1f}, {trajectory[-1]['y']:.1f})")


if __name__ == "__main__":
    main()
