import csv
import filetype
import os
from send2trash import send2trash


def is_image_file(file_path):
    """
    判断文件是否为图片
    :param file_path: 文件路径
    :return: 如果是图片返回 True，否则返回 False
    """
    try:
        kind = filetype.guess(file_path)
        if kind is None:
            return False
        return kind.mime.startswith("image/")
    except Exception as e:
        print(f"无法判断文件类型: {file_path}, 错误: {e}")
        return False


def is_video_file(file_path):
    """
    判断文件是否为视频
    :param file_path: 文件路径
    :return: 如果是视频返回 True，否则返回 False
    """
    try:
        kind = filetype.guess(file_path)
        if kind is None:
            return False
        return kind.mime.startswith("video/")
    except Exception as e:
        print(f"无法判断文件类型: {file_path}, 错误: {e}")
        return False


def is_compressed_file(file_path):
    """
    判断文件是否为压缩包
    :param file_path: 文件路径
    :return: 如果是压缩包返回 True，否则返回 False
    """
    try:
        kind = filetype.guess(file_path)
        if kind is None:
            return False
        return kind.mime in ["application/x-rar-compressed", "application/zip", "application/x-tar", "application/x-gzip", "application/x-bzip2"]
    except Exception as e:
        print(f"无法判断文件类型: {file_path}, 错误: {e}")
        return False

def is_xmp_file(file_path):
    """
    判断文件是否为XMP
    :param file_path: 文件路径
    :return: 如果是XMP返回 True，否则返回 False
    """
    try:
        _, ext = os.path.splitext(file_path)  # 获取文件扩展名
        return ext.lower() == ".xmp"  # 判断扩展名是否为 .xmp
    except Exception as e:
        print(f"无法判断文件类型: {file_path}, 错误: {e}")
        return False


def process_csv(csv_file, user_input):
    """
    处理 CSV 文件，判断文件类型并处理未删除的文件。
    :param csv_file: CSV 文件路径
    """
    with open(csv_file, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["是否删除"] == "0":  # 只处理未删除的文件
                file_path = row["文件路径"]

                if not os.path.exists(file_path):
                    print(f"文件不存在: {file_path}")
                    continue

                # 判断文件是否为图片、视频或压缩包
                if is_image_file(file_path) or is_video_file(file_path) or is_compressed_file(file_path) or is_xmp_file(file_path):
                    continue

                # 如果不是图片、视频或压缩包，则打印文件路径并询问是否删除
                print(f"文件路径: {file_path}")
                if user_input == "1":
                    try:
                        send2trash(file_path)
                        print(f"文件 {file_path} 已移入回收站")
                    except Exception as e:
                        print(f"删除文件 {file_path} 时出错: {e}")


if __name__ == "__main__":
    csv_file = "../1_md5/处理总文件md5.csv"  # CSV 文件路径
    # 如果不是图片、视频或压缩包，则打印文件路径并询问是否删除
    user_input = input("是否删除此文件？输入1删除，其他键跳过: ")
    process_csv(csv_file, user_input)
