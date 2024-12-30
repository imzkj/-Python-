import os
from send2trash import send2trash

def delete_jpg_files(directory):
    """
    删除指定目录中以 `(1).jpg` 结尾的文件，将其移入回收站，并统计删除的文件数量。
    """
    if not os.path.exists(directory) or not os.path.isdir(directory):
        print(f"无效的目录: {directory}")
        return 0  # 返回删除文件数为 0

    deleted_count = 0

    for root, _, files in os.walk(directory):
        for file_name in files:
            if file_name.endswith(".cfg"):
                file_path = os.path.join(root, file_name)
                try:
                    send2trash(file_path)
                    print(f"已移入回收站: {file_path}")
                    deleted_count += 1
                except Exception as e:
                    print(f"无法删除文件 {file_path}，错误: {e}")

    return deleted_count

if __name__ == "__main__":
    input_directory = "J:\机械G\尘封的回忆"
    total_deleted = delete_jpg_files(input_directory)
    print(f"处理完成，总共删除了 {total_deleted} 个文件。")
