import cv2
import numpy as np
import json
import os

def detect_green_in_frame(frame):
    """检测单帧中的绿点位置"""
    # 转换到HSV色彩空间
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # 定义绿色的HSV范围
    lower_green = np.array([35, 50, 50])
    upper_green = np.array([85, 255, 255])

    # 创建掩码
    mask = cv2.inRange(hsv, lower_green, upper_green)

    # 形态学操作，去除噪点
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    # 查找轮廓
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        # 找到最大的轮廓（假设这是绿点）
        largest_contour = max(contours, key=cv2.contourArea)

        # 计算轮廓的中心点
        M = cv2.moments(largest_contour)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            return (cx, cy)
    return None


def detect_green_dot(video_path, output_json=None, num_samples=20):
    """
    检测视频中绿点的位置并生成坐标数组
    先找到所有有绿点的帧，然后从中均匀采样

    Args:
        video_path: 视频文件路径
        output_json: 输出JSON文件路径（可选）
        num_samples: 采样数量（默认20）

    Returns:
        坐标数组列表 [(x, y), ...]
    """
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print(f"无法打开视频文件: {video_path}")
        return []

    # 获取视频信息
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"视频信息: {total_frames} 帧, {fps} FPS")

    # 第一步：找到所有有绿点的帧
    print("\n第一步: 扫描所有帧，查找绿点...")
    valid_frames = []
    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        if frame_count % 50 == 0:
            print(f"  扫描进度: {frame_count}/{total_frames} 帧")

        pos = detect_green_in_frame(frame)
        if pos is not None:
            valid_frames.append((frame_count, pos))

    print(f"\n找到 {len(valid_frames)} 帧包含绿点")

    if len(valid_frames) == 0:
        print("警告: 没有找到绿点!")
        cap.release()
        return []

    # 第二步：从有效帧中均匀采样
    print(f"\n第二步: 从有效帧中采样 {num_samples} 个点...")
    coordinates = []

    if len(valid_frames) <= num_samples:
        # 如果有效帧数少于等于采样数，全部使用
        coordinates = [{"frame": f, "x": x, "y": y} for f, (x, y) in valid_frames]
        print(f"有效帧数({len(valid_frames)})少于采样数({num_samples})，使用全部有效帧")
    else:
        # 均匀采样
        step = len(valid_frames) / num_samples
        for i in range(num_samples):
            idx = int(i * step)
            frame_num, (x, y) = valid_frames[idx]
            coordinates.append({"frame": frame_num, "x": x, "y": y})

    cap.release()
    print(f"\n处理完成! 共采样 {len(coordinates)} 个坐标点")

    # 保存到JSON文件
    if output_json:
        with open(output_json, 'w', encoding='utf-8') as f:
            json.dump({
                "video": os.path.basename(video_path),
                "total_frames": frame_count,
                "sampled_frames": len(coordinates),
                "fps": fps,
                "coordinates": coordinates
            }, f, indent=2, ensure_ascii=False)
        print(f"坐标数据已保存到: {output_json}")

    return coordinates


if __name__ == "__main__":
    video_path = "video/test.mp4"
    output_json = "output/json/green_dot_coordinates.json"

    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_json), exist_ok=True)

    print("开始检测视频中的绿点位置...")
    coordinates = detect_green_dot(video_path, output_json, num_samples=20)

    # 打印所有有效坐标
    valid_coords = [c for c in coordinates if c["x"] is not None]
    print(f"\n检测到 {len(valid_coords)} 个有效坐标点")
    if valid_coords:
        print("\n所有坐标:")
        for coord in valid_coords:
            print(f"  帧 {coord['frame']}: ({coord['x']}, {coord['y']})")
