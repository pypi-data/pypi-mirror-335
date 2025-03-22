import torch
import torch.nn as nn


class FeatureExtractor(nn.Module):
    def __init__(self):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.Conv2d(128, 256, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2)
        )
        self.fc = nn.Sequential(
            nn.Linear(256 * 8 * 8, 4096),
            nn.ReLU(),
            nn.Linear(4096, 2048),
        )

    def forward(self, x):
        x = self.features(x)
        x = torch.flatten(x, 1)
        x = self.fc(x)
        return x


class CNN(nn.Module):
    def __init__(self, num_classes=10):
        super().__init__()
        self.features = FeatureExtractor()
        self.fc3 = nn.Linear(2048, num_classes)
        self.relu = nn.ReLU()

    def save(self, path):
        torch.save(self.features.state_dict(), path)

    def forward(self, x):
        x = self.features(x)
        x = self.relu(x)
        x = self.fc3(x)
        return x


# 定义残差块
class ResidualBlock(nn.Module):
    def __init__(self, channels):
        super().__init__()
        self.res = nn.Sequential(
            nn.Conv2d(channels, channels, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(channels),
            nn.ReLU(),
            nn.Conv2d(channels, channels, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(channels),
            nn.ReLU(),
        )

    def forward(self, x):
        residual = x
        out = self.res(x)
        return out + residual


# 编码器
class Encoder(nn.Module):
    def __init__(self, mask_ratio=0.3):
        super().__init__()
        self.mask_ratio = mask_ratio
        # Conv1 + ResidualBlock1
        self.conv1 = nn.Sequential(
            nn.Conv2d(3, 16, 3, stride=2, padding=1),
            nn.BatchNorm2d(16),
            nn.ReLU(),
            ResidualBlock(16)
        )
        # Conv2 + ResidualBlock2
        self.conv2 = nn.Sequential(
            nn.Conv2d(16, 32, 3, stride=2, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            ResidualBlock(32)
        )
        # Conv3 + ResidualBlock3
        self.conv3 = nn.Sequential(
            nn.Conv2d(32, 64, 3, stride=2, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            ResidualBlock(64)
        )
        # Conv4 + ResidualBlock4
        self.conv4 = nn.Sequential(
            nn.Conv2d(64, 128, 3, stride=1, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(),
            ResidualBlock(128)
        )
        self.flatten = nn.Flatten()
        self.fc = nn.Linear(128 * 4 * 4, 512)

    def add_noise(self, x):
        if self.training:
            mask = (torch.rand_like(x) > self.mask_ratio).float()
            return x * mask
        return x

    def forward(self, x):
        x = self.add_noise(x)
        x = self.conv1(x)
        x = self.conv2(x)
        x = self.conv3(x)
        x = self.conv4(x)
        x = self.flatten(x)
        x = self.fc(x)
        return x


# 解码器
class Decoder(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc = nn.Linear(512, 2048)
        self.unFlatten = nn.Unflatten(1, (128, 4, 4))

        self.deConv = nn.Sequential(
            # DeConv1
            nn.ConvTranspose2d(128, 64, 3, stride=1, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            # DeConv2
            nn.ConvTranspose2d(64, 32, 3, stride=2, padding=1, output_padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            # DeConv3
            nn.ConvTranspose2d(32, 16, 3, stride=2, padding=1, output_padding=1),
            nn.BatchNorm2d(16),
            nn.ReLU(),
            # DeConv4 (输出层)
            nn.ConvTranspose2d(16, 3, 3, stride=2, padding=1, output_padding=1),
        )

    def forward(self, x):
        x = self.fc(x)
        x = self.unFlatten(x)
        x = self.deConv(x)
        # return torch.sigmoid(x)  # 假设输出在[0,1]范围
        return x


class DRCAE(nn.Module):
    def __init__(self):
        super().__init__()
        self.encoder = Encoder()
        self.decoder = Decoder()

    def forward(self, x):
        x = self.encoder(x)
        x = self.decoder(x)
        return x

    def save(self, path):
        torch.save(self.encoder.state_dict(), path)

    def save_decoder(self, path):
        torch.save(self.decoder.state_dict(), path)


class FCNN(nn.Module):
    def __init__(self, out_channels=518):
        super().__init__()
        self.fc4 = nn.Linear(2048, 1024)
        self.fc5 = nn.Linear(1024, out_channels)

    def forward(self, x):
        x = self.fc4(x)
        x = self.fc5(x)
        return x


class LSELoss(nn.Module):
    def __init__(self, hsa_matrix):
        """
               LSE损失函数实现
               Args:
                   hsa_matrix (Tensor): HSA矩阵 [num_classes, feature_dim]
               """
        super().__init__()
        self.register_buffer('hsa', hsa_matrix)  # 注册为buffer保证设备一致性

    def forward(self, embedded_features, targets):
        """
        前向计算
        Args:
            embedded_features (Tensor): 嵌入特征 [batch_size, feature_dim]
            targets (LongTensor): 类别标签 [batch_size]
        Returns:
            Tensor: 损失值
        """
        # 选择对应类别的HSA向量
        selected_hsa = self.hsa[targets]  # [batch_size, feature_dim]

        # 计算最小二乘误差
        loss = torch.sum((embedded_features - selected_hsa) ** 2) / targets.size(0)

        return loss


def create_cnn(path, num_classes=10):
    model = CNN(num_classes=num_classes)
    model.load_state_dict(torch.load(path, map_location='cpu', weights_only=True))
    return model


def create_fcnn(path, output_dim=518):
    fcnn = FCNN(out_channels=output_dim)
    weights_dict = torch.load(path, map_location='cpu', weights_only=True)
    missing_keys, unexpected_keys = fcnn.load_state_dict(weights_dict)
    if len(missing_keys) != 0 or len(unexpected_keys) != 0:
        print("missing_keys: ", missing_keys)
        print("unexpected_keys: ", unexpected_keys)
    return fcnn


def create_feature_extractor(path):
    feature_extractor = FeatureExtractor()
    weights_dict = torch.load(path, map_location='cpu', weights_only=True)
    missing_keys, unexpected_keys = feature_extractor.load_state_dict(weights_dict, strict=False)
    if len(missing_keys) != 0 or len(unexpected_keys) != 0:
        print("missing_keys: ", missing_keys)
        print("unexpected_keys: ", unexpected_keys)
    for param in feature_extractor.parameters():
        param.requires_grad = False
    return feature_extractor


if __name__ == '__main__':
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    # model = CNN()
    # torch.save(model.features.state_dict(), 'model.pth')
    # # model.save_feature_extractor('model.pth')
    # a = torch.load('model.pth', map_location='cpu', weights_only=True)
    # b = FeatureExtractor()
    # missing_keys, unexpected_keys = b.load_state_dict(a)
    # print(a)
