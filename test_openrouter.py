"""
OpenRouter Setup Test Script
Comprehensive testing to verify your OpenRouter integration is working

Run this after setup to verify everything is configured correctly
"""

import os
import sys
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def print_test(test_name, passed, message=""):
    """Print test result"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} - {test_name}")
    if message:
        print(f"        {message}")


def test_env_file():
    """Test 1: Check if .env file exists"""
    print_header("TEST 1: Environment File Check")
    
    if not os.path.exists('.env'):
        print_test("Environment file exists", False, ".env file not found")
        print("\n💡 Solution:")
        print("   1. Copy .env.example to .env")
        print("   2. Edit .env and add your API key")
        return False
    
    print_test("Environment file exists", True, ".env file found")
    return True


def test_api_key():
    """Test 2: Check if API key is configured"""
    print_header("TEST 2: API Key Configuration")
    
    api_key = os.getenv("OPENROUTER_API_KEY")
    
    if not api_key:
        print_test("API key configured", False, "OPENROUTER_API_KEY not found in .env")
        print("\n💡 Solution:")
        print("   1. Get API key from: https://openrouter.ai/keys")
        print("   2. Add to .env: OPENROUTER_API_KEY=sk-or-v1-your-key")
        return False
    
    if api_key == "sk-or-v1-your-key-here" or api_key == "your-key-here":
        print_test("API key configured", False, "API key is still the example value")
        print("\n💡 Solution:")
        print("   Replace the example key with your real key from OpenRouter")
        return False
    
    if not api_key.startswith("sk-or-v1-"):
        print_test("API key format", False, "API key doesn't look correct")
        print("\n💡 Note:")
        print("   OpenRouter API keys start with: sk-or-v1-")
        return False
    
    print_test("API key configured", True, f"Key: {api_key[:20]}...")
    return True


def test_openai_library():
    """Test 3: Check if openai library is installed"""
    print_header("TEST 3: Required Libraries")
    
    try:
        import openai
        print_test("openai library", True, f"Version: {openai.__version__}")
    except ImportError:
        print_test("openai library", False, "Not installed")
        print("\n💡 Solution:")
        print("   pip install openai")
        return False
    
    try:
        from dotenv import load_dotenv
        print_test("python-dotenv library", True)
    except ImportError:
        print_test("python-dotenv library", False, "Not installed")
        print("\n💡 Solution:")
        print("   pip install python-dotenv")
        return False
    
    return True


def test_client_file():
    """Test 4: Check if openrouter_client.py exists"""
    print_header("TEST 4: Client Files")
    
    if not os.path.exists('openrouter_client.py'):
        print_test("openrouter_client.py", False, "File not found")
        print("\n💡 Solution:")
        print("   Copy openrouter_client.py to your project root directory")
        return False
    
    print_test("openrouter_client.py", True, "File exists")
    
    # Check if we can import it
    try:
        from openrouter_client import OpenRouterClient
        print_test("openrouter_client import", True, "Can import successfully")
    except Exception as e:
        print_test("openrouter_client import", False, str(e))
        return False
    
    return True


def test_logger():
    """Test 5: Check if logger is available"""
    print_header("TEST 5: Logging System")
    
    # Check if src/utils/logger.py exists
    if not os.path.exists('src/utils/logger.py'):
        print_test("logger.py exists", False, "src/utils/logger.py not found")
        print("\n💡 Note:")
        print("   This should be in your project template")
        print("   Make sure you cloned the refactoring-swarm-template correctly")
        return False
    
    print_test("logger.py exists", True)
    
    # Try to import it
    try:
        sys.path.insert(0, 'src')
        from utils.logger import log_experiment, ActionType
        print_test("logger import", True, "Can import logger and ActionType")
    except Exception as e:
        print_test("logger import", False, str(e))
        return False
    
    # Check if logs directory exists
    if not os.path.exists('logs'):
        print_test("logs directory", False, "logs/ directory not found")
        print("\n💡 Creating logs directory...")
        os.makedirs('logs', exist_ok=True)
        print_test("logs directory created", True)
    else:
        print_test("logs directory", True)
    
    return True


def test_api_connection():
    """Test 6: Make actual API call"""
    print_header("TEST 6: API Connection Test")
    
    print("🔌 Attempting to connect to OpenRouter API...")
    print("   (This will use a small amount of credits)")
    
    try:
        from openrouter_client import OpenRouterClient
        
        # Initialize client
        client = OpenRouterClient(model="anthropic/claude-3-haiku")  # Use cheaper model for testing
        print_test("Client initialization", True)
        
        # Make a simple API call
        test_prompt = "Say exactly: 'Test successful!'"
        print(f"\n   Sending test prompt...")
        
        response = client.generate(test_prompt, max_tokens=20)
        
        print_test("API call successful", True)
        print(f"\n   📨 Prompt: {test_prompt}")
        print(f"   📬 Response: {response[:100]}")
        
        return True
        
    except ValueError as e:
        if "OPENROUTER_API_KEY not found" in str(e):
            print_test("API call", False, "API key not configured")
        else:
            print_test("API call", False, str(e))
        return False
        
    except Exception as e:
        error_str = str(e)
        print_test("API call", False)
        print(f"\n   Error: {error_str}")
        
        # Provide specific guidance based on error
        if "insufficient_quota" in error_str.lower() or "credits" in error_str.lower():
            print("\n💡 Solution:")
            print("   Your OpenRouter account needs credits")
            print("   1. Go to: https://openrouter.ai/credits")
            print("   2. Add $5-10 to start")
        elif "unauthorized" in error_str.lower() or "invalid" in error_str.lower():
            print("\n💡 Solution:")
            print("   Your API key may be invalid")
            print("   1. Check your key at: https://openrouter.ai/keys")
            print("   2. Make sure it's correctly copied to .env")
        elif "connection" in error_str.lower() or "network" in error_str.lower():
            print("\n💡 Solution:")
            print("   Check your internet connection")
            print("   Try again in a moment")
        else:
            print("\n💡 For help:")
            print("   Visit: https://openrouter.ai/docs")
        
        return False


def test_logging_integration():
    """Test 7: Test logging integration"""
    print_header("TEST 7: Logging Integration")
    
    try:
        sys.path.insert(0, 'src')
        from utils.logger import log_experiment, ActionType
        from openrouter_client import OpenRouterClient
        
        # Log a test entry
        log_experiment(
            agent_name="TestAgent",
            model_used="anthropic/claude-3-haiku",
            action=ActionType.ANALYSIS,
            details={
                "input_prompt": "Test prompt",
                "output_response": "Test response",
                "test_run": True,
            },
            status="SUCCESS"
        )
        
        print_test("Log entry created", True)
        
        # Verify log file was created/updated
        if os.path.exists('logs/experiment_data.json'):
            with open('logs/experiment_data.json', 'r') as f:
                data = json.load(f)
                print_test("Log file readable", True, f"{len(data)} entries total")
        else:
            print_test("Log file created", False, "logs/experiment_data.json not found")
            return False
        
        return True
        
    except Exception as e:
        print_test("Logging integration", False, str(e))
        return False


def test_example_files():
    """Test 8: Check if example files exist"""
    print_header("TEST 8: Example Files")
    
    files = {
        'example_agents.py': 'Example agents with logging',
        'generate_test_dataset.py': 'Test dataset generator',
        'validate_logs.py': 'Log validator',
    }
    
    all_exist = True
    for filename, description in files.items():
        exists = os.path.exists(filename)
        print_test(f"{filename}", exists, description if exists else "Not found")
        if not exists:
            all_exist = False
    
    if not all_exist:
        print("\n💡 Note:")
        print("   Some optional files are missing")
        print("   These are helpful but not required for OpenRouter to work")
    
    return True  # Don't fail the test suite for this


def run_all_tests():
    """Run all tests and provide summary"""
    print("\n" + "="*70)
    print("🧪 OPENROUTER SETUP TEST SUITE")
    print("="*70)
    print("Testing your OpenRouter integration...")
    
    tests = [
        ("Environment File", test_env_file),
        ("API Key Configuration", test_api_key),
        ("Required Libraries", test_openai_library),
        ("Client Files", test_client_file),
        ("Logging System", test_logger),
        ("API Connection", test_api_connection),
        ("Logging Integration", test_logging_integration),
        ("Example Files", test_example_files),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ Test crashed: {test_name}")
            print(f"   Error: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {test_name}")
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    # Final verdict
    print("\n" + "="*70)
    if passed == total:
        print("🎉 SUCCESS! Your OpenRouter setup is complete and working!")
        print("="*70)
        print("\n✅ You can now:")
        print("   1. Run example agents: python example_agents.py")
        print("   2. Build your own agents using openrouter_client.py")
        print("   3. Validate logs: python validate_logs.py")
        print("   4. Generate reports: python generate_quality_report.py")
    elif passed >= total - 2:
        print("✅ MOSTLY WORKING! Minor issues detected.")
        print("="*70)
        print("\n💡 You can probably proceed, but review the failures above")
    else:
        print("⚠️  SETUP INCOMPLETE - Fix the errors above")
        print("="*70)
        print("\n💡 Common issues:")
        print("   1. Missing API key in .env file")
        print("   2. Insufficient credits on OpenRouter")
        print("   3. Missing required files")
        print("\n📘 Review: SETUP_GUIDE.md for detailed instructions")
    
    print("="*70 + "\n")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)