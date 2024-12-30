import os
import hashlib
import csv
import send2trash
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

def get_files_with_md5(directory, num_threads):
    """
    获取目录下所有文件的文件名和 MD5 值（支持多线程）
    返回字典 { (文件名, MD5): 文件路径 }
    """
    file_map = {}
    file_paths = []

    # 收集文件路径
    for root, _, files in os.walk(directory):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            file_paths.append((file_name, file_path))

    # 使用多线程计算 MD5
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        future_to_file = {executor.submit(calculate_md5, file_path): (file_name, file_path) for file_name, file_path in file_paths}
        for future in as_completed(future_to_file):
            file_name, file_path = future_to_file[future]
            try:
                md5 = future.result()
                if md5:
                    file_map[(file_name, md5)] = file_path
            except Exception as e:
                print(f"处理文件 {file_path} 时出错: {e}")

    return file_map

def compare_directories(dir1, dir2, delete_dir=None, num_threads=4, output_file="独有文件.csv"):
    """
    比较两个目录的文件，输出独有文件或指示目录完全一致
    如果提供了删除目录参数，将其与其他目录文件名和 MD5 值都相同的文件移入回收站
    """
    print(f"正在扫描目录: {dir1} 和 {dir2}，使用 {num_threads} 个线程...")
    files_dir1 = get_files_with_md5(dir1, num_threads)
    files_dir2 = get_files_with_md5(dir2, num_threads)

    # 计算独有文件
    unique_to_dir1 = {key: files_dir1[key] for key in files_dir1 if key not in files_dir2}
    unique_to_dir2 = {key: files_dir2[key] for key in files_dir2 if key not in files_dir1}




    unique_to_dir6 = {key: files_dir1[key] for key in files_dir1 if key in files_dir2}



    # 如果两个目录完全一致
    if not unique_to_dir1 and not unique_to_dir2:
        print("目录完全一致")
        return

    # 输出独有文件到 CSV
    with open(output_file, mode="w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["目录", "文件名", "MD5", "文件路径"])

        for (file_name, md5), file_path in unique_to_dir1.items():
            writer.writerow([dir1, file_name, md5, file_path])

        for (file_name, md5), file_path in unique_to_dir2.items():
            writer.writerow([dir2, file_name, md5, file_path])

    print(f"结果已保存到 {output_file}")
    print(f"{dir1} 独有文件数量: {len(unique_to_dir1)}")
    print(f"{dir2} 独有文件数量: {len(unique_to_dir2)}")

    # 删除指定目录中与其他目录相同的文件
    if delete_dir:
        print(f"正在扫描删除目录: {delete_dir}")
        delete_files = [
            file_path
            for key, file_path in get_files_with_md5(delete_dir, num_threads).items()
            if key in files_dir1 and key in files_dir2
        ]
        for file_path in delete_files:
            try:
                send2trash.send2trash(file_path)
                print(f"已移入回收站: {file_path}")
            except Exception as e:
                print(f"无法删除文件 {file_path}，错误: {e}")
        print(f"已删除文件数量: {len(delete_files)}")

if __name__ == "__main__":
    input_dirs = "I:\BaiduNetdiskDownload\尘封的回忆;I:\BaiduNetdiskDownload\来自：本地电脑\尘封的回忆"
    directories = input_dirs.split(";")

    if len(directories) < 2:
        print("请输入两个有效的目录路径")
    else:
        dir1, dir2 = directories[0].strip(), directories[1].strip()
        delete_dir = input("请输入需要删除文件的目录（可为空）: ").strip() or None
        num_threads = 4096
        compare_directories(dir1, dir2, delete_dir=delete_dir, num_threads=num_threads)
