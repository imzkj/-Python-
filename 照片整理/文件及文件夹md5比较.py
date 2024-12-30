import os
import hashlib
import csv
from collections import defaultdict

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

def process_folders(folder_paths):
    """
    遍历多个文件夹并计算文件 MD5 值
    """
    md5_to_files = {}
    folder_contents = {}
    for folder in folder_paths.split(";"):
        folder = folder.strip()
        if not os.path.exists(folder) or not os.path.isdir(folder):
            print(f"无效的文件夹路径: {folder}")
            continue

        for root, dirs, files in os.walk(folder):
            # 记录文件夹内容信息
            relative_path = os.path.relpath(root, folder)
            folder_contents[root] = {
                "files": sorted([(file, calculate_md5(os.path.join(root, file))) for file in files]),
                "subdirs": sorted(dirs),
            }

            # 记录 MD5 值和对应的文件路径
            for file_name in files:
                file_path = os.path.join(root, file_name)
                md5 = calculate_md5(file_path)
                if md5:
                    if md5 not in md5_to_files:
                        md5_to_files[md5] = []
                    md5_to_files[md5].append(file_path)

    # 对每个 MD5 的文件路径列表进行升序排序
    for md5 in md5_to_files:
        md5_to_files[md5].sort()
    return md5_to_files, folder_contents

def check_filenames_consistency(file_paths):
    """
    检查文件名是否一致
    """
    file_names = {os.path.basename(path) for path in file_paths}
    return "一致" if len(file_names) == 1 else "不一致"

def group_similar_folders(folder_contents):
    """
    按照文件夹内容分组，找出一致的文件夹
    """
    content_to_folders = defaultdict(list)
    for folder, content in folder_contents.items():
        # 将文件名和 MD5、子文件夹名称作为内容标识
        content_signature = (
            tuple(content["files"]),
            tuple(content["subdirs"]),
        )
        content_to_folders[content_signature].append(folder)
    return [folders for folders in content_to_folders.values() if len(folders) > 1]

def save_to_csv(md5_to_files, folder_groups, output_md5_file, output_folder_file):
    """
    保存 MD5 和一致文件夹到 CSV 文件
    """
    # 保存 MD5 文件
    with open(output_md5_file, mode="w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        max_files = max(len(paths) for paths in md5_to_files.values())
        headers = ["MD5", "文件名是否一致"] + [f"文件路径{i+1}" for i in range(max_files)]
        writer.writerow(headers)

        for md5, file_paths in md5_to_files.items():
            consistency = check_filenames_consistency(file_paths)
            row = [md5, consistency] + file_paths + [""] * (max_files - len(file_paths))
            writer.writerow(row)

    # 保存一致文件夹文件
    with open(output_folder_file, mode="w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["一致文件夹组"])
        for group in folder_groups:
            writer.writerow(group)

if __name__ == "__main__":
    input_folders = "K:\测试1;K:\测试2;K:\测试3;K:\测试4;K:\测试5"
    output_md5_csv = "md5_files_with_consistency.csv"
    output_folder_csv = "similar_folders.csv"

    md5_files_map, folder_contents = process_folders(input_folders)
    folder_groups = group_similar_folders(folder_contents)

    save_to_csv(md5_files_map, folder_groups, output_md5_csv, output_folder_csv)
    print(f"MD5 结果已保存到 {output_md5_csv}")
    print(f"一致文件夹结果已保存到 {output_folder_csv}")
