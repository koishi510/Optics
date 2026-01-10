# Ray-Optics Python 控制器

通过Python代码或外部JSON文件生成[Ray-Optics](https://phydemo.app/ray-optics/simulator/)光学仿真场景。

## 特性

- ✅ Python API创建光学场景
- ✅ 支持主要光学元件（光源、镜子、透镜、棱镜等）
- ✅ 一键转换JSON为HTML查看器和PNG截图
- ✅ **光源轨迹动画生成** - 模拟移动光源
- ✅ **外部文件支持** - 从JSON文件加载场景和轨迹

## 快速开始

先在仓库内运行

```bash
git clone https://github.com/ricktu288/ray-optics.git
```

然后按照其文档本地搭建仿真器

### 方式1：使用外部JSON文件

```bash
# 1. 生成轨迹文件
python create_trajectory.py -t line -o my_traj.json \
    --start 100 300 --end 600 300 -n 20

# 2. 从外部文件生成动画
python generate_trajectory.py example_scene.json my_traj.json \
    -o my_animation -w 650 -b 0.9

# 3. 转换为图片
python json_to_image.py

# 4. 查看结果
open output/index.html
```

### 方式2：使用Python编程

```python
from ray_optics_controller import *

# 创建场景
scene = RayOpticsScene("我的光学实验", width=1200, height=600)

# 添加点光源
scene.add_object(PointSource(
    position=Point(200, 300),
    wavelength=550,    # 绿光 (nm)
    brightness=0.8
))

# 添加平面镜
scene.add_object(FlatMirror(
    p1=Point(400, 200),
    p2=Point(500, 400)
))

# 保存JSON
scene.save("output/json/my_scene.json")
```

### 2. 一键转换为HTML和图片

```bash
# 方法1: 使用一键转换工具（推荐）
python json_to_image.py

# 方法2: 手动加载JSON
# 访问 https://phydemo.app/ray-optics/simulator/
# 点击菜单 ☰ → Open → 选择JSON文件
```

### 3. 查看结果

```bash
# 打开索引页面（查看所有场景）
open output/index.html
```

## 运行示例

```bash
# 生成3个基础示例
python ray_optics_controller.py

# 生成6个高级示例
python example_usage.py

# 生成3个快速示例
python quickstart.py

# 生成光源轨迹动画（96帧）
python trajectory_example.py

# 一键转换所有JSON为HTML和图片
python json_to_image.py
```

## 支持的光学元件

| 类                 | 描述        | 示例                                                      |
| ------------------ | ----------- | --------------------------------------------------------- |
| **PointSource**    | 点光源      | `PointSource(Point(100, 300), wavelength=650)`            |
| **ParallelLight**  | 平行光束    | `ParallelLight(Point(100, 300), direction=Point(1, 0))`   |
| **FlatMirror**     | 平面镜      | `FlatMirror(Point(300, 200), Point(400, 400))`            |
| **CurvedMirror**   | 抛物面镜    | `CurvedMirror(p1, p2, p3)`                                |
| **IdealLens**      | 理想透镜    | `IdealLens(p1, p2, focal_length=100)`                     |
| **GlassRefractor** | 玻璃/棱镜   | `GlassRefractor([Point(...), ...], refractive_index=1.5)` |
| **Blocker**        | 遮挡物/屏幕 | `Blocker(Point(800, 0), Point(800, 600))`                 |

## 项目结构

```
├── ray_optics_controller.py   # 核心库（含轨迹生成函数）
├── json_to_image.py            # JSON→HTML+图片转换工具
├── generate_trajectory.py      # 外部文件轨迹生成工具
├── create_trajectory.py        # 轨迹文件生成辅助工具
├── screenshot_helper.py        # HTML生成和截图
├── compress_json.js            # JSON压缩（Node.js）
├── example_usage.py            # 高级示例（6个场景）
├── quickstart.py               # 快速示例（3个场景）
├── trajectory_example.py       # 光源轨迹示例（5个动画，96帧）
├── demo_trajectory.py          # 轨迹快速演示（10帧）
├── test_validation.py          # JSON验证
├── README.md                   # 项目文档
├── TRAJECTORY_GUIDE.md         # 轨迹功能详细指南
├── example_scene.json          # 示例场景文件
├── example_trajectory.json     # 示例轨迹文件
└── output/                     # 输出目录
    ├── json/                   # JSON场景文件
    ├── html/                   # HTML查看器
    ├── images/                 # PNG截图
    └── index.html              # 索引页面
```

## 工作流程

```
1. 编写Python代码
   └─> 生成JSON场景 (output/json/)

2. 运行 json_to_image.py
   ├─> 生成HTML查看器 (output/html/)
   └─> 自动截图 (output/images/)

3. 打开 output/index.html
   └─> 查看所有场景
```

## 依赖

### 基础功能（生成JSON）

- Python 3.6+
- 无需额外依赖

### HTML和截图（json_to_image.py）

- **Node.js**: `npm install json-url @babel/runtime`
- **Python依赖**:
  - Selenium: `pip install selenium` 或 `conda install selenium`
  - Pillow: `pip install pillow` 或 `conda install pillow`
- **Chrome浏览器**

**注意**：如果使用conda环境，请确保在激活的环境中安装所有Python依赖：

```bash
conda activate your_env
conda install pillow selenium
```

## API文档

### Point(x, y)

坐标点

### RayOpticsScene(name, width=1200, height=600)

场景容器

**方法：**

- `add_object(obj)` - 添加单个对象
- `add_objects([obj1, obj2, ...])` - 批量添加
- `to_json(indent=2)` - 生成JSON字符串
- `save(filename)` - 保存到文件

### 光源参数

```python
PointSource(
    position=Point(x, y),
    wavelength=550,    # 380-750nm (可见光)
    brightness=0.5     # 0.0-1.0
)

ParallelLight(
    position=Point(x, y),
    direction=Point(dx, dy),
    wavelength=550,
    brightness=0.5,
    width=50           # 光束宽度
)
```

## 示例场景

```python
# 透镜聚焦
scene = RayOpticsScene("透镜聚焦")
scene.add_object(PointSource(Point(200, 300), wavelength=550))
scene.add_object(IdealLens(Point(500, 200), Point(500, 400), focal_length=150))
scene.save("output/json/lens_focus.json")

# 三棱镜色散
scene = RayOpticsScene("彩虹")
for wl in [650, 550, 450]:  # 红绿蓝
    scene.add_object(ParallelLight(Point(100, 300), Point(1, 0), wavelength=wl))

prism = GlassRefractor([Point(400, 400), Point(600, 300), Point(400, 200)],
                       refractive_index=1.5)
scene.add_object(prism)
scene.save("output/json/rainbow.json")
```

## 光源轨迹动画

生成移动光源的连续帧，可用于制作动画。支持两种方式：

### 方式1：Python API（适合编程生成）

```python
from ray_optics_controller import *

# 创建基础场景（只有光学元件，无光源）
scene = RayOpticsScene("光源移动")
scene.add_object(IdealLens(Point(600, 200), Point(600, 400), focal_length=150))
scene.add_object(Blocker(Point(1000, 100), Point(1000, 500)))

# 定义光源移动轨迹
trajectory = [Point(100 + i * 30, 300) for i in range(20)]

# 生成轨迹帧
generate_light_trajectory(
    base_scene=scene,
    trajectory=trajectory,
    light_type=PointSource,
    light_params={"wavelength": 650, "brightness": 0.8},
    output_prefix="moving_light"
)
```

### 方式2：外部JSON文件（适合手动设计场景）

**第1步：创建场景JSON**（在ray-optics网页上设计并导出，或使用Python生成）

**第2步：创建轨迹JSON**

```bash
# 使用辅助工具生成轨迹文件
python create_trajectory.py -t line -o my_traj.json \
    --start 100 300 --end 600 300 -n 20

# 或手动编写JSON
# [{"x": 100, "y": 300}, {"x": 130, "y": 300}, ...]
```

**第3步：生成轨迹序列**

```bash
python generate_trajectory.py scene.json my_traj.json \
    -o my_animation -w 650 -b 0.9
```

**第4步：转换为图片**

```bash
python json_to_image.py
```

### 轨迹类型示例

使用 `create_trajectory.py` 快速生成：

```bash
# 水平直线
python create_trajectory.py -t line -o horizontal.json \
    --start 100 300 --end 600 300 -n 20

# 完整圆周
python create_trajectory.py -t circle -o circle.json \
    --center 500 400 --radius 150 -n 36

# 圆弧（-60°到+60°）
python create_trajectory.py -t circle -o arc.json \
    --center 500 400 --radius 200 -n 20 \
    --start-angle -60 --end-angle 60

# 网格扫描
python create_trajectory.py -t grid -o grid.json \
    --x-range 100 500 --y-range 100 500 \
    --x-steps 10 --y-steps 5 --zigzag
```

## 常见问题

**Q: JSON在仿真器中无法加载？**
A: 运行 `python test_validation.py` 检查格式是否正确。

**Q: 如何批量转换JSON？**
A: 运行 `python json_to_image.py` 自动转换所有JSON文件。

**Q: HTML文件无法加载场景？**
A: 确保已安装Node.js依赖：`npm install json-url @babel/runtime`

**Q: 自动截图失败？**
A: 确保已安装Selenium和Chrome浏览器。

**Q: 光线不可见？**
A: 检查：1）亮度是否太低，2）波长是否在可见光范围（380-750nm），3）光源位置是否在场景内。

**Q: 截图中有顶部工具栏，如何去除？**
A: 默认已自动裁剪顶部75px。如需调整：

- 编辑 `json_to_image.py`，修改 `SCREENSHOT_CROP_TOP = 80`（数值越大裁剪越多）
- 或直接调用 `screenshot_with_selenium(..., crop_top=80)`

## 技术细节

### JSON格式

生成符合ray-optics v5格式的JSON文件。所有对象类型名称使用正确的驼峰命名：

- `PointSource`（不是"laser"）
- `Beam`（不是"parallel"）
- `Mirror`, `ParabolicMirror`, `IdealLens`, `Glass`, `Blocker`

### HTML场景加载

使用Node.js的 `json-url('lzma')` 库压缩场景数据，生成正确的URL hash格式（以`XQAAAA`开头），与ray-optics完全兼容。

### 目录结构

- `output/json/` - JSON场景文件（可手动加载）
- `output/html/` - HTML查看器（自动加载场景）
- `output/images/` - PNG截图（1920x1080）
- `output/index.html` - 索引页面（查看所有场景）

## 致谢

- Ray-Optics仿真器：https://github.com/ricktu288/ray-optics
- 在线演示：https://phydemo.app/ray-optics/simulator/
