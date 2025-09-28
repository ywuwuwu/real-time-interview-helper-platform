#!/usr/bin/env python3
"""
测试可用的OpenAI模型
"""

import openai
from config import config

def test_available_models():
    """测试可用的模型"""
    print("🔍 测试可用的OpenAI模型...")
    print(f"API Key: {'已配置' if config.OPENAI_API_KEY else '未配置'}")
    
    client = openai.OpenAI(api_key=config.OPENAI_API_KEY)
    
    try:
        # 获取可用模型列表
        models = client.models.list()
        print(f"✅ 成功获取模型列表，共 {len(models.data)} 个模型")
        
        # 显示可用的模型
        available_models = []
        for model in models.data:
            if model.id.startswith('gpt-') or model.id.startswith('o1-') or model.id.startswith('o4-'):
                available_models.append(model.id)
                print(f"  - {model.id}")
        
        print(f"\n📊 可用模型统计:")
        print(f"  - GPT模型: {len([m for m in available_models if m.startswith('gpt-')])}")
        print(f"  - O1模型: {len([m for m in available_models if m.startswith('o1-')])}")
        print(f"  - O4模型: {len([m for m in available_models if m.startswith('o4-')])}")
        
        return available_models
        
    except Exception as e:
        print(f"❌ 获取模型列表失败: {e}")
        return []

def test_model_completion(model_name):
    """测试特定模型的完成功能"""
    print(f"\n🧪 测试模型: {model_name}")
    
    client = openai.OpenAI(api_key=config.OPENAI_API_KEY)
    
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "user", "content": "Hello, can you respond with 'OK'?"}
            ],
            max_tokens=10
        )
        
        result = response.choices[0].message.content
        print(f"✅ 模型 {model_name} 测试成功: {result}")
        return True
        
    except Exception as e:
        print(f"❌ 模型 {model_name} 测试失败: {e}")
        return False

def main():
    """主函数"""
    print("🚀 开始测试OpenAI模型可用性...")
    print("=" * 50)
    
    # 测试可用模型
    available_models = test_available_models()
    
    if not available_models:
        print("❌ 没有找到可用的模型")
        return
    
    # 测试常用模型
    common_models = [
        "gpt-4o-mini",
        "gpt-4o",
        "gpt-4-turbo",
        "gpt-3.5-turbo",
        "o1-mini",
        "o1-preview"
    ]
    
    print("\n🧪 测试常用模型...")
    working_models = []
    
    for model in common_models:
        if model in available_models:
            if test_model_completion(model):
                working_models.append(model)
    
    print("\n" + "=" * 50)
    print("📊 测试结果总结:")
    
    if working_models:
        print(f"✅ 可用的模型: {', '.join(working_models)}")
        print(f"\n💡 建议使用: {working_models[0]}")
        
        # 更新配置文件
        print(f"\n🔧 请将 config.py 中的 LLM_MODEL 设置为: {working_models[0]}")
    else:
        print("❌ 没有找到可用的模型")
        print("💡 请检查API Key权限或联系OpenAI支持")

if __name__ == "__main__":
    main() 