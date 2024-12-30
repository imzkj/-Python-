import cv2

def is_same_image(image_path1, image_path2, threshold=0.75):
    """
    判断两张图片是否相同（通过特征点匹配）。
    :param image_path1: 图片1路径
    :param image_path2: 图片2路径
    :param threshold: 特征点匹配比例（越大越严格）
    :return: True 表示图片相同，False 表示图片不同
    """
    img1 = cv2.imread(image_path1, cv2.IMREAD_GRAYSCALE)
    img2 = cv2.imread(image_path2, cv2.IMREAD_GRAYSCALE)

    # 使用 ORB 检测器
    orb = cv2.ORB_create()
    kp1, des1 = orb.detectAndCompute(img1, None)
    kp2, des2 = orb.detectAndCompute(img2, None)

    # 使用 BFMatcher 进行特征匹配
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(des1, des2)
    matches = sorted(matches, key=lambda x: x.distance)

    # 计算匹配比例
    match_ratio = len(matches) / min(len(kp1), len(kp2))
    return match_ratio >= threshold

# 示例调用
image1 = "K:\测试1\\1.jpg"
image2 = "K:\测试1\\2.png"
if is_same_image(image1, image2):
    print("两张图片是相同的")
else:
    print("两张图片不同")
