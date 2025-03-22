import os

import numpy as np
from PIL import Image
from torch import nn
from torch.utils.data import Dataset, DataLoader, ConcatDataset
from torchvision import transforms

from models.HSAZLM import CNN


class CustomDataset(Dataset):
    def __init__(self, root_dir, transform, class_to_label=None):
        self.root_dir = root_dir
        self.transform = transform
        self.class_to_label = class_to_label if class_to_label is not None else {}
        self.images = [f for f in os.listdir(root_dir) if f.endswith(('.bmp', '.jpg', '.png'))]

        # 如果没有提供class_to_label字典，我们在这里创建它
        if not self.class_to_label:
            self._create_class_to_label_mapping()
            self.class_to_idx = {cls_name: i for i, cls_name in enumerate(self.class_to_label)}

    def _create_class_to_label_mapping(self):
        # 假设类别是从0开始编号的连续整数
        self.classes = sorted(set([filename.split('_')[0] for filename in self.images]))
        self.class_to_label = {cls: i for i, cls in enumerate(self.classes)}

    def get_class_to_label(self):
        return self.class_to_label

    def __len__(self):
        return len(self.images)

    def __getitem__(self, idx):
        # 获取图片路径
        image_path = os.path.join(self.root_dir, self.images[idx])
        # 打开图片并转换为RGB格式
        # image = Image.open(image_path).convert('RGB')
        image = Image.open(image_path)
        # 如果有变换，则进行变换
        if self.transform:
            image = self.transform(image)

        # 提取文件名中的类别
        base_filename = os.path.splitext(self.images[idx])[0]
        class_name = base_filename.split('_')[0]
        # 将类别转换为标签
        label = self.class_to_label[class_name]

        return image, label


if __name__ == '__main__':
    dataset1 = CustomDataset(root_dir=r'../../data/dataset/D0/val',
                             transform=transforms.ToTensor())
    dataset2 = CustomDataset(root_dir=r'../../data/dataset/D0/train',
                             transform=transforms.ToTensor())
    dataset = ConcatDataset([dataset1, dataset2])
    validation_loader = DataLoader(dataset=dataset, batch_size=1, shuffle=False)
    for images, labels in validation_loader:
        pass
