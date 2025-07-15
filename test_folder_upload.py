#!/usr/bin/env python3
"""
测试文件夹上传功能的脚本
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from file_transfer_client import FileTransferClient

def test_folder_upload():
    """测试文件夹上传功能"""
    print("🧪 测试文件夹上传功能")
    print("=" * 40)
    
    # 连接到本地服务器
    client = FileTransferClient('localhost', 8080)
    
    if not client.connect():
        print("❌ 无法连接到服务器，请确保服务器正在运行")
        return False
    
    try:
        # 测试上传test_folder
        test_folder = "./test_folder"
        
        if not os.path.exists(test_folder):
            print(f"❌ 测试文件夹不存在: {test_folder}")
            print("💡 请先运行主程序创建测试文件夹")
            return False
        
        print(f"📁 开始测试上传文件夹: {test_folder}")
        
        # 上传文件夹
        if client.upload_file(test_folder):
            print("✅ 文件夹上传测试成功")
        else:
            print("❌ 文件夹上传测试失败")
            return False
        
        # 列出服务器文件
        print("\n📂 查看上传后的文件列表:")
        client.list_files()
        
        return True
        
    finally:
        client.disconnect()

def main():
    print("🚀 文件夹上传测试脚本")
    print("=" * 35)
    
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help']:
        print("使用说明:")
        print("1. 确保服务器正在 localhost:8080 运行")
        print("2. 确保存在 ./test_folder 测试文件夹")
        print("3. 运行此脚本测试文件夹上传功能")
        return
    
    print("💡 确保服务器正在运行，并且存在 ./test_folder 文件夹")
    
    # 询问是否继续
    response = input("是否开始测试文件夹上传? (y/N): ").strip().lower()
    if response not in ['y', 'yes', '是']:
        print("测试取消")
        return
    
    # 执行测试
    if test_folder_upload():
        print("\n🎉 所有测试通过！")
    else:
        print("\n❌ 测试失败")

if __name__ == "__main__":
    main()
