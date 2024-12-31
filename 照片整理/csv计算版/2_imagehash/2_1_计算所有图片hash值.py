import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import csv
from PIL import Image
import imagehash
from tqdm import tqdm
from PIL import ImageFile

# 提高 Pillow 的像素限制
Image.MAX_IMAGE_PIXELS = None  # 或者设置为一个更大的值
ImageFile.LOAD_TRUNCATED_IMAGES = True

def calculate_image_hash(image_path, hash_method):
    """
    计算图片的感知哈希值。
    :param image_path: 图片路径
    :param hash_method: 哈希方法（phash、average_hash、dhash）
    :return: 图片哈希值（str），如果无法计算返回 None
    """
    try:
        with Image.open(image_path) as img:
            if hash_method == "phash":
                return str(imagehash.phash(img))
            elif hash_method == "average_hash":
                return str(imagehash.average_hash(img))
            elif hash_method == "dhash":
                return str(imagehash.dhash(img))
            else:
                return None
    except Exception:
        return None


def process_file(file_path, hash_methods):
    """
    处理单个文件，计算多种哈希值并返回结果。
    :param file_path: 文件路径
    :param hash_methods: 哈希方法列表（如 ['phash', 'average_hash', 'dhash']）
    :return: 包含文件信息和所有哈希值的字典，如果不是图片返回 None
    """
    file_name = os.path.basename(file_path)
    file_dir = os.path.dirname(file_path)
    hash_values = {}

    for hash_method in hash_methods:
        hash_value = calculate_image_hash(file_path, hash_method)
        if hash_value:
            hash_values[hash_method] = hash_value

    if hash_values:  # 至少成功计算一种哈希值
        return {
            "文件名": file_name,
            "文件目录": file_dir,
            "文件路径": file_path,
            "是否删除": "0",  # 默认未删除
            **hash_values  # 展开哈希值
        }
    else:
        # print(f"{file_name}不是图片")
        return None


def process_directories(directories, output_csv_prefix, hash_methods, max_threads=4):
    """
    遍历给定目录，计算所有图片的哈希值，并保存到多个 CSV 文件。
    :param directories: 多个目录路径，用分号连接
    :param output_csv_prefix: 输出 CSV 文件前缀
    :param hash_methods: 哈希方法列表（如 ['phash', 'average_hash', 'dhash']）
    :param max_threads: 最大线程数
    """
    # 准备存储结果的列表
    results = []
    all_files = 0
    all_image_files = 0
    file_paths = []

    # 遍历所有目录
    for directory in directories.split(";"):
        directory = directory.strip()  # 去掉前后空格
        if not os.path.exists(directory):
            print(f"目录不存在：{directory}")
            continue

        # 收集所有文件路径
        for root, _, files in os.walk(directory):
            for file in files:
                all_files += 1
                file_paths.append(os.path.join(root, file))

    print(f"总共扫描{all_files}个文件，开始计算 imagehash...")
    # 使用多线程处理文件
    with ThreadPoolExecutor(max_threads) as executor:
        future_to_file = {executor.submit(process_file, file_path, hash_methods): file_path for file_path in file_paths}
        for future in tqdm(as_completed(future_to_file), total=len(future_to_file), desc="计算 ImageHash", unit="文件"):
            try:
                result = future.result()
                if result:
                    all_image_files += 1
                    results.append(result)
            except Exception as e:
                print(f"处理文件时出错：{e}")

    print(f"总共扫描{all_files}个文件，成功处理{all_image_files}个图片")
    print("============================================================================================================")

    # 为每种哈希方法分别写入结果到 CSV 文件
    for hash_method in hash_methods:
        output_csv = f"{output_csv_prefix}_{hash_method}.csv"
        with open(output_csv, mode="w", newline="", encoding="utf-8") as file:
            fieldnames = ["imagehash", "文件名", "文件目录", "文件路径", "是否删除"]
            writer = csv.DictWriter(file, fieldnames=fieldnames)

            # 写入表头
            writer.writeheader()

            # 写入每行数据
            for row in results:
                if hash_method in row:  # 仅写入当前哈希方法的值
                    writer.writerow({
                        "imagehash": row[hash_method],
                        "文件名": row["文件名"],
                        "文件目录": row["文件目录"],
                        "文件路径": row["文件路径"],
                        "是否删除": row["是否删除"]
                    })

        print(f"结果已保存到 {output_csv}")


if __name__ == '__main__':
    max_threads = 128  # 指定线程数
    hash_methods = ["phash", "average_hash", "dhash"]  # 多种哈希方法


    # 原始文件
    start_time = time.time()
    directories = r"D:\JisuCloud;D:\BaiduNetdiskDownload\pc08803;D:\BaiduNetdiskDownload\PS;D:\BaiduNetdiskDownload\相册·2;D:\桌面;F:\FileRecv;G:\尘封的回忆;K:\BaiduNetdiskDownload"  # 多个目录，用分号分隔
    process_directories(directories, "原始总文件image", hash_methods, max_threads)
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"原始文件处理耗时： {elapsed_time} 秒")

    # 处理文件
    start_time = time.time()
    directories = r"I:\BaiduNetdiskDownload;J:\机械D;J:\机械F;J:\机械G"  # 多个目录，用分号分隔
    process_directories(directories, "处理总文件image", hash_methods, max_threads)
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"处理文件处理耗时： {elapsed_time} 秒")
