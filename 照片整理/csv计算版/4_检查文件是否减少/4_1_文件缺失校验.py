import os
import csv
from collections import defaultdict
from PIL import Image
import imagehash

def update_file_existence(csv_file):
    """
    检查文件是否存在，更新是否删除字段为 1（已删除）。
    :param csv_file: 输入的 CSV 文件路径
    """
    updated_rows = []
    with open(csv_file, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if not os.path.exists(row["文件路径"]):
                row["是否删除"] = "1"
            else:
                row["是否删除"] = "0"
            updated_rows.append(row)

    # 写回文件
    with open(csv_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=reader.fieldnames)
        writer.writeheader()
        writer.writerows(updated_rows)

    print(f"文件 {csv_file} 已更新")


def find_missing_md5(original_csv, processed_csv):
    """
    找出原始文件中有但处理文件中没有的 MD5 记录，并打印缺失文件路径。
    :param original_csv: 原始总文件 MD5 CSV 文件路径
    :param processed_csv: 处理总文件 MD5 CSV 文件路径
    """
    original_md5 = {}
    processed_md5 = set()

    # 读取原始文件
    with open(original_csv, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["是否删除"] == "0":
                original_md5[row["MD5"]] = row["文件路径"]

    # 读取处理文件
    with open(processed_csv, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["是否删除"] == "0":
                processed_md5.add(row["MD5"])

    # 找出缺失的 MD5
    missing_md5 = {md5: path for md5, path in original_md5.items() if md5 not in processed_md5}
    print("缺失MD5文件路径：")
    for md5, path in missing_md5.items():
        print(f"MD5: {md5}, 文件路径: {path}")

    return missing_md5


def find_similar_images(missing_md5, processed_image_csv, original_image_csv, threshold):
    """
    根据缺失 MD5 文件路径查找相似图片。
    :param missing_md5: 缺失 MD5 的字典 {MD5: 文件路径}
    :param processed_image_csv: 处理总文件 image_dhash CSV 文件路径
    :param original_image_csv: 原始总文件 image_dhash CSV 文件路径
    :param threshold: 汉明距离阈值
    """

    # 获取处理文件中未删除的 imagehash
    processed_images = []
    with open(processed_image_csv, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["是否删除"] == "0":
                processed_images.append(row)

    # 查找缺失 MD5 的 imagehash
    missing_imagehash = {}
    with open(original_image_csv, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["文件路径"] in missing_md5.values() and row["是否删除"] == "0":
                missing_imagehash[row["文件路径"]] = row["imagehash"]

    # 比较相似图片
    output_data = []
    for md5, original_path in missing_md5.items():
        original_hash = missing_imagehash.get(original_path)
        if not original_hash:
            continue

        similar_paths = []
        for processed_image in processed_images:
            processed_hash = processed_image["imagehash"]
            distance = sum(c1 != c2 for c1, c2 in zip(original_hash, processed_hash))
            if distance <= threshold:
                similar_paths.append(processed_image["文件路径"])

        output_data.append({
            "MD5": md5,
            "原始文件路径": original_path,
            **{f"文件路径{i+1}": path for i, path in enumerate(similar_paths)}
        })

    # 确定字段名
    max_files = max(len(row) - 2 for row in output_data) if output_data else 0
    fieldnames = ["MD5", "原始文件路径"] + [f"文件路径{i+1}" for i in range(max_files)]

    # 写入结果文件
    output_csv = "缺失MD5相似图片.csv"
    with open(output_csv, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for row in output_data:
            writer.writerow(row)

    print(f"总计缺失: {len(missing_md5)} 个文件，其中 {len(missing_imagehash)} 个图片")
    print(f"相似图片结果已保存到 {output_csv}")


if __name__ == "__main__":
    original_md5_csv = "../1_md5/原始总文件md5.csv"
    processed_md5_csv = "../1_md5/处理总文件md5.csv"
    processed_image_csv = "../2_imagehash/处理总文件image_dhash.csv"
    original_image_csv = "../2_imagehash/原始总文件image_dhash.csv"
    threshold = int(input("请输入阈值: "))

    # 步骤 1 和 3：更新文件存在状态
    update_file_existence(original_md5_csv)
    update_file_existence(processed_md5_csv)
    # 更新 image_dhash 文件的是否删除状态
    update_file_existence(processed_image_csv)
    update_file_existence(original_image_csv)

    # 步骤 2：找出缺失的 MD5 文件路径
    missing_md5 = find_missing_md5(original_md5_csv, processed_md5_csv)

    # 步骤 4：查找缺失 MD5 对应的相似图片
    find_similar_images(missing_md5, processed_image_csv, original_image_csv, threshold)
