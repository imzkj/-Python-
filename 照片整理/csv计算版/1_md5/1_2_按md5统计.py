import csv
from collections import defaultdict

def process_md5_csv(input_csv, output_csv, count_dir = None):
    """
    根据输入的 MD5 文件，输出目标格式。
    """
    # 用于存储 MD5 和对应文件信息的字典
    md5_dict = defaultdict(list)

    # 读取输入 CSV 文件
    with open(input_csv, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["是否删除"] == "0":  # 仅处理未删除的文件
                if count_dir:
                    if row["文件目录"].startswith(count_dir):
                        md5_dict[row["MD5"]].append(row)
                else:
                    md5_dict[row["MD5"]].append(row)

    # 准备输出内容
    output_data = []
    max_dirs_count = 1  # 假设最多支持10个目录列，按需调整

    # 遍历字典
    for md5, files in md5_dict.items():
        if len(files) > max_dirs_count:
            max_dirs_count = len(files)

    for md5, files in md5_dict.items():
        # 获取文件名集合和目录集合
        file_names = {file["文件名"] for file in files}
        directories = sorted([file["文件目录"] for file in files])  # 升序排序目录

        # 判断文件名是否一致
        file_name_consistency = "一致" if len(file_names) == 1 else "不一致"

        # 构造输出行
        output_row = {
            "MD5": md5,
            "文件个数": len(files),
            "文件名是否一致": file_name_consistency,
        }

        # 填充目录列
        for i in range(min(max_dirs_count, len(directories))):
            output_row[f"文件目录{i+1}"] = directories[i]

        # 如果目录数量少于最大列数，填充空值
        for i in range(len(directories), max_dirs_count):
            output_row[f"文件目录{i+1}"] = ""

        output_data.append(output_row)

    # 写入输出 CSV 文件
    with open(output_csv, mode="w", newline="", encoding="utf-8") as file:
        # 动态生成表头，确保包括所有目录列
        fieldnames = ["MD5", "文件个数", "文件名是否一致"] + [f"文件目录{i+1}" for i in range(max_dirs_count)]
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        # 写入表头
        writer.writeheader()

        # 写入内容
        for row in output_data:
            writer.writerow(row)

    print(f"处理完成，结果已保存到 {output_csv}")

if __name__ == "__main__":
    # 示例调用
    input_csv = "处理总文件md5.csv"  # 输入文件
    output_csv = "按md5统计.csv"  # 输出文件
    count_dir = input("请输入需要统计文件的目录（可为空）: ").strip() or None
    process_md5_csv(input_csv, output_csv, count_dir)
