import argparse
import os

import numpy as np
import scipy.io as sio
import torch
from torch.optim.lr_scheduler import ReduceLROnPlateau
from torch.utils.data import DataLoader
from torchvision import transforms

from models.HSAZLM import create_feature_extractor, FCNN, LSELoss
from tools.dataset import CustomDataset
from tools.plotting import plot_metrics
from tools.tool import initialize_results_file, append_to_results_file
from tools.train_eval_utils import train_fcnn_one_epoch


def main(args):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    output_dir = args.output_dir
    vis_dir = os.path.join(output_dir, 'vis')
    print("Using {} device training.".format(device.type))
    results_file = os.path.join(output_dir, 'results_fcnn.txt')
    column_order = ['epoch', 'train_losses', 'val_losses', 'lr']
    column_widths = [5, 12, 10]  # 根据实际需要调整宽度
    initialize_results_file(results_file, '\t'.join(column_order) + '\n')

    batch_size = args.batch_size
    # 初始化验证集Dataset
    validation_dir = os.path.join(args.data_path, 'val')  # 替换为你的验证集图片目录
    validation_dataset = CustomDataset(root_dir=validation_dir, transform=transforms.ToTensor())
    val_loader = DataLoader(dataset=validation_dataset, batch_size=batch_size, shuffle=False)
    # 训练集数据加载器
    train_dir = os.path.join(args.data_path, 'train')
    train_dataset = CustomDataset(root_dir=train_dir, transform=transforms.ToTensor())
    train_loader = DataLoader(dataset=train_dataset, batch_size=batch_size, shuffle=True)

    mat_data = sio.loadmat(args.hsa_path)
    hsa_matrix = mat_data.get('HSA')
    hsa_matrix = torch.tensor(hsa_matrix)

    feature_extractor = create_feature_extractor(args.feature_path).to(device)
    fcnn = FCNN(args.fcnn_channels).to(device)
    optimizer = torch.optim.Adam(fcnn.parameters(), lr=args.lr)
    scheduler = ReduceLROnPlateau(optimizer, factor=0.5, min_lr=1e-8, patience=5)
    criterion = LSELoss(hsa_matrix).to(device)
    train_losses = []
    val_losses = []
    last = None
    best = None
    best_loss = np.inf

    for epoch in range(args.epochs):
        result = train_fcnn_one_epoch(
            cnn=feature_extractor, fcnn=fcnn, optimizer=optimizer, train_loader=train_loader,
            val_loader=val_loader, device=device, criterion=criterion, epoch=epoch
        )
        result.update({'lr': scheduler.get_last_lr()})
        scheduler.step(result['val_loss'])
        train_losses.append(result['train_loss'])
        val_losses.append(result['val_loss'])
        append_to_results_file(results_file, result, column_order, column_widths)

        if last is not None:
            os.remove(last)
        last = os.path.join(output_dir, f'fcnn_epoch_{epoch + 1}.pth')
        torch.save(fcnn.state_dict(), last)
        if result['val_loss'] < best_loss:
            best_loss = result['val_loss']
            if best is not None:
                os.remove(best)
            best = os.path.join(output_dir, f'fcnn_best.pth')
            torch.save(fcnn.state_dict(), best)

    plot_metrics(train_losses, val_losses, args.epochs, name='FCNN Loss',
                 save_path=os.path.join(vis_dir, 'fcnn_loss.png'))


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--lr', type=float, default=1e-4)
    parser.add_argument('--epochs', type=int, default=1)
    parser.add_argument('--batch_size', type=int, default=32)
    parser.add_argument('--fcnn-channels', type=int, default=517)
    parser.add_argument('--data-path', default=r'./../data/dataset/D0')
    parser.add_argument('--output_dir', default=r'./../data/output/train_D0')
    parser.add_argument('--feature-path', default=r'./../data/output/train_D0/best_feature_extractor.pth')
    parser.add_argument('--hsa-path', default=r'./../data/output/train_D0/HSA.mat')
    return parser.parse_args()


if __name__ == '__main__':
    opt = parse_args()
    print(opt)
    main(opt)
