import argparse
import os
from typing import Dict, List, Tuple

import torch
from torch import nn, optim
from torch.optim.lr_scheduler import ConstantLR
from torch.utils.data import DataLoader
from torchvision import transforms

from models.HSAZLM import CNN, DRCAE
from tools.dataset import CustomDataset
from tools.plotting import plot_confusion_matrix, plot_metrics, plot_single
from tools.tool import initialize_results_file, append_to_results_file
from tools.train_eval_utils import train_feature_extractor_one_epoch, train_decae_one_epoch


class JointTrainingSession:
    """联合训练会话的配置和状态管理"""

    def __init__(self, args):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.args = args
        self.output_dir = args.output_dir
        self.vis_dir = os.path.join(self.output_dir, 'vis')

        # 结果文件配置
        self.results_config = {
            'cnn': {
                'file': os.path.join(self.output_dir, 'cnn_results.txt'),
                'columns': ['epoch', 'train_losses', 'val_losses', 'accuracy', 'precision', 'recalls', 'f1_score',
                            'lr'],
                'widths': [5, 12, 10, 8, 9, 7, 8, 10]
            },
            'decae': {
                'file': os.path.join(self.output_dir, 'decae_results.txt'),
                'columns': ['epoch', 'train_losses', 'val_losses', 'lr'],
                'widths': [5, 12, 10]
            }
        }
        self._setup_directories()

        # 数据加载
        self.train_loader, self.val_loader = self._create_dataloaders()
        self.class_names = self.train_loader.dataset.classes

        # 模型初始化
        self.cnn_model = CNN().to(self.device)
        self.decae = DRCAE().to(self.device)

        # 优化器和调度器
        self.cnn_optimizer = optim.Adam(self.cnn_model.parameters(), lr=args.cnn_lr)
        self.decae_optimizer = optim.Adam(self.decae.parameters(), lr=args.decae_lr)
        self.cnn_scheduler = ConstantLR(self.cnn_optimizer, factor=1)
        self.decae_scheduler = ConstantLR(self.decae_optimizer, factor=1)

        # 训练状态跟踪
        self.metrics: Dict[str, Dict[str, List]] = {
            'cnn': {'train_loss': [], 'val_loss': [], 'train_accuracy': [], 'accuracy': [],
                    'precision': [], 'recall': [], 'f1_score': [], 'lr': []},
            'decae': {'train_loss': [], 'val_loss': [], 'lr': []}
        }
        self.best_metrics = {'cnn_f1': -1.0, 'decae_loss': float('inf')}

    def _setup_directories(self):
        """创建输出目录结构"""
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.vis_dir, exist_ok=True)
        # 初始化结果文件
        for model_type in ['cnn', 'decae']:
            header = '\t'.join(self.results_config[model_type]['columns']) + '\n'
            initialize_results_file(self.results_config[model_type]['file'], header)

    def _create_dataloaders(self) -> Tuple[DataLoader, DataLoader]:
        """创建训练和验证数据加载器"""
        transform = transforms.ToTensor()

        def create_loader(subset: str) -> DataLoader:
            path = os.path.join(self.args.data_path, subset)
            dataset = CustomDataset(root_dir=path, transform=transform)
            return DataLoader(
                dataset=dataset,
                batch_size=self.args.batch_size,
                shuffle=(subset == 'train'),
                pin_memory=True
            )

        return create_loader('train'), create_loader('val')

    def _save_model(self, model, model_type: str, epoch: int, metric_value: float):
        """智能保存模型并管理文件"""
        # 保存最新模型
        last_path = os.path.join(self.output_dir, f'{model_type}_last.pth')
        # torch.save(model.state_dict(), last_path)
        model.save(last_path)

        # 更新最佳模型
        if (model_type == 'cnn' and metric_value > self.best_metrics['cnn_f1']) or \
                (model_type == 'decae' and metric_value < self.best_metrics['decae_loss']):

            best_path = os.path.join(self.output_dir, f'best_{model_type}.pth')
            # torch.save(model.state_dict(), best_path)
            model.save(best_path)

            # 更新最佳指标记录
            if model_type == 'cnn':
                self.best_metrics['cnn_f1'] = metric_value
            else:
                self.best_metrics['decae_loss'] = metric_value

    def _train_cnn_phase(self):
        """CNN特征提取器训练阶段"""
        criterion = nn.CrossEntropyLoss()

        print('\n#### CNN Feature Extractor Training ####')
        for epoch in range(self.args.cnn_epochs):
            # 执行训练epoch
            cnn_res, train_acc = train_feature_extractor_one_epoch(
                model=self.cnn_model,
                train_loader=self.train_loader,
                val_loader=self.val_loader,
                device=self.device,
                optimizer=self.cnn_optimizer,
                criterion=criterion,
                epoch=epoch
            )

            # 更新学习率和指标
            cnn_res.update({'lr': self.cnn_scheduler.get_last_lr()[0]})
            self.cnn_scheduler.step()

            # 记录指标
            for key in ['train_losses', 'val_losses', 'accuracy', 'precision', 'recalls', 'f1_score']:
                key = key.replace('es', '') if 'es' in key else key
                key = 'recall' if 'recalls' in key else key
                self.metrics['cnn'][key].append(cnn_res[key])
            self.metrics['cnn']['train_accuracy'].append(train_acc)
            self.metrics['cnn']['lr'].append(cnn_res['lr'])

            # 保存模型和结果
            self._save_model(self.cnn_model, 'cnn', epoch, cnn_res['f1_score'])
            self._log_results('cnn', cnn_res, epoch)
            self._plot_confusion_matrix(cnn_res['cm'], epoch)

    def _train_decae_phase(self):
        """DECAE训练阶段"""
        criterion = nn.MSELoss()

        print('\n#### DECAE Training ####')
        for epoch in range(self.args.decae_epochs):
            # 执行训练epoch
            decae_res = train_decae_one_epoch(
                model=self.decae,
                train_loader=self.train_loader,
                val_loader=self.val_loader,
                device=self.device,
                optimizer=self.decae_optimizer,
                criterion=criterion,
                epoch=epoch
            )

            # 更新学习率和指标
            decae_res.update({'lr': self.decae_scheduler.get_last_lr()[0]})
            self.decae_scheduler.step()

            # 记录指标
            for key in ['train_losses', 'val_losses']:
                key = key.replace('es', '') if 'es' in key else key
                self.metrics['decae'][key].append(decae_res[key])
                # self.metrics['decae'][key.replace('es', '')].append(decae_res[key])
            self.metrics['decae']['lr'].append(decae_res['lr'])

            # 保存模型和结果
            self._save_model(self.decae, 'decae', epoch, decae_res['val_loss'])
            self._log_results('decae', decae_res, epoch)

    def _log_results(self, model_type: str, results: dict, epoch: int):
        """统一记录训练结果"""
        config = self.results_config[model_type]
        append_to_results_file(
            file_path=config['file'],
            data_dict=results,
            column_order=config['columns'],
            column_widths=config['widths']
        )

    def _plot_confusion_matrix(self, cm, epoch: int):
        """绘制并保存混淆矩阵"""
        plot_confusion_matrix(
            cm=cm,
            classes=self.class_names,
            title=f'Confusion Matrix (Epoch {epoch + 1})',
            save_path=os.path.join(self.vis_dir, f'confusion_matrix_{epoch + 1}.png')
        )

    def visualize_results(self):
        """可视化所有训练结果"""
        # CNN相关可视化
        plot_metrics(
            self.metrics['cnn']['train_accuracy'],
            self.metrics['cnn']['accuracy'],
            self.args.cnn_epochs,
            name='Accuracy',
            save_path=os.path.join(self.vis_dir, 'accuracy.png')
        )
        plot_metrics(
            self.metrics['cnn']['train_loss'],
            self.metrics['cnn']['val_loss'],
            self.args.cnn_epochs,
            name='CNN Loss',
            save_path=os.path.join(self.vis_dir, 'cnn_loss.png')
        )
        plot_single(
            self.metrics['cnn']['precision'],
            self.args.cnn_epochs,
            'Precision',
            save_path=os.path.join(self.vis_dir, 'precision.png')
        )
        plot_single(
            self.metrics['cnn']['recall'],
            self.args.cnn_epochs,
            'Recall',
            save_path=os.path.join(self.vis_dir, 'recall.png')
        )
        plot_single(
            self.metrics['cnn']['f1_score'],
            self.args.cnn_epochs,
            'F1 Score',
            save_path=os.path.join(self.vis_dir, 'f1_score.png')
        )

        # DECAE相关可视化
        plot_metrics(
            self.metrics['decae']['train_loss'],
            self.metrics['decae']['val_loss'],
            self.args.decae_epochs,
            name='DECAE Loss',
            save_path=os.path.join(self.vis_dir, 'decae_loss.png')
        )

    def run(self):
        """执行完整训练流程"""
        print(f"Using {self.device.type} for training")
        self._train_cnn_phase()
        self._train_decae_phase()
        self.visualize_results()
        print("Training completed. Results saved to:", self.output_dir)


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='Joint CNN-DECAE Training Pipeline')
    parser.add_argument('--data-path', required=True, default='', help='Dataset root directory')
    parser.add_argument('--batch-size', type=int, default=32, help='Input batch size')
    parser.add_argument('--cnn-epochs', type=int, default=1, help='CNN training epochs')
    parser.add_argument('--decae-epochs', type=int, default=1, help='DECAE training epochs')
    parser.add_argument('--output-dir', default='./output', help='Output directory')
    parser.add_argument('--cnn-lr', type=float, default=1e-4, help='CNN learning rate')
    parser.add_argument('--decae-lr', type=float, default=1e-4, help='DECAE learning rate')
    return parser.parse_args()


if __name__ == '__main__':
    opt = parse_args()
    print(opt)
    trainer = JointTrainingSession(opt)
    trainer.run()
