import os
import sys
import subprocess

def main():
    """执行所有测试用例"""
    # 获取当前目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 收集测试文件
    test_files = []
    for file in os.listdir(current_dir):
        if file.startswith("test_") and file.endswith(".py"):
            test_files.append(os.path.join(current_dir, file))
    test_files.sort()
    
    # 一个一个执行测试文件
    for test_file in test_files:
        print(f"\n执行测试文件: {os.path.basename(test_file)}")
        subprocess.run([sys.executable, test_file])

if __name__ == "__main__":
    main() 