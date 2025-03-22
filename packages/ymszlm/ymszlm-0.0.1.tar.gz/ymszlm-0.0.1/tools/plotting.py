import os

import numpy as np
from matplotlib import pyplot as plt, rcParams


def plot_confusion_matrix(cm, classes,
                          save_path='confusion_matrix_D1.png',
                          normalize=False,
                          title='Confusion matrix',
                          cmap=plt.cm.Blues):
    """
        绘制混淆矩阵的函数
        这个函数不修改原始数据，但会返回混淆矩阵。
        """
    plt.figure()
    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        print("Normalized confusion matrix")
    else:
        print('Confusion matrix, without normalization')

    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.colorbar()
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=45)
    plt.yticks(tick_marks, classes)

    fmt = '.2f' if normalize else 'd'
    # 用于判断变量normalize的值。如果normalize为True，则将格式化字符串.2f赋值给变量fmt；否则，将格式化字符串'd'赋值给变量fmt。
    # 其中，.2f表示保留两位小数，'d'表示以十进制形式显示。
    thresh = cm.max() / 2.
    for i, j in np.ndindex(cm.shape):
        plt.text(j, i, format(cm[i, j], fmt),
                 horizontalalignment="center",
                 color="white" if cm[i, j] > thresh else "black")

    plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label')
    plt.savefig(save_path)
    plt.close()


def plot_all_metrics(metrics_dict, num_epochs, img_name, save_path):
    """
    绘制训练指标曲线

    参数：
        metrics_dict: 包含指标数据的字典，键为指标名称，值为一个列表
        num_epochs: 训练的总轮数
        save_path: 保存图像的路径，默认为 'metrics.png'
    """
    # 检查是否存在 train_losses 和 val_losses
    has_train_loss = 'train_losses' in metrics_dict
    has_val_loss = 'val_losses' in metrics_dict

    # 获取指标名称列表，排除 'epoch'
    metric_names = [key for key in metrics_dict.keys() if key != 'epoch']

    # 如果有 train_losses 和 val_losses，添加一个特殊的键
    if has_train_loss and has_val_loss:
        metric_names.append('train_val_loss')

    # 计算子图的行数和列数，使得 m*n 最接近 metric_names 的数量
    num_metrics = len(metric_names)
    m = int(np.ceil(np.sqrt(num_metrics)))
    n = int(np.ceil(num_metrics / m))

    # 创建子图
    fig, axes = plt.subplots(m, n, figsize=(12 * n, 6 * m))
    axes = axes.flatten()  # 将二维数组的 axes 展平为一维

    # 绘制每个指标的曲线
    for i, name in enumerate(metric_names):
        ax = axes[i]

        if name == 'train_val_loss':
            # 绘制 train_losses 和 val_losses 在同一张图
            train_loss = metrics_dict['train_losses']
            val_loss = metrics_dict['val_losses']
            ax.plot(range(1, num_epochs + 1), train_loss, label='Training Loss')
            ax.plot(range(1, num_epochs + 1), val_loss, label='Validation Loss')
            ax.set_title('Loss over epochs')
        else:
            # 绘制其他指标
            metric = metrics_dict[name]
            ax.plot(range(1, num_epochs + 1), metric, label=f'{name}')
            ax.set_title(f'{name} over epochs')

        ax.set_xlabel('Epochs')
        ax.set_ylabel(f'{name}')
        ax.legend()
        ax.grid(True)

    # 删除多余的子图
    for j in range(i + 1, len(axes)):
        fig.delaxes(axes[j])

    # 调整布局并保存图像
    plt.tight_layout()
    plt.savefig(os.path.join(save_path, f'{img_name}_metrics.png'))
    plt.close()

    # 为每个指标单独绘制一张图
    for name in metric_names:
        plt.figure(figsize=(12, 6))
        if name == 'train_val_loss':
            # 绘制 train_losses 和 val_losses 在同一张图
            train_loss = metrics_dict['train_losses']
            val_loss = metrics_dict['val_losses']
            plt.plot(range(1, num_epochs + 1), train_loss, label='Training Loss')
            plt.plot(range(1, num_epochs + 1), val_loss, label='Validation Loss')
            plt.title('Loss over epochs')
        else:
            # 绘制其他指标
            metric = metrics_dict[name]
            plt.plot(range(1, num_epochs + 1), metric, label=f'{name}')
            plt.title(f'{name} over epochs')

        plt.xlabel('Epochs')
        plt.ylabel(f'{name}')
        plt.legend()
        plt.grid(True)
        plt.savefig(os.path.join(save_path, f'{img_name}_{name}.png'))
        plt.close()


def plot_metrics(metric1, metric2, num_epochs, name, save_path='metrics.png'):
    plt.figure(figsize=(12, 6))
    plt.plot(range(1, num_epochs + 1), metric1, label=f'Training {name}')
    plt.plot(range(1, num_epochs + 1), metric2, label=f'Validation {name}')
    plt.title(f'{name} over epochs')
    plt.xlabel('Epochs')
    plt.ylabel(f'{name}')
    plt.legend()
    plt.grid(True)
    plt.savefig(save_path)
    plt.close()


def plot_single(met, num_epochs, name, save_path='metrics.png'):
    plt.figure(figsize=(12, 6))
    plt.plot(range(1, num_epochs + 1), met)
    plt.title(f'{name} over epochs')
    plt.xlabel('Epochs')
    plt.ylabel(f'{name}')
    plt.grid(True)
    plt.savefig(save_path)
    plt.close()


def plot_data_from_files(file_paths, exclude_headers=None, save_path='metrics.png'):
    """
    Plot data from multiple text files, excluding specified headers, with a fixed 2 rows layout.
    Use folder name as label if file names are consistent, otherwise use file name.

    Args:
    - file_paths (list): A list of file paths to read data from.
    - exclude_headers (list): A list of headers to exclude from plotting.
    """
    # 设置支持中文的字体
    rcParams['font.family'] = 'Microsoft YaHei'  # Windows系统
    # rcParams['font.family'] = 'PingFang SC'  # macOS系统
    rcParams['axes.unicode_minus'] = False  # 正确显示负号
    if exclude_headers is None:
        exclude_headers = ['epoch', 'lr']  # 默认排除的头部

    # 初始化一个列表来存储所有数据
    all_data = []

    # 处理每个文件
    for path in file_paths:
        data = {}
        with open(path, 'r') as file:
            headers = file.readline().strip().split('\t')
            for header in headers:
                data[header] = []
            for line in file:
                values = line.strip().split('\t')
                for header, value in zip(headers, values):
                    data[header].append(float(value))
        all_data.append(data)

    # 提取共同的epochs
    epochs = all_data[0]['epoch']  # 假设所有文件都有相同的epochs

    # 创建子图
    num_metrics = len([m for m in all_data[0].keys() if m not in exclude_headers])
    num_cols = (num_metrics + 1) // 2 + (1 if num_metrics % 2 else 0)  # 计算列数
    fig, axs = plt.subplots(2, num_cols, figsize=(15, 8), constrained_layout=True)
    axs = axs.flatten()  # 展平数组以便更容易迭代

    # 检查文件名是否一致，以确定使用文件名还是文件夹名作为标签
    file_names = [os.path.basename(path) for path in file_paths]
    unique_names = set(file_names)
    if len(unique_names) == 1:
        labels = [os.path.basename(os.path.dirname(path)) for path in file_paths]
    else:
        labels = file_names

    # 绘制每个指标的曲线图
    for i, key in enumerate([m for m in all_data[0].keys() if m not in exclude_headers]):
        for j, data in enumerate(all_data):
            axs[i].plot(epochs, data[key], label=f'{labels[j]} {key}', color=f'C{j}')
        axs[i].set_title(f'{key} over Epochs')
        axs[i].set_xlabel('Epoch')
        axs[i].set_ylabel(key)
        axs[i].legend()

    # 隐藏多余的子图
    for i in range(num_metrics, len(axs)):
        axs[i].axis('off')

    # 显示图表
    plt.savefig(save_path)
    plt.close()
