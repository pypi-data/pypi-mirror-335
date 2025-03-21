import torch
import torchvision.models.segmentation as models

from ..fcn.src import *

class export_model:

    @staticmethod
    def export_model_efficient(export_modeldict):
        model = torch.load(export_modeldict, map_location='cpu')['state_dict']
        return model

    @staticmethod
    def export_model_fcn(export_modeldict):
        # model = fcn_resnet50(aux=self.aux, num_classes=self.num_classes)
        # weights_dict = torch.load(export_modeldict, map_location='cpu')
        # model.load_state_dict(weights_dict, strict=False)
        # return model
        # 加载模型权重
        model_pt= torch.load(export_modeldict, map_location='cpu')
        diymodel_dict = {
            "fcn_resnet50": fcn_resnet50,
            "fcn_resnet18": fcn_resnet18,
            "fcn_resnet34": fcn_resnet34,
            "deeplabv3_resnet18": deeplabv3_resnet18,
            "deeplabv3_resnet34": deeplabv3_resnet34,
        }

        model_arch = model_pt["model_type"]
        if model_arch in diymodel_dict:
            model = diymodel_dict[model_arch](aux=False, num_classes=model_pt['num_classes'] + 1)
        else:
            model = models.__dict__[model_arch](pretrained=False, pretrained_backbone=False,
                                                      num_classes=model_pt['num_classes'] + 1,
                                                      aux_loss=False)
        model_dict = model_pt['model']
        # 只保留去除了 aux 相关参数的 state_dict
        weights_dict = model_dict.state_dict()

        # 删除包含 "aux" 关键字的权重
        for k in list(weights_dict.keys()):
            if "aux" in k:
                del weights_dict[k]

        # 重新包装 model，返回修改后的状态字典
        model.load_state_dict(weights_dict)
        return model