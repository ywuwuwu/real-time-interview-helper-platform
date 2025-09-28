#!/usr/bin/env python3
"""
安装AI功能所需的依赖包
"""

import subprocess
import sys

def install_package(package):
    """安装单个包"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ 成功安装 {package}")
        return True
    except subprocess.CalledProcessError:
        print(f"❌ 安装 {package} 失败")
        return False

def main():
    """主安装函数"""
    print("🚀 开始安装AI功能依赖包...")
    print("=" * 50)
    
    # 需要安装的包
    packages = [
        "PyPDF2==3.0.1",
        "python-docx==1.1.0", 
        "Pillow==10.4.0",
        "openai==1.97.0"
    ]
    
    success_count = 0
    for package in packages:
        if install_package(package):
            success_count += 1
    
    print("\n" + "=" * 50)
    print(f"📊 安装结果: {success_count}/{len(packages)} 个包安装成功")
    
    if success_count == len(packages):
        print("🎉 所有依赖安装成功！可以开始使用AI功能了！")
        print("\n💡 下一步:")
        print("1. 确保.env文件中有OPENAI_API_KEY")
        print("2. 运行 python test_real_ai.py 测试AI功能")
        print("3. 启动服务: python app_memory.py")
    else:
        print("⚠️  部分依赖安装失败，请检查网络连接或手动安装")

if __name__ == "__main__":
    main() 