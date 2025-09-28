#!/usr/bin/env python3
"""
Simple test for Interview Helper Memory Version
"""

import requests
import time

def test_backend():
    """Test if backend is running"""
    try:
        response = requests.get("http://localhost:8000/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running!")
            return True
        else:
            print(f"❌ Backend returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Backend is not running")
        return False
    except Exception as e:
        print(f"❌ Error testing backend: {e}")
        return False

def test_planner_api():
    """Test the planner API"""
    try:
        # Test creating a plan
        plan_data = {
            "job_title": "Software Engineer",
            "job_description": "We are looking for a software engineer...",
            "skills": ["Python", "React"],
            "experience_years": 3
        }
        
        response = requests.post(
            "http://localhost:8000/api/planner/create",
            json=plan_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Planner API working! Plan ID: {result['id']}")
            return True
        else:
            print(f"❌ Planner API failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing planner API: {e}")
        return False

def main():
    print("Testing Interview Helper Memory Version...")
    print("=" * 50)
    
    # Test backend
    if not test_backend():
        print("\nPlease start the backend first:")
        print("cd backend")
        print("python app_memory.py")
        return
    
    # Test planner API
    test_planner_api()
    
    print("\n✅ Testing completed!")

if __name__ == "__main__":
    main() 