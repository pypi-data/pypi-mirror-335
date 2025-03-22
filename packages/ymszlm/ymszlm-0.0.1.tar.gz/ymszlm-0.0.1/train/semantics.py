import argparse
import os.path
from collections import defaultdict

import numpy as np
import torch
from scipy.io import savemat
from torch.utils.data import DataLoader, ConcatDataset
from torchvision import transforms
from tqdm import tqdm

from models.HSAZLM import Encoder
from tools.dataset import CustomDataset


def create_encoder(encoder_path):
    """创建并加载预训练编码器"""
    encoder = Encoder()
    encoder.load_state_dict(torch.load(encoder_path, map_location='cpu', weights_only=True))
    return encoder


def extract_features(encoder, loader, device):
    """从数据集中提取特征"""
    features = defaultdict(list)
    encoder.eval()
    with torch.no_grad():
        for images, labels in tqdm(loader, desc="Extracting features", colour='blue'):
            outputs = encoder(images.to(device))
            for label, feat in zip(labels.cpu().numpy(), outputs.cpu().numpy()):
                features[int(label)].append(feat)
    return features


def calculate_label_means(features_dict):
    """计算每个类别的特征均值并保持原始顺序"""
    sorted_labels = sorted(features_dict.keys())
    return np.array([np.mean(features_dict[label], axis=0) for label in sorted_labels])


def new_extract_features(encoder, loader, device):
    """从数据集中提取特征并分离特征与标签"""
    features_list = []  # 存储特征
    labels_list = []  # 存储标签

    encoder.eval()
    with torch.no_grad():
        for images, labels in tqdm(loader, desc="Extracting features", colour='blue'):
            # 将图像数据移动到指定设备
            images = images.to(device)

            # 提取特征
            outputs = encoder(images)

            # 将特征和标签转换为numpy数组并存储
            features_np = outputs.cpu().numpy()
            labels_np = labels.cpu().numpy()

            # 追加到列表（保持对应关系）
            features_list.extend(features_np)
            labels_list.extend(labels_np)  # 确保标签为整数类型

    return features_list, labels_list


def main(args):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    # 初始化数据集和数据加载器
    data_dir = args.root_dir
    dataset1 = CustomDataset(os.path.join(data_dir, 'train'), transform=transforms.ToTensor())
    dataset2 = CustomDataset(os.path.join(data_dir, 'val'), transform=transforms.ToTensor())
    dataset = ConcatDataset([dataset1, dataset2])
    loader = DataLoader(dataset, batch_size=args.batch_size, shuffle=False)

    # 特征提取
    encoder = create_encoder(args.encoder_path).to(device)

    # features_list, labels_list = new_extract_features(encoder, loader, device)
    # savemat('train.mat', {'features': features_list, 'labels': labels_list})
    features_dict = extract_features(encoder, loader, device)
    nsa_array = calculate_label_means(features_dict)

    # 合并语义属性
    sa_matrix = np.loadtxt(args.sa_path, dtype=float)
    hsa = np.concatenate([sa_matrix, nsa_array], axis=1)

    # 保存结果
    savemat(args.save_path, {'HSA': hsa})
    print(f"Saved HSA matrix with shape {hsa.shape} to {args.save_path}")


def parse_args():
    parser = argparse.ArgumentParser(description='Generate HSA matrix')
    parser.add_argument('--batch_size', type=int, default=1)
    parser.add_argument('--root_dir', default=r'D:\Code\2-ZSL\Zero-Shot-Learning\data\新建文件夹\dataset\CRWU\D0')
    parser.add_argument('--encoder_path', default=r'D:\Code\2-ZSL\1-output\train_D0\best_encoder.pth')
    parser.add_argument('--sa_path', default=r'./../data/dataset/predicate-matrix.txt')
    parser.add_argument('--save_path', default=r'./../data/output/train_D0/HSA.mat')
    return parser.parse_args()


if __name__ == '__main__':
    opt = parse_args()
    # opt.root_dir = os.path.abspath(opt.root_dir)
    # opt.sa_path = os.path.abspath(opt.sa_path)
    # opt.save_path = os.path.abspath(opt.save_path)
    # opt.encoder_path = os.path.abspath(opt.encoder_path)
    print(opt)
    main(opt)
