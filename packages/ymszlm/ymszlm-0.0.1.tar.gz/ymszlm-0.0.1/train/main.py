import argparse
import os

import torch
from torch import nn
from torch.optim.lr_scheduler import ReduceLROnPlateau
from torch.utils.data import DataLoader
from torchvision import transforms

from models.HSAZLM import CNN, DRCAE
from tools.dataset import CustomDataset
from tools.plotting import plot_confusion_matrix, plot_all_metrics
from tools.tool import initialize_results_file, append_to_results_file
from tools.train_eval_utils import train_feature_extractor_one_epoch, train_decae_one_epoch


def main(args):
    output_dir = args.output_dir
    vis_dir = os.path.join(output_dir, 'vis')
    confusion_matrix_dir = os.path.join(output_dir, 'confusion_matrix')
    os.makedirs(vis_dir, exist_ok=True)
    os.makedirs(confusion_matrix_dir, exist_ok=True)

    cnn_results_file = os.path.join(output_dir, 'cnn_results.txt')
    decae_results_file = os.path.join(output_dir, 'decae_results.txt')
    cnn_column_order = ['epoch', 'train_losses', 'val_losses', 'accuracy', 'precision', 'recalls', 'f1_score', 'lr']
    decae_column_order = ['epoch', 'train_losses', 'val_losses', 'lr']
    cnn_column_widths = [5, 12, 10, 8, 9, 7, 8, 10]
    decae_column_widths = [5, 12, 10]  # 根据实际需要调整宽度
    initialize_results_file(cnn_results_file, '\t'.join(cnn_column_order) + '\n')
    initialize_results_file(decae_results_file, '\t'.join(decae_column_order) + '\n')

    device = torch.device('cuda:0' if torch.cuda.is_available() else "cpu")
    print("Using {} device training.".format(device.type))

    # 初始化验证集Dataset
    validation_dir = os.path.join(args.data_path, 'val')  # 替换为你的验证集图片目录
    validation_dataset = CustomDataset(root_dir=validation_dir, transform=transforms.ToTensor())
    val_loader = DataLoader(dataset=validation_dataset, batch_size=args.batch_size, shuffle=False)

    # 训练集数据加载器
    train_dir = os.path.join(args.data_path, 'train')
    train_dataset = CustomDataset(root_dir=train_dir, transform=transforms.ToTensor())
    train_loader = DataLoader(dataset=train_dataset, batch_size=args.batch_size, shuffle=True)

    cnn_model = CNN(args.cnn_num).to(device)
    decae = DRCAE().to(device)
    cnn_optimizer = torch.optim.Adam(cnn_model.parameters(), lr=args.cnn_lr)
    decae_optimizer = torch.optim.Adam(decae.parameters(), lr=args.decae_lr)
    cnn_scheduler = ReduceLROnPlateau(cnn_optimizer, factor=0.5, min_lr=1e-8, patience=5)
    decae_scheduler = ReduceLROnPlateau(decae_optimizer, factor=0.5, min_lr=1e-8, patience=5)
    cnn_criterion = nn.CrossEntropyLoss()
    decae_criterion = nn.MSELoss()
    # 记录结果
    metrics = {
        'cnn': {'train_loss': [], 'val_loss': [], 'train_accuracy': [], 'accuracy': [],
                'precision': [], 'recall': [], 'f1_score': [], 'lr': []},
        'decae': {'train_loss': [], 'val_loss': [], 'lr': []}
    }
    save_model = {'best_feature_extractor': None, 'best_encoder': None,
                  'last_feature_extractor': None, 'last_encoder': None, 'best_cnn': None}
    best_model = {'cnn': -1, 'encoder': 1e8}

    print('feature extractor training...')
    for epoch in range(args.cnn_epochs):
        cnn_res, train_accuracy = train_feature_extractor_one_epoch(model=cnn_model,
                                                                    train_loader=train_loader,
                                                                    val_loader=val_loader,
                                                                    device=device,
                                                                    optimizer=cnn_optimizer,
                                                                    criterion=cnn_criterion,
                                                                    epoch=epoch)
        cnn_res.update({'lr': cnn_scheduler.get_last_lr()[0]})
        cnn_scheduler.step(cnn_res['train_loss'])
        metrics['cnn']['train_loss'].append(cnn_res['train_loss'])
        metrics['cnn']['val_loss'].append(cnn_res['val_loss'])
        metrics['cnn']['train_accuracy'].append(train_accuracy)
        metrics['cnn']['accuracy'].append(cnn_res['accuracy'])
        metrics['cnn']['precision'].append(cnn_res['precision'])
        metrics['cnn']['recall'].append(cnn_res['recall'])
        metrics['cnn']['f1_score'].append(cnn_res['f1_score'])
        metrics['cnn']['lr'].append(cnn_res['lr'])

        # 保存模型
        if save_model['last_feature_extractor'] is not None:
            os.remove(save_model['last_feature_extractor'])
        save_model['last_feature_extractor'] = os.path.join(output_dir, f'feature_extractor_{epoch + 1}.pth')
        cnn_model.save(path=save_model['last_feature_extractor'])
        # 最好的模型
        if cnn_res['f1_score'] > best_model['cnn']:
            best_model['cnn'] = cnn_res['f1_score']
            if save_model['best_feature_extractor'] is not None:
                os.remove(save_model['best_feature_extractor'])
                os.remove(save_model['best_cnn'])
            save_model['best_feature_extractor'] = os.path.join(output_dir, f'best_feature_extractor.pth')
            save_model['best_cnn'] = os.path.join(output_dir, f'cnn_model.pth')
            cnn_model.save(path=save_model['best_feature_extractor'])
            torch.save(cnn_model.state_dict(), save_model['best_cnn'])

        plot_confusion_matrix(cnn_res['cm'], classes=train_dataset.classes, title='Confusion matrix',
                              save_path=os.path.join(confusion_matrix_dir, f'confusion_matrix_{epoch + 1}.png'))
        append_to_results_file(cnn_results_file, cnn_res, cnn_column_order, cnn_column_widths)

    print('DECAE training...')
    for epoch in range(args.decae_epochs):
        decae_res = train_decae_one_epoch(model=decae, train_loader=train_loader,
                                          val_loader=val_loader, device=device,
                                          epoch=epoch, optimizer=decae_optimizer,
                                          criterion=decae_criterion)
        decae_res.update({'lr': decae_scheduler.get_last_lr()[0]})
        decae_scheduler.step(decae_res['train_loss'])
        metrics['decae']['train_loss'].append(decae_res['train_loss'])
        metrics['decae']['val_loss'].append(decae_res['val_loss'])
        metrics['decae']['lr'].append(decae_res['lr'])
        append_to_results_file(decae_results_file, decae_res, decae_column_order, decae_column_widths)

        if save_model['last_encoder'] is not None:
            os.remove(save_model['last_encoder'])
        save_model['last_encoder'] = os.path.join(output_dir, f'encoder_{epoch + 1}.pth')
        decae.save(path=save_model['last_encoder'])
        if decae_res['val_loss'] < best_model['encoder']:
            best_model['encoder'] = decae_res['val_loss']
            if save_model['best_encoder'] is not None:
                os.remove(save_model['best_encoder'])
            save_model['best_encoder'] = os.path.join(output_dir, f'best_encoder.pth')
            decae.save(path=save_model['best_encoder'])

    # 结果可视化
    plot_all_metrics(metrics['cnn'], args.cnn_epochs, save_path=vis_dir, img_name='cnn')
    plot_all_metrics(metrics['decae'], args.decae_epochs, save_path=vis_dir, img_name='decae')


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cnn-num', type=int, default=4)
    parser.add_argument('--batch-size', type=int, default=32)
    parser.add_argument('--cnn-epochs', type=int, default=1)
    parser.add_argument('--decae-epochs', type=int, default=1)
    parser.add_argument('--cnn-lr', type=float, default=1e-4)
    parser.add_argument('--decae-lr', type=float, default=1e-4)
    parser.add_argument('--data-path', default=r'./../data/dataset/D0')
    parser.add_argument('--output-dir', default=r'./../data/output/train_D0')
    return parser.parse_args()


if __name__ == '__main__':
    opt = parse_args()
    print(opt)
    os.makedirs(opt.output_dir, exist_ok=True)
    main(opt)
