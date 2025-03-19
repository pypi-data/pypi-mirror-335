import pytest
from ddq_ui.ddq_tkinter.ddq_widgets.ddq_button_group import ButtonGroup
from ddq_ui.ddq_tkinter.ddq_widgets.ddq_button import Button

@pytest.fixture
def button_group(root_window):
    """创建按钮组实例"""
    group = ButtonGroup(root_window)
    group.pack()
    root_window.update()
    return group

def test_button_group_initialization(button_group):
    """测试按钮组初始化"""
    assert isinstance(button_group, ButtonGroup)
    assert button_group.direction == "horizontal"  # 默认水平布局
    assert button_group.spacing == 5  # 默认间距
    assert button_group.align == "left"  # 默认左对齐
    assert len(button_group.buttons) == 0  # 初始无按钮

def test_button_group_add_button(button_group):
    """测试添加已有按钮"""
    button = Button(button_group.container, text="测试按钮")
    button_group.add(button)
    assert len(button_group.buttons) == 1
    assert button_group.buttons[0] == button

def test_button_group_add_new_button(button_group):
    """测试创建并添加新按钮"""
    clicked = []
    def on_click():
        clicked.append(True)
        
    button = button_group.add_new("测试按钮", command=on_click)
    assert len(button_group.buttons) == 1
    assert button.cget("text") == "测试按钮"
    
    button.invoke()
    assert len(clicked) == 1


if __name__ == "__main__":
    pytest.main(["-v", __file__])