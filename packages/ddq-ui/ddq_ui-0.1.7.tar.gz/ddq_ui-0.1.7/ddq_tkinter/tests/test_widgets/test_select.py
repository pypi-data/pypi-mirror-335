import pytest
import tkinter as tk
from tkinter import ttk
from ddq_ui.ddq_tkinter.ddq_widgets.ddq_select import Select

@pytest.fixture(scope="session")
def root_window():
    root = tk.Tk()
    yield root
    root.destroy()

def test_select_creation(root_window):
    """测试下拉框的基本创建"""
    options = ["选项1", "选项2", "选项3"]
    select = Select(root_window, options=options)
    
    assert isinstance(select, Select)
    assert isinstance(select, ttk.Combobox)  # 继承自 ttk.Combobox
    assert list(select['values']) == options  # 验证选项列表

def test_select_value(root_window):
    """测试下拉框的值操作"""
    options = ["选项1", "选项2", "选项3"]
    select = Select(root_window, options=options)
    
    # 测试默认值
    assert select.get() == options[0]  # 默认选中第一项
    
    # 测试设置值
    select.set("选项2")
    assert select.get() == "选项2"

def test_select_default_value(root_window):
    """测试默认值设置"""
    options = ["选项1", "选项2", "选项3"]
    select = Select(root_window, options=options, default="选项2")
    
    assert select.get() == "选项2"  # 验证默认值

def test_select_empty_options(root_window):
    """测试空选项列表"""
    select = Select(root_window, options=[])
    
    assert list(select['values']) == []
    assert select.get() == ""

if __name__ == "__main__":
    pytest.main(["-v", __file__]) 