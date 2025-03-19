import tkinter as tk
from tkinter import ttk
from typing import List, Optional

class Select(ttk.Combobox):
    """下拉选择框组件"""
    
    def __init__(
        self,
        master,
        options: List[str],
        default: Optional[str] = None,
        placeholder: Optional[str] = None,  # 添加 placeholder 参数
        **kwargs
    ):
        super().__init__(master, **kwargs)
        
        # 保存原始选项和占位符
        self._original_options = options.copy()
        self._placeholder = placeholder
        
        # 如果有占位符，添加到选项列表的首位
        if placeholder and placeholder not in options:
            display_options = [placeholder] + options
        else:
            display_options = options
            
        # 设置选项列表
        self['values'] = display_options
        self['state'] = 'readonly'  # 设置为只读模式
        
        # 创建变量并绑定
        self.var = tk.StringVar()
        self.configure(textvariable=self.var)
        
        # 设置默认值
        if default and default in options:
            self.var.set(default)
        elif placeholder:
            self.var.set(placeholder)
        elif options:
            self.var.set(options[0])
            
        # 禁用鼠标滚轮切换选项
        self.bind("<MouseWheel>", self._disable_mousewheel)
        self.bind("<Button-4>", self._disable_mousewheel)  # Linux
        self.bind("<Button-5>", self._disable_mousewheel)  # Linux
        
        # 选择选项后自动失去焦点
        self.bind("<<ComboboxSelected>>", self._on_select)
        
        # 绑定全局点击事件，点击空白处取消选中状态
        self._bind_unfocus_events()
            
    def _disable_mousewheel(self, event):
        """禁用鼠标滚轮事件"""
        return "break"
    
    def _on_select(self, event):
        """选择后自动失去焦点"""
        # 使用after延迟执行，确保选择完成后再失去焦点
        self.after(10, lambda: self.master.focus_set())
    
    def _bind_unfocus_events(self):
        """绑定点击空白处取消选中状态的事件"""
        # 获取顶层窗口
        toplevel = self.winfo_toplevel()
        
        # 点击事件处理函数
        def on_click(event):
            # 确保不是点击自己
            if event.widget != self and not str(event.widget).startswith(str(self)):
                # 取消焦点
                if self.focus_get() == self:
                    self.master.focus_set()
        
        # 绑定到顶层窗口
        toplevel.bind("<Button-1>", on_click, add="+")
            
    @property
    def value(self) -> str:
        """获取值(用于表单)"""
        current = self.var.get()
        # 如果是 placeholder，返回空值
        if current == self._placeholder:
            return ""
        return current
        
    @value.setter
    def value(self, new_value: str):
        """设置值(用于表单)"""
        if not new_value and self._placeholder:
            self.var.set(self._placeholder)
        elif new_value in self._original_options:
            self.var.set(new_value)
        elif self._original_options:
            self.var.set(self._original_options[0])