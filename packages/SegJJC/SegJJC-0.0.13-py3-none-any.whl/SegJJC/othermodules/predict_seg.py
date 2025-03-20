import os
import json
import time
import torch
from torchvision import transforms
import numpy as np
from PIL import Image
import torchvision.models.segmentation as models
from pathlib import Path

from SegJJC.fcn.src import fcn_resnet50,fcn_resnet18,fcn_resnet34,deeplabv3_resnet18,deeplabv3_resnet34
try:
    from ultralytics.utils.plotting import colors
    ULTRALYTICS_COLORS_AVAILABLE = True
except ImportError:
    ULTRALYTICS_COLORS_AVAILABLE = False

class PredictSahi_fcn:
    def __init__(self, model_path,params):
        self.modelpath=model_path
        self.trueimgsize = params["inferimgsz"]
        self.testimg_dir = params['testimg']
        self.saveimg_dir = params['inferedimg']
        self.aux=False
        self.inferdevicehandle=params.get("inferdevicehandle",0)
        # if self.inferdevicehandle=='gpu':
        #     self.inferdevicehandle=0
        # 加载 palette
        self.palette = self.load_palette()
        self.yolocolors=True##是否使用yolo自带的掩膜color颜色盘，用于标记目标区域
        self.infer_format=params.get("infer_format","pt")
        self.inferbatch=params.get("inferbatch",1)
        ##sahi参数##
        self.ifsahi=params.get("ifsahi",False)
        self.overlap_ratio=params.get("overlap_ratio",0.2)
        self.merge_strategy=params.get("merge_strategy","average")
        self.save_sahipic=params.get("save_sahipic",False)
        ##固定，不要改！！
        self.has_warned_batch_mismatch=False
        ##sahi参数##
    def load_palette(self):
        """ 从 JSON 文件加载颜色映射 """
        json_path = os.path.join(os.path.dirname(__file__), "..", "fcn", "palette.json")
        if not os.path.exists(json_path):
            raise FileNotFoundError(f"颜色映射文件 {json_path} 不存在！")

        with open(json_path, "r") as f:
            return json.load(f)
    def time_synchronized(self):
        torch.cuda.synchronize() if torch.cuda.is_available() else None
        return time.time()

    def mask_to_color(self,mask,palette=None):
        """
        将语义分割得到的 mask（每个像素为类别ID）转换成彩色图
        """
        if not palette:
            palette=colors.palette
            h, w = mask.shape
            color_mask = np.zeros((h, w, 3), dtype=np.uint8)
            cls_id=0
            for color in palette:
                color_mask[mask == cls_id] = color
                cls_id+=1
            return color_mask
        else:
            """
            将语义分割得到的 mask（每个像素为类别ID）转换成彩色图
            """
            h, w = mask.shape
            color_mask = np.zeros((h, w, 3), dtype=np.uint8)
            for cls_id, color in palette.items():
                cls_id = int(cls_id)  # 将字符串类型的类别ID转换为整数
                color_mask[mask == cls_id] = color
            return color_mask

    def blend_mask_region(self,original_img, color_mask, mask, alpha=0.3):
        """
        仅对 mask 区域进行半透明叠加
          - original_img：原始RGB图像 (PIL Image)
          - color_mask：彩色mask (numpy数组，形状(H,W,3))
          - mask：语义分割结果 (numpy数组，像素值代表类别ID, 背景通常为0)
          - alpha：混合因子，在目标区域使用
        """
        # 转换为 numpy 数组（float32）
        original = np.array(original_img).astype(np.float32)
        overlay = color_mask.astype(np.float32)

        # 构造布尔 mask，将其沿通道重复3次，形状变为 (H, W, 3)
        mask_bool = np.repeat((mask > 0)[:, :, None], 3, axis=2)

        # 使用 np.where 只在 mask 区域混合，否则保持原图
        blended = np.where(mask_bool, original * (1 - alpha) + overlay * alpha, original)
        blended = np.clip(blended, 0, 255).astype(np.uint8)
        return Image.fromarray(blended)

    # 修正坐标生成逻辑，确保覆盖到图像边缘
    def generate_coords(self,total_size, window_size, stride):
        coords = []
        current = 0
        max_x = total_size - window_size  # 最后一个有效起始位置
        if total_size <= window_size:
            return []
        while current <= max_x:
            coords.append(current)
            current += stride
        # 检查最后一块是否覆盖到边缘
        if coords:
            last_pos = coords[-1]
            if (last_pos + window_size) < total_size:
                coords.append(max_x)
        else:
            coords.append(max_x)
        return coords

    #模型推理
    # region 模型推理函数inferenceit
    def inferenceit(self,model,batch):
        if self.infer_format in ['pt', 'pth']:
            out = model(batch)['out']
        if self.infer_format in ['onnx']:
            input_name = model.get_inputs()[0].name
            output_name = model.get_outputs()[0].name
            batch_np = batch.numpy() if hasattr(batch, 'numpy') else batch
            #获取模型期望batch
            expected_batch_size = model.get_inputs()[0].shape[0]
            sample_batch_size = batch_np.shape[0]
            #检查 batch_size 是否匹配，不匹配则调整
            if self.inferbatch != expected_batch_size:
                # 只打印一次警告
                if not self.has_warned_batch_mismatch:
                    print(f"!!!警告:输入 batch_size ({self.inferbatch}) 与onnx模型期望的 batch_size ({expected_batch_size}) 不匹配!!!")
                    print(f"正在调整输入为 batch_size={expected_batch_size}个样本处理，输出将按顺序合并。")
                    self.has_warned_batch_mismatch = True  # 标记已警告
                outputs = []
                num_batches = (sample_batch_size + expected_batch_size - 1) // expected_batch_size
                for i in range(num_batches):
                    start = i * expected_batch_size
                    end = (i + 1) * expected_batch_size
                    sub_batch = batch_np[start:end]

                    # 填充不足的 batch
                    if sub_batch.shape[0] < expected_batch_size:
                        pad_size = expected_batch_size - sub_batch.shape[0]
                        sub_batch = np.concatenate([sub_batch, np.zeros_like(sub_batch[:pad_size])])

                    # 推理
                    sub_output = model.run([output_name], {input_name: sub_batch})[0]

                    # 剔除填充部分
                    valid_output = sub_output[:sub_batch.shape[0]]
                    outputs.append(valid_output)

                out = np.concatenate(outputs)
            else:
                out = model.run([output_name], {input_name: batch_np})[0]
            out = torch.from_numpy(out)  # 转换为 PyTorch 张量
        if self.infer_format in ['openvino']:
            # 获取模型输入输出名称
            input_name = model.model_inputs[0].get_any_name()
            output_name = model.model_outputs[0].get_any_name()
            batch_np = batch.numpy() if hasattr(batch, 'numpy') else batch
            # 获取模型期望batch
            expected_batch_size = model.model_inputs[0].shape[0]
            sample_batch_size=batch_np.shape[0]
            # 检查 batch_size 是否匹配，不匹配则调整
            if self.inferbatch != expected_batch_size:
                # 只打印一次警告
                if not self.has_warned_batch_mismatch:
                    print(
                        f"!!!警告:输入 batch_size ({self.inferbatch}) 与openvino(onnx)模型期望的 batch_size ({expected_batch_size}) 不匹配!!!")
                    print(f"正在调整输入为 batch_size={expected_batch_size}个样本处理，输出将按顺序合并。")
                    self.has_warned_batch_mismatch = True  # 标记已警告
                outputs = []
                num_batches = (sample_batch_size + expected_batch_size - 1) // expected_batch_size
                for i in range(num_batches):
                    start = i * expected_batch_size
                    end = (i + 1) * expected_batch_size
                    sub_batch = batch_np[start:end]

                    # 填充不足的 batch
                    if sub_batch.shape[0] < expected_batch_size:
                        pad_size = expected_batch_size - sub_batch.shape[0]
                        sub_batch = np.concatenate([sub_batch, np.zeros_like(sub_batch[:pad_size])])

                    # 推理
                    sub_output = model.infer({input_name:sub_batch})[output_name]

                    # 剔除填充部分
                    valid_output = sub_output[:sub_batch.shape[0]]
                    outputs.append(valid_output)

                results = np.concatenate(outputs)
            else:
                results = model.infer({input_name: batch_np})[output_name]
            # results = model.infer({input_name: batch_np})
            out = torch.from_numpy(results)  # 转换为 PyTorch 张量
        return out
    # endregion

    def slice_and_merge(self,model,image_tensor: torch.Tensor) -> np.ndarray:
        batch_size, channels, H, W = image_tensor.shape
        #####self.trueimgsize[0]是否考虑到size不是矩形的情况！！！
        stride = int(self.trueimgsize[0] * (1 - self.overlap_ratio))

        # 修正坐标生成逻辑，确保覆盖到图像边缘

        x_coords = self.generate_coords(H, self.trueimgsize[0], stride)
        y_coords = self.generate_coords(W, self.trueimgsize[1], stride)

        # 生成 positions（仅包含有效坐标）
        positions = []
        for x in x_coords:
            for y in y_coords:
                positions.append((x, y))

        # 处理无切片的情况（图像尺寸不足 window_size）
        if not positions:
            # 直接处理整个图像
            model.eval()
            with torch.no_grad():
                output = model(image_tensor)['out']
            final_mask = output.argmax(1).squeeze(0).cpu().numpy().astype(np.uint8)
            return final_mask

        # 生成切片（保证尺寸为 window_size × window_size）
        patches = []
        for (x, y) in positions:
            patch = image_tensor[:, :, x:x + self.trueimgsize[0], y:y + self.trueimgsize[1]]
            patches.append(patch)
        patches = torch.cat(patches, dim=0)

        # 保存原始切片（可选）
        if self.save_sahipic:
            output_slices_dir = os.path.join(self.saveimg_dir, "slices", os.path.splitext(self.testimg_dir)[0])
            os.makedirs(output_slices_dir, exist_ok=True)
            for i in range(len(patches)):
                patch_image = transforms.ToPILImage()(patches[i].cpu())
                patch_image.save(os.path.join(output_slices_dir, f"patch_{i}_original.png"))

        # 标准化切片（与训练时一致）
        mean = torch.tensor([0.485, 0.456, 0.406], device=patches.device).view(1, 3, 1, 1)
        std = torch.tensor([0.229, 0.224, 0.225], device=patches.device).view(1, 3, 1, 1)
        patches = (patches - mean) / std

        # 批量推理
        outputs = []
        with torch.no_grad():
            for i in range(0, len(patches), self.inferbatch):  # 每次处理 8 张切片
                batch = patches[i:i + self.inferbatch].to(image_tensor.device)
                #推理
                # out = model(batch)['out']
                out=self.inferenceit(model,batch)
                outputs.append(out)
        outputs = torch.cat(outputs, dim=0)

        # 保存掩码切片（可选）
        if self.save_sahipic:
            for i in range(len(outputs)):
                output = outputs[i].cpu()
                mask_patch = output.argmax(0).numpy().astype(np.uint8)
                color_mask_patch = self.mask_to_color(mask_patch)  # 假设 palette 已定义
                color_mask_image = Image.fromarray(color_mask_patch)
                color_mask_image.save(os.path.join(output_slices_dir, f"patch_{i}_color_mask.png"))

        # 合并结果
        num_classes = outputs.shape[1]
        result = torch.zeros((batch_size, num_classes, H, W), device=image_tensor.device)
        count = torch.zeros((H, W), device=image_tensor.device)
        vote = torch.zeros((H, W, num_classes), device=image_tensor.device)

        for idx in range(len(outputs)):
            output_patch = outputs[idx]
            x, y = positions[idx]
            x_end = x + self.trueimgsize[0]
            y_end = y + self.trueimgsize[1]
            result[:, :, x:x_end, y:y_end] += output_patch.unsqueeze(0)
            count[x:x_end, y:y_end] += 1

            if self.merge_strategy == "majority_vote":
                pred = output_patch.argmax(0)
                for c in range(num_classes):
                    mask = (pred == c)
                    vote[x:x_end, y:y_end, c] += mask.float()

        # 根据策略选择合并方式
        if self.merge_strategy == "average":
            merged = result / (count.unsqueeze(0).unsqueeze(0) + 1e-8)
        elif self.merge_strategy == "max":
            max_vals = torch.zeros_like(result)
            for idx in range(len(outputs)):
                output_patch = outputs[idx]
                x, y = positions[idx]
                x_end = x + self.trueimgsize[0]
                y_end = y + self.trueimgsize[1]
                max_vals[:, :, x:x_end, y:y_end] = torch.max(
                    max_vals[:, :, x:x_end, y:y_end],
                    output_patch.unsqueeze(0)
                )
            merged = max_vals
        elif self.merge_strategy == "weighted_avg":
            # 基于距离中心的加权平均（示例：中心权重更高）
            weights = torch.zeros_like(result[0])
            for idx in range(len(outputs)):
                x, y = positions[idx]
                output_patch = outputs[idx]
                x_center = x + (self.trueimgsize[0] // 2)
                y_center = y + (self.trueimgsize[1] // 2)
                yy, xx = torch.meshgrid(
                    torch.arange(x, x + self.trueimgsize[0]),
                    torch.arange(y, y + self.trueimgsize[1])
                )
                dist = torch.sqrt((xx - x_center) ** 2 + (yy - y_center) ** 2)
                #####self.trueimgsize[0]是否考虑到size不是矩形的情况！！！
                weight = torch.exp(-dist ** 2 / (2 * (self.trueimgsize[0] / 4) ** 2)).to(weights.device)
                weight = weight.unsqueeze(0)
                patch_weight = weight.expand(num_classes, -1, -1)
                result[:, :, x:x + self.trueimgsize[0], y:y + self.trueimgsize[1]] += output_patch * patch_weight.unsqueeze(0)
                weights[:, x:x + self.trueimgsize[0], y:y + self.trueimgsize[1]] += patch_weight
            merged = result / (weights.unsqueeze(0) + 1e-8)
        elif self.merge_strategy == "majority_vote":
            vote = vote.permute(2, 0, 1)
            merged = vote.unsqueeze(0)
        else:
            raise ValueError(f"Unknown merge_strategy: {self.merge_strategy}")

        # 最终结果处理
        final_mask = merged.argmax(1).squeeze(0).cpu().numpy().astype(np.uint8)
        return final_mask

    # region process_image处理预测集合
    def process_image(self,model, device, img_path, output_path):
        # pt/pth模式推理(考虑把多个if里面的写成一个个函数)
        if self.infer_format in ['pt', 'pth']:
            # 正常模式推理
            if not self.ifsahi:
                self.proce_img_pt_noraml(model, device, img_path, output_path)
            # sahi模式推理
            else:
                self.proce_img_pt_sahi(model, device, img_path, output_path)

        # onnx模式推理
        if self.infer_format in ['onnx']:
            # 正常模式推理
            if not self.ifsahi:
                self.proce_img_onnx_normal(model, device, img_path, output_path)
            # sahi模式推理
            else:
                self.proce_img_onnx_sahi(model, device, img_path, output_path)
        # openvino模式推理
        if self.infer_format in ['openvino']:
            # 正常模式推理
            if not self.ifsahi:
                self.proce_img_openvino_normal(model, device, img_path, output_path)
            # sahi模式推理
            else:
                self.proce_img_openvino_sahi(model, device, img_path, output_path)
    def proce_img_pt_noraml(self,model,device,img_path, output_path):
            # 加载图像
            original_img = Image.open(img_path)
            if original_img.mode != 'RGB':
                original_img = original_img.convert('RGB')

            # 图像预处理
            data_transform = transforms.Compose([
                transforms.Resize(self.trueimgsize[0]),
                transforms.ToTensor(),
                transforms.Normalize(mean=(0.485, 0.456, 0.406),
                                     std=(0.229, 0.224, 0.225))
            ])
            img_tensor = data_transform(original_img)
            img_tensor = torch.unsqueeze(img_tensor, dim=0).to(device)

            model.eval()
            with torch.no_grad():
                t_start = self.time_synchronized()
                output = model(img_tensor)
                t_end = self.time_synchronized()
                print(f"Inference time for {os.path.basename(img_path)}: {t_end - t_start:.3f}s")

            # 假设模型输出 'out' 为分割结果
            prediction = output['out'].argmax(1).squeeze(0)
            mask = prediction.cpu().numpy().astype(np.uint8)

            # 将 mask 转为彩色图
            # 生成彩色 mask
            if ULTRALYTICS_COLORS_AVAILABLE and self.yolocolors:
                color_mask = self.mask_to_color(mask)
            else:
                color_mask = self.mask_to_color(mask, self.palette)
            # color_mask = self.mask_to_color(mask, self.palette)
            # 仅在 mask 区域进行半透明叠加
            blended_img = self.blend_mask_region(original_img, color_mask, mask, alpha=0.5)
            blended_img.save(output_path)
            print("Saved result to", output_path)
    def proce_img_pt_sahi(self,model,device,img_path, output_path):
        # 加载图像
        original_img = Image.open(img_path)
        if original_img.mode != 'RGB':
            original_img = original_img.convert('RGB')

        # 图像预处理
        # ✅ 修改预处理：先 ToTensor，不提前标准化（标准化在切图后）
        data_transform = transforms.Compose([
            transforms.ToTensor()  # 仅转换为 [0,1] 的张量，不标准化
        ])
        img_tensor = data_transform(original_img).unsqueeze(0).to(device)

        model.eval()
        with torch.no_grad():
            t_start = self.time_synchronized()
            mask = self.slice_and_merge(model, img_tensor)
            t_end = self.time_synchronized()
            print(f"Inference time for {os.path.basename(img_path)}: {t_end - t_start:.3f}s")

        # 将 mask 转为彩色图
        # 生成彩色 mask
        if ULTRALYTICS_COLORS_AVAILABLE and self.yolocolors:
            color_mask = self.mask_to_color(mask)
        else:
            color_mask = self.mask_to_color(mask, self.palette)
        # color_mask = self.mask_to_color(mask, self.palette)
        # 仅在 mask 区域进行半透明叠加
        blended_img = self.blend_mask_region(original_img, color_mask, mask, alpha=0.5)
        blended_img.save(output_path)
        print("Saved result to", output_path)
    def proce_img_onnx_normal(self,model,device,img_path, output_path):
            # 加载图像
            original_img = Image.open(img_path)
            if original_img.mode != 'RGB':
                original_img = original_img.convert('RGB')

            # 图像预处理
            data_transform = transforms.Compose([
                transforms.Resize(self.trueimgsize[0]),
                transforms.ToTensor(),
                transforms.Normalize(mean=(0.485, 0.456, 0.406),
                                     std=(0.229, 0.224, 0.225))
            ])
            img_tensor = data_transform(original_img).unsqueeze(0).numpy()  # 转换为 numpy

            # 获取 ONNX 输入名
            input_name = model.get_inputs()[0].name
            output_name = model.get_outputs()[0].name
            t_start = self.time_synchronized()
            output = model.run([output_name], {input_name: img_tensor})[0]
            t_end = self.time_synchronized()
            print(f"Inference time for {os.path.basename(img_path)}: {t_end - t_start:.3f}s")
            # 获取最大概率类别
            prediction = np.argmax(output, axis=1).squeeze(0).astype(np.uint8)

            # 将 mask 转为彩色图
            # 生成彩色 mask
            if ULTRALYTICS_COLORS_AVAILABLE and self.yolocolors:
                color_mask = self.mask_to_color(prediction)
            else:
                color_mask = self.mask_to_color(prediction, self.palette)
            # color_mask = self.mask_to_color(mask, self.palette)
            # 仅在 mask 区域进行半透明叠加
            blended_img = self.blend_mask_region(original_img, color_mask, prediction, alpha=0.5)
            blended_img.save(output_path)
            print("Saved result to", output_path)
    def proce_img_onnx_sahi(self,model,device,img_path, output_path):
        # 加载图像
        original_img = Image.open(img_path)
        if original_img.mode != 'RGB':
            original_img = original_img.convert('RGB')

        # 图像预处理
        # ✅ 修改预处理：先 ToTensor，不提前标准化（标准化在切图后）
        data_transform = transforms.Compose([
            transforms.ToTensor()  # 仅转换为 [0,1] 的张量，不标准化
        ])
        img_tensor = data_transform(original_img).unsqueeze(0)

        with torch.no_grad():
            t_start = self.time_synchronized()
            mask = self.slice_and_merge(model, img_tensor)
            t_end = self.time_synchronized()
            print(f"Inference time for {os.path.basename(img_path)}: {t_end - t_start:.3f}s")

        # 将 mask 转为彩色图
        # 生成彩色 mask
        if ULTRALYTICS_COLORS_AVAILABLE and self.yolocolors:
            color_mask = self.mask_to_color(mask)
        else:
            color_mask = self.mask_to_color(mask, self.palette)
        # color_mask = self.mask_to_color(mask, self.palette)
        # 仅在 mask 区域进行半透明叠加
        blended_img = self.blend_mask_region(original_img, color_mask, mask, alpha=0.5)
        blended_img.save(output_path)
        print("Saved result to", output_path)
    def proce_img_openvino_normal(self,model,device,img_path, output_path):
            # 加载图像
            original_img = Image.open(img_path)
            if original_img.mode != 'RGB':
                original_img = original_img.convert('RGB')

            # 图像预处理
            data_transform = transforms.Compose([
                transforms.Resize(self.trueimgsize[0]),
                transforms.ToTensor(),
                transforms.Normalize(mean=(0.485, 0.456, 0.406),
                                     std=(0.229, 0.224, 0.225))
            ])
            img_tensor = data_transform(original_img).unsqueeze(0).numpy()  # 转换为 numpy

            # 获取模型输入输出名称
            input_name = model.inputs[0].get_any_name()
            output_name = model.outputs[0].get_any_name()
            # 创建推理请求，并执行推理
            infer_request = model.create_infer_request()
            t_start = self.time_synchronized()
            results = infer_request.infer({input_name: img_tensor})
            t_end = self.time_synchronized()
            print(f"Inference time for {os.path.basename(img_path)}: {t_end - t_start:.3f}s")
            # 获取输出（假定输出形状为 (1, num_classes, 256, 256)）
            output = results[output_name]
            prediction = np.argmax(output, axis=1).squeeze(0).astype(np.uint8)

            # 将 mask 转为彩色图
            # 生成彩色 mask
            if ULTRALYTICS_COLORS_AVAILABLE and self.yolocolors:
                color_mask = self.mask_to_color(prediction)
            else:
                color_mask = self.mask_to_color(prediction, self.palette)
            # color_mask = self.mask_to_color(mask, self.palette)
            # 仅在 mask 区域进行半透明叠加
            blended_img = self.blend_mask_region(original_img, color_mask, prediction, alpha=0.5)
            blended_img.save(output_path)
            print("Saved result to", output_path)
    def proce_img_openvino_sahi(self,model,device,img_path, output_path):
        # 加载图像
        original_img = Image.open(img_path)
        if original_img.mode != 'RGB':
            original_img = original_img.convert('RGB')

        # 图像预处理
        # ✅ 修改预处理：先 ToTensor，不提前标准化（标准化在切图后）
        data_transform = transforms.Compose([
            transforms.ToTensor()  # 仅转换为 [0,1] 的张量，不标准化
        ])
        img_tensor = data_transform(original_img).unsqueeze(0)

        # 创建推理请求，并执行推理
        infer_request = model.create_infer_request()
        with torch.no_grad():
            t_start = self.time_synchronized()
            mask = self.slice_and_merge(infer_request, img_tensor)
            t_end = self.time_synchronized()
            print(f"Inference time for {os.path.basename(img_path)}: {t_end - t_start:.3f}s")

        # 将 mask 转为彩色图
        # 生成彩色 mask
        if ULTRALYTICS_COLORS_AVAILABLE and self.yolocolors:
            color_mask = self.mask_to_color(mask)
        else:
            color_mask = self.mask_to_color(mask, self.palette)
        # color_mask = self.mask_to_color(mask, self.palette)
        # 仅在 mask 区域进行半透明叠加
        blended_img = self.blend_mask_region(original_img, color_mask, mask, alpha=0.5)
        blended_img.save(output_path)
        print("Saved result to", output_path)
    # endregion

    # region 预测图像函数集合
    def predict_normal(self):
        #pt/pth模式推理
        if self.infer_format in ['pt','pth']:
            self.pred_normal_pt()
        # onnx模式推理
        if self.infer_format in['onnx']:
            self.pred_normal_onnx()
        # openvino模式推理
        if self.infer_format in['openvino']:
            self.pred_normal_openvino()
    def pred_normal_pt(self):
        # 获取所有设备
        # 获取所有 GPU 设备
        num_gpus = torch.cuda.device_count()
        gpu_list = [f"{i}: {torch.cuda.get_device_name(i)}" for i in range(num_gpus)]

        print(f"Available GPUs: {gpu_list}")
        # 配置设备
        if self.inferdevicehandle == 'cpu':
            device = torch.device("cpu")
        elif self.inferdevicehandle == 'gpu':
            device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        else:
            device = torch.device(f"cuda:{self.inferdevicehandle}" if torch.cuda.is_available() else "cpu")
        print("Using device:", device)
        # 创建模型（使用 FCN-ResNet50）
        model_dict = torch.load(self.modelpath, map_location='cpu')
        diymodel_dict = {
            "fcn_resnet50": fcn_resnet50,
            "fcn_resnet18": fcn_resnet18,
            "fcn_resnet34": fcn_resnet34,
            "deeplabv3_resnet18": deeplabv3_resnet18,
            "deeplabv3_resnet34": deeplabv3_resnet34,
        }

        model_arch = model_dict["model_type"]
        if model_arch in diymodel_dict:
            model = diymodel_dict[model_arch](aux=self.aux, num_classes=model_dict['num_classes'] + 1)
        else:
            model = models.__dict__[model_arch](pretrained=False, pretrained_backbone=False,
                                                num_classes=model_dict['num_classes'] + 1,
                                                aux_loss=self.aux)
        weights_dict = model_dict['model'].state_dict()
        for k in list(weights_dict.keys()):
            if "aux" in k:
                del weights_dict[k]
        model.load_state_dict(weights_dict)
        model.to(device)
        model.eval()
        # from pathlib import Path
        Path(self.saveimg_dir).mkdir(parents=True, exist_ok=True)

        for root, _, files in os.walk(self.testimg_dir):
            for filename in files:
                if filename.lower().endswith((".jpg", ".jpeg", ".png", ".bmp")):
                    img_path = os.path.join(root, filename)  # 输入图像路径
                    # 计算相对路径
                    relative_path = os.path.relpath(root, self.testimg_dir)
                    # 生成输出目录，并保持相对路径结构
                    output_dir = os.path.join(self.saveimg_dir, relative_path)
                    os.makedirs(output_dir, exist_ok=True)
                    output_path = os.path.join(output_dir, filename)  # 输出路径

                    print(f"Processing {img_path} ...")
                    self.process_image(model, device, img_path, output_path)
    def pred_normal_onnx(self):
        import onnxruntime as ort
        # 获取所有设备
        providers = ort.get_available_providers()
        print("Available ONNX Runtime providers:", providers)
        num_gpus = torch.cuda.device_count()
        gpu_list = [f"{i}: {torch.cuda.get_device_name(i)}" for i in range(num_gpus)]
        print(f"Available GPUs: {gpu_list}")
        # 配置设备
        if self.inferdevicehandle == 'cpu':
            device = ['CPUExecutionProvider']
        elif self.inferdevicehandle == 'gpu':
            device = ['CUDAExecutionProvider' if torch.cuda.is_available() else 'CPUExecutionProvider']
        else:
            device = [('CUDAExecutionProvider',
                       {'device_id': int(
                           self.inferdevicehandle)}) if torch.cuda.is_available() else 'CPUExecutionProvider']
            # device = torch.device(f"cuda:{self.inferdevicehandle}" if torch.cuda.is_available() else "cpu")
        print("Using device:", device)
        # 创建模型（使用 FCN-ResNet50）
        # 加载 ONNX 模型
        onnx_session = ort.InferenceSession(self.modelpath, providers=device)

        # from pathlib import Path
        Path(self.saveimg_dir).mkdir(parents=True, exist_ok=True)

        for root, _, files in os.walk(self.testimg_dir):
            for filename in files:
                if filename.lower().endswith((".jpg", ".jpeg", ".png", ".bmp")):
                    img_path = os.path.join(root, filename)  # 输入图像路径
                    # 计算相对路径
                    relative_path = os.path.relpath(root, self.testimg_dir)
                    # 生成输出目录，并保持相对路径结构
                    output_dir = os.path.join(self.saveimg_dir, relative_path)
                    os.makedirs(output_dir, exist_ok=True)
                    output_path = os.path.join(output_dir, filename)  # 输出路径

                    print(f"Processing {img_path} ...")
                    self.process_image(onnx_session, device, img_path, output_path)
    def pred_normal_openvino(self):
        from openvino.runtime import Core
        # 获取所有设备
        core = Core()
        devices = core.available_devices
        device_info = {device: core.get_property(device, "FULL_DEVICE_NAME") for device in devices}
        print("Available OpenVINO devices:", device_info)
        # 配置设备
        if self.inferdevicehandle == 'cpu':
            device = "CPU"
        elif self.inferdevicehandle == 'gpu':
            # device = "GPU"
            device = "GPU.0"
        else:
            device = f"GPU.{self.inferdevicehandle}" if torch.cuda.is_available() else "CPU"
            # device = torch.device(f"cuda:{self.inferdevicehandle}" if torch.cuda.is_available() else "cpu")
        print("Using device:", device)

        # 创建模型（使用 FCN-ResNet50）
        model = core.read_model(self.modelpath)
        compiled_model = core.compile_model(model, device)
        # from pathlib import Path
        Path(self.saveimg_dir).mkdir(parents=True, exist_ok=True)
        # os.makedirs(self.saveimg_dir, exist_ok=True)#传统创建
        # # 遍历文件夹中的所有图像
        # for filename in os.listdir(self.testimg_dir):
        #     if filename.lower().endswith((".jpg", ".jpeg", ".png", ".bmp")):
        #         img_path = os.path.join(self.testimg_dir, filename)
        #         output_path = os.path.join(self.saveimg_dir, filename)
        #         print(f"Processing {img_path} ...")
        #         self.process_image(model, device, img_path, output_path)

        # 遍历 self.testimg_dir 下的所有子文件夹和图片
        for root, _, files in os.walk(self.testimg_dir):
            for filename in files:
                if filename.lower().endswith((".jpg", ".jpeg", ".png", ".bmp")):
                    img_path = os.path.join(root, filename)  # 输入图像路径
                    # 计算相对路径
                    relative_path = os.path.relpath(root, self.testimg_dir)
                    # 生成输出目录，并保持相对路径结构
                    output_dir = os.path.join(self.saveimg_dir, relative_path)
                    os.makedirs(output_dir, exist_ok=True)
                    output_path = os.path.join(output_dir, filename)  # 输出路径

                    print(f"Processing {img_path} ...")
                    self.process_image(compiled_model, device, img_path, output_path)
    # endregion

    # region 原版process_image写法，所有集成
    # def process_image(self,model, device, img_path, output_path):
    #     # pt/pth模式推理(考虑把多个if里面的写成一个个函数)
    #     if self.infer_format in ['pt', 'pth']:
    #         # 正常模式推理
    #         if not self.ifsahi:
    #             # 加载图像
    #             original_img = Image.open(img_path)
    #             if original_img.mode != 'RGB':
    #                 original_img = original_img.convert('RGB')
    #
    #             # 图像预处理
    #             data_transform = transforms.Compose([
    #                 transforms.Resize(self.trueimgsize[0]),
    #                 transforms.ToTensor(),
    #                 transforms.Normalize(mean=(0.485, 0.456, 0.406),
    #                                      std=(0.229, 0.224, 0.225))
    #             ])
    #             img_tensor = data_transform(original_img)
    #             img_tensor = torch.unsqueeze(img_tensor, dim=0).to(device)
    #
    #             model.eval()
    #             with torch.no_grad():
    #                 t_start = self.time_synchronized()
    #                 output = model(img_tensor)
    #                 t_end = self.time_synchronized()
    #                 print(f"Inference time for {os.path.basename(img_path)}: {t_end - t_start:.3f}s")
    #
    #             # 假设模型输出 'out' 为分割结果
    #             prediction = output['out'].argmax(1).squeeze(0)
    #             mask = prediction.cpu().numpy().astype(np.uint8)
    #
    #             # 将 mask 转为彩色图
    #             # 生成彩色 mask
    #             if ULTRALYTICS_COLORS_AVAILABLE and self.yolocolors:
    #                 color_mask = self.mask_to_color(mask)
    #             else:
    #                 color_mask = self.mask_to_color(mask, self.palette)
    #             # color_mask = self.mask_to_color(mask, self.palette)
    #             # 仅在 mask 区域进行半透明叠加
    #             blended_img = self.blend_mask_region(original_img, color_mask, mask, alpha=0.5)
    #             blended_img.save(output_path)
    #             print("Saved result to", output_path)
    #         # sahi模式推理
    #         else:
    #             # 加载图像
    #             original_img = Image.open(img_path)
    #             if original_img.mode != 'RGB':
    #                 original_img = original_img.convert('RGB')
    #
    #             # 图像预处理
    #             # ✅ 修改预处理：先 ToTensor，不提前标准化（标准化在切图后）
    #             data_transform = transforms.Compose([
    #                 transforms.ToTensor()  # 仅转换为 [0,1] 的张量，不标准化
    #             ])
    #             img_tensor = data_transform(original_img).unsqueeze(0).to(device)
    #
    #             model.eval()
    #             with torch.no_grad():
    #                 t_start = self.time_synchronized()
    #                 mask = self.slice_and_merge(model, img_tensor)
    #                 t_end = self.time_synchronized()
    #                 print(f"Inference time for {os.path.basename(img_path)}: {t_end - t_start:.3f}s")
    #
    #
    #             # 将 mask 转为彩色图
    #             # 生成彩色 mask
    #             if ULTRALYTICS_COLORS_AVAILABLE and self.yolocolors:
    #                 color_mask = self.mask_to_color(mask)
    #             else:
    #                 color_mask = self.mask_to_color(mask, self.palette)
    #             # color_mask = self.mask_to_color(mask, self.palette)
    #             # 仅在 mask 区域进行半透明叠加
    #             blended_img = self.blend_mask_region(original_img, color_mask, mask, alpha=0.5)
    #             blended_img.save(output_path)
    #             print("Saved result to", output_path)
    #
    #     # onnx模式推理
    #     if self.infer_format in ['onnx']:
    #         # 正常模式推理
    #         if not self.ifsahi:
    #             # 加载图像
    #             original_img = Image.open(img_path)
    #             if original_img.mode != 'RGB':
    #                 original_img = original_img.convert('RGB')
    #
    #             # 图像预处理
    #             data_transform = transforms.Compose([
    #                 transforms.Resize(self.trueimgsize[0]),
    #                 transforms.ToTensor(),
    #                 transforms.Normalize(mean=(0.485, 0.456, 0.406),
    #                                      std=(0.229, 0.224, 0.225))
    #             ])
    #             img_tensor = data_transform(original_img).unsqueeze(0).numpy()  # 转换为 numpy
    #
    #             # 获取 ONNX 输入名
    #             input_name = model.get_inputs()[0].name
    #             output_name = model.get_outputs()[0].name
    #             t_start = self.time_synchronized()
    #             output = model.run([output_name], {input_name: img_tensor})[0]
    #             t_end = self.time_synchronized()
    #             print(f"Inference time for {os.path.basename(img_path)}: {t_end - t_start:.3f}s")
    #             # 获取最大概率类别
    #             prediction = np.argmax(output, axis=1).squeeze(0).astype(np.uint8)
    #
    #             # 将 mask 转为彩色图
    #             # 生成彩色 mask
    #             if ULTRALYTICS_COLORS_AVAILABLE and self.yolocolors:
    #                 color_mask = self.mask_to_color(prediction)
    #             else:
    #                 color_mask = self.mask_to_color(prediction, self.palette)
    #             # color_mask = self.mask_to_color(mask, self.palette)
    #             # 仅在 mask 区域进行半透明叠加
    #             blended_img = self.blend_mask_region(original_img, color_mask, prediction, alpha=0.5)
    #             blended_img.save(output_path)
    #             print("Saved result to", output_path)
    #         # sahi模式推理
    #         else:
    #             # 加载图像
    #             original_img = Image.open(img_path)
    #             if original_img.mode != 'RGB':
    #                 original_img = original_img.convert('RGB')
    #
    #             # 图像预处理
    #             # ✅ 修改预处理：先 ToTensor，不提前标准化（标准化在切图后）
    #             data_transform = transforms.Compose([
    #                 transforms.ToTensor()  # 仅转换为 [0,1] 的张量，不标准化
    #             ])
    #             img_tensor = data_transform(original_img).unsqueeze(0)
    #
    #             with torch.no_grad():
    #                 t_start = self.time_synchronized()
    #                 mask = self.slice_and_merge(model, img_tensor)
    #                 t_end = self.time_synchronized()
    #                 print(f"Inference time for {os.path.basename(img_path)}: {t_end - t_start:.3f}s")
    #
    #
    #             # 将 mask 转为彩色图
    #             # 生成彩色 mask
    #             if ULTRALYTICS_COLORS_AVAILABLE and self.yolocolors:
    #                 color_mask = self.mask_to_color(mask)
    #             else:
    #                 color_mask = self.mask_to_color(mask, self.palette)
    #             # color_mask = self.mask_to_color(mask, self.palette)
    #             # 仅在 mask 区域进行半透明叠加
    #             blended_img = self.blend_mask_region(original_img, color_mask, mask, alpha=0.5)
    #             blended_img.save(output_path)
    #             print("Saved result to", output_path)
    #     # openvino模式推理
    #     if self.infer_format in ['openvino']:
    #         # 正常模式推理
    #         if not self.ifsahi:
    #             # 加载图像
    #             original_img = Image.open(img_path)
    #             if original_img.mode != 'RGB':
    #                 original_img = original_img.convert('RGB')
    #
    #             # 图像预处理
    #             data_transform = transforms.Compose([
    #                 transforms.Resize(self.trueimgsize[0]),
    #                 transforms.ToTensor(),
    #                 transforms.Normalize(mean=(0.485, 0.456, 0.406),
    #                                      std=(0.229, 0.224, 0.225))
    #             ])
    #             img_tensor = data_transform(original_img).unsqueeze(0).numpy()  # 转换为 numpy
    #
    #             # 获取模型输入输出名称
    #             input_name = model.inputs[0].get_any_name()
    #             output_name = model.outputs[0].get_any_name()
    #             # 创建推理请求，并执行推理
    #             infer_request = model.create_infer_request()
    #             t_start = self.time_synchronized()
    #             results = infer_request.infer({input_name: img_tensor})
    #             t_end = self.time_synchronized()
    #             print(f"Inference time for {os.path.basename(img_path)}: {t_end - t_start:.3f}s")
    #             # 获取输出（假定输出形状为 (1, num_classes, 256, 256)）
    #             output = results[output_name]
    #             prediction = np.argmax(output, axis=1).squeeze(0).astype(np.uint8)
    #
    #             # 将 mask 转为彩色图
    #             # 生成彩色 mask
    #             if ULTRALYTICS_COLORS_AVAILABLE and self.yolocolors:
    #                 color_mask = self.mask_to_color(prediction)
    #             else:
    #                 color_mask = self.mask_to_color(prediction, self.palette)
    #             # color_mask = self.mask_to_color(mask, self.palette)
    #             # 仅在 mask 区域进行半透明叠加
    #             blended_img = self.blend_mask_region(original_img, color_mask, prediction, alpha=0.5)
    #             blended_img.save(output_path)
    #             print("Saved result to", output_path)
    #         # sahi模式推理
    #         else:
    #             # 加载图像
    #             original_img = Image.open(img_path)
    #             if original_img.mode != 'RGB':
    #                 original_img = original_img.convert('RGB')
    #
    #             # 图像预处理
    #             # ✅ 修改预处理：先 ToTensor，不提前标准化（标准化在切图后）
    #             data_transform = transforms.Compose([
    #                 transforms.ToTensor()  # 仅转换为 [0,1] 的张量，不标准化
    #             ])
    #             img_tensor = data_transform(original_img).unsqueeze(0)
    #
    #             # 创建推理请求，并执行推理
    #             infer_request = model.create_infer_request()
    #             with torch.no_grad():
    #                 t_start = self.time_synchronized()
    #                 mask = self.slice_and_merge(infer_request, img_tensor)
    #                 t_end = self.time_synchronized()
    #                 print(f"Inference time for {os.path.basename(img_path)}: {t_end - t_start:.3f}s")
    #
    #
    #             # 将 mask 转为彩色图
    #             # 生成彩色 mask
    #             if ULTRALYTICS_COLORS_AVAILABLE and self.yolocolors:
    #                 color_mask = self.mask_to_color(mask)
    #             else:
    #                 color_mask = self.mask_to_color(mask, self.palette)
    #             # color_mask = self.mask_to_color(mask, self.palette)
    #             # 仅在 mask 区域进行半透明叠加
    #             blended_img = self.blend_mask_region(original_img, color_mask, mask, alpha=0.5)
    #             blended_img.save(output_path)
    #             print("Saved result to", output_path)
    # endregion

    # region 原版predict_normal写法，所有集成
    # def predict_normal(self):
    #     #pt/pth模式推理
    #     if self.infer_format in ['pt','pth']:
    #         #获取所有设备
    #         # 获取所有 GPU 设备
    #         num_gpus = torch.cuda.device_count()
    #         gpu_list = [f"{i}: {torch.cuda.get_device_name(i)}" for i in range(num_gpus)]
    #
    #         print(f"Available GPUs: {gpu_list}")
    #         # 配置设备
    #         if self.inferdevicehandle == 'cpu' :
    #             device = torch.device("cpu")
    #         elif self.inferdevicehandle == 'gpu':
    #             device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    #         else:
    #             device = torch.device(f"cuda:{self.inferdevicehandle}" if torch.cuda.is_available() else "cpu")
    #         print("Using device:", device)
    #         # 创建模型（使用 FCN-ResNet50）
    #         model_dict = torch.load(self.modelpath, map_location='cpu')
    #         diymodel_dict = {
    #             "fcn_resnet50": fcn_resnet50,
    #             "fcn_resnet18": fcn_resnet18,
    #             "fcn_resnet34": fcn_resnet34,
    #             "deeplabv3_resnet18": deeplabv3_resnet18,
    #             "deeplabv3_resnet34": deeplabv3_resnet34,
    #         }
    #
    #         model_arch = model_dict["model_type"]
    #         if model_arch in diymodel_dict:
    #             model = diymodel_dict[model_arch](aux=self.aux, num_classes=model_dict['num_classes'] + 1)
    #         else:
    #             model = models.__dict__[model_arch](pretrained=False, pretrained_backbone=False,
    #                                                       num_classes=model_dict['num_classes'] + 1,
    #                                                       aux_loss=self.aux)
    #         weights_dict = model_dict['model'].state_dict()
    #         for k in list(weights_dict.keys()):
    #             if "aux" in k:
    #                 del weights_dict[k]
    #         model.load_state_dict(weights_dict)
    #         model.to(device)
    #         model.eval()
    #         # from pathlib import Path
    #         Path(self.saveimg_dir).mkdir(parents=True, exist_ok=True)
    #         # os.makedirs(self.saveimg_dir, exist_ok=True)#传统创建
    #         # # 遍历文件夹中的所有图像
    #         # for filename in os.listdir(self.testimg_dir):
    #         #     if filename.lower().endswith((".jpg", ".jpeg", ".png", ".bmp")):
    #         #         img_path = os.path.join(self.testimg_dir, filename)
    #         #         output_path = os.path.join(self.saveimg_dir, filename)
    #         #         print(f"Processing {img_path} ...")
    #         #         self.process_image(model, device, img_path, output_path)
    #
    #         # 遍历 self.testimg_dir 下的所有子文件夹和图片
    #         for root, _, files in os.walk(self.testimg_dir):
    #             for filename in files:
    #                 if filename.lower().endswith((".jpg", ".jpeg", ".png", ".bmp")):
    #                     img_path = os.path.join(root, filename)  # 输入图像路径
    #                     # 计算相对路径
    #                     relative_path = os.path.relpath(root, self.testimg_dir)
    #                     # 生成输出目录，并保持相对路径结构
    #                     output_dir = os.path.join(self.saveimg_dir, relative_path)
    #                     os.makedirs(output_dir, exist_ok=True)
    #                     output_path = os.path.join(output_dir, filename)  # 输出路径
    #
    #                     print(f"Processing {img_path} ...")
    #                     self.process_image(model, device, img_path, output_path)
    #     # onnx模式推理
    #     if self.infer_format in['onnx']:
    #         import onnxruntime as ort
    #         # 获取所有设备
    #         providers = ort.get_available_providers()
    #         print("Available ONNX Runtime providers:", providers)
    #         num_gpus = torch.cuda.device_count()
    #         gpu_list = [f"{i}: {torch.cuda.get_device_name(i)}" for i in range(num_gpus)]
    #         print(f"Available GPUs: {gpu_list}")
    #         #配置设备
    #         if self.inferdevicehandle == 'cpu':
    #             device = ['CPUExecutionProvider']
    #         elif self.inferdevicehandle == 'gpu':
    #             device = ['CUDAExecutionProvider' if torch.cuda.is_available() else 'CPUExecutionProvider']
    #         else:
    #             device = [('CUDAExecutionProvider',
    #                        {'device_id': int(self.inferdevicehandle)}) if torch.cuda.is_available() else 'CPUExecutionProvider']
    #             # device = torch.device(f"cuda:{self.inferdevicehandle}" if torch.cuda.is_available() else "cpu")
    #         print("Using device:", device)
    #         # 创建模型（使用 FCN-ResNet50）
    #         # 加载 ONNX 模型
    #         onnx_session = ort.InferenceSession(self.modelpath, providers=device)
    #
    #         # from pathlib import Path
    #         Path(self.saveimg_dir).mkdir(parents=True, exist_ok=True)
    #         # os.makedirs(self.saveimg_dir, exist_ok=True)#传统创建
    #         # # 遍历文件夹中的所有图像
    #         # for filename in os.listdir(self.testimg_dir):
    #         #     if filename.lower().endswith((".jpg", ".jpeg", ".png", ".bmp")):
    #         #         img_path = os.path.join(self.testimg_dir, filename)
    #         #         output_path = os.path.join(self.saveimg_dir, filename)
    #         #         print(f"Processing {img_path} ...")
    #         #         self.process_image(model, device, img_path, output_path)
    #
    #         # 遍历 self.testimg_dir 下的所有子文件夹和图片
    #         for root, _, files in os.walk(self.testimg_dir):
    #             for filename in files:
    #                 if filename.lower().endswith((".jpg", ".jpeg", ".png", ".bmp")):
    #                     img_path = os.path.join(root, filename)  # 输入图像路径
    #                     # 计算相对路径
    #                     relative_path = os.path.relpath(root, self.testimg_dir)
    #                     # 生成输出目录，并保持相对路径结构
    #                     output_dir = os.path.join(self.saveimg_dir, relative_path)
    #                     os.makedirs(output_dir, exist_ok=True)
    #                     output_path = os.path.join(output_dir, filename)  # 输出路径
    #
    #                     print(f"Processing {img_path} ...")
    #                     self.process_image(onnx_session, device, img_path, output_path)
    #     # openvino模式推理
    #     if self.infer_format in['openvino']:
    #         from openvino.runtime import Core
    #         #获取所有设备
    #         core = Core()
    #         devices = core.available_devices
    #         device_info = {device: core.get_property(device, "FULL_DEVICE_NAME") for device in devices}
    #         print("Available OpenVINO devices:", device_info)
    #         # 配置设备
    #         if self.inferdevicehandle == 'cpu':
    #             device = "CPU"
    #         elif self.inferdevicehandle == 'gpu':
    #             # device = "GPU"
    #             device = "GPU.0"
    #         else:
    #             device = f"GPU.{self.inferdevicehandle}" if torch.cuda.is_available() else "CPU"
    #             # device = torch.device(f"cuda:{self.inferdevicehandle}" if torch.cuda.is_available() else "cpu")
    #         print("Using device:", device)
    #
    #         # 创建模型（使用 FCN-ResNet50）
    #         model = core.read_model(self.modelpath)
    #         compiled_model = core.compile_model(model, device)
    #         # from pathlib import Path
    #         Path(self.saveimg_dir).mkdir(parents=True, exist_ok=True)
    #         # os.makedirs(self.saveimg_dir, exist_ok=True)#传统创建
    #         # # 遍历文件夹中的所有图像
    #         # for filename in os.listdir(self.testimg_dir):
    #         #     if filename.lower().endswith((".jpg", ".jpeg", ".png", ".bmp")):
    #         #         img_path = os.path.join(self.testimg_dir, filename)
    #         #         output_path = os.path.join(self.saveimg_dir, filename)
    #         #         print(f"Processing {img_path} ...")
    #         #         self.process_image(model, device, img_path, output_path)
    #
    #         # 遍历 self.testimg_dir 下的所有子文件夹和图片
    #         for root, _, files in os.walk(self.testimg_dir):
    #             for filename in files:
    #                 if filename.lower().endswith((".jpg", ".jpeg", ".png", ".bmp")):
    #                     img_path = os.path.join(root, filename)  # 输入图像路径
    #                     # 计算相对路径
    #                     relative_path = os.path.relpath(root, self.testimg_dir)
    #                     # 生成输出目录，并保持相对路径结构
    #                     output_dir = os.path.join(self.saveimg_dir, relative_path)
    #                     os.makedirs(output_dir, exist_ok=True)
    #                     output_path = os.path.join(output_dir, filename)  # 输出路径
    #
    #                     print(f"Processing {img_path} ...")
    #                     self.process_image(compiled_model, device, img_path, output_path)
    # endregion
    # def predict_normal_onnx(self):
    #     # 配置设备
    #     if self.inferdevicehandle == 'cpu' :
    #         device = ['CPUExecutionProvider']
    #     elif self.inferdevicehandle == 'gpu':
    #         device = ['CUDAExecutionProvider' if torch.cuda.is_available() else 'CPUExecutionProvider']
    #     else:
    #         device = [('CUDAExecutionProvider', {'device_id': f"{self.inferdevicehandle}"}) if torch.cuda.is_available() else 'CPUExecutionProvider']
    #         # device = torch.device(f"cuda:{self.inferdevicehandle}" if torch.cuda.is_available() else "cpu")
    #     print("Using device:", device)
    #
    #     # 创建模型（使用 FCN-ResNet50）
    #     # 加载 ONNX 模型
    #     onnx_session = ort.InferenceSession(self.modelpath, providers=[
    #         'CUDAExecutionProvider' if torch.cuda.is_available() else 'CPUExecutionProvider'])
    #
    #     # from pathlib import Path
    #     Path(self.saveimg_dir).mkdir(parents=True, exist_ok=True)
    #     # os.makedirs(self.saveimg_dir, exist_ok=True)#传统创建
    #     # # 遍历文件夹中的所有图像
    #     # for filename in os.listdir(self.testimg_dir):
    #     #     if filename.lower().endswith((".jpg", ".jpeg", ".png", ".bmp")):
    #     #         img_path = os.path.join(self.testimg_dir, filename)
    #     #         output_path = os.path.join(self.saveimg_dir, filename)
    #     #         print(f"Processing {img_path} ...")
    #     #         self.process_image(model, device, img_path, output_path)
    #
    #     # 遍历 self.testimg_dir 下的所有子文件夹和图片
    #     for root, _, files in os.walk(self.testimg_dir):
    #         for filename in files:
    #             if filename.lower().endswith((".jpg", ".jpeg", ".png", ".bmp")):
    #                 img_path = os.path.join(root, filename)  # 输入图像路径
    #                 # 计算相对路径
    #                 relative_path = os.path.relpath(root, self.testimg_dir)
    #                 # 生成输出目录，并保持相对路径结构
    #                 output_dir = os.path.join(self.saveimg_dir, relative_path)
    #                 os.makedirs(output_dir, exist_ok=True)
    #                 output_path = os.path.join(output_dir, filename)  # 输出路径
    #
    #                 print(f"Processing {img_path} ...")
    #                 self.process_image(onnx_session, device, img_path, output_path)