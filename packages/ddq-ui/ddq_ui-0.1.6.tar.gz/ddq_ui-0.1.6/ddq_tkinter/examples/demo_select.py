import tkinter as tk
from ddq_ui.ddq_tkinter.ddq_widgets.ddq_select import Select

class SelectDemo(tk.Frame):
    """Select组件演示"""
    
    def __init__(self, master):
        super().__init__(master)
        
        # 基本用法
        tk.Label(self, text="基本用法:").pack(anchor="w", pady=(10,5))
        select1 = Select(
            self, 
            options=["选项1", "选项2", "选项3"]
        )
        select1.pack(fill="x", padx=10)
        
        # 带默认值
        tk.Label(self, text="带默认值:").pack(anchor="w", pady=(10,5))
        select2 = Select(
            self,
            options=["选项A", "选项B", "选项C"],
            default="选项B"
        )
        select2.pack(fill="x", padx=10)
        
        # 值变化回调
        tk.Label(self, text="值变化回调:").pack(anchor="w", pady=(10,5))
        select3 = Select(
            self,
            options=["红色", "绿色", "蓝色"]
        )
        select3.pack(fill="x", padx=10)
        
        # 显示当前值的标签
        self.value_label = tk.Label(self, text="当前值: ")
        self.value_label.pack(pady=5)
        
        # 绑定值变化事件
        select3.bind('<<ComboboxSelected>>', lambda e: self.on_value_change(select3))
        
        # 操作按钮
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)
        
        tk.Button(
            btn_frame, 
            text="获取值",
            command=lambda: self.show_value(select3)
        ).pack(side="left", padx=5)
        
        tk.Button(
            btn_frame,
            text="设置值",
            command=lambda: select3.set("绿色")
        ).pack(side="left", padx=5)

    def on_value_change(self, select):
        """值变化回调"""
        self.value_label.config(text=f"当前值: {select.get()}")
        
    def show_value(self, select):
        """显示当前值"""
        tk.messagebox.showinfo("当前值", f"选中的值是: {select.get()}")

def main():
    root = tk.Tk()
    root.title("Select组件演示")
    root.geometry("300x400")
    
    demo = SelectDemo(root)
    demo.pack(fill="both", expand=True, padx=20, pady=20)
    
    root.mainloop()

if __name__ == "__main__":
    main() 