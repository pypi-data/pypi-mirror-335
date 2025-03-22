import os
import re

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix


# 读取txt内两个不同表格的数据，并将结果转换为字典列表输出
def read_multi_table_txt(file_path):
    # 读取原始内容
    with open(file_path, 'r') as f:
        content = f.read()

    # 按表格标题分割内容（假设每个新表格以"epoch"开头）
    table_blocks = re.split(r'\n(?=epoch\s)', content.strip())

    # 处理每个表格块
    table_dicts = []
    for block in table_blocks:
        lines = [line.strip() for line in block.split('\n') if line.strip()]

        # 解析列名（处理制表符和混合空格）
        columns = re.split(r'\s{2,}|\t', lines[0])

        # 解析数据行（处理混合分隔符）
        data = []
        for line in lines[1:]:
            # 使用正则表达式分割多个连续空格/制表符
            row = re.split(r'\s{2,}|\t', line)
            data.append(row)

        # 创建DataFrame并自动转换数值类型
        df = pd.DataFrame(data, columns=columns)
        df = df.apply(pd.to_numeric, errors='coerce')  # 自动识别数值列，非数值转换为NaN

        # 将DataFrame转换为字典，每列以列表形式保存
        table_dict = df.to_dict(orient='list')
        table_dicts.append(table_dict)

    return table_dicts


# val和test时的相关结果指标计算
def calculate_results(all_labels, all_predictions, classes, average='macro'):
    results = {
        'accuracy': accuracy_score(y_true=all_labels, y_pred=all_predictions),
        'precision': precision_score(y_true=all_labels, y_pred=all_predictions, average=average),
        'recall': recall_score(y_true=all_labels, y_pred=all_predictions, average=average),
        'f1_score': f1_score(y_true=all_labels, y_pred=all_predictions, average=average),
        'cm': confusion_matrix(y_true=all_labels, y_pred=all_predictions, labels=np.arange(len(classes)))
    }
    return results


def initialize_results_file(results_file, result_info):
    """
    初始化结果文件，确保文件存在且第一行包含指定的内容。

    参数:
        results_file (str): 结果文件的路径。
        result_info (str): 需要写入的第一行内容。
    """
    # 检查文件是否存在
    if os.path.exists(results_file):
        # 如果文件存在，读取第一行
        with open(results_file, "r") as f:
            first_line = f.readline().strip()
        # 检查第一行是否与 result_info 一致
        if first_line == result_info.strip():
            print(f"文件 {results_file} 已存在且第一行已包含 result_info，不进行写入。")
        else:
            # 如果不一致，写入 result_info
            with open(results_file, "w") as f:
                f.write(result_info)
            print(f"文件 {results_file} 已被重新初始化。")
    else:
        # 如果文件不存在，创建并写入 result_info
        with open(results_file, "w") as f:
            f.write(result_info)
        print(f"文件 {results_file} 已创建并写入 result_info。")


def append_to_results_file(file_path: str,
                           data_dict: dict,
                           column_order: list,
                           column_widths: list = None,
                           float_precision: int = 5) -> None:
    """
    通用格式化文本行写入函数

    参数：
    file_path: 目标文件路径
    data_dict: 包含数据的字典，键为列名
    column_order: 列顺序列表，元素为字典键
    column_widths: 每列字符宽度列表 (可选)
    float_precision: 浮点数精度位数 (默认4位)
    """
    formatted_data = []

    # 遍历指定列顺序处理数据
    for i, col in enumerate(column_order):
        # 处理字典键的别名
        if col == 'train_losses':
            dict_key = 'train_loss'
        elif col == 'val_losses':
            dict_key = 'val_loss'
        elif col == 'recalls':
            dict_key = 'recall'
        else:
            dict_key = col

        if dict_key not in data_dict:
            raise ValueError(f"Missing required column: {dict_key}")

        value = data_dict[dict_key]
        col_type = type(value)

        # 根据数据类型进行格式化
        if isinstance(value, (int, np.integer)):
            fmt_value = f"{value:d}"
        elif isinstance(value, (float, np.floating)):
            if col in ['train_losses', 'val_losses']:  # 如果列名是'train_losses'或'val_losses'，保留浮点数精度位数+1位
                fmt_value = f"{value:.{float_precision + 1}f}"
            elif col == 'lr':  # 如果列名是'lr'，保留8位小数
                fmt_value = f"{value:.8f}"
            else:
                fmt_value = f"{value:.{float_precision}f}"
        elif isinstance(value, str):
            fmt_value = value
        else:  # 处理其他类型转换为字符串
            fmt_value = str(value)

        # 应用列宽对齐
        if column_widths and i < len(column_widths):
            try:
                if i == len(column_order) - 1:  # 最后一列左边对齐
                    fmt_value = fmt_value.ljust(column_widths[i])
                else:
                    fmt_value = fmt_value.rjust(column_widths[i])
            except TypeError:  # 处理非字符串类型
                if i == len(column_order) - 1:  # 最后一列左边对齐
                    fmt_value = str(fmt_value).ljust(column_widths[i])
                else:
                    fmt_value = str(fmt_value).rjust(column_widths[i])

        formatted_data.append(fmt_value)

    # 构建文本行并写入
    line = '\t'.join(formatted_data) + '\n'
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write(line)


def get_path(path):
    return os.path.abspath(path)
