#!/bin/bash
# 完整演示：从外部文件生成轨迹动画

echo "=========================================="
echo "外部文件轨迹生成完整演示"
echo "=========================================="

# 第1步：生成轨迹文件
echo ""
echo "第1步：生成轨迹文件"
echo "------------------------------------------"

echo "生成水平轨迹..."
python create_trajectory.py -t line -o demo_horizontal.json \
    --start 100 300 --end 500 300 -n 12

echo ""
echo "生成圆周轨迹..."
python create_trajectory.py -t circle -o demo_circle.json \
    --center 500 400 --radius 120 -n 18

# 第2步：使用示例场景生成动画
echo ""
echo "第2步：生成动画序列"
echo "------------------------------------------"

echo "生成水平移动动画..."
python generate_trajectory.py example_scene.json demo_horizontal.json \
    -o demo_h -w 650 -b 0.9

echo ""
echo "生成圆周运动动画..."
python generate_trajectory.py example_scene.json demo_circle.json \
    -o demo_c -w 450 -b 0.85

# 第3步：统计生成结果
echo ""
echo "=========================================="
echo "✓ 完成！"
echo "=========================================="
echo ""
echo "生成统计："
echo "  水平轨迹帧数: $(ls -1 output/json/demo_h_*.json 2>/dev/null | wc -l)"
echo "  圆周轨迹帧数: $(ls -1 output/json/demo_c_*.json 2>/dev/null | wc -l)"
echo ""
echo "下一步："
echo "  1. 运行: python json_to_image.py"
echo "  2. 打开: output/index.html"
echo ""
echo "=========================================="
