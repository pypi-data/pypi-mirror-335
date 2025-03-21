import torch
from torch import nn
import SegJJC.fcn.train_utils.distributed_utils as utils
import torchvision.models.segmentation as models

def criterion(inputs, target):
    losses = {}
    for name, x in inputs.items():
        # 忽略target中值为255的像素，255的像素是目标边缘或者padding填充
        losses[name] = nn.functional.cross_entropy(x, target, ignore_index=255)

    if len(losses) == 1:
        return losses['out']

    return losses['out'] + 0.5 * losses['aux']


def evaluate(model, data_loader, device, num_classes,params):
    model.eval()
    print_freq = params.get("traininfo_printepoch", 10)
    confmat = utils.ConfusionMatrix(num_classes)
    metric_logger = utils.MetricLogger(delimiter="  ")
    header = 'Test:'
    with torch.no_grad():
        for image, target in metric_logger.log_every(data_loader, print_freq, header):
            image, target = image.to(device), target.to(device)
            output = model(image)
            output = output['out']

            confmat.update(target.flatten(), output.argmax(1).flatten())

        confmat.reduce_from_all_processes()

    # 计算 mean IoU(nobackground)
    _, _, iu = confmat.compute()
    mean_iou_nobackground = iu[1:].mean().item() * 100
    return confmat,mean_iou_nobackground

def evaluate_sahi(model, data_loader, device, num_classes,params):
    model.eval()
    print_freq=params.get("traininfo_printepoch", 10)
    patch_batch_size=params.get("sahitrain_batch", None)
    ifsahi=params.get("sahi", False)
    confmat = utils.ConfusionMatrix(num_classes)
    metric_logger = utils.MetricLogger(delimiter="  ")
    header = 'Test:'
    with torch.no_grad():
        for image, target in metric_logger.log_every(data_loader, print_freq, header):
            image, target = image.to(device), target.to(device)
            if not ifsahi or patch_batch_size is None or image.shape[0] <= patch_batch_size:
                output = model(image)['out']
                pred = output.argmax(1)
                targets=target
            # 如果需要 mini-batch 推理（避免一次性送入太多切片）
            else:
                num_patches = image.shape[0]
                pred_list = []
                target_list = []
                for i in range(0, num_patches, patch_batch_size):
                    mini_imgs = image[i:i+patch_batch_size]
                    mini_targets = target[i:i+patch_batch_size]
                    mini_output = model(mini_imgs)['out']
                    pred_list.append(mini_output.argmax(1))
                    target_list.append(mini_targets)
                pred = torch.cat(pred_list, dim=0)
                targets = torch.cat(target_list, dim=0)

            confmat.update(targets.flatten(), pred.flatten())

        confmat.reduce_from_all_processes()

    # 计算 mean IoU(nobackground)
    _, _, iu = confmat.compute()
    mean_iou_nobackground = iu[1:].mean().item() * 100
    return confmat,mean_iou_nobackground


#deeplabv3的aspppooling归一化层删除
def disable_bn_in_aspp(model):
    # 直接访问并禁用特定的 BatchNorm2d 层
    aspp_pooling_bn = model.classifier[0].convs[4][2]
    aspp_pooling_bn.training = False

def train_one_epoch(model, optimizer, data_loader, device, epoch, lr_scheduler, print_freq=10, scaler=None):
    model.train()
    # 直接访问并禁用特定的 BatchNorm2d 层
    if isinstance(model,models.DeepLabV3):
        disable_bn_in_aspp(model)
    metric_logger = utils.MetricLogger(delimiter="  ")
    metric_logger.add_meter('lr', utils.SmoothedValue(window_size=1, fmt='{value:.6f}'))
    header = 'Epoch: [{}]'.format(epoch)

    for image, target in metric_logger.log_every(data_loader, print_freq, header):
        image, target = image.to(device), target.to(device)
        # 获取 unique 的标签值
        unique_labels, counts = torch.unique(target, return_counts=True)
        with torch.cuda.amp.autocast(enabled=scaler is not None):
            output = model(image)
            loss = criterion(output, target)

        optimizer.zero_grad()
        if scaler is not None:
            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()
        else:
            loss.backward()
            optimizer.step()

        lr_scheduler.step()

        lr = optimizer.param_groups[0]["lr"]
        metric_logger.update(loss=loss.item(), lr=lr)

    return metric_logger.meters["loss"].global_avg, lr

def train_one_epoch_sahi(model, optimizer, data_loader, device, epoch, lr_scheduler, params,print_freq=10, scaler=None):
    patch_batch_size=params.get("sahitrain_batch", None)
    ifsahi=params.get("sahi", False)
    model.train()
    # 直接访问并禁用特定的 BatchNorm2d 层
    if isinstance(model,models.DeepLabV3):
        disable_bn_in_aspp(model)
    metric_logger = utils.MetricLogger(delimiter="  ")
    metric_logger.add_meter('lr', utils.SmoothedValue(window_size=1, fmt='{value:.6f}'))
    header = 'Epoch: [{}]'.format(epoch)

    for image, target in metric_logger.log_every(data_loader, print_freq, header):
        image, target = image.to(device), target.to(device)
        ##正常
        if not ifsahi or patch_batch_size is None or image.shape[0] <= patch_batch_size:
            # 获取 unique 的标签值
            unique_labels, counts = torch.unique(target, return_counts=True)
            with torch.cuda.amp.autocast(enabled=scaler is not None):
                output = model(image)
                loss = criterion(output, target)

            optimizer.zero_grad()
            if scaler is not None:
                scaler.scale(loss).backward()
                scaler.step(optimizer)
                scaler.update()
            else:
                loss.backward()
                optimizer.step()

            lr_scheduler.step()

            lr = optimizer.param_groups[0]["lr"]
            metric_logger.update(loss=loss.item(), lr=lr)
        else:
            accumulated_loss = 0.0
            num_patches = image.shape[0]
            optimizer.zero_grad()
            for i in range(0, num_patches, patch_batch_size):
                mini_imgs = image[i:i+patch_batch_size]
                mini_masks = target[i:i+patch_batch_size]
                unique_labels, counts = torch.unique(mini_masks, return_counts=True)
                with torch.cuda.amp.autocast(enabled=scaler is not None):
                    mini_outputs = model(mini_imgs)
                    mini_loss = criterion(mini_outputs, mini_masks)

                if scaler is not None:
                    scaler.scale(mini_loss).backward()
                else:
                    mini_loss.backward()
                accumulated_loss += mini_loss.item() * mini_imgs.shape[0]
            # 完成所有 mini-batch 后，只调用一次更新
            if scaler is not None:
                scaler.step(optimizer)
                scaler.update()
            else:
                optimizer.step()
            # 计算整个 batch 的平均 loss
            batch_loss = accumulated_loss / num_patches
            lr_scheduler.step()

            lr = optimizer.param_groups[0]["lr"]
            #计算整个batch（即这张原图切片总数）的平均loss,控制台输出的是这个值！！
            metric_logger.update(loss=batch_loss, lr=lr)

    return metric_logger.meters["loss"].global_avg, lr

def create_lr_scheduler(optimizer,
                        num_step: int,
                        epochs: int,
                        warmup=True,
                        warmup_epochs=1,
                        warmup_factor=1e-3):
    assert num_step > 0 and epochs > 0
    if warmup is False:
        warmup_epochs = 0

    def f(x):
        """
        根据step数返回一个学习率倍率因子，
        注意在训练开始之前，pytorch会提前调用一次lr_scheduler.step()方法
        """
        if warmup is True and x <= (warmup_epochs * num_step):
            alpha = float(x) / (warmup_epochs * num_step)
            # warmup过程中lr倍率因子从warmup_factor -> 1
            return warmup_factor * (1 - alpha) + alpha
        else:
            # warmup后lr倍率因子从1 -> 0
            # 参考deeplab_v2: Learning rate policy
            return (1 - (x - warmup_epochs * num_step) / ((epochs - warmup_epochs) * num_step)) ** 0.9

    return torch.optim.lr_scheduler.LambdaLR(optimizer, lr_lambda=f)
