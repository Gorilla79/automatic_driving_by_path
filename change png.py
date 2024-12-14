import cv2
import numpy as np
import matplotlib.pyplot as plt
import os

# 정확한 이미지 경로 지정
image_path = r"D:\capstone\24_12_13\415inside.png"  # 파일 경로를 수정
if not os.path.exists(image_path):
    print(f"File not found: {image_path}")
    exit()

# 이미지 불러오기
map_img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

if map_img is None:
    print(f"Failed to load image from {image_path}")
    exit()

# 색상 변환
color_map = cv2.cvtColor(map_img, cv2.COLOR_GRAY2BGR)

# 그레이스케일 범위 정의
gray_min, gray_max = 200, 210  # 회색 영역
white_min = 254  # 흰색 최소값

# 회색을 초록색으로 변환
color_map[(map_img >= gray_min) & (map_img <= gray_max)] = [0, 255, 0]  # 초록색

# 흰색을 노란색으로 변환 -> 연초록색이 나와서 흰색으로 변경
color_map[map_img >= white_min] = [255, 255, 255]  # 흰색

# 결과 표시
plt.figure(figsize=(10, 10))
plt.imshow(cv2.cvtColor(color_map, cv2.COLOR_BGR2RGB))
plt.title("Gray to Green, White to Yellow")
plt.axis("off")
plt.show()

# 결과 저장
output_path = r"D:\capstone\24_12_13\processed_415inside.png"
cv2.imwrite(output_path, color_map)
print(f"Processed image saved to {output_path}")