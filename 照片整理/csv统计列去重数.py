import pandas as pd
import datetime

def count_unique_values(csv_file_path):
    # 读取 CSV 文件
    df = pd.read_csv(csv_file_path)

    # 将 'received_at' 从 Unix 时间戳转换为日期
    df['received_at'] = pd.to_datetime(df['received_at'], unit='s')

    # 筛选出 'received_at' 为 2024/12/16 的数据
    filter_date = datetime.datetime(2024, 12, 16)
    df_filtered = df[df['received_at'].dt.date == filter_date.date()]

    # 筛选出 'activity_kind' 为 'install' 的数据
    df_filtered = df_filtered[df_filtered['activity_kind'] == 'install']

    # 获取每列的总数（未去重的数量）和去重的数量
    total_counts = df_filtered.count()
    unique_counts = df_filtered.nunique()

    # 创建一个 DataFrame 用于显示每列的去重数和未去重数
    result = pd.DataFrame({
        'Total Count': total_counts,
        'Unique Count': unique_counts
    })

    # 按 'Unique Count' 值倒序排序
    result_sorted = result.sort_values(by='Unique Count', ascending=False)

    # 输出每列的总数和去重数
    for column, row in result_sorted.iterrows():
        print(f"Column: {column}, Total Count: {row['Total Count']}, Unique Count: {row['Unique Count']}")

# 示例：调用函数并传入 CSV 文件路径
csv_file_path = 'C:\\Users\\Administrator\\Downloads\\adjust_event.csv'  # 替换为你的 CSV 文件路径
count_unique_values(csv_file_path)
