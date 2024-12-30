import csv
from collections import defaultdict
from send2trash import send2trash


def process_md5_csv(input_csv, directory, delete_flag):
    """
    处理 MD5 文件，删除重复的文件，并更新总文件 MD5 CSV。
    如果需要删除，将文件移动到回收站。
    """
    # 读取 CSV 文件
    with open(input_csv, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        rows = list(reader)

    # 根据给定目录过滤未删除的文件
    filtered_files = [row for row in rows if row["文件目录"].startswith(directory) and row["是否删除"] == "0"]

    # 统计每个 MD5 对应的文件路径
    md5_dict = defaultdict(list)
    for row in filtered_files:
        md5_dict[row["MD5"]].append(row)

    # 初始化删除日志
    delete_log = []
    delete_count = 0

    # 处理每个 MD5 对应的文件
    for md5, files in md5_dict.items():
        if len(files) > 1 and delete_flag == "1":  # 如果有多个文件且需要删除
            # 按路径升序排序
            files_sorted = sorted(files, key=lambda x: x["文件路径"])

            # 保留一个文件，删除其他文件
            for file in files_sorted[1:]:
                try:
                    send2trash(file["文件路径"])  # 将文件移入回收站
                    delete_log.append(file["文件路径"])
                    delete_count += 1
                    file["是否删除"] = "1"  # 标记为删除
                except Exception as e:
                    print(f"无法删除文件 {file['文件路径']}：{e}")

    # 更新 CSV 文件
    with open(input_csv, mode="w", newline="", encoding="utf-8") as file:
        fieldnames = ["MD5", "文件名", "文件目录", "文件路径", "是否删除"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        # 写入表头
        writer.writeheader()

        # 写入更新后的数据
        writer.writerows(rows)

    # 打印删除日志
    if delete_count > 0:
        print(f"删除了 {delete_count} 个文件 (已移入回收站):")
        for path in delete_log:
            print(path)
    else:
        print("没有需要删除的文件。")


if __name__ == "__main__":
    # 控制台输入参数
    input_csv = "处理总文件md5.csv"  # 输入的 CSV 文件
    directory = input("请输入目录: ")  # 目录
    delete_flag = input("是否删除 (1 删除，0 不删除): ")  # 是否删除

    # 执行处理
    process_md5_csv(input_csv, directory, delete_flag)
