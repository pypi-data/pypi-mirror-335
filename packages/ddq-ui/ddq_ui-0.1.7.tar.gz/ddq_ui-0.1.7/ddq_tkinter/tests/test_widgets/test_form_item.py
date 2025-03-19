import pytest
from ddq_ui.ddq_tkinter.ddq_widgets.ddq_form_item import FormItem

@pytest.fixture(scope="session")
def test_form_item_basic(root_window):
    """测试基本的表单项创建"""
    item = FormItem(root_window, "测试标签")
    assert isinstance(item, FormItem)
    assert item.label.cget("text") == "测试标签"
    assert item.widget is None

def test_form_item_input(root_window):
    """测试输入框表单项"""
    item = FormItem.input(root_window, "用户名", placeholder="请输入用户名")
    assert item.label.cget("text") == "用户名"
    assert hasattr(item, "var")
    
    # 测试值的设置和获取
    item.value = "test_user"
    assert item.value == "test_user"

# def test_form_item_select(root_window):
#     """测试下拉选择框"""
#     options = ["选项1", "选项2", "选项3"]
#     item = FormItem.select(root_window, "选择", options=options)
#     assert item.label.cget("text") == "选择"
#     assert list(item.widget["values"]) == options


def test_form_item_radio(root_window):
    """测试单选框组"""
    options = ["选项1", "选项2", "选项3"]
    item = FormItem.radio(root_window, "单选", options=options)
    assert item.label.cget("text") == "单选"
    
    # 测试值的设置和获取
    item.value = "选项2"
    assert item.value == "选项2"

def test_form_item_visibility(root_window):
    """测试表单项的显示和隐藏"""
    item = FormItem.input(root_window, "测试")
    assert item.visible is True
    
    item.hide()
    assert item.visible is False
    
    item.show()
    assert item.visible is True

def test_form_item_state(root_window):
    """测试表单项状态设置"""
    item = FormItem.input(root_window, "测试")
    
    item.set_state("disabled")
    assert str(item.widget.cget("state")) == "disabled"
    
    item.set_state("normal")
    assert str(item.widget.cget("state")) == "normal"

if __name__ == "__main__":
    pytest.main(["-v", __file__]) 