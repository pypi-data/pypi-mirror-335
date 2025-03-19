# DDQ UI Framework

一个灵活的 UI 框架，支持多种后端实现。目前提供了基于 Tkinter 的实现。

## 特性

- 提供了一套统一的 UI 组件接口
- 支持多种后端实现（目前支持 Tkinter）
- 包含丰富的基础组件：按钮、文本框、下拉框等
- 提供配置管理功能，支持配置的保存和加载
- 支持组件的联动和状态管理

## 安装

```bash
pip install ddq_ui
```

## 快速开始

```python
import tkinter as tk
from ddq_ui.ddq_tkinter.ddq_widgets import Form, ButtonGroup

# 创建窗口
root = tk.Tk()
root.title("DDQ UI Demo")

# 创建表单
form = Form(root)
form.input("name", "姓名:", required=True)
form.select("gender", "性别:", options=["男", "女"])
form.pack()

# 创建按钮组
buttons = ButtonGroup(root)
buttons.add_new("提交", lambda: print(form.get_values()))
buttons.pack()

root.mainloop()
```

## 组件

### Form（表单）
- 支持多种输入控件：文本框、下拉框、单选框等
- 支持表单验证
- 支持表单联动

### ButtonGroup（按钮组）
- 统一的按钮样式
- 支持按钮的启用/禁用状态
- 支持按钮的布局配置

### ConfigurableTool（可配置工具）
- 支持配置的保存和加载
- 提供配置管理面板
- 支持配置的导入导出

## 示例

查看 `examples` 目录获取更多示例：
- `demo_form.py`: 表单组件示例
- `demo_button_group.py`: 按钮组示例
- `demo_config_manager.py`: 配置管理示例

## 许可证

MIT License 