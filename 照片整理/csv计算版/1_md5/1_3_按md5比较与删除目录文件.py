import os
import csv
import send2trash
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm


import chardet

def read_csv_with_auto_encoding(csv_path):
    """
    自动检测文件编码并读取 CSV 文件。
    读取 CSV 文件，返回未删除的记录。
    """
    data = []
    try:
        # 使用检测到的编码读取文件
        with open(csv_path, mode="r", encoding="utf-8") as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                if row["是否删除"] == "0":
                    data.append(row)
        return data
    except Exception as e:
        print(f"读取 CSV 文件失败: {e}")
        return None

def filter_files_by_directories(data, dir1, dir2):
    """
    筛选出属于给定两个目录的文件。
    """
    dir1_files = []
    dir2_files = []
    for row in data:
        file_path = row["文件路径"]
        # dir1是dir2的父目录
        if dir2.startswith(dir1):
            if file_path.startswith(dir2):
                dir2_files.append(row)
            elif file_path.startswith(dir1):
                dir1_files.append(row)
        elif dir1.startswith(dir2):
            if file_path.startswith(dir1):
                dir1_files.append(row)
            elif file_path.startswith(dir2):
                dir2_files.append(row)
        else:
            if file_path.startswith(dir1):
                dir1_files.append(row)
            elif file_path.startswith(dir2):
                dir2_files.append(row)
    return dir1_files, dir2_files


def compare_files(dir1_files, dir2_files):
    """
    比较两个目录的文件 MD5 和文件名，返回独有文件和 MD5、文件名都相同的文件信息。
    """
    dir1_md5_set = {row["MD5"] for row in dir1_files}
    dir2_md5_set = {row["MD5"] for row in dir2_files}

    unique_to_dir1 = [row for row in dir1_files if row["MD5"] not in dir2_md5_set]
    unique_to_dir2 = [row for row in dir2_files if row["MD5"] not in dir1_md5_set]

    dir2_md5_name_set = {(row["MD5"], row["文件名"]) for row in dir2_files}
    # 获取 MD5 都相同的文件
    same_files = []
    for row1 in dir1_files:
        for row2 in dir2_files:
            if row1["MD5"] == row2["MD5"]:
                same_files.append({
                    "MD5": row1["MD5"],
                    "文件名1": row1["文件名"],
                    "文件名2": row2["文件名"],
                    "名称是否相同": "1" if row1["文件名"] == row2["文件名"] else "0",
                    "文件目录1": row1["文件目录"],
                    "文件目录2": row2["文件目录"],
                })
                break  # 找到匹配的 MD5 后跳出内层循环

    return unique_to_dir1, unique_to_dir2, same_files


def save_to_csv(data, output_file):
    """
    将结果保存为 CSV 文件。
    """
    try:
        with open(output_file, mode="w", newline="", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["MD5", "文件名", "文件目录", "文件路径"])
            for row in data:
                writer.writerow([row["MD5"], row["文件名"], row["文件目录"], row["文件路径"]])
        print(f"结果已保存到 {output_file}")
    except Exception as e:
        print(f"保存 CSV 文件失败: {e}")

def save_same_to_csv(data, output_file):
    """
    将结果保存为 CSV 文件。
    """
    try:
        with open(output_file, mode="w", newline="", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["MD5", "文件名1", "文件名2", "名称是否相同", "文件目录1", "文件目录2"])
            for row in data:
                writer.writerow([row["MD5"], row["文件名1"], row["文件名2"], row["名称是否相同"], row["文件目录1"], row["文件目录2"]])
        print(f"结果已保存到 {output_file}")
    except Exception as e:
        print(f"保存 CSV 文件失败: {e}")

def delete_files_with_same_md5(data, delete_dir, compare_dir, csv_path, num_threads=4):
    """
    删除 delete_dir 中与 compare_dir 中有相同 MD5 的文件，并更新 CSV 文件。
    """

    delete_dir_files, compare_dir_files = filter_files_by_directories(data, delete_dir, compare_dir)
    # 获取 compare_dir 的 MD5 集合
    compare_md5_set = {row["MD5"] for row in compare_dir_files}

    # 筛选出 delete_dir 中 MD5 相同的文件
    delete_tasks = [
        row for row in delete_dir_files if row["MD5"] in compare_md5_set
    ]

    if not delete_tasks:
        print(f"未找到需要删除的文件，目录 {delete_dir} 中没有与目录 {compare_dir} 相同的文件。")
        return

    # 删除文件并显示进度
    progress_bar = tqdm(total=len(delete_tasks), desc="删除文件", unit="文件")
    success_count = 0  # 成功删除文件的计数器

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = {executor.submit(send2trash.send2trash, row["文件路径"]): row for row in delete_tasks}
        for future in as_completed(futures):
            row = futures[future]
            # 更新 CSV 中的 "是否删除" 列
            row["是否删除"] = "1"
            try:
                future.result()
                progress_bar.update(1)
                success_count += 1  # 成功删除文件计数加一
            except Exception as e:
                print(f"删除文件失败: {row['文件路径']}，错误: {e}")
    progress_bar.close()

    # 更新 CSV 文件
    try:
        with open(csv_path, mode="w", newline="", encoding="utf-8") as csv_file:
            fieldnames = ["MD5", "文件名", "文件目录", "文件路径", "是否删除"]
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        print(f"CSV 文件已更新: {csv_path}")
    except Exception as e:
        print(f"更新 CSV 文件失败: {e}")

    # 输出成功删除的文件总数
    print(f"应删除文件数：{len(delete_tasks)}，成功删除了 {success_count} 个文件。")

def start_with_str(csv_file_path, unique_files_output_csv, same_files_output_csv, dir, num_threads):
    count = 0
    for sub_dir in dir.split("\n"):
        count += 1
        single_dir_list = sub_dir.split(";")
        dir1 = single_dir_list[0].strip()
        dir2 = single_dir_list[1].strip()
        delete_dir = None
        if len(single_dir_list) > 2:
            delete_dir = single_dir_list[2].strip()

        if not dir1 or not dir2:
            print("请输入有效的目录路径！")
        elif dir1 == dir2:
            print("比较目录不能是同一个！")
        else:
            data = read_csv_with_auto_encoding(csv_file_path)

            # 筛选文件
            dir1_files, dir2_files = filter_files_by_directories(data, dir1, dir2)
            print(f"目录【{dir1}】文件数为： {len(dir1_files)}")
            print(f"目录【{dir2}】文件数为： {len(dir2_files)}")

            # 比较文件
            unique_to_dir1, unique_to_dir2, same_files = compare_files(dir1_files, dir2_files)
            print(f"目录【{dir1}】独有文件数为： {len(unique_to_dir1)}")
            print(f"目录【{dir2}】独有文件数为： {len(unique_to_dir2)}")
            print(f"目录【{dir1}&{dir2}】完全相同的文件数为： {len(same_files)}")

            # 保存独有文件到 CSV
            save_to_csv(unique_to_dir1 + unique_to_dir2, unique_files_output_csv.replace(".csv", "_"+str(count)+".csv"))
            save_same_to_csv(same_files, same_files_output_csv.replace(".csv", "_"+str(count)+".csv"))

            # 删除相同文件并更新 CSV
            if delete_dir:
                if delete_dir not in [dir1, dir2]:
                    print("删除目录必须是给定的两个目录之一！")
                else:
                    compare_dir = dir1 if delete_dir == dir2 else dir2
                    delete_files_with_same_md5(data, delete_dir, compare_dir, csv_file_path, num_threads=num_threads)
        print("=============================================================================================================")

def start_with_input(csv_file_path, unique_files_output_csv, same_files_output_csv, dir, num_threads):
    dir1 = dir.split(";")[0].strip()
    dir2 = dir.split(";")[1].strip()
    delete_dir = input("请输入需要删除文件的目录（可为空）: ").strip() or None

    if not dir1 or not dir2:
        print("请输入有效的目录路径！")
    elif dir1 == dir2:
        print("比较目录不能是同一个！")
    else:
        data = read_csv_with_auto_encoding(csv_file_path)

        # 筛选文件
        dir1_files, dir2_files = filter_files_by_directories(data, dir1, dir2)
        print(f"目录【{dir1}】文件数为： {len(dir1_files)}")
        print(f"目录【{dir2}】文件数为： {len(dir2_files)}")

        # 比较文件
        unique_to_dir1, unique_to_dir2, same_files = compare_files(dir1_files, dir2_files)
        print(f"目录【{dir1}】独有文件数为： {len(unique_to_dir1)}")
        print(f"目录【{dir2}】独有文件数为： {len(unique_to_dir2)}")
        print(f"目录【{dir1}&{dir2}】完全相同的文件数为： {len(same_files)}")

        # 保存独有文件到 CSV
        save_to_csv(unique_to_dir1 + unique_to_dir2, unique_files_output_csv)
        save_same_to_csv(same_files, same_files_output_csv)

        # 删除相同文件并更新 CSV
        if delete_dir:
            if delete_dir not in [dir1, dir2]:
                print("删除目录必须是给定的两个目录之一！")
            else:
                compare_dir = dir1 if delete_dir == dir2 else dir2
                delete_files_with_same_md5(data, delete_dir, compare_dir, csv_file_path, num_threads=num_threads)


if __name__ == "__main__":
    dir = r'''I:\BaiduNetdiskDownload\微信图片备份;I:\BaiduNetdiskDownload\来自：NX563J\WeiXin;I:\BaiduNetdiskDownload\微信图片备份
I:\BaiduNetdiskDownload\来自：NX563J\DCIM\Camera;I:\BaiduNetdiskDownload\来自：本地电脑\尘封的回忆\DCIM\努比亚;I:\BaiduNetdiskDownload\来自：NX563J\DCIM\Camera
J:\机械G\尘封的回忆\DCIM\努比亚\克隆\其他相册\1688850913082673;J:\机械G\尘封的回忆\DCIM\努比亚\其他相册\1688850913082673;J:\机械G\尘封的回忆\DCIM\努比亚\克隆\其他相册\1688850913082673
J:\机械G\尘封的回忆\DCIM\努比亚;J:\机械G\尘封的回忆\DCIM\努比亚\全景;J:\机械G\尘封的回忆\DCIM\努比亚
I:\BaiduNetdiskDownload\来自：NX563J\DCIM\Camera\Dng;I:\BaiduNetdiskDownload\来自：本地电脑\QQ备份\601869492\FileRecv\MobileFile;I:\BaiduNetdiskDownload\来自：本地电脑\QQ备份\601869492\FileRecv\MobileFile
I:\BaiduNetdiskDownload\201711台湾旅游（公司）;I:\BaiduNetdiskDownload\微信图片备份;I:\BaiduNetdiskDownload\微信图片备份
J:\机械D\JisuCloud;J:\机械G\尘封的回忆\FoeverLove\20230424四周年;J:\机械D\JisuCloud
J:\机械G\尘封的回忆\DCIM\努比亚;J:\机械G\尘封的回忆\DCIM\努比亚\连拍;J:\机械G\尘封的回忆\DCIM\努比亚
J:\机械G\尘封的回忆\DCIM\努比亚;J:\机械G\尘封的回忆\DCIM\努比亚\微距;J:\机械G\尘封的回忆\DCIM\努比亚
J:\机械G\尘封的回忆\DCIM\努比亚\克隆\其他相册\ALIMP;J:\机械G\尘封的回忆\DCIM\努比亚\其他相册\ALIMP;J:\机械G\尘封的回忆\DCIM\努比亚\克隆\其他相册\ALIMP
J:\机械D\PS;J:\机械D\pc08803\ps;J:\机械D\pc08803\ps
J:\机械G\尘封的回忆\DCIM\努比亚\克隆\其他相册\BossZhipin;J:\机械G\尘封的回忆\DCIM\努比亚\其他相册\BossZhipin;J:\机械G\尘封的回忆\DCIM\努比亚\克隆\其他相册\BossZhipin
I:\BaiduNetdiskDownload\求婚视频\婚纱照\原格式;I:\BaiduNetdiskDownload\求婚视频\婚纱照\淘宝精修原格式;I:\BaiduNetdiskDownload\求婚视频\婚纱照\淘宝精修原格式
J:\机械G\尘封的回忆\DCIM\努比亚;J:\机械G\尘封的回忆\DCIM\努比亚\克隆;J:\机械G\尘封的回忆\DCIM\努比亚
J:\机械G\尘封的回忆\DCIM\努比亚\克隆\其他相册\360;J:\机械G\尘封的回忆\DCIM\努比亚\其他相册\360;J:\机械G\尘封的回忆\DCIM\努比亚\克隆\其他相册\360
J:\机械G\尘封的回忆\DCIM\努比亚;J:\机械G\尘封的回忆\DCIM\努比亚\人像;J:\机械G\尘封的回忆\DCIM\努比亚
J:\机械D\JisuCloud\摄图网_video_27560\粉色浪漫婚礼 folder-1\(Footage)\素材;J:\机械F\FileRecv;J:\机械D\JisuCloud\摄图网_video_27560\粉色浪漫婚礼 folder-1\(Footage)\素材
J:\机械G\尘封的回忆\DCIM\努比亚;J:\机械G\尘封的回忆\DCIM\努比亚\电子光圈;J:\机械G\尘封的回忆\DCIM\努比亚
J:\机械G\尘封的回忆\DCIM\努比亚;J:\机械G\尘封的回忆\DCIM\努比亚\光绘;J:\机械G\尘封的回忆\DCIM\努比亚
J:\机械D\桌面;J:\机械G\尘封的回忆\FoeverLove\20230703领证咯;J:\机械D\桌面
J:\机械G\尘封的回忆\DCIM\努比亚\克隆\其他相册\1688SaveImage;J:\机械G\尘封的回忆\DCIM\努比亚\其他相册\1688SaveImage;J:\机械G\尘封的回忆\DCIM\努比亚\克隆\其他相册\1688SaveImage
J:\机械G\尘封的回忆\DCIM\努比亚;J:\机械G\尘封的回忆\DCIM\努比亚\Dng;J:\机械G\尘封的回忆\DCIM\努比亚
J:\机械D\桌面;J:\机械G\尘封的回忆\DCIM\新建文件夹\Camera;J:\机械D\桌面
J:\机械G\尘封的回忆\DCIM\努比亚;J:\机械G\尘封的回忆\DCIM\努比亚\时光;J:\机械G\尘封的回忆\DCIM\努比亚
J:\机械G\尘封的回忆\DCIM\努比亚\克隆\其他相册\.lockpaper;J:\机械G\尘封的回忆\DCIM\努比亚\其他相册\.lockpaper;J:\机械G\尘封的回忆\DCIM\努比亚\克隆\其他相册\.lockpaper
J:\机械D\JisuCloud\摄图网_video_27560\__MACOSX\粉色浪漫婚礼 folder-1;J:\机械D\JisuCloud\摄图网_video_27560\__MACOSX\粉色浪漫婚礼 folder-1\(Footage)\素材;J:\机械D\JisuCloud\摄图网_video_27560\__MACOSX\粉色浪漫婚礼 folder-1
J:\机械D\JisuCloud\摄图网_video_27560\__MACOSX\粉色浪漫婚礼 folder-1\(Footage);J:\机械D\JisuCloud\摄图网_video_27560\__MACOSX\粉色浪漫婚礼 folder-1\(Footage)\素材;J:\机械D\JisuCloud\摄图网_video_27560\__MACOSX\粉色浪漫婚礼 folder-1\(Footage)
J:\机械D\JisuCloud\摄图网_video_27560\__MACOSX\粉色浪漫婚礼 folder-1;J:\机械D\JisuCloud\摄图网_video_27560\__MACOSX\粉色浪漫婚礼 folder-1\(Footage);J:\机械D\JisuCloud\摄图网_video_27560\__MACOSX\粉色浪漫婚礼 folder-1
J:\机械G\尘封的回忆\单反\100ND780;J:\机械G\尘封的回忆\单反\100ND780\姐-婚礼;J:\机械G\尘封的回忆\单反\100ND780'''

    csv_file_path = "处理总文件md5.csv"  # 输入的 CSV 文件路径
    unique_files_output_csv = "unique_files.csv"  # 输出的独有文件 CSV
    same_files_output_csv = "same_files.csv"  # 输出的独有文件 CSV
    num_threads = 2048
    if dir.__contains__("\n"):
        start_with_str(csv_file_path, unique_files_output_csv, same_files_output_csv, dir, num_threads)
    else:
        start_with_input(csv_file_path, unique_files_output_csv, same_files_output_csv, dir, num_threads)