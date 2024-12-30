import os
import hashlib
import csv
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm  # 引入进度条模块

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
    遍历多个文件夹并计算文件 MD5 值（支持多线程，线程数可配置，带进度条）
    """
    md5_to_files = {}
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
                file_paths.append(file_path)

    total_files = len(file_paths)
    print(f"共找到 {total_files} 个文件，开始计算 MD5...")

    # 使用多线程计算 MD5
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        future_to_file = {executor.submit(process_file, file_path): file_path for file_path in file_paths}

        # 使用 tqdm 显示进度条
        with tqdm(total=total_files, desc="文件处理进度", unit="文件") as pbar:
            for future in as_completed(future_to_file):
                try:
                    md5, file_path = future.result()
                    if md5:
                        if md5 not in md5_to_files:
                            md5_to_files[md5] = []
                        md5_to_files[md5].append(file_path)
                except Exception as e:
                    print(f"处理文件时出错: {e}")
                finally:
                    pbar.update(1)  # 每完成一个任务，进度条更新

    # 对每个 MD5 的文件路径列表进行升序排序
    for md5 in md5_to_files:
        md5_to_files[md5].sort()
    return md5_to_files

def check_filenames_consistency(file_paths):
    """
    检查文件名是否一致
    """
    file_names = {os.path.basename(path) for path in file_paths}
    return "一致" if len(file_names) == 1 else "不一致"

def save_to_csv(md5_to_files, output_file):
    """
    将 MD5 和对应文件路径保存为 CSV 文件
    """
    with open(output_file, mode="w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        # 写入表头
        max_files = max(len(paths) for paths in md5_to_files.values())
        headers = ["MD5", "文件数", "文件名是否一致"] + [f"文件路径{i+1}" for i in range(max_files)]
        writer.writerow(headers)

        # 写入内容
        for md5, file_paths in md5_to_files.items():
            consistency = check_filenames_consistency(file_paths)
            row = [md5, len(file_paths), consistency] + file_paths + [""] * (max_files - len(file_paths))
            writer.writerow(row)

if __name__ == "__main__":
    input_folders = "I:\\BaiduNetdiskDownload\\尘封的回忆;I:\\BaiduNetdiskDownload\\来自：本地电脑\\尘封的回忆"  # 输入文件夹路径，多个路径用分号分隔
    output_csv = "md5_files_with_consistency.csv"  # 默认保存为当前目录下的 md5_files_with_consistency.csv
    num_threads = 8192  # 指定线程数量，设置为 None 则自动选择核心数
    md5_files_map = process_folders(input_folders, num_threads=num_threads)
    save_to_csv(md5_files_map, output_csv)
    print(f"处理完成，结果已保存到 {output_csv}")
