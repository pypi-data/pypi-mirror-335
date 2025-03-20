import torch
import torch.nn as nn
import torchvision.models as models
from torchvision.models._utils import IntermediateLayerGetter
from torchvision.models.segmentation.deeplabv3 import DeepLabV3_ResNet101_Weights,DeepLabV3, DeepLabHead, FCNHead
from torchvision.models.resnet import ResNet18_Weights, ResNet34_Weights
from typing import Optional, Any


def _deeplabv3_resnet_custom(
        backbone: models.ResNet,
        num_classes: int,
        aux: Optional[bool],
) -> DeepLabV3:
    """
    适配 ResNet-18/34 作为 DeepLabV3 的 backbone。
    """
    return_layers = {"layer4": "out"}
    if aux:
        return_layers["layer3"] = "aux"

    backbone = IntermediateLayerGetter(backbone, return_layers=return_layers)

    # 适配 ResNet-18/34，layer4 输出通道数是 512，而 ResNet-50/101 是 2048
    classifier = DeepLabHead(512, num_classes)
    aux_classifier = FCNHead(256, num_classes) if aux else None

    return DeepLabV3(backbone, classifier, aux_classifier)

def deeplabv3_resnet18(
    *,
    weights: Optional[DeepLabV3_ResNet101_Weights] = None,
    progress: bool = True,
    num_classes: Optional[int] = None,
    aux: Optional[bool] = None,
    weights_backbone: Optional[ResNet18_Weights] = None,  # 不使用预训练权重
    **kwargs: Any,
) -> DeepLabV3:
    """Constructs a DeepLabV3 model with a ResNet-18 backbone (no pretrained weights)."""

    if weights is not None:
        weights_backbone = None
        num_classes = _overwrite_value_param("num_classes", num_classes, len(weights.meta["categories"]))
        aux = _overwrite_value_param("aux_loss", aux, True)
    elif num_classes is None:
        num_classes = 21

    # 不加载预训练权重
    backbone = models.resnet18(weights=weights_backbone, replace_stride_with_dilation=[False, False, False])
    model = _deeplabv3_resnet_custom(backbone, num_classes, aux)

    if weights is not None:
        model.load_state_dict(weights.get_state_dict(progress=progress))

    return model

def deeplabv3_resnet34(
    *,
    weights: Optional[DeepLabV3_ResNet101_Weights] = None,
    progress: bool = True,
    num_classes: Optional[int] = None,
    aux: Optional[bool] = None,
    weights_backbone: Optional[ResNet34_Weights] = None,  # 不使用预训练权重
    **kwargs: Any,
) ->DeepLabV3:
    """Constructs a DeepLabV3 model with a ResNet-34 backbone (no pretrained weights)."""

    if weights is not None:
        weights_backbone = None
        num_classes = _overwrite_value_param("num_classes", num_classes, len(weights.meta["categories"]))
        aux = _overwrite_value_param("aux_loss", aux, True)
    elif num_classes is None:
        num_classes = 21

    # 不加载预训练权重
    backbone = models.resnet34(weights=weights_backbone, replace_stride_with_dilation=[False, False, False])
    model = _deeplabv3_resnet_custom(backbone, num_classes, aux)

    if weights is not None:
        model.load_state_dict(weights.get_state_dict(progress=progress))

    return model

def _overwrite_value_param(param_name, param_value, default_value):
    """Helper function to overwrite parameter values if needed."""
    return default_value if param_value is None else param_value
