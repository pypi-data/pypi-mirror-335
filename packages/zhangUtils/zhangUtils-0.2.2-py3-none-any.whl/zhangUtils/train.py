import torch
from tqdm import tqdm
import os
from torch import nn


def test(model, testloader, criterion, metric=None):
    """
        测试函数，用于在测试数据集上评估模型性能。

        该函数将模型设置为评估模式，关闭梯度计算，然后遍历测试数据集，
        对每个批次计算损失，并根据需要计算额外的评价指标（如准确率、F1 分数等）。
        最后输出并返回测试数据集上的平均损失值。

        参数：
            model (torch.nn.Module): 待评估的模型。
            testloader (torch.utils.data.DataLoader): 提供测试数据的 DataLoader 对象。
            criterion (torch.nn.Module): 损失函数，用于计算测试时的损失。
            metric (callable, 可选): 用于计算其他评价指标的函数，默认值为 None。

        返回：
            float: 测试数据集上的平均损失值。
        """
    model.eval()  # 将模型设置为评估模式
    criterion = criterion.cuda()
    sum_loss = 0
    loop = enumerate(testloader)
    sum_metric = 0
    cnt = 0
    with torch.no_grad():
        for i, (data, targets) in loop:
            if torch.cuda.is_available():
                data, targets = data.cuda(), targets.cuda()
            scores = model(data)
            loss = criterion(scores, targets)
            sum_loss += loss.item()
            if metric is not None:
                m = metric(scores, targets)
                sum_metric += m
                cnt += 1

    if metric is not None:
        print(f'metric:{sum_metric / cnt}')

    print(f'test loss:{sum_loss / (testloader.__len__())}')

    return sum_loss / (testloader.__len__()), sum_metric / cnt


def train(model, criterion, optimizer, trainloader, epochs, testloader,
          testEpoch, modelSavedPath='./checkpoint/',
          scheduler=None, checkpoint_path=None, metric=None):
    """
       参数：
           model (torch.nn.Module): 待训练的模型。
           criterion (torch.nn.Module): 计算损失的函数。
           optimizer (torch.optim.Optimizer): 优化器，用于更新模型参数。
           trainloader (torch.utils.data.DataLoader): 提供训练数据的 DataLoader。
           epochs (int): 总训练轮数。
           testloader (torch.utils.data.DataLoader): 提供测试数据的 DataLoader。
           testEpoch (int): 每隔几个epoch进行一次测试评估。
           modelSavedPath (str, optional): 模型检查点和最终模型的保存目录，默认为 './checkpoint/'。
           scheduler (optional): 学习率调度器，用于调整optimizer的学习率，默认值为 None。
           checkpoint_path (str, optional): 若有则加载的检查点路径，实现断点续训，默认值为 None。
           metric (callable, optional): 可选的评价指标函数，根据模型输出和目标计算评估指标，默认值为 None.
       """

    if not os.path.exists(modelSavedPath):
        os.makedirs(modelSavedPath)
        print(f'{modelSavedPath} mkdir success')

    start_epoch = 0
    test_min_loss = 9e9
    max_metric = 0

    if checkpoint_path is not None:
        if not os.path.exists(checkpoint_path):
            print(f"Checkpoint not found at {checkpoint_path}")

        print(f"Loading checkpoint from {checkpoint_path}")
        checkpoint = torch.load(checkpoint_path)
        model.load_state_dict(checkpoint['model_state_dict'])
        optimizer.load_state_dict(checkpoint['optimizer_state_dict'])

        for state in optimizer.state.values():
            for k, v in state.items():
                if torch.is_tensor(v):
                    state[k] = v.cuda()

        start_epoch = checkpoint['epoch'] + 1

        if scheduler is not None and 'scheduler_state_dict' in checkpoint:
            scheduler.load_state_dict(checkpoint['scheduler_state_dict'])

        print(f"Resumed training from epoch {start_epoch}")

    if torch.cuda.is_available():
        model = model.cuda()
        criterion = criterion.cuda()

    for epoch in range(start_epoch, epochs):

        loop = tqdm(enumerate(trainloader), total=(len(trainloader)))
        loop.set_description(f'Epoch [{epoch}/{epochs}]')
        current_lr = optimizer.param_groups[0]['lr']
        loop.set_postfix(lr=current_lr)

        sum_loss = 0
        count = 0
        for i, (data, targets) in loop:
            # forward
            if torch.cuda.is_available():
                data, targets = data.cuda(), targets.cuda()
            scores = model(data)
            loss = criterion(scores, targets)

            sum_loss += loss.item()
            count += 1

            # backward
            optimizer.zero_grad()

            loss.backward()
            optimizer.step()

        print(f'train loss:{sum_loss / count}')

        if epoch % testEpoch == 0 and epoch != 0:

            test_loss, metric_val = test(model, testloader, criterion, metric=metric)

            if test_loss < test_min_loss:
                test_min_loss = test_loss
                # Save checkpoint
                checkpoint = {
                    'epoch': epoch,
                    'model_state_dict': model.state_dict(),
                    'optimizer_state_dict': optimizer.state_dict(),
                }
                if scheduler is not None:
                    checkpoint['scheduler_state_dict'] = scheduler.state_dict()
                torch.save(checkpoint, os.path.join(modelSavedPath, f'checkpoint_min_loss.pth'))
                print(f'min loss Checkpoint saved at epoch {epoch}')

            if metric is not None and metric_val > max_metric:
                max_metric = metric_val
                # Save checkpoint
                checkpoint = {
                    'epoch': epoch,
                    'model_state_dict': model.state_dict(),
                    'optimizer_state_dict': optimizer.state_dict(),
                }
                if scheduler is not None:
                    checkpoint['scheduler_state_dict'] = scheduler.state_dict()
                torch.save(checkpoint, os.path.join(modelSavedPath, f'checkpoint_max_metric.pth'))
                print(f'max metric Checkpoint saved at epoch {epoch}')

        # test后再scheduler
        if scheduler is not None:
            scheduler.step()

    checkpoint = {
        'epoch': epochs,
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
    }
    if scheduler is not None:
        checkpoint['scheduler_state_dict'] = scheduler.state_dict()
    torch.save(checkpoint, os.path.join(modelSavedPath, 'latest.pth'))
    print(f'Checkpoint saved at epoch {epochs}')