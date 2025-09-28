# test_project_imports.py
import importlib
import sys
import os

def test_project_imports():
    """测试项目实际使用的导入"""
    
    print("🧪 测试项目实际导入...")
    print("=" * 50)
    
    # 基于你的项目代码的实际导入
    project_imports = [
        # 从 app.py
        ('fastapi', 'FastAPI'),
        ('uvicorn', 'uvicorn'),
        ('sqlalchemy', 'sqlalchemy'),
        ('pydantic', 'BaseModel'),
        ('openai', 'openai'),
        ('dotenv', 'load_dotenv'),
        ('websockets', 'websockets'),
        
        # 从 services/planner_analysis.py
        ('openai', 'openai'),
        ('json', 'json'),
        ('re', 're'),
        ('datetime', 'datetime'),
        
        # 从 rag/rag_pipeline.py
        ('numpy', 'np'),
        ('openai', 'OpenAI'),
        
        # 从 tts/voice_synthesis.py
        ('openai', 'openai'),
        ('os', 'os'),
        ('io', 'BytesIO'),
        
        # 从 models/
        ('sqlalchemy', 'Column'),
        ('sqlalchemy', 'String'),
        ('sqlalchemy', 'Integer'),
        ('sqlalchemy', 'DateTime'),
        ('uuid', 'uuid'),
        
        # 文件处理
        ('PyPDF2', 'PyPDF2'),
        ('aiofiles', 'aiofiles'),
        ('requests', 'requests'),
        
        # 数据处理
        ('numpy', 'numpy'),
        ('pandas', 'pandas'),
        ('sklearn', 'sklearn'),
        
        # AI/ML
        ('torch', 'torch'),
        ('transformers', 'transformers'),
        ('sentence_transformers', 'sentence_transformers'),
    ]
    
    success_count = 0
    total_count = len(project_imports)
    
    for package_name, import_name in project_imports:
        try:
            if package_name in ['json', 're', 'datetime', 'os', 'io', 'uuid']:
                # 标准库
                module = importlib.import_module(package_name)
                print(f"✅ {package_name:<20} | 标准库")
                success_count += 1
            else:
                # 第三方库
                module = importlib.import_module(package_name)
                version = getattr(module, '__version__', 'unknown')
                print(f"✅ {package_name:<20} | 版本: {version}")
                success_count += 1
        except ImportError as e:
            print(f"❌ {package_name:<20} | 错误: {e}")
        except Exception as e:
            print(f"⚠️ {package_name:<20} | 警告: {e}")
    
    print("=" * 50)
    print(f"📊 测试结果: {success_count}/{total_count}")
    
    if success_count == total_count:
        print("🎉 所有项目依赖都已正确安装!")
        return True
    else:
        print("❌ 部分依赖缺失")
        return False

if __name__ == "__main__":
    test_project_imports()