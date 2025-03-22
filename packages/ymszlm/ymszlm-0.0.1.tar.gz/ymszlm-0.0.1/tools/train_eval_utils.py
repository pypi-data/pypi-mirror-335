import sys

import torch
from sklearn.metrics import accuracy_score
from tqdm import tqdm

from tools.tool import calculate_results


def train_feature_extractor_one_epoch(model, train_loader, val_loader, device, optimizer, criterion, epoch):
    mean_loss = torch.zeros(1).to(device)
    all_predictions = []
    all_labels = []
    model.train()
    train_iterator = tqdm(train_loader, file=sys.stdout, colour='blue')
    for step, (images, labels) in enumerate(train_iterator):
        # 将数据转移到设备
        images, labels = images.to(device), labels.to(device)
        # 梯度清0
        optimizer.zero_grad()
        # 前向传播
        outputs = model(images)
        # 计算损失
        loss = criterion(outputs, labels)
        # 反向传播
        loss.backward()
        # 更新参数
        optimizer.step()
        # 数值计算
        mean_loss = (mean_loss * step + loss.detach()) / (step + 1)
        _, predicted = torch.max(outputs, 1)
        # 设置进度条
        train_iterator.set_postfix(loss=loss.item(), mean_loss=mean_loss.item())
        all_predictions.extend(predicted.cpu().numpy())
        all_labels.extend(labels.cpu().numpy())

    train_accuracy = accuracy_score(y_true=all_labels, y_pred=all_predictions)
    print(f'the {epoch + 1} train accuracy is {train_accuracy}, and the train loss is {mean_loss.item():.6f}')

    val_loss = torch.zeros(1).to(device)
    all_predictions = []
    all_labels = []
    model.eval()
    val_iterator = tqdm(val_loader, file=sys.stdout, colour='GREEN')
    # 不计算梯度
    with torch.no_grad():
        for step, (images, labels) in enumerate(val_iterator):
            # 将数据转移到设备
            images, labels = images.to(device), labels.to(device)
            # 计算结果
            outputs = model(images)
            # 计算损失
            loss = criterion(outputs, labels)
            # 计算预测正确的样本
            _, predicted = torch.max(outputs, 1)
            val_iterator.set_postfix(loss=loss.item())
            val_loss = (val_loss * step + loss.detach()) / (step + 1)

            all_predictions.extend(predicted.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())

        results = calculate_results(all_predictions, all_labels, train_loader.dataset.classes)
        results.update({'epoch': (epoch + 1), 'train_loss': mean_loss.item(), 'val_loss': val_loss.item()})
        print(f'val loss:{val_loss.item():.6f}, acc:{results["accuracy"]:.6f}, f1:{results["f1_score"]:.6f}, precision:'
              f'{results["precision"]:.6f}, recall:{results["recall"]:.6f}')
    return results, train_accuracy


def train_decae_one_epoch(model, train_loader, val_loader, device, optimizer, criterion, epoch):
    results = {'train_loss': 0., 'val_loss': 0., 'epoch': 0}
    train_loss = torch.zeros(1).to(device)
    model.train()
    train_iterator = tqdm(train_loader, file=sys.stdout, colour='yellow')
    for step, (images, label) in enumerate(train_iterator):
        images = images.to(device)

        optimizer.zero_grad()

        outputs = model(images)

        loss = criterion(outputs, images)

        loss.backward()
        optimizer.step()

        train_loss = (train_loss * step + loss.detach()) / (step + 1)
        train_iterator.set_postfix(loss=loss.item(), mean_loss=train_loss.item())

    print(f'the epoch {epoch + 1} train loss is {train_loss.item():.6f}')
    val_loss = torch.zeros(1).to(device)
    model.eval()
    val_iterator = tqdm(val_loader, file=sys.stdout, colour='MAGENTA')
    with torch.no_grad():
        for step, (images, label) in enumerate(val_iterator):
            images = images.to(device)

            outputs = model(images)
            loss = criterion(outputs, images)
            val_loss = (val_loss * step + loss.detach()) / (step + 1)

            val_iterator.set_postfix(loss=loss.item(), mean_loss=val_loss.item())
    print(f'the epoch {epoch + 1} val loss is {val_loss.item():.6f}')
    results['train_loss'] = train_loss.item()
    results['val_loss'] = val_loss.item()
    results['epoch'] = epoch + 1
    return results


def train_fcnn_one_epoch(cnn, fcnn, train_loader, val_loader, device, optimizer, criterion, epoch):
    results = {'train_loss': 0., 'val_loss': 0., 'epoch': 0}
    train_loss = torch.zeros(1).to(device)
    fcnn.train()
    train_iterator = tqdm(train_loader, file=sys.stdout, colour='yellow')
    for step, (images, label) in enumerate(train_iterator):
        images, label = images.to(device), label.to(device)
        optimizer.zero_grad()
        feature = cnn(images)
        outputs = fcnn(feature)
        loss = criterion(outputs, label)
        loss.backward()
        optimizer.step()
        train_loss = (train_loss * step + loss.detach()) / (step + 1)
        train_iterator.set_postfix(loss=loss.item(), mean_loss=train_loss.item())
    print(f'the epoch {epoch + 1} train loss is {train_loss.item():.6f}')
    fcnn.eval()
    val_loss = torch.zeros(1).to(device)
    val_iterator = tqdm(val_loader, file=sys.stdout, colour='MAGENTA')
    with torch.no_grad():
        for step, (images, label) in enumerate(val_iterator):
            images = images.to(device)
            feature = cnn(images)
            outputs = fcnn(feature)
            loss = criterion(outputs, label)
            val_loss = (val_loss * step + loss.detach()) / (step + 1)
            val_iterator.set_postfix(loss=loss.item(), mean_loss=val_loss.item())
    print(f'the epoch {epoch + 1} val loss is {val_loss.item():.6f}')
    results['train_loss'] = train_loss.item()
    results['val_loss'] = val_loss.item()
    results['epoch'] = epoch + 1
    return results


@torch.no_grad()
def cnn_predict(model, test_loader, device):
    model.eval()
    all_predictions = []
    all_labels = []
    test_iterator = tqdm(test_loader, file=sys.stdout, colour='yellow')
    for _, (images, labels) in enumerate(test_iterator):
        images, labels = images.to(device), labels.to(device)
        outputs = model(images)
        _, predicted = torch.max(outputs, 1)

        all_predictions.extend(predicted.cpu().numpy())
        all_labels.extend(labels.cpu().numpy())
    return calculate_results(all_predictions, all_labels, test_loader.dataset.classes)


@torch.no_grad()
def zlm_predict(feature_extractor, fcnn, test_loader, device, hsa_matrix):
    all_predictions = []
    all_labels = []
    predict_iterator = tqdm(test_loader, file=sys.stdout, colour='yellow')
    feature_extractor.eval()
    fcnn.eval()
    for images, label in predict_iterator:
        images, label = images.to(device), label.to(device)
        features = feature_extractor(images)
        embeddings = fcnn(features)
        # 批量计算所有样本与所有HSA的距离
        distances = torch.cdist(embeddings, hsa_matrix, p=2)  # [batch_size, num_classes]
        # 找到每个样本的最小距离索引
        _, predicted = torch.min(distances, dim=1)
        all_predictions.extend(predicted.cpu().numpy())
        all_labels.extend(label.cpu().numpy())
    return calculate_results(all_labels=all_labels, all_predictions=all_predictions,
                             classes=test_loader.dataset.classes)
