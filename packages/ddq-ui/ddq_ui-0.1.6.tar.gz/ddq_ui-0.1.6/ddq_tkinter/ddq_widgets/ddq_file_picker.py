import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import os
import subprocess
import platform
from typing import Optional, List, Tuple, Literal
from .ddq_input import Input

class FilePicker(ttk.Frame):
    def __init__(
        self,
        master,
        label: str = "",
        mode: str = "file",  # 'file', 'folder' 或 'all'
        filetypes: Optional[List[Tuple[str, str]]] = None,
        multiple_buttons: bool = False,
        placeholder: str = None,
        show_open_button: bool = True,  # 添加显示打开按钮的选项
        **kwargs
    ):
        super().__init__(master, **kwargs)
        self._mode = mode
        self.filetypes = filetypes or [("所有文件", "*.*")]
        self.show_open_button = show_open_button
        
        # 保存 placeholder
        self._placeholder = placeholder
        
        # 创建路径变量
        self.path_var = tk.StringVar()
        
        # 创建输入框
        self.entry = ttk.Entry(
            self,
            textvariable=self.path_var
        )
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 如果有占位符，设置初始状态
        if placeholder:
            self.path_var.set(placeholder)
            self.entry.configure(foreground="gray")
            
            # 绑定焦点事件
            self.entry.bind('<FocusIn>', self._on_focus_in)
            self.entry.bind('<FocusOut>', self._on_focus_out)
        else:
            # 无占位符时使用默认颜色
            self.entry.configure(foreground="black")
        
        # 创建按钮框架
        self.button_frame = ttk.Frame(self)
        self.button_frame.pack(side=tk.LEFT, padx=(5, 0))
        
        # 创建图标按钮
        self._create_icon_buttons()
        
        # 根据模式显示按钮
        self._update_buttons()
        
    def _create_icon_buttons(self):
        """创建带图标的按钮"""
        # 创建选择文件按钮
        self.file_button = ttk.Button(
            self.button_frame, 
            text="📄",
            width=3,
            command=self._select_file
        )
        
        # 创建选择目录按钮
        self.folder_button = ttk.Button(
            self.button_frame, 
            text="📁",
            width=3,
            command=self._select_folder
        )
        
        # 创建打开按钮
        self.open_button = ttk.Button(
            self.button_frame,
            text="🔍",
            width=3,
            command=self._open_path
        )
    
    @property
    def value(self) -> str:
        """获取值"""
        current = self.path_var.get()
        if current == self._placeholder:
            return ""
        return current
        
    @value.setter
    def value(self, val: str):
        """设置值"""
        if not val and self._placeholder:
            self.path_var.set(self._placeholder)
            self.entry.configure(foreground="gray")
        else:
            self.path_var.set(val)
            self.entry.configure(foreground="black")
        
    def _update_buttons(self):
        """根据模式更新按钮显示"""
        # 先移除所有按钮
        self.file_button.pack_forget()
        self.folder_button.pack_forget()
        self.open_button.pack_forget()
        
        if self._mode == "file":
            self.file_button.pack(side=tk.LEFT)
        elif self._mode == "folder":
            self.folder_button.pack(side=tk.LEFT)
        else:  # "all" 或 "both"
            self.file_button.pack(side=tk.LEFT)
            self.folder_button.pack(side=tk.LEFT, padx=(5, 0))
            
        # 如果启用了打开按钮，添加到最后
        if self.show_open_button:
            self.open_button.pack(side=tk.LEFT, padx=(5, 0))
        
    def set_mode(self, mode: str):
        """设置模式（文件/文件夹/全部）"""
        if mode not in ["file", "folder", "all", "both"]:
            raise ValueError("mode must be 'file', 'folder', 'all' or 'both'")
        self._mode = mode
        self._update_buttons()
    
    def _open_path(self):
        """打开文件或文件夹"""
        path = self.value
        if not path:
            return
            
        # 确保路径存在
        if not os.path.exists(path):
            return
            
        # 根据系统打开文件或文件夹
        try:
            if platform.system() == "Windows":
                os.startfile(path)
            elif platform.system() == "Darwin":  # macOS
                subprocess.call(["open", path])
            else:  # Linux
                subprocess.call(["xdg-open", path])
        except Exception as e:
            print(f"打开失败: {e}")
        
    def _select_file(self):
        """选择文件"""
        path = filedialog.askopenfilename(filetypes=self.filetypes)
        if path:
            self.path_var.set(path)
            self.entry.config(foreground='black')
            
    def _select_folder(self):
        """选择目录"""
        path = filedialog.askdirectory()
        if path:
            self.path_var.set(path)
            self.entry.config(foreground='black')
            
    def set_path(self, path: str):
        """设置路径"""
        if path:
            self.path_var.set(path)
            self.entry.config(foreground='black')
            
    def _on_focus_in(self, event):
        """获得焦点时的处理"""
        if self.path_var.get() == self._placeholder:
            self.path_var.set("")
            self.entry.configure(foreground="black")
            
    def _on_focus_out(self, event):
        """失去焦点时的处理"""
        if not self.path_var.get():
            self.path_var.set(self._placeholder)
            self.entry.configure(foreground="gray")
            