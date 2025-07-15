#!/usr/bin/env python3
"""
文件传输功能自动测试脚本
"""

import os
import sys
import tempfile
import hashlib
from file_transfer_client import FileTransferClient

def create_test_file(filename, size_mb=1):
    """创建测试文件"""
    content = "Hello, this is a test file for file transfer!\n" * (size_mb * 1024 * 10)
    
    with open(filename, 'w') as f:
        f.write(content[:size_mb * 1024 * 1024])  # 确保文件大小
    
    return filename

def calculate_file_hash(filepath):
    """计算文件的MD5哈希值"""
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def test_file_transfer():
    """测试文件传输功能"""
    print("🧪 开始文件传输测试")
    print("=" * 40)
    
    # 连接到服务器
    client = FileTransferClient()
    if not client.connect():
        print("❌ 无法连接到服务器，请确保服务器正在运行")
        return False
    
    success_count = 0
    total_tests = 5
    
    try:
        # 测试1: 发送普通命令
        print("\n🧪 测试1: 发送hello命令")
        if client.send_message("hello"):
            print("✅ 测试1通过")
            success_count += 1
        else:
            print("❌ 测试1失败")
        
        # 测试2: 列出文件（可能为空）
        print("\n🧪 测试2: 列出服务器文件")
        if client.list_files():
            print("✅ 测试2通过")
            success_count += 1
        else:
            print("❌ 测试2失败")
        
        # 测试3: 创建并上传小文件
        print("\n🧪 测试3: 上传小文件")
        test_file1 = "test_small.txt"
        create_test_file(test_file1, 0.01)  # 10KB文件
        original_hash = calculate_file_hash(test_file1)
        
        if client.upload_file(test_file1):
            print("✅ 测试3通过 - 小文件上传成功")
            success_count += 1
        else:
            print("❌ 测试3失败 - 小文件上传失败")
        
        # 测试4: 上传稍大的文件
        print("\n🧪 测试4: 上传中等文件")
        test_file2 = "test_medium.txt"
        create_test_file(test_file2, 1)  # 1MB文件
        
        if client.upload_file(test_file2):
            print("✅ 测试4通过 - 中等文件上传成功")
            success_count += 1
        else:
            print("❌ 测试4失败 - 中等文件上传失败")
        
        # 测试5: 下载文件并验证
        print("\n🧪 测试5: 下载文件并验证完整性")
        download_dir = "./test_downloads"
        os.makedirs(download_dir, exist_ok=True)
        
        if client.download_file("test_small.txt", download_dir):
            downloaded_file = os.path.join(download_dir, "test_small.txt")
            if os.path.exists(downloaded_file):
                downloaded_hash = calculate_file_hash(downloaded_file)
                if original_hash == downloaded_hash:
                    print("✅ 测试5通过 - 文件下载并验证成功")
                    success_count += 1
                else:
                    print("❌ 测试5失败 - 文件哈希不匹配")
            else:
                print("❌ 测试5失败 - 下载的文件不存在")
        else:
            print("❌ 测试5失败 - 文件下载失败")
        
        # 再次列出文件查看结果
        print("\n📂 最终文件列表:")
        client.list_files()
        
    except Exception as e:
        print(f"❌ 测试过程中发生异常: {e}")
    finally:
        client.disconnect()
        
        # 清理测试文件
        for filename in ["test_small.txt", "test_medium.txt"]:
            if os.path.exists(filename):
                os.remove(filename)
        
        # 清理下载目录
        if os.path.exists("./test_downloads"):
            import shutil
            shutil.rmtree("./test_downloads")
    
    print(f"\n📊 测试结果: {success_count}/{total_tests} 通过")
    return success_count == total_tests

if __name__ == "__main__":
    if test_file_transfer():
        print("🎉 所有测试通过！")
        sys.exit(0)
    else:
        print("💥 部分测试失败")
        sys.exit(1)
