import csv


def hamming_distance(hash1, hash2):
    """
    计算两个哈希值的汉明距离。
    :param hash1: 哈希值1（字符串）
    :param hash2: 哈希值2（字符串）
    :return: 汉明距离（整数）
    """
    # return sum(c1 != c2 for c1, c2 in zip(hash1, hash2))

    # 将十六进制字符串转换为整数
    hash1_int = int(hash1, 16)
    hash2_int = int(hash2, 16)

    # 计算两个整数之间的差异
    return abs(hash1_int - hash2_int)


def process_imagehash(input_csv, output_csv, threshold):
    """
    统计所有文件及相似文件组，输出到指定的 CSV 文件，字段按升序排序。
    :param input_csv: 输入文件（总文件imagehash.csv）
    :param output_csv: 输出文件
    :param threshold: 哈希相似度阈值
    """
    # 读取输入文件并筛选未删除的文件
    files = []
    with open(input_csv, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["是否删除"] == "0":  # 仅处理未删除的文件
                files.append(row)

    # 按 imagehash 分组，并允许根据阈值计算相似组
    groups = []
    for file1 in files:
        matched = False
        for group in groups:
            # 如果文件哈希与组内任一文件相似，归入该组
            if any(hamming_distance(file1["imagehash"], f["imagehash"]) <= threshold for f in group):
                group.append(file1)
                matched = True
                break
        if not matched:
            groups.append([file1])

    # 准备输出数据
    output_data = []
    for group in groups:
        row = {"文件数": len(group)}
        for i, file in enumerate(group):
            row[f"文件名{i+1}"] = file["文件名"]
            row[f"文件目录{i+1}"] = file["文件目录"]
            row[f"文件路径{i+1}"] = file["文件路径"]
        output_data.append(row)

    # 确定所有字段名并排序
    max_files = max(len(group) for group in groups)
    fieldnames = ["文件数"]
    for i in range(1, max_files + 1):
        fieldnames.extend([f"文件名{i}", f"文件目录{i}", f"文件路径{i}"])
    fieldnames = sorted(fieldnames)  # 按升序排序字段名

    # 写入输出文件
    with open(output_csv, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        writer.writeheader()
        for row in output_data:
            # 对 row 的键进行排序
            sorted_row = {key: row.get(key, "") for key in fieldnames}
            writer.writerow(sorted_row)

    print(f"处理完成，结果已保存到 {output_csv}")


if __name__ == '__main__':
    # 输入文件路径
    input_csvs = "处理总文件image_dhash.csv;处理总文件image_average_hash.csv;处理总文件image_phash.csv"  # 输入文件
    # 用户输入阈值
    threshold = int(input("请输入哈希阈值："))
    for input_csv in input_csvs.split(";"):
        hash_method = input_csv.replace(".csv", "").replace("处理总文件image_", "")
        # 输出文件路径
        output_csv = f"按_{hash_method}_统计_{threshold}.csv"

        # 调用函数处理
        process_imagehash(input_csv, output_csv, threshold)
