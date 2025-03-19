import tkinter as tk
from configurable_tool_demo import DemoTool

def main():
    root = tk.Tk()
    root.title("ConfigurableTool Demo")
    root.geometry("800x600")
    
    app = DemoTool(root)
    app.pack(fill=tk.BOTH, expand=True)
    
    root.mainloop()

if __name__ == "__main__":
    main() 