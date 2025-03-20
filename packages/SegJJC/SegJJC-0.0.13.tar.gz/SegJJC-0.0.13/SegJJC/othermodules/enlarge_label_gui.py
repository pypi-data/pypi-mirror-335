import tkinter as tk
from tkinter import filedialog, messagebox
from enlarge_label import enlarge_label_det
import sys

class InitialDialog:
    def __init__(self, root):
        self.root = root
        self.root.title("是否已有 Halcon")
        self.root.geometry("300x150")  # 窗口大小

        self.import_HALCONdll = tk.BooleanVar(value=True)  # 默认选择为True（表示安装了Halcon）

        # 提示标签
        tk.Label(root, text="本地是否已经安装 Halcon?").pack(pady=20)

        # 创建选择按钮
        self.install_button = tk.Button(root, text="已安装", command=self.select_install)
        self.install_button.pack(pady=5)

        self.no_install_button = tk.Button(root, text="未安装", command=self.select_no_install)
        self.no_install_button.pack(pady=5)

        # 绑定窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.forceclose_dialog)

    def select_install(self):
        self.import_HALCONdll.set(False)  # 用户选择安装 Halcon
        self.close_dialog()  # 关闭当前窗口并进入主界面

    def select_no_install(self):
        self.import_HALCONdll.set(True)  # 用户选择不安装 Halcon
        self.close_dialog()  # 关闭当前窗口并进入主界面

    def close_dialog(self):
        """仅关闭选择窗口，不退出整个程序"""
        self.root.quit()  # 退出主循环，关闭当前界面
        self.root.destroy()  # 销毁界面
    def forceclose_dialog(self):
        """仅关闭选择窗口，不退出整个程序"""
        self.root.quit()  # 退出主循环，关闭当前界面
        self.root.destroy()  # 销毁界面
        # 如果你不希望窗口退出，可以调用 sys.exit(0) 来退出程序
        sys.exit(0)  # 完全退出程序

    def get_selection(self):
        return self.import_HALCONdll.get()  # 获取选择的值


# 自定义类用于重定向 print 输出到 Text 控件
class PrintRedirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, message):
        """将标准输出的消息插入到 Text 控件中"""
        if message != '\n':  # 防止插入空行
            self.text_widget.insert(tk.END, message)
            self.text_widget.see(tk.END)  # 滚动到最新的输出

    def flush(self):
        """flush 函数通常在重定向时需要，但这里我们不需要执行任何操作"""
        pass


# GUI 界面部分
class LabelEnlargerApp:
    def __init__(self, root, import_HALCONdll):
        self.root = root
        self.root.title("标签扩大工具")
        self.root.geometry("600x450")  # 设置初始大小
        self.root.resizable(True, True)  # 允许用户调整窗口大小

        self.model_mode = tk.StringVar()
        self.enlarge_mode = tk.StringVar()
        self.labels = tk.StringVar()
        self.areamins = tk.StringVar()
        self.dict_path = ""
        self.enlarged_dict_path = ""
        self.import_HALCONdll = import_HALCONdll  # 根据选择传入的值

        # 路径选择框 (路径编辑框在前)
        tk.Label(root, text="选择 dict 文件路径").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.dict_path_entry = tk.Entry(root, width=40)
        self.dict_path_entry.grid(row=2, column=1, padx=10, pady=10, sticky="ew")
        self.dict_button = tk.Button(root, text="选择文件", command=self.select_dict_path)
        self.dict_button.grid(row=2, column=2, padx=10, pady=10)

        tk.Label(root, text="选择 enlarged_dict 输出路径").grid(row=3, column=0, padx=10, pady=10, sticky="w")
        self.enlarged_dict_entry = tk.Entry(root, width=40)
        self.enlarged_dict_entry.grid(row=3, column=1, padx=10, pady=10, sticky="ew")
        self.enlarged_button = tk.Button(root, text="选择输出", command=self.select_enlarged_dict_path)
        self.enlarged_button.grid(row=3, column=2, padx=10, pady=10)

        # 模式选择框
        tk.Label(root, text="选择模型模式").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.model_mode.set("detect")
        tk.OptionMenu(root, self.model_mode, "detect").grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        tk.Label(root, text="选择扩大模式").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.enlarge_mode.set("area")
        tk.OptionMenu(root, self.enlarge_mode, "area").grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        # 标签输入框，设置淡颜色字体
        tk.Label(root, text="输入标签 (逗号分隔)").grid(row=4, column=0, padx=10, pady=10, sticky="w")
        label_entry = tk.Entry(root, textvariable=self.labels, fg="lightgray")  # 淡灰色字体
        label_entry.grid(row=4, column=1, padx=10, pady=10, sticky="ew")
        label_entry.insert(0, '晕斑,划痕')

        # 监听标签输入框内容变化
        label_entry.bind("<FocusIn>", lambda event: self.on_focus_in(event, label_entry, '例如: 晕斑,划痕'))
        label_entry.bind("<FocusOut>", lambda event: self.on_focus_out(event, label_entry, '例如: 晕斑,划痕'))

        # 最小面积输入框，设置淡颜色字体
        tk.Label(root, text="输入最小面积 (逗号分隔)").grid(row=5, column=0, padx=10, pady=10, sticky="w")
        area_entry = tk.Entry(root, textvariable=self.areamins, fg="lightgray")  # 淡灰色字体
        area_entry.grid(row=5, column=1, padx=10, pady=10, sticky="ew")
        area_entry.insert(0, '100,100')

        # 监听最小面积输入框内容变化
        area_entry.bind("<FocusIn>", lambda event: self.on_focus_in(event, area_entry, '例如: 100,100'))
        area_entry.bind("<FocusOut>", lambda event: self.on_focus_out(event, area_entry, '例如: 100,100'))

        # 执行按钮
        self.run_button = tk.Button(root, text="执行", command=self.run_enlargement)
        self.run_button.grid(row=6, column=0, columnspan=3, padx=10, pady=10)

        # 控制台输出区域，增大控制台的高度
        self.output_console = tk.Text(root, height=15, width=70)  # 增大控制台区域
        self.output_console.grid(row=7, column=0, columnspan=3, padx=10, pady=10)
        self.output_console.config(state=tk.NORMAL)  # 允许写入

        self.root.grid_rowconfigure(7, weight=1)

        # 将标准输出和错误输出重定向到控制台区域
        sys.stdout = PrintRedirector(self.output_console)
        sys.stderr = PrintRedirector(self.output_console)

    def select_dict_path(self):
        self.dict_path = filedialog.askopenfilename(filetypes=[("HALCON Dict Files", "*.hdict")])
        self.dict_path_entry.delete(0, tk.END)  # 清除旧路径
        self.dict_path_entry.insert(0, self.dict_path)

    def select_enlarged_dict_path(self):
        self.enlarged_dict_path = filedialog.asksaveasfilename(defaultextension=".hdict",
                                                               filetypes=[("HALCON Dict Files", "*.hdict")])
        self.enlarged_dict_entry.delete(0, tk.END)  # 清除旧路径
        self.enlarged_dict_entry.insert(0, self.enlarged_dict_path)

    def on_focus_in(self, event, entry_widget, default_text):
        if entry_widget.get() == default_text:
            entry_widget.delete(0, tk.END)
            entry_widget.config(fg="black")

    def on_focus_out(self, event, entry_widget, default_text):
        if entry_widget.get() == "":
            entry_widget.insert(0, default_text)
            entry_widget.config(fg="lightgray")

    def run_enlargement(self):
        missing_fields = []
        if not self.dict_path:
            missing_fields.append("dict 文件路径")
        if not self.enlarged_dict_path:
            missing_fields.append("enlarged_dict 输出路径")
        if not self.labels.get():
            missing_fields.append("标签")
        if not self.areamins.get():
            missing_fields.append("最小面积")

        if missing_fields:
            print(f"请确保以下字段已填写:\n" + "\n".join(missing_fields))
            return

        labels = self.labels.get().split(",")
        areamins = self.areamins.get().split(",")
        if len(labels) != len(areamins):
            print("标签和最小面积数量不匹配")
            return

        enlargeit = enlarge_label_det(self.dict_path, self.import_HALCONdll)
        enlargeit.enlarge_label_area(labels, [int(x) for x in areamins], self.enlarged_dict_path)

        print(f"标签扩展已完成！")
        print(f"标签: {labels}")
        print(f"最小面积: {areamins}")
        print(f"输出路径: {self.enlarged_dict_path}")
        print("操作成功！")


# 创建程序启动界面，选择是否安装 Halcon
def start_app():
    root = tk.Tk()
    dialog = InitialDialog(root)
    root.mainloop()  # 显示选择界面

    # 获取选择结果，进入主应用
    import_HALCONdll = dialog.get_selection()

    # 启动主应用窗口
    root = tk.Tk()
    app = LabelEnlargerApp(root, import_HALCONdll)
    root.mainloop()


if __name__ == "__main__":
    start_app()
