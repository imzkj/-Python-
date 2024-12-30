import cv2
import numpy as np

def is_same_image(image_path1, image_path2, threshold=0.99):
    """
    判断两张图片是否相同（通过像素相似度）。
    :param image_path1: 图片1路径
    :param image_path2: 图片2路径
    :param threshold: 相似度阈值（1.0 完全相同）
    :return: True 表示图片相同，False 表示图片不同
    """
    img1 = cv2.imread(image_path1, cv2.IMREAD_GRAYSCALE)
    img2 = cv2.imread(image_path2, cv2.IMREAD_GRAYSCALE)

    # 如果图片大小不同，调整到相同尺寸
    if img1.shape != img2.shape:
        img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))

    # 计算结构相似度
    score = np.sum((img1 == img2)) / img1.size
    return score >= threshold

# 示例调用
image1 = "K:\\测试1\\1.jpg"
image2 = "K:\\测试1\\2.png"
if is_same_image(image1, image2):
    print("两张图片是相同的")
else:
    print("两张图片不同")
