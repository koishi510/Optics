# 视频处理工具 - 使用指南

## 功能概述

`process_video_to_scenes()` 是一个封装的函数，可以：
1. 捕获视频中绿点的位置坐标
2. 根据坐标转换规则生成光学场景JSON文件
3. 自动生成对应的HTML和图片文件

## 快速开始

```python
from process_video_to_scenes import process_video_to_scenes

# 基本使用
result = process_video_to_scenes(
    json_template="output/json/test_00.json",
    video_path="video/test.mp4",
    num_samples=20,
    output_prefix="test"
)
```

## 函数参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `json_template` | str | 必需 | 模板JSON文件路径 |
| `video_path` | str | 必需 | 视频文件路径 |
| `num_samples` | int | 20 | 采样数量 |
| `output_prefix` | str | "scene" | 输出文件前缀 |
| `generate_images` | bool | True | 是否生成图片 |
| `crop_top` | int | 75 | 截图裁剪顶部像素 |
| `verbose` | bool | True | 是否显示详细信息 |

## 坐标转换规则

由于视频坐标系和JSON坐标系不同，函数会自动进行转换：

- **横坐标 (x)**：保持不变
- **纵坐标 (y)**：加上偏移量

偏移量计算公式：
```
y_offset = 模板光源y坐标 - 第一个捕获的y坐标
转换后y坐标 = 捕获的y坐标 + y_offset
```

### 示例

- 模板光源坐标：(400, 625)
- 第一个捕获坐标：(398, 556)
- 偏移量：625 - 556 = 69
- 转换后坐标：(398, 556 + 69) = (398, 625)

## 返回值

函数返回一个字典，包含生成的文件列表：

```python
{
    "json_files": ["output/json/test_01.json", ...],
    "html_files": ["output/html/test_01.html", ...],
    "image_files": ["output/images/test_01.png", ...]
}
```

## 输出目录结构

```
output/
├── json/          # JSON场景文件
│   ├── test_01.json
│   ├── test_02.json
│   └── ...
├── html/          # HTML可视化文件
│   ├── test_01.html
│   ├── test_02.html
│   └── ...
└── images/        # PNG截图
    ├── test_01.png
    ├── test_02.png
    └── ...
```

## 使用场景

### 1. 基本用法
```python
result = process_video_to_scenes(
    json_template="output/json/test_00.json",
    video_path="video/test.mp4",
    num_samples=20,
    output_prefix="test"
)
```

### 2. 快速模式（不生成图片）
```python
result = process_video_to_scenes(
    json_template="output/json/test_00.json",
    video_path="video/test.mp4",
    num_samples=10,
    output_prefix="quick",
    generate_images=False  # 跳过图片生成
)
```

### 3. 批量处理
```python
videos = [
    ("template1.json", "video1.mp4", "scene_a"),
    ("template2.json", "video2.mp4", "scene_b"),
]

for template, video, prefix in videos:
    result = process_video_to_scenes(
        json_template=template,
        video_path=video,
        output_prefix=prefix,
        verbose=False
    )
```

### 4. 自定义采样数量
```python
# 生成5个场景
result = process_video_to_scenes(
    json_template="output/json/test_00.json",
    video_path="video/test.mp4",
    num_samples=5,
    output_prefix="sparse"
)
```

## 工作流程

1. **读取模板** - 加载模板JSON文件，提取光源坐标
2. **视频扫描** - 扫描视频所有帧，找到包含绿点的帧
3. **均匀采样** - 从有效帧中均匀采样指定数量的坐标
4. **坐标转换** - 应用坐标转换规则
5. **生成文件** - 批量生成JSON、HTML和图片文件

## 依赖项

确保已安装以下依赖：
```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate

# 安装依赖
pip install opencv-python numpy selenium pillow
```

## 注意事项

1. **视频格式**：支持常见视频格式（MP4、AVI等）
2. **绿点检测**：使用HSV色彩空间检测绿色（H: 35-85, S: 50-255, V: 50-255）
3. **性能**：生成图片需要时间，可设置 `generate_images=False` 加快速度
4. **模板要求**：JSON模板中必须包含 `PointSource` 对象

## 相关文件

- `process_video_to_scenes.py` - 主函数文件
- `example_video_processing.py` - 使用示例
- `detect_green_dot.py` - 绿点检测模块
- `batch_generate_json.py` - JSON批量生成模块

## 问题排查

### 1. 没有找到绿点
- 检查视频中是否真的有绿色物体
- 调整HSV检测范围（修改 `detect_green_in_frame` 函数）

### 2. 坐标偏移不正确
- 确认模板JSON中光源坐标是否正确
- 检查视频第一帧的绿点位置

### 3. 图片生成失败
- 确保已安装 selenium 和 pillow
- 检查浏览器驱动是否正确配置

## 更多示例

查看 `example_video_processing.py` 获取更多使用示例。
