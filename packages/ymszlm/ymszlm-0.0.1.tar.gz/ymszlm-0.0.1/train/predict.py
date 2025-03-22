import argparse
import os
from pathlib import Path

import scipy.io as sio
import torch
from torch.utils.data import DataLoader
from torchvision import transforms

from models.HSAZLM import create_cnn, create_fcnn
from tools.dataset import CustomDataset
from tools.plotting import plot_confusion_matrix
from tools.tool import initialize_results_file, append_to_results_file
from tools.train_eval_utils import cnn_predict, zlm_predict
from train_fcnn import create_feature_extractor


def main(args):
    device = torch.device('cuda:0' if torch.cuda.is_available() else "cpu")
    print("Using {} device.".format(device.type))
    output_dir = args.output_dir
    path = Path(args.data_path)
    parent_dir = path.parent
    data_name = parent_dir.name
    column_widths = [5, 4, 8, 9, 7, 8]  # 根据实际需要调整宽度

    results_file = os.path.join(output_dir, 'predict_results.txt')
    column_order = ['model', 'data', 'accuracy', 'precision', 'recalls', 'f1_score']
    initialize_results_file(results_file, '\t'.join(column_order) + '\n')

    predict_data = CustomDataset(root_dir=args.data_path, transform=transforms.ToTensor())
    predict_loader = DataLoader(predict_data, batch_size=args.batch_size, shuffle=True)
    feature_extractor = create_feature_extractor(args.feature_path).to(device)
    fcnn = create_fcnn(args.model_path, output_dim=args.fcnn_dim).to(device)
    cnn = create_cnn(args.cnn_path, args.cnn_dim).to(device)

    mat_data = sio.loadmat(args.hsa_path)
    hsa_matrix = mat_data.get('HSA')
    hsa_matrix = torch.tensor(hsa_matrix).float().to(device)

    cnn_result = cnn_predict(cnn, predict_loader, device)
    cnn_result.update({'model': 'cnn', 'data': data_name})
    print(f'cnn Accuracy: {cnn_result["accuracy"]:.2%}, Precision: {cnn_result["precision"]:.2%}, '
          f'Recall: {cnn_result["recall"]:.2%}, F1: {cnn_result["f1_score"]:.2%}')

    zlm_result = zlm_predict(feature_extractor, fcnn, predict_loader, device, hsa_matrix)
    zlm_result.update({'model': 'zlm', 'data': data_name})
    print(f'ZLM Accuracy: {zlm_result["accuracy"]:.2%}, Precision: {zlm_result["precision"]:.2%}, '
          f'Recall: {zlm_result["recall"]:.2%}, F1: {zlm_result["f1_score"]:.2%}')

    append_to_results_file(results_file, zlm_result, column_order, column_widths)
    append_to_results_file(results_file, cnn_result, column_order, column_widths)
    plot_confusion_matrix(zlm_result['cm'], classes=predict_data.classes, title='Confusion matrix',
                          save_path=os.path.join(output_dir, f'zlm_confusion_matrix_{data_name}.png'))
    plot_confusion_matrix(cnn_result['cm'], classes=predict_data.classes, title='Confusion matrix',
                          save_path=os.path.join(output_dir, f'cnn_confusion_matrix_{data_name}.png'))


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--fcnn-dim', type=int, default=517)
    parser.add_argument('--cnn-dim', type=int, default=4)
    parser.add_argument('--data_path', default=r'./../data/dataset')
    parser.add_argument('--model_path', default=r'./../data/output/train_D0/fcnn_best.pth')
    parser.add_argument('--hsa_path', default=r'./../data/output/train_D0/HSA.mat')
    parser.add_argument('--feature_path', default=r'./../data/output/train_D0/best_feature_extractor.pth')
    parser.add_argument('--cnn_path', default=r'./../data/output/train_D0/cnn_model.pth')
    parser.add_argument('--output-dir', default=r'./../data/output/train_D0/predict')
    parser.add_argument('--batch-size', type=int, default=40)
    return parser.parse_args()


def list_folders(path):
    # 获取目录下的所有内容
    entries = os.listdir(path)
    # 筛选只保留文件夹
    folders = [entry for entry in entries if os.path.isdir(os.path.join(path, entry))]
    return folders


if __name__ == '__main__':
    opt = parse_args()
    print(opt)
    os.makedirs(opt.output_dir, exist_ok=True)
    data_dir = os.path.abspath(opt.data_path)
    dir_list = list_folders(data_dir)
    for dir_name in dir_list:
        print(f'predict {dir_name}...')
        opt.data_path = os.path.join(data_dir, dir_name, 'val')
        main(opt)
