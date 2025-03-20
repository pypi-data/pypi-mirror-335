'''enlarge_label_det1.0'''

import ctypes
import os
import sys

class enlarge_label_det:
    def __init__(self,dict_path,import_HALCONdll=True):
        # 如果电脑装了halcon且lisence在有效期，则import_HALCONdll=False,
        # 否则设置为True，导入dll，该操作开启默认从SegJJC的dll中获取
        self.dict_path=dict_path
        self.import_HALCONdll=import_HALCONdll

    def enlarge_label_area(self,labels, areamins, enlarged_dict_path):
        # 初始化 HALCON 环境
        if self.import_HALCONdll:
            self.setup_halcon_environment()
        import halcon as ha

        print("开始扩大...")

        # 读取字典
        dict_to_enlarge = ha.read_dict(self.dict_path, [], [])
        labellist_to_enlarge = ha.as_python_dict(dict_to_enlarge)

        # 获取 class_names 列表
        class_names = labellist_to_enlarge['class_names']

        # 对每个标签进行处理
        for label, areamin in zip(labels, areamins):
            if label not in class_names:
                print(f"Label '{label}' not found in class names.")
                continue

            # 获取标签对应的 labelid
            labelid_to_enlarge = class_names.index(label)

            # 获取 samples 列表
            samples = labellist_to_enlarge['samples']

            # 遍历 samples，查找匹配的 bbox_label_id 并获取对应的矩形坐标
            for sample in samples:
                bbox_label_ids = sample['bbox_label_id']

                # 遍历 bbox_label_ids 中所有等于 labelid_to_enlarge 的元素
                for i, bbox_label_id in enumerate(bbox_label_ids):
                    if bbox_label_id == labelid_to_enlarge:
                        # 获取矩形框的坐标
                        y1 = sample['bbox_row1'][i]
                        x1 = sample['bbox_col1'][i]
                        y2 = sample['bbox_row2'][i]
                        x2 = sample['bbox_col2'][i]

                        # 计算矩形面积
                        area = (y2 - y1) * (x2 - x1)

                        # 如果面积小于最小值，扩展矩形
                        if area < areamin:
                            # 计算扩展比例
                            scale_factor = (areamin / area) ** 0.5  # 保持矩形比例

                            # 计算新的矩形坐标，扩展至最小面积
                            center_y = (y1 + y2) / 2
                            center_x = (x1 + x2) / 2
                            height = y2 - y1
                            width = x2 - x1

                            new_height = height * scale_factor
                            new_width = width * scale_factor

                            # 计算扩展后的新的 y1, x1, y2, x2
                            y1 = int(center_y - new_height / 2)
                            x1 = int(center_x - new_width / 2)
                            y2 = int(center_y + new_height / 2)
                            x2 = int(center_x + new_width / 2)

                            # 更新矩形的值
                            sample['bbox_row1'][i] = y1
                            sample['bbox_col1'][i] = x1
                            sample['bbox_row2'][i] = y2
                            sample['bbox_col2'][i] = x2

        # 返回更新后的 labellist_enlarged
        labellist_enlarged = labellist_to_enlarge
        Dict_enlarged = ha.from_python_dict(labellist_enlarged)
        ha.write_dict(Dict_enlarged, enlarged_dict_path, [], [])
        print(f"已对{labels}等标签进行面积比例扩大!\n扩大后最小面积为{areamins}!\n并成功导出到:{enlarged_dict_path}")

    def setup_halcon_environment(self):
        """
        设置 HALCON 运行环境，包括动态加载 DLL 和许可证检查。
        """
        # 获取当前脚本路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # DLL 文件夹路径（假设 DLL 文件夹在脚本的上一级目录）
        dll_path = os.path.join(os.path.dirname(current_dir), 'dll')

        # 动态添加 DLL 路径到 PATH 环境变量
        if dll_path not in os.environ['PATH']:
            os.environ['PATH'] = dll_path + os.pathsep + os.environ['PATH']

        # 手动加载 HALCON 主 DLL，确保动态库可用
        try:
            ctypes.windll.LoadLibrary(os.path.join(dll_path, "halcon.dll"))  # 替换为实际 DLL 文件名
            print("HALCON DLL 加载成功")
        except Exception as e:
            print(f"HALCON DLL 加载失败: {e}")
            sys.exit(1)  # 退出脚本，提示用户检查 DLL 配置


# ##使用##
# dict_path = r'E:\ALLvision\pycharmproject\pvk\infer\218\out\datajson\predictions.hdict'
# enlarged_dict_path = r'E:\ALLvision\pycharmproject\pvk\infer\218\out\datajson\predictions_enlarged.hdict'
# # labels = ['晕斑', '划痕']  # 输入多个标签
# # areamins = [100, 100]  # 对应每个标签的最小面积
# labels = ['晕斑']  # 输入多个标签
# areamins = [100]  # 对应每个标签的最小面积
# #实例化enlarge_label_det类
# enlargeit=enlarge_label_det(dict_path)
# # 调用 enlarge_label_area 函数
# enlargeit.enlarge_label_area(labels, areamins, enlarged_dict_path)

