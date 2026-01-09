"""
Simple Test Script - Verify OpenRouter API Calls Work
Run this to test that your API key works and calls are happening
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_api_key_exists():
    """Test 1: Check if API key is configured"""
    print("\n" + "="*70)
    print("TEST 1: Checking API Key Configuration")
    print("="*70)
    
    api_key = os.getenv("OPENROUTER_API_KEY")
    
    if not api_key:
        print("❌ FAILED: OPENROUTER_API_KEY not found in .env file")
        print("\n💡 Solution:")
        print("1. Open your .env file")
        print("2. Add this line: OPENROUTER_API_KEY=sk-or-v1-your-key-here")
        print("3. Get your key from: https://openrouter.ai/keys")
        return False
    
    print(f"✅ PASSED: API key found")
    print(f"   Key starts with: {api_key[:15]}...")
    return True


def test_library_installed():
    """Test 2: Check if openai library is installed"""
    print("\n" + "="*70)
    print("TEST 2: Checking OpenAI Library")
    print("="*70)
    
    try:
        import openai
        print(f"✅ PASSED: openai library installed (version {openai.__version__})")
        return True
    except ImportError:
        print("❌ FAILED: openai library not installed")
        print("\n💡 Solution:")
        print("pip install openai")
        return False


def test_api_call():
    """Test 3: Make an actual API call"""
    print("\n" + "="*70)
    print("TEST 3: Making Test API Call")
    print("="*70)
    
    try:
        from openrouter_client import OpenRouterClient
        
        # Initialize client
        print("Initializing OpenRouter client...")
        client = OpenRouterClient(model="anthropic/claude-3.5-sonnet")
        
        # Make a simple API call
        print("Sending test prompt to API...")
        test_prompt = "Say 'Hello! API is working!' in exactly those words."
        
        response = client.generate(test_prompt, max_tokens=50)
        
        print(f"✅ PASSED: API call successful!")
        print(f"\n📨 Prompt sent: {test_prompt}")
        print(f"📬 Response received: {response[:100]}...")
        
        return True
        
    except FileNotFoundError:
        print("❌ FAILED: openrouter_client.py not found")
        print("\n💡 Solution:")
        print("Make sure openrouter_client.py is in your project root directory")
        return False
        
    except ValueError as e:
        if "OPENROUTER_API_KEY not found" in str(e):
            print("❌ FAILED: API key not configured")
            print("\n💡 Solution:")
            print("Add OPENROUTER_API_KEY to your .env file")
        else:
            print(f"❌ FAILED: {str(e)}")
        return False
        
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        print("\n💡 Possible causes:")
        print("1. API key is invalid")
        print("2. No credits on OpenRouter account")
        print("3. Internet connection issues")
        print("4. OpenRouter API is down")
        return False


def test_logging():
    """Test 4: Check if logging works"""
    print("\n" + "="*70)
    print("TEST 4: Testing Logging System")
    print("="*70)
    
    try:
        import sys
        sys.path.insert(0, 'src')
        from utils.logger import log_experiment, ActionType
        
        # Try to log something
        log_experiment(
            agent_name="TestAgent",
            model_used="anthropic/claude-3.5-sonnet",
            action=ActionType.ANALYSIS,
            details={
                "input_prompt": "test prompt",
                "output_response": "test response",
                "test": True
            },
            status="SUCCESS"
        )
        
        print("✅ PASSED: Logging system works")
        print("   Check logs/experiment_data.json")
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        print("\n💡 Make sure src/utils/logger.py exists")
        return False


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("🧪 OPENROUTER API INTEGRATION TEST")
    print("="*70)
    print("This will test if your OpenRouter setup is working correctly")
    
    results = []
    
    # Run all tests
    results.append(("API Key Configuration", test_api_key_exists()))
    results.append(("OpenAI Library", test_library_installed()))
    results.append(("API Call", test_api_call()))
    results.append(("Logging System", test_logging()))
    
    # Summary
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 SUCCESS! Everything is working!")
        print("\nYou can now:")
        print("1. Use openrouter_client.py in your agents")
        print("2. Run example_agent_with_openrouter.py")
        print("3. Start building your refactoring system")
    else:
        print("\n⚠️  Some tests failed. Fix the issues above and try again.")
    
    print("="*70 + "\n")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)