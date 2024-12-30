import os
import ctypes
from ctypes import wintypes
from PIL import Image
from PIL.ExifTags import TAGS
from datetime import datetime

# 定义 Windows API 函数和结构
class FILETIME(ctypes.Structure):
    _fields_ = [("dwLowDateTime", wintypes.DWORD), ("dwHighDateTime", wintypes.DWORD)]

def get_filetime(dt):
    """
    将 datetime 转换为 Windows FILETIME
    """
    epoch_start = datetime(1601, 1, 1)
    hundred_ns_intervals = int((dt - epoch_start).total_seconds() * 10**7)
    low = hundred_ns_intervals & 0xFFFFFFFF
    high = hundred_ns_intervals >> 32
    return FILETIME(low, high)

def set_file_creation_time(file_path, creation_time):
    """
    设置文件的创建时间
    """
    handle = ctypes.windll.kernel32.CreateFileW(
        file_path,
        0x40000000,  # GENERIC_WRITE
        0,
        None,
        3,  # OPEN_EXISTING
        0x80,  # FILE_ATTRIBUTE_NORMAL
        None
    )
    if handle == -1:
        print(f"无法打开文件: {file_path}")
        return False

    creation_filetime = get_filetime(creation_time)
    result = ctypes.windll.kernel32.SetFileTime(
        handle,
        ctypes.byref(creation_filetime),  # 创建时间
        None,  # 访问时间（保持不变）
        None   # 修改时间（保持不变）
    )
    ctypes.windll.kernel32.CloseHandle(handle)

    if not result:
        print(f"无法设置文件创建时间: {file_path}")
        return False

    print(f"成功设置创建时间: {file_path}")
    return True

def get_photo_taken_date(file_path):
    """
    从图片 EXIF 数据中提取拍摄日期
    """
    try:
        img = Image.open(file_path)
        exif_data = img._getexif()
        if not exif_data:
            return None

        for tag_id, value in exif_data.items():
            tag_name = TAGS.get(tag_id, tag_id)
            if tag_name == "DateTime":
                return datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
    except Exception as e:
        print(f"无法获取拍摄日期: {file_path}, 错误: {e}")
    return None

def process_folder(folder_path):
    """
    遍历文件夹，修改所有图片文件的创建日期为拍摄日期
    """
    for root, dirs, files in os.walk(folder_path):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            if file_name.lower().endswith(('.jpg', '.jpeg', '.png')):
                taken_date = get_photo_taken_date(file_path)
                if taken_date:
                    set_file_creation_time(file_path, taken_date)
                else:
                    print(f"跳过没有拍摄日期的文件: {file_path}")

if __name__ == "__main__":
    folder_to_process = input("请输入文件夹路径: ").strip()
    if os.path.exists(folder_to_process) and os.path.isdir(folder_to_process):
        process_folder(folder_to_process)
    else:
        print("无效的文件夹路径！")
