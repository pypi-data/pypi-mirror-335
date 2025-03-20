import os
import numpy as np
import torch.utils.data as data
from PIL import Image,ImageDraw


import torch
# from torch.utils.data import DataLoader,Dataset,random_split
from torchvision import transforms
import cv2

class myDataset(data.Dataset):
    def __init__(self,dat_root,transforms=None):
        self.transforms = transforms
        self.imgsdir=dat_root+'/images'
        self.labelsdir = dat_root + '/labels'
        images_names=os.listdir(self.imgsdir)
        #到时可以实际情况修改是否加“_gt”
        self.masks = [os.path.join(self.labelsdir, x.split('.')[0] + '.png').replace('\\', '/') for x in images_names]
        self.images = [os.path.join(self.imgsdir, xi).replace('\\', '/') for xi in images_names]
    def __len__(self):
        return len(self.images)

    def __getitem__(self, index):
        img = Image.open(self.images[index]).convert('RGB')
        target = Image.open(self.masks[index])

        if self.transforms is not None:
            img, target = self.transforms(img, target)

        return img, target

    @staticmethod
    def collate_fn(batch):
        images, targets = list(zip(*batch))
        batched_imgs = cat_list(images, fill_value=0)
        batched_targets = cat_list(targets, fill_value=255)
        return batched_imgs, batched_targets

class myDataset_yaml(data.Dataset):
    def __init__(self,dat_root,transforms=None,params=None):
        self.transforms = transforms
        self.imgsdir=dat_root
        self.labelsdir = dat_root.split('/images')[0] + '/labels'+dat_root.split('/images')[1]
        images_names=os.listdir(self.imgsdir)
        #到时可以实际情况修改是否加“_gt”
        self.masks_txt = [os.path.join(self.labelsdir, x.split('.')[0] +'.txt').replace('\\', '/') for x in images_names]
        self.images = [os.path.join(self.imgsdir, xi).replace('\\', '/') for xi in images_names]
        ####sahi参数###
        self.sahi = params.get("sahi",False)
        self.window_size = params.get("imgsz",[256,256])[0]
        self.overlap=params.get("overlap_ratio",0)
        self.stride = self.window_size if self.overlap == 0.0 else int(self.window_size * (1 - self.overlap))
        ####sahi参数###
    def __len__(self):
        return len(self.images)

    def __getitem__(self, index):
        img = Image.open(self.images[index]).convert('RGB')
        target = txt2mask(img,self.masks_txt[index])
        if not self.sahi:
            if self.transforms is not None:
                img, target = self.transforms(img, target)
            return img, target
        else:
            #先切图再transforms
            patches = self.slice_image_and_mask(img, target, self.window_size, self.stride)
            if self.transforms is not None:
                patches = [self.transforms(p_img, p_mask) for p_img, p_mask in patches]
            return patches  # 返回切片列表
    @staticmethod
    def collate_fn(batch):
        """
        如果 sahi 模式，每个样本返回的是切片列表，直接平铺所有切片；
        否则直接将样本合并成 batch。
        """
        if isinstance(batch[0], list):
            images, targets = [], []
            for patch_list in batch:
                for img, target in patch_list:
                    images.append(img)
                    targets.append(target)
            batched_imgs = cat_list(images, fill_value=0)
            batched_targets = cat_list(targets, fill_value=255)
            return batched_imgs, batched_targets
        else:
            images, targets = list(zip(*batch))
            batched_imgs = cat_list_ori(images, fill_value=0)
            batched_targets = cat_list_ori(targets, fill_value=255)
            return batched_imgs, batched_targets

    def slice_image_and_mask(self,img, mask, window_size, stride):
        """
        将 PIL Image 图像和对应的 numpy mask 切分为多个小块。
        如果最后一行或最后一列不足一个完整窗口，则额外增加一个切片，
        并调整起始位置使得该切片与原图边界对齐。
        返回一个列表，每个元素为 (img_patch, mask_patch)
        """
        img_np = np.array(img)
        H, W, _ = img_np.shape
        mask=np.array(mask, dtype=np.uint8)
        # 计算垂直方向的起始坐标
        x_indices = list(range(0, H - window_size + 1, stride))
        if not x_indices:
            x_indices = [0]
        elif x_indices[-1] + window_size < H:
            x_indices.append(H - window_size)

        # 计算水平方向的起始坐标
        y_indices = list(range(0, W - window_size + 1, stride))
        if not y_indices:
            y_indices = [0]
        elif y_indices[-1] + window_size < W:
            y_indices.append(W - window_size)

        patches = []
        for i in x_indices:
            for j in y_indices:
                img_patch = img_np[i:i + window_size, j:j + window_size, :]
                mask_patch = mask[i:i + window_size, j:j + window_size]
                patches.append((Image.fromarray(img_patch), Image.fromarray(mask_patch)))
        return patches
def txt2mask(img,mask_txt):
    # 获取原始图像的尺寸
    width, height = img.size

    # 创建一个与图像相同尺寸的空白单通道（灰度）掩码图像
    mask = Image.new('L', (width, height), 0)
    draw = ImageDraw.Draw(mask)

    # 读取 .txt 文件
    with open(mask_txt, 'r') as file:
        lines = file.readlines()

    # 解析每一行
    for line in lines:
        parts = line.strip().split()
        label_index = int(parts[0])
        points = [float(p) for p in parts[1:]]

        # 将归一化的点坐标转换为图像坐标
        points = [(p * width, q * height) for p, q in zip(points[0::2], points[1::2])]

        # 绘制多边形并填充
        color = label_index + 1  # 使用标签索引+1作为灰度值
        draw.polygon(points, fill=color)
    # t=mask_txt.split("/")[-1].split(".txt")[0]
    # # 定义掩码图像的保存路径
    # mask_file_name = f"E:\\ALLvision\\pycharmproject\\yoloseg\\try\\826\\mask\\{t}.png"
    # # 保存掩码图像
    # mask.save(mask_file_name) # 保存掩码图像到文件
    return mask

class VOCSegmentation(data.Dataset):
    def __init__(self, voc_root, year="mydata", transforms=None, txt_name: str = "train.txt"):
        super(VOCSegmentation, self).__init__()
        assert year in ["2007", "2012","mydata"], "year must be in ['2007', '2012','mydata']"
        root = os.path.join(voc_root, "VOCdevkitMyself", f"VOC{year}")
        assert os.path.exists(root), "path '{}' does not exist.".format(root)
        image_dir = os.path.join(root, 'ImageDog')
        mask_dir = os.path.join(root, 'SegmentationClass')

        txt_path = os.path.join(root, "ImageSets", "Segmentation", txt_name)
        assert os.path.exists(txt_path), "file '{}' does not exist.".format(txt_path)
        with open(os.path.join(txt_path), "r") as f:
            file_names = [x.strip() for x in f.readlines() if len(x.strip()) > 0]

        self.images = [os.path.join(image_dir, x + ".jpg") for x in file_names]
        self.masks = [os.path.join(mask_dir, x + ".png") for x in file_names]
        assert (len(self.images) == len(self.masks))
        self.transforms = transforms

    def __getitem__(self, index):
        """
        Args:
            index (int): Index

        Returns:
            tuple: (image, target) where target is the image segmentation.
        """
        img = Image.open(self.images[index]).convert('RGB')
        target = Image.open(self.masks[index])

        if self.transforms is not None:
            img, target = self.transforms(img, target)

        return img, target

    def __len__(self):
        return len(self.images)

    @staticmethod
    def collate_fn(batch):
        images, targets = list(zip(*batch))
        batched_imgs = cat_list(images, fill_value=0)
        batched_targets = cat_list(targets, fill_value=255)
        return batched_imgs, batched_targets
def cat_list_ori(images, fill_value=0):
    # 计算该batch数据中，channel, h, w的最大值
    max_size = tuple(max(s) for s in zip(*[img.shape for img in images]))
    batch_shape = (len(images),) + max_size
    batched_imgs = images[0].new(*batch_shape).fill_(fill_value)
    for img, pad_img in zip(images, batched_imgs):
        pad_img[..., :img.shape[-2], :img.shape[-1]].copy_(img)
    return batched_imgs
def cat_list(images, fill_value=0):
    """
    将 PIL 图像转换为 numpy 数组后，对齐尺寸，再堆叠成 tensor。
    支持彩色（H,W,3）或灰度（H,W）图像。
    如果是灰度图（仅1个通道），返回 tensor 形状为 (B, H, W)；
    如果是彩色图，返回 (B, C, H, W)。
    """
    sizes = [np.array(img).shape for img in images]
    max_size = tuple(np.max(np.array(sizes), axis=0))
    batched = []
    for img in images:
        img_np = np.array(img)
        padded = np.full(max_size, fill_value, dtype=img_np.dtype)
        # 如果图像是灰度图（2维），扩展为3维
        if img_np.ndim == 2:
            h, w = img_np.shape
            padded[:h, :w] = img_np
        elif img_np.ndim == 3:
            h, w, c = img_np.shape
            padded[:h, :w, :c] = img_np
        batched.append(padded)
    batched = np.stack(batched, axis=0)

    return torch.from_numpy(batched)
    # # 如果彩色图像 (C > 1)，调整为 (B, C, H, W)
    # if len(max_size) == 3 and max_size[2] > 1:
    #     return torch.from_numpy(batched).permute(0, 3, 1, 2).float()
    # else:
    #     # 灰度图：先 squeeze 掉最后一维，得到 (B, H, W)
    #     return torch.from_numpy(batched).squeeze(-1).float()

# dat_root="E:/ALLvision/pycharmproject/yoloseg/githubtry/diyFCN/try2_yaml/fcn/Data_seg/images/train"
# imgsdir = dat_root
# labelsdir = dat_root.split('/images')[0] + '/labels' + dat_root.split('/images')[1]
# images_names = os.listdir(imgsdir)
# masks_txt = [os.path.join(labelsdir, x.split('.')[0] + '.txt').replace('\\', '/') for x in images_names]
# images = [os.path.join(imgsdir, xi).replace('\\', '/') for xi in images_names]
# index=1
# img = Image.open(images[index]).convert('RGB')
# target = txt2mask(img, masks_txt[index])
# # 构造完整的文件路径
# target_path = "E:/ALLvision/pycharmproject/yoloseg/githubtry/diyFCN/try2_yaml/fcn/tryimgsave/1.png"
# # 保存 target 图像
# target.save(target_path)
# ss=Image.open(target_path)
# t=ss
