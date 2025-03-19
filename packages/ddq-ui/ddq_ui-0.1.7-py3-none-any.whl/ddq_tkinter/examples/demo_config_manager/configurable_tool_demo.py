import tkinter as tk
import os
from ddq_ui.ddq_tkinter.ddq_config_manager.configurable_tool import ConfigurableTool
from ddq_ui.ddq_tkinter.ddq_widgets.ddq_form import Form
from ddq_ui.ddq_tkinter.ddq_widgets.ddq_text import Text
from ddq_ui.ddq_tkinter.ddq_widgets.ddq_card import Card
from ddq_ui.ddq_tkinter.ddq_widgets.ddq_table import Table

class DemoTool(ConfigurableTool):
    def __init__(self, master):
        # 定义按钮配置
        buttons = [
            {
                'text': '提交',
                'handler': 'handle_submit',
                # 可以添加其他按钮属性，如 width, style 等
            },
            {
                'text': '查询记录',
                'handler': 'handle_query',
            }
        ]
        
        default_config = {
            "name": "张三",
            "age": "18",
            "password": "",
            "education": "本科",
            "gender": "男",
            "show_hobbies": "否",
            "hobbies": [False, False, False, False, False],
            "description": "这是一段个人描述...",
            "is_file": "是",        
            "file_type": "文件夹",
            "file_path": ""
        }
        
        config_dir = os.path.dirname(os.path.abspath(__file__))
        
        super().__init__(
            master=master,
            tool_name="Demo Tool",
            config_dir=config_dir,
            buttons=buttons,  # 传入按钮配置
            default_config=default_config,
            on_form_change=self.handle_form_change
        )
        
        # 在最上方添加状态卡片
        status_card = Card(self.right_container, title="状态信息")
        self.status_text = Text(
            status_card.content,
            text="准备就绪"
        )
        
        # 在 form 之后添加一个表格
        self.table = Table(
            self.right_container,  # 使用 right_container 作为父容器
            title="提交记录",
            columns=[
                {"id": "name", "text": "姓名"},
                {"id": "age", "text": "年龄"},
                {"id": "gender", "text": "性别"},
                {"id": "education", "text": "学历"}
            ],
            buttons=[
                {"text": "删除", "command": self.handle_delete}
            ]
        )
    
    def create_form(self, parent: tk.Widget) -> Form:
        """实现表单创建"""
        form = Form(parent)
        
        # 创建基本信息分区
        basic_section = form.section("基本信息")
        basic_section.input("name", "姓名:", required=True, placeholder="请输入姓名")
        basic_section.input("age", "年龄:", placeholder="请输入年龄")
        basic_section.password("password", "密码:", placeholder="请输入密码")
        basic_section.select(
            "education", 
            "学历:", 
            options=["高中", "大专", "本科", "硕士", "博士"]
        )
        basic_section.radio(
            "gender", 
            "性别:", 
            options=["男", "女"],
            default="男"
        )
        
        # 添加一个控制显隐的单选框
        basic_section.radio(
            "show_hobbies",
            "是否显示兴趣爱好:",
            options=["是", "否"],
            default="否"
        )
        
        # 保存为成员变量以便控制显隐
        self.hobbies_item = basic_section.checkbox(
            "hobbies", 
            "兴趣爱好:", 
            options=["阅读", "音乐", "运动", "游戏", "编程"]
        )
        
        basic_section.textarea(
            "description", 
            "个人描述:",
            height=3,
            placeholder="请输入个人描述..."
        )
        
        # 创建文件选择分区
        file_section = form.section("文件选择")
        file_section.radio(
            "is_file", 
            "是否需要文件:", 
            options=["是", "否"],
            default="是"
        )
        
        # 创建文件详情分区
        self.file_section = form.section("文件详情")
        self.file_section.hide()  # 默认隐藏
        
        self.file_section.radio(
            "file_type", 
            "文件类型:", 
            options=["文件", "文件夹", "全部"],
            default="文件",
        )
        
        self.file_picker = self.file_section.file_picker(
            "file_path", 
            "选择路径:",
            mode="file",
            placeholder="请选择文件路径..."
        )
        
        # 根据默认配置设置初始状态
        if self.default_config["show_hobbies"] == "否":
            self.hobbies_item.hide()
             
        return form
        
    def handle_form_change(self, values):
        """处理表单联动"""
        print("\nForm change event triggered")
        print(f"All form values: {values}")
        
        # 处理文件类型联动
        is_file = values.get("is_file")       
        print(f"is_file value: {is_file}")
        if is_file == "否":
            self.file_section.hide()
        else:
            self.file_section.show()
            
        # 处理兴趣爱好显隐
        show_hobbies = values.get("show_hobbies")
        print(f"show_hobbies raw value: {show_hobbies}")
        print(f"show_hobbies type: {type(show_hobbies)}")
        if show_hobbies == "是":
            print("Showing hobbies")
            self.hobbies_item.show()
        else:
            print("Hiding hobbies")
            self.hobbies_item.hide()
            
        # 处理文件选择器模式联动
        file_type = values.get("file_type")
        if file_type and hasattr(self.file_picker, 'set_mode'):
            if file_type == "文件夹":
                self.file_picker.set_mode("folder")
            elif file_type == "文件":
                self.file_picker.set_mode("file")                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       
            else:  # "全部"
                self.file_picker.set_mode("all")
        
    def handle_submit(self):
        """处理提交按钮点击"""
        values = self._form.get_values()
        print("提交表单数据:", values)
        
        # 更新状态文本
        self.status_text.value = "提交成功"
        
        # 将表单数据添加到表格
        self.table.insert_record([
            values.get("name", ""),
            values.get("age", ""),
            values.get("gender", ""),
            values.get("education", "")
        ])
        
    def handle_query(self):
        """处理查询记录按钮点击"""
        print("查询记录")
        
    def handle_delete(self):
        """处理删除按钮点击"""
        selection = self.table.tree.selection()
        if selection:
            for item in selection:
                self.table.tree.delete(item)
        
