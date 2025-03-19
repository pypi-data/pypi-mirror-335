import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional

class Textarea(ttk.Frame):
    """自适应文本域组件
    
    特性：
    1. 自动适应父容器大小
    2. 内置滚动条
    3. 支持只读/禁用状态
    4. 支持自动换行
    5. 支持最大行数限制
    6. 支持数据实时更新
    7. 支持扩展编辑功能
    """
    
    def __init__(
        self,
        master,
        height: int = 10,           
        max_lines: int = 1000,      
        wrap: str = tk.WORD,        
        readonly: bool = False,
        placeholder: str = None,     # 添加 placeholder 参数
        on_change: Optional[Callable] = None,  # 添加变化回调
        update_mode: str = "realtime",  # 实时更新模式："realtime" 或 "focusout"
        enable_expand: bool = True,  # 是否启用扩展编辑功能
        expand_dialog_title: str = "扩展编辑",  # 扩展对话框标题
        **kwargs
    ):
        super().__init__(master)
        
        # 保存 placeholder
        self._placeholder = placeholder
        self._on_change = on_change
        self._update_mode = update_mode
        self._enable_expand = enable_expand
        self._expand_dialog_title = expand_dialog_title
        
        # 创建一个包含文本框和可能的扩展按钮的容器
        self.content_frame = ttk.Frame(self)
        self.content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 创建文本框和滚动条
        self.text = tk.Text(
            self.content_frame,
            height=height,
            wrap=wrap,
            **kwargs
        )
        self.scrollbar = ttk.Scrollbar(
            self,
            orient="vertical",
            command=self.text.yview
        )
        
        # 关联文本框和滚动条
        self.text.configure(yscrollcommand=self.scrollbar.set)
        
        # 如果启用了扩展功能，添加扩展按钮
        if enable_expand:
            self.expand_button = ttk.Button(
                self.content_frame, 
                text="⤢",  # 使用一个扩展符号
                width=2,
                command=self._show_expand_dialog
            )
            self.expand_button.place(relx=1.0, rely=0.0, anchor="ne")
        
        # 布局
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 初始化 placeholder
        if placeholder:
            self.text.insert('1.0', placeholder)
            self.text.configure(foreground='gray')
            
            # 绑定焦点事件
            self.text.bind('<FocusIn>', self._on_focus_in)
            self.text.bind('<FocusOut>', self._on_focus_out)
        
        # 绑定数据更新事件
        self._setup_update_events()
        
        # 保存配置
        self.max_lines = max_lines
        self._readonly = readonly
        
        # 设置初始状态
        if readonly:
            self.set_readonly(True)
    
    def _setup_update_events(self):
        """设置数据更新事件"""
        if self._update_mode == "realtime":
            # 绑定键盘事件，实时更新
            self.text.bind('<KeyRelease>', self._on_text_changed)
        
        # 无论如何都绑定失去焦点事件
        self.text.bind('<FocusOut>', self._on_focus_out)
    
    def _show_expand_dialog(self):
        """显示扩展编辑对话框"""
        # 创建对话框
        dialog = tk.Toplevel(self)
        dialog.title(self._expand_dialog_title)
        dialog.geometry("600x400")  # 更大的尺寸
        dialog.minsize(400, 300)
        dialog.grab_set()  # 模态对话框
        
        # 创建一个更大的文本域
        expanded_textarea = Textarea(
            dialog,
            height=20,
            wrap=self.text.cget("wrap"),
            readonly=self._readonly,
            on_change=None,  # 这里我们不需要在编辑时触发原始组件的回调
            update_mode="focusout",
            enable_expand=False  # 避免递归的扩展按钮
        )
        expanded_textarea.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 5))
        
        # 设置当前文本内容
        current_content = self.value
        expanded_textarea.value = "" if current_content == self._placeholder else current_content
        
        # 按钮框架
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # 保存和取消按钮
        save_button = ttk.Button(
            button_frame, 
            text="保存", 
            command=lambda: self._save_expanded_content(expanded_textarea.value, dialog)
        )
        save_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        cancel_button = ttk.Button(
            button_frame, 
            text="取消", 
            command=dialog.destroy
        )
        cancel_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        # 使对话框居中
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    
    def _save_expanded_content(self, content, dialog):
        """保存扩展编辑的内容并关闭对话框"""
        self.value = content
        
        # 如果有变化回调，触发它
        if self._on_change:
            self._on_change(content)
            
        # 关闭对话框
        dialog.destroy()
        
    def _on_text_changed(self, event):
        """文本变化时的回调"""
        # 如果当前内容是 placeholder，不触发回调
        if self.text.get('1.0', 'end-1c') == self._placeholder:
            return
            
        # 调用变化回调
        if self._on_change:
            self._on_change(self.value)
            
    def _on_focus_in(self, event):
        """获得焦点时的处理"""
        if self.text.get('1.0', 'end-1c') == self._placeholder:
            self.text.delete('1.0', 'end')
            self.text.configure(foreground='black')
            
    def _on_focus_out(self, event):
        """失去焦点时的处理"""
        # 处理 placeholder
        if not self.text.get('1.0', 'end-1c').strip():
            self.text.delete('1.0', 'end')
            self.text.insert('1.0', self._placeholder)
            self.text.configure(foreground='gray')
        
        # 如果是失去焦点更新模式，调用回调
        if self._update_mode == "focusout" and self._on_change:
            current_text = self.text.get('1.0', 'end-1c')
            if current_text != self._placeholder:
                self._on_change(current_text)
            
    def get_text(self) -> str:
        """获取文本内容"""
        return self.text.get("1.0", "end-1c")
        
    def set_text(self, content: str):
        """设置文本内容"""
        # 暂时启用文本框以便设置内容
        current_state = self.text.cget('state')
        self.text.configure(state='normal')
        
        # 设置内容
        self.text.delete("1.0", tk.END)
        self.text.insert("1.0", content)
        self._check_max_lines()
        
        # 恢复原来的状态
        self.text.configure(state=current_state)
        
    def append_text(self, content: str):
        """追加文本内容"""
        self.text.insert(tk.END, content)
        self._check_max_lines()
        
    def clear(self):
        """清空文本内容"""
        self.text.delete("1.0", tk.END)
        
    def set_readonly(self, readonly: bool = True):
        """设置只读状态"""
        self._readonly = readonly
        state = 'disabled' if readonly else 'normal'
        self.text.configure(state=state)
        
    def set_disabled(self, disabled: bool = True):
        """设置禁用状态"""
        state = 'disabled' if disabled else 'normal'
        self.text.configure(state=state)
        
    def set_on_change(self, callback: Callable):
        """设置变化回调"""
        self._on_change = callback
        
    def set_update_mode(self, mode: str):
        """设置更新模式
        
        mode: "realtime" 或 "focusout"
        """
        if mode not in ["realtime", "focusout"]:
            raise ValueError("Update mode must be 'realtime' or 'focusout'")
            
        self._update_mode = mode
        
        # 重新设置事件
        self._setup_update_events()
        
    def _check_max_lines(self):
        """检查并限制最大行数"""
        if self.max_lines <= 0:
            return
            
        # 获取当前行数
        num_lines = int(self.text.index('end-1c').split('.')[0])
        
        # 如果超过最大行数，删除前面的行
        if num_lines > self.max_lines:
            # 删除前面一半的行数
            lines_to_delete = num_lines - self.max_lines
            self.text.delete("1.0", f"{lines_to_delete + 1}.0")
            
    @property
    def value(self) -> str:
        """获取值(用于表单)"""
        current = self.text.get('1.0', 'end-1c')
        # 如果是 placeholder，返回空值
        if current == self._placeholder:
            return ""
        return current
        
    @value.setter
    def value(self, content: str):
        """设置值(用于表单)"""
        # 暂时启用文本框以便设置内容
        current_state = self.text.cget('state')
        self.text.configure(state='normal')
        
        # 设置内容
        self.text.delete('1.0', 'end')
        if not content and self._placeholder:
            self.text.insert('1.0', self._placeholder)
            self.text.configure(foreground='gray')
        else:
            self.text.insert('1.0', content or "")
            self.text.configure(foreground='black')
        
        # 检查最大行数
        self._check_max_lines()
        
        # 恢复原来的状态
        self.text.configure(state=current_state)
        
    def set_expand_enabled(self, enabled: bool):
        """启用或禁用扩展功能"""
        if enabled == self._enable_expand:
            return
            
        self._enable_expand = enabled
        
        if enabled:
            # 添加扩展按钮
            self.expand_button = ttk.Button(
                self.content_frame, 
                text="⤢", 
                width=2,
                command=self._show_expand_dialog
            )
            self.expand_button.place(relx=1.0, rely=0.0, anchor="ne")
        else:
            # 移除扩展按钮
            if hasattr(self, 'expand_button'):
                self.expand_button.destroy()
                delattr(self, 'expand_button') 