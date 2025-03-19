import pytest
import tkinter as tk
from unittest.mock import Mock

@pytest.fixture(scope="session")
def root_window():
    """创建一个全局的 root 窗口"""
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    
    # 保存原始的子窗口列表
    original_children = set(root.winfo_children())
    
    yield root
    
    # 只清理测试过程中创建的窗口
    for child in set(root.winfo_children()) - original_children:
        child.destroy()
    
    root.destroy()

@pytest.fixture(autouse=True)
def clean_test_widgets():
    """每个测试后清理，但只清理当前测试创建的窗口"""
    root = tk._default_root
    if root:
        before_test = set(root.winfo_children())
        yield
        after_test = set(root.winfo_children())
        # 只清理本次测试创建的窗口
        for widget in after_test - before_test:
            widget.destroy()
    else:
        yield

@pytest.fixture(autouse=True)
def mock_messagebox(monkeypatch):
    """自动模拟所有消息框"""
    mock = Mock()
    mock.showwarning = Mock(return_value='ok')
    mock.showerror = Mock(return_value='ok')
    mock.showinfo = Mock(return_value='ok')
    mock.askyesno = Mock(return_value=True)
    monkeypatch.setattr('tkinter.messagebox', mock)

@pytest.fixture(autouse=True)
def clean_environment():
    """每个测试前清理环境"""
    # 清理之前的状态
    yield
    # 清理测试后的状态
    import tkinter as tk
    if tk._default_root:
        for widget in tk._default_root.winfo_children():
            widget.destroy()