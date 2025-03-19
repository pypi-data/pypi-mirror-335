import tkinter as tk
from tkinter import messagebox, simpledialog
import json

from ddq_ui.ddq_tkinter.ddq_widgets import Form, Card, SplitLayout, ButtonGroup, Text, FilePicker

class FormDemo:
    def __init__(self, root):
        self.root = root
        self.root.title("Form 组件全面功能测试")
        self.root.geometry("1200x800")
        
        # 创建左右布局容器
        self.split = SplitLayout(root)
        
        # 创建主表单
        self.form = Form(self.split.left, columns=1, use_card=True, title="表单组件分类演示")
        
        # 第一模块 - 输入框类
        self.input_section = self.form.section("输入框类组件", columns=2)
        
        # 文本输入框
        self.input_section.input(
            "text_input", 
            "文本输入:", 
            placeholder="请输入普通文本"
        )
        
        # 密码输入框
        self.input_section.password(
            "password_input", 
            "密码输入:", 
            placeholder="请输入密码"
        )
        
        # 多行文本框
        self.input_section.textarea(
            "multiline_input", 
            "多行文本框:", 
            height=3,
            placeholder="支持多行输入的文本框"
        )
        
        # 第二模块 - 选项类
        self.option_section = self.form.section("选项类组件", columns=2)
        
        # 单选框
        self.option_section.radio(
            "radio_option", 
            "单选框:", 
            options=["选项一", "选项二", "选项三"]
        )
        
        # 复选框
        self.option_section.checkbox(
            "checkbox_option", 
            "复选框:", 
            options=["选项A", "选项B", "选项C", "选项D"]
        )
        
        # 下拉框
        self.option_section.select(
            "select_option", 
            "下拉框:", 
            options=["下拉项1", "下拉项2", "下拉项3"],
            placeholder="请选择"
        )
        
        # 下拉输入框（组合框）
        self.option_section.combobox(
            "combobox_option", 
            "下拉输入框:", 
            options=["可输入项1", "可输入项2", "可输入项3"],
            placeholder="支持选择或手动输入"
        )
        
        # 第三模块 - 文件输入类
        self.file_section = self.form.section("文件输入类组件", columns=1)
        
        # 文件输入
        self.file_section.file_picker(
            "file_input", 
            "文件输入:", 
            mode="file", 
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")],
            placeholder="选择单个文件",
            show_open_button=True
        )
        
        # 文件夹输入
        self.file_section.file_picker(
            "folder_input", 
            "文件夹输入:", 
            mode="folder",
            placeholder="选择文件夹",
            show_open_button=True
        )
        
        # 文件/文件夹输入
        self.file_section.file_picker(
            "file_or_folder_input", 
            "文件/文件夹:", 
            mode="both",
            placeholder="选择文件或文件夹",
            show_open_button=True
        )
        
        # 右侧结果展示区
        self.result_card = Card(
            self.split.right, 
            title="组件数据实时展示",
            expand=True
        )
        
        # 结果展示文本
        self.result_text = Text(
            self.result_card.content,
            wraplength=500,
            justify=tk.LEFT
        )
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 功能按钮区
        self.button_group = ButtonGroup(
            self.split.right, 
            direction="horizontal"
        )
        
        # 添加功能按钮
        buttons = [
            ("重置", self._reset_form),
            ("保存", self._save_form),
            ("验证", self._validate_form)
        ]
        
        for text, command in buttons:
            self.button_group.add_new(text, command=command)
        
        # 设置初始默认值
        initial_defaults = {
            "text_input": "默认文本",
            "password_input": "123456",
            "multiline_input": "第一行\n第二行\n第三行",
            "radio_option": "选项二",
            "checkbox_option": ["选项A", "选项C"],
            "select_option": "下拉项2",
            "combobox_option": "可输入项1"
        }
        
        # 先设置变化回调
        self.form.on_change(self._update_result_display)
        
        # 再设置默认值
        self.form.set_defaults(initial_defaults)
        
        # 初始化显示
        self._update_result_display(initial_defaults)
        
    def _update_result_display(self, values):
        """实时更新结果展示"""
        try:
            # 格式化展示
            display_text = "📊 组件数据实时展示:\n\n"
            
            # 第一模块数据
            display_text += "📝 输入框类数据:\n"
            display_text += f"  • 文本输入: {values.get('text_input', '')}\n"
            display_text += f"  • 密码输入: {values.get('password_input', '')}\n"
            multiline_value = values.get('multiline_input', '').replace('\n', ' [换行] ')
            display_text += f"  • 多行文本: {multiline_value}\n\n"
            
            # 第二模块数据
            display_text += "🔘 选项类数据:\n"
            display_text += f"  • 单选框: {values.get('radio_option', '')}\n"
            display_text += f"  • 复选框: {values.get('checkbox_option', [])}\n"
            display_text += f"  • 下拉框: {values.get('select_option', '')}\n"
            display_text += f"  • 下拉输入框: {values.get('combobox_option', '')}\n\n"
            
            # 第三模块数据
            display_text += "📂 文件输入类数据:\n"
            display_text += f"  • 文件输入: {values.get('file_input', '')}\n"
            display_text += f"  • 文件夹输入: {values.get('folder_input', '')}\n"
            display_text += f"  • 文件/文件夹: {values.get('file_or_folder_input', '')}\n\n"
            
            # 添加额外信息
            modified = self.form.is_modified()
            modified_items = [k for k, v in modified.items() if v]
            
            display_text += f"✏️ 已修改组件: {modified_items}\n"
            
            # 完整数据(JSON格式)
            display_text += "\n🔍 完整数据(JSON):\n"
            display_text += json.dumps(values, ensure_ascii=False, indent=2)
            
            # 更新显示
            self.result_text.set_text(display_text)
            self.root.update_idletasks()
            
        except Exception as e:
            self.result_text.set_text(f"更新出错: {str(e)}")
    
    def _reset_form(self):
        """重置表单"""
        self.form.reset()
        messagebox.showinfo("重置", "表单已重置为初始状态")
    
    def _save_form(self):
        """保存表单"""
        values = self.form.get_values()
        
        # 格式化为JSON
        json_str = json.dumps(values, ensure_ascii=False, indent=2)
        
        # 显示保存成功对话框
        messagebox.showinfo("保存成功", f"表单数据已保存:\n\n{json_str}")
    
    def _validate_form(self):
        """表单验证"""
        values = self.form.get_values()
        errors = []
        
        # 验证文本输入
        if not values.get('text_input'):
            errors.append("文本输入不能为空")
        
        # 验证密码输入
        if len(values.get('password_input', '')) < 6:
            errors.append("密码长度必须大于6位")
        
        # 验证选项
        if not values.get('radio_option'):
            errors.append("请选择一个单选框选项")
        
        if not values.get('checkbox_option'):
            errors.append("请至少选择一个复选框选项")
        
        if errors:
            messagebox.showerror("验证错误", "\n".join(errors))
        else:
            messagebox.showinfo("验证通过", "所有验证通过！表单数据有效")

def main():
    root = tk.Tk()
    app = FormDemo(root)
    root.mainloop()

if __name__ == "__main__":
    main()