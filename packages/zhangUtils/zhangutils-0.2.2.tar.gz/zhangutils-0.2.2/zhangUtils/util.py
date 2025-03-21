__version__ = '0.1.6'

from torchvision import transforms
from torch import Tensor
import numpy as np
from PIL import Image
from skimage import io
from skimage.metrics import structural_similarity
import torch.nn.functional as F
import os
import matplotlib.pyplot as plt


def visualize_tensor(tensor):
    """
    直接可视化tensor，支持多种形式并进行归一化显示
    Args:
        tensor: 输入tensor，可以是(H,W), (3,H,W), (1,H,W), (B,1,H,W), (B,3,H,W)
    """
    # 将tensor转换为numpy数组
    if isinstance(tensor, Tensor):
        tensor = tensor.detach().cpu().numpy()
    # 获取tensor维度
    ndim = len(tensor.shape)
    # 处理不同形式的tensor
    if ndim == 2:  # (H, W)
        images = [tensor]
    elif ndim == 3:  # (3, H, W) 或 (1, H, W)
        if tensor.shape[0] == 1 or tensor.shape[0] == 3:
            images = [tensor]
        else:
            raise ValueError(f"Unsupported tensor shape: {tensor.shape}")
    elif ndim == 4:  # (B, 1, H, W) 或 (B, 3, H, W)
        batch_size = tensor.shape[0]
        images = [tensor[i] for i in range(batch_size)]
    else:
        raise ValueError(f"Unsupported tensor shape: {tensor.shape}")
    # 计算子图布局
    n_images = len(images)
    cols = min(n_images, 3)  # 每行最多显示3张图
    rows = (n_images + cols - 1) // cols
    # 创建画布
    plt.figure(figsize=(5 * cols, 5 * rows))
    # 处理并显示每个图像
    for idx, img in enumerate(images):
        # 如果有通道维度，移到最后
        if len(img.shape) == 3:
            img = np.transpose(img, (1, 2, 0))  # (C, H, W) -> (H, W, C)
        # 移除单一通道维度
        if len(img.shape) == 3 and img.shape[2] == 1:
            img = img.squeeze(-1)
        # 归一化到0-1范围用于显示
        if img.max() != img.min():
            img = (img - img.min()) / (img.max() - img.min())
        else:
            img = img - img.min()  # 如果max==min，则移到0
        # 创建子图
        plt.subplot(rows, cols, idx + 1)
        # 根据图像类型选择显示方式
        if len(img.shape) == 2:  # 灰度图
            plt.imshow(img, cmap='gray')
        else:  # RGB图
            plt.imshow(img)
        plt.title(f'Image {idx}')
        plt.axis('off')
    plt.tight_layout()
    plt.show()

def shape(tensor):
    print(tensor.size())


def save_tensor_as_image(tensor, img_name='test', img_path='./images'):
    """
    将tensor保存为图片，支持多种tensor形式并进行归一化

    Args:
        tensor: 输入tensor，可以是(H,W), (3,H,W), (1,H,W), (B,1,H,W), (B,3,H,W)
        img_name: 保存的图片名称，默认'test'
        img_path: 保存路径，默认'./images'
    """
    os.makedirs(img_path, exist_ok=True)
    if isinstance(tensor, torch.Tensor):
        tensor = tensor.detach().cpu().numpy()
    ndim = len(tensor.shape)
    if ndim == 2:  # (H, W)
        images = [tensor]
        base_name = img_name
    elif ndim == 3:  # (3, H, W) 或 (1, H, W)
        if tensor.shape[0] == 1 or tensor.shape[0] == 3:
            images = [tensor]
            base_name = img_name
        else:
            raise ValueError(f"Unsupported tensor shape: {tensor.shape}")
    elif ndim == 4:  # (B, 1, H, W) 或 (B, 3, H, W)
        batch_size = tensor.shape[0]
        images = [tensor[i] for i in range(batch_size)]
        base_name = img_name
    else:
        raise ValueError(f"Unsupported tensor shape: {tensor.shape}")
    # 处理每个图像
    for idx, img in enumerate(images):
        # 如果有通道维度，移到最后
        if len(img.shape) == 3:
            img = np.transpose(img, (1, 2, 0))  # (C, H, W) -> (H, W, C)
        # 移除单一通道维度
        if len(img.shape) == 3 and img.shape[2] == 1:
            img = img.squeeze(-1)
        # 归一化到0-255
        if img.max() != img.min():
            img = (img - img.min()) / (img.max() - img.min()) * 255
        else:
            img = img * 255
        img = img.astype(np.uint8)
        # 生成文件名
        if len(images) > 1:
            file_name = f"{base_name}_{idx}.png"
        else:
            file_name = f"{base_name}.png"

        # 保存图片
        full_path = os.path.join(img_path, file_name)
        if len(img.shape) == 2:  # 灰度图
            Image.fromarray(img, mode='L').save(full_path)
        else:  # RGB图
            Image.fromarray(img, mode='RGB').save(full_path)

def readImage(imagePath, typeNumber=2):

    #typyNumber返回的照片参数
    #                       1:ndarry 2:tensor 3:PIL.Image
    img = io.imread(imagePath)

    if typeNumber == 1:
        return img

    if typeNumber == 2:
        return transforms.ToTensor()(img)
    
    # PIL Image
    if typeNumber == 3:
        return Image.open(imagePath).convert('RGB')
    

def ssim(cleanImagePath, dehazeImagePath):
    clean_image = transforms.ToTensor()(io.imread(cleanImagePath)) #转为tensor,并且将数据进行归一化
    dehaze_image = transforms.ToTensor()(io.imread(dehazeImagePath))
    ssim_val = structural_similarity(clean_image.permute(1, 2, 0).cpu().numpy(),
                                     dehaze_image.permute(1, 2, 0).numpy(),
                                     data_range=1, multichannel=True, channel_axis=-1)
    return ssim_val

def psnr(cleanImagePath, dehazeImagePath):
    clean_image = transforms.ToTensor()(io.imread(cleanImagePath))#转为tensor,并且将数据进行归一化
    dehaze_image = transforms.ToTensor()(io.imread(dehazeImagePath))
    psnr_val = 10 * torch.log10(1 / F.mse_loss(dehaze_image, clean_image))
    return psnr_val.item()

def evaluation(gtImagesPath, dehazeImagesPath):
    ssim_val = 0
    psnr_val = 0
    dehazeImagesName = os.listdir(dehazeImagesPath)
    for i in dehazeImagesName:
        gtImagePath = os.path.join(gtImagesPath, i)
        dehazeImagePath = os.path.join(dehazeImagesPath, i)
        ssim_val += ssim(gtImagePath, dehazeImagePath)
        psnr_val += psnr(gtImagePath, dehazeImagePath)

    ssim_val /= len(dehazeImagesName)
    psnr_val /= len(dehazeImagesName)

    return ssim_val, psnr_val

def calculate_ssim(tensor1, tensor2):
    ssim_val = 0
    # Ensure the tensors are on the CPU and convert them to numpy arrays
    tensor1 = tensor1[0].cpu().numpy()
    tensor2 = tensor2.cpu().numpy()
    for i in range(len(tensor1)):
        a = tensor1[i].transpose(1, 2, 0)
        b = tensor2[i].transpose(1, 2, 0)
        ssim_val += structural_similarity(a, b, data_range=1, multichannel=True, channel_axis=-1)
    # Calculate SSI

    return ssim_val/len(tensor1)



  