from PIL import Image
import imagehash


def is_same_image(image_path1, image_path2, threshold=1):
    """
    判断两张图片是否相同（通过感知哈希）。
    :param image_path1: 图片1路径
    :param image_path2: 图片2路径
    :param threshold: 哈希差异阈值（越小越严格）
    :return: True 表示图片相同，False 表示图片不同
    """
    # hash1 = imagehash.phash(Image.open(image_path1))  # 感知哈希
    # hash2 = imagehash.phash(Image.open(image_path2))

    hash1 = imagehash.average_hash(Image.open(image_path1))  # 感知哈希
    hash2 = imagehash.average_hash(Image.open(image_path2))
    #
    # hash1 = imagehash.dhash(Image.open(image_path1))  # 感知哈希
    # hash2 = imagehash.dhash(Image.open(image_path2))

    print(hash1, hash2)
    return abs(hash1 - hash2) <= threshold


# 示例调用
image1 = r"J:\机械G\尘封的回忆\单反\100ND780\姐-婚礼\ZKJ_0357.JPG"
image2 = r"J:\机械G\尘封的回忆\单反\100ND780\姐-婚礼\ZKJ_0357.NEF"


if is_same_image(image1, image2):
    print("两张图片是相同的")
else:
    print("两张图片不同")
