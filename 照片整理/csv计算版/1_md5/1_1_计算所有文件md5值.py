import os
import hashlib
import csv
import time

from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

def calculate_md5(file_path):
    """
    计算文件的 MD5 值
    """
    hash_md5 = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception as e:
        print(f"无法计算文件 {file_path} 的 MD5，错误: {e}")
        return None

def process_file(file_path):
    """
    多线程任务：计算文件 MD5 并返回结果
    """
    md5 = calculate_md5(file_path)
    return md5, file_path

def process_folders(folder_paths, num_threads=None):
    """
    遍历多个文件夹并计算文件 MD5 值（支持多线程，线程数可配置）
    """
    results = []
    file_paths = []

    # 收集所有文件路径
    for folder in folder_paths.split(";"):
        folder = folder.strip()
        if not os.path.exists(folder) or not os.path.isdir(folder):
            print(f"无效的文件夹路径: {folder}")
            continue

        for root, _, files in os.walk(folder):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                file_paths.append((file_name, root, file_path))

    print(f"共找到 {len(file_paths)} 个文件，开始计算 MD5...")

    # 使用多线程计算 MD5，并显示进度条
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        future_to_file = {executor.submit(calculate_md5, file_path[2]): file_path for file_path in file_paths}
        for future in tqdm(as_completed(future_to_file), total=len(future_to_file), desc="计算 MD5 值", unit="文件"):
            try:
                md5 = future.result()
                if md5:
                    file_name, directory, file_path = future_to_file[future]
                    results.append((md5, file_name, directory, file_path, 0))
            except Exception as e:
                print(f"处理文件时出错: {e}")

    return results

def save_to_csv(data, output_file):
    """
    将结果保存为 CSV 文件
    """
    with open(output_file, mode="w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        # 写入表头
        writer.writerow(["MD5", "文件名", "文件目录", "文件路径", "是否删除"])

        # 写入内容
        writer.writerows(data)

if __name__ == "__main__":
    num_threads = 16384

    # 原始文件
    input_folders = "I:\BaiduNetdiskDownload\单反\原始"
    output_csv = "原始总文件md5.csv"  # 输出文件名
    if not input_folders:
        print("未输入有效的目录路径，程序退出。")
    else:
        start_time = time.time()
        results = process_folders(input_folders, num_threads=num_threads)
        save_to_csv(results, output_csv)
        print(f"处理完成，结果已保存到 {output_csv}")
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"原始文件处理耗时： {elapsed_time} 秒")

    # 处理文件
    input_folders = "I:\BaiduNetdiskDownload\单反\处理"
    output_csv = "处理总文件md5.csv"  # 输出文件名
    if not input_folders:
        print("未输入有效的目录路径，程序退出。")
    else:
        start_time = time.time()
        results = process_folders(input_folders, num_threads=num_threads)
        save_to_csv(results, output_csv)
        print(f"处理完成，结果已保存到 {output_csv}")
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"处理文件处理耗时： {elapsed_time} 秒")