"""
Test Dataset Generator for Quality & Data Manager
Creates intentionally buggy Python files to test the Refactoring Swarm system
Author: Quality & Data Manager
"""

import os
from typing import List, Dict

class TestDatasetGenerator:
    """Generates buggy Python files for testing the refactoring system"""
    
    def __init__(self, output_dir: str = 'sandbox/test_dataset'):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.test_files = []
    
    def generate_all(self):
        """Generate all test files"""
        print("🔧 Generating Test Dataset...")
        print(f"📂 Output directory: {self.output_dir}\n")
        
        self.generate_missing_docstrings()
        self.generate_syntax_errors()
        self.generate_logic_bugs()
        self.generate_style_violations()
        self.generate_missing_tests()
        self.generate_complex_issues()
        
        self._create_readme()
        
        print(f"\n✅ Generated {len(self.test_files)} test files")
        print(f"📁 Location: {self.output_dir}/")
        print("\n💡 Use these files to test your refactoring system before submission!")
    
    def generate_missing_docstrings(self):
        """Test Case 1: Missing docstrings and poor documentation"""
        code = '''# Missing docstrings test file

def calculate_total(items):
    total = 0
    for item in items:
        total += item
    return total

def process_data(data):
    result = []
    for d in data:
        if d > 0:
            result.append(d * 2)
    return result

class DataProcessor:
    def __init__(self, name):
        self.name = name
        self.data = []
    
    def add_data(self, value):
        self.data.append(value)
    
    def get_average(self):
        if len(self.data) == 0:
            return 0
        return sum(self.data) / len(self.data)
'''
        self._save_file('test_missing_docstrings.py', code, {
            'description': 'Missing docstrings and documentation',
            'issues': ['No module docstring', 'No function docstrings', 'No class docstring'],
            'expected_fixes': ['Add comprehensive docstrings to all functions and classes']
        })
    
    def generate_syntax_errors(self):
        """Test Case 2: Syntax errors"""
        code = '''# Syntax errors test file

def calculate_sum(numbers)  # Missing colon
    total = 0
    for num in numbers:
        total += num
    return total

def process_items(items):
    result = []
    for item in items
        result.append(item * 2)  # Missing colon in for loop
    return result

def divide_numbers(a, b):
    if b == 0
        return None  # Missing colon
    return a / b
'''
        self._save_file('test_syntax_errors.py', code, {
            'description': 'Multiple syntax errors',
            'issues': ['Missing colons after function definition and control structures'],
            'expected_fixes': ['Add missing colons']
        })
    
    def generate_logic_bugs(self):
        """Test Case 3: Logic errors"""
        code = '''"""Module with logic bugs for testing"""

def find_maximum(numbers):
    """Find the maximum number in a list - BUT HAS A BUG"""
    if not numbers:
        return None
    max_num = 0  # BUG: Should initialize with first element or -infinity
    for num in numbers:
        if num > max_num:
            max_num = num
    return max_num

def calculate_average(numbers):
    """Calculate average - BUT HAS A BUG"""
    if not numbers:
        return 0
    total = sum(numbers)
    return total / (len(numbers) + 1)  # BUG: Should divide by len(numbers), not len(numbers) + 1

def is_even(number):
    """Check if number is even - BUT HAS A BUG"""
    return number % 2 == 1  # BUG: Should be == 0 for even numbers

def reverse_string(text):
    """Reverse a string - BUT HAS A BUG"""
    reversed_text = ""
    for i in range(len(text)):
        reversed_text += text[i]  # BUG: Should be text[-(i+1)] or use text[::-1]
    return reversed_text
'''
        self._save_file('test_logic_bugs.py', code, {
            'description': 'Logic errors in algorithms',
            'issues': [
                'find_maximum fails with negative numbers',
                'calculate_average divides by wrong value',
                'is_even returns wrong result',
                'reverse_string does not reverse'
            ],
            'expected_fixes': ['Fix the logic errors in each function']
        })
    
    def generate_style_violations(self):
        """Test Case 4: PEP 8 style violations"""
        code = '''# PEP 8 violations test file

def CalculateTotal( items,tax_rate ):  # Bad naming, spacing
    Total=0  # Bad variable naming
    for Item in items:  # Bad variable naming
        Total+=Item*(1+tax_rate)  # Missing spaces around operators
    return Total

class data_processor:  # Should be DataProcessor (PascalCase)
    def __init__(self,name,age):  # Missing spaces after commas
        self.Name=name  # Inconsistent naming
        self.AGE=age  # All caps should be for constants
    
    def ProcessData(self):  # Should be process_data (snake_case)
        pass

# Line too long violation below
def very_long_function_name_that_does_something(parameter1, parameter2, parameter3, parameter4, parameter5, parameter6, parameter7, parameter8):
    pass

x=1;y=2;z=3  # Multiple statements on one line

import os,sys,json  # Multiple imports on one line
'''
        self._save_file('test_style_violations.py', code, {
            'description': 'PEP 8 style violations',
            'issues': [
                'Inconsistent naming conventions',
                'Missing spaces around operators',
                'Lines too long',
                'Multiple statements on one line',
                'Multiple imports on one line'
            ],
            'expected_fixes': ['Fix all PEP 8 violations to improve Pylint score']
        })
    
    def generate_missing_tests(self):
        """Test Case 5: Code without any tests"""
        code = '''"""Calculator module - NO TESTS PROVIDED"""

class Calculator:
    """A simple calculator class"""
    
    def add(self, a, b):
        """Add two numbers"""
        return a + b
    
    def subtract(self, a, b):
        """Subtract b from a"""
        return a - b
    
    def multiply(self, a, b):
        """Multiply two numbers"""
        return a * b
    
    def divide(self, a, b):
        """Divide a by b"""
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b
    
    def power(self, base, exponent):
        """Calculate base raised to exponent"""
        return base ** exponent

def factorial(n):
    """Calculate factorial of n"""
    if n < 0:
        raise ValueError("Factorial not defined for negative numbers")
    if n == 0 or n == 1:
        return 1
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result
'''
        
        # Also create an empty test file
        test_code = '''"""Test file for calculator module - EMPTY"""

import unittest
from test_missing_tests import Calculator, factorial

# TODO: Add test cases here
'''
        
        self._save_file('test_missing_tests.py', code, {
            'description': 'Module without unit tests',
            'issues': ['No test coverage', 'Missing test file'],
            'expected_fixes': ['Generate comprehensive unit tests using pytest']
        })
        
        self._save_file('test_missing_tests_empty.py', test_code, {
            'description': 'Empty test file',
            'issues': ['No test cases implemented'],
            'expected_fixes': ['Generate actual test cases']
        })
    
    def generate_complex_issues(self):
        """Test Case 6: Multiple issues combined"""
        code = '''# Complex issues - combination of multiple problems

import sys,os  # Multiple imports on one line

def ProcessUserData(UserData):  # Bad naming, missing docstring
    Results=[]  # Bad naming
    for Data in UserData:  # Bad naming
        if Data>0  # Missing colon (syntax error)
            Results.append(Data*2)
    return Results

class user_manager:  # Should be UserManager
    def __init__(self,name):  # Missing space
        self.Name=name
        self.users=[]
    
    def AddUser(self,user):  # Should be add_user, missing space
        self.users.append(user)
    
    def GetUserCount(self):
        return len(self.users)+1  # Logic bug: should not add 1

def calculate(a,b,c):  # Missing docstring, spaces
    result=a+b*c  # Unclear logic, missing spaces
    return result

# Function with too many problems
def processComplexData(data_list, filter_value, transform_func, output_format, verbose_mode, debug_enabled):  # Too long, bad naming
    if not data_list  # Missing colon
        return None
    filtered=[]
    for item in data_list:
        if item>filter_value:  # Missing spaces
            filtered.append(transform_func(item))
    return filtered
'''
        self._save_file('test_complex_issues.py', code, {
            'description': 'Multiple types of issues combined',
            'issues': [
                'Syntax errors (missing colons)',
                'PEP 8 violations',
                'Logic bugs',
                'Missing docstrings',
                'Bad naming conventions'
            ],
            'expected_fixes': [
                'Fix all syntax errors',
                'Apply PEP 8 standards',
                'Fix logic bugs',
                'Add comprehensive documentation'
            ]
        })
    
    def _save_file(self, filename: str, code: str, metadata: Dict):
        """Save a test file and track its metadata"""
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(code)
        
        self.test_files.append({
            'filename': filename,
            'filepath': filepath,
            'metadata': metadata
        })
        
        print(f"✅ Created: {filename}")
        print(f"   Issues: {', '.join(metadata['issues'])}")
    
    def _create_readme(self):
        """Create a README file documenting all test cases"""
        readme_content = '''# Test Dataset Documentation

This directory contains intentionally buggy Python files for testing the Refactoring Swarm system.

## Test Files Overview

'''
        for i, test_file in enumerate(self.test_files, 1):
            readme_content += f"\n### {i}. {test_file['filename']}\n"
            readme_content += f"**Description:** {test_file['metadata']['description']}\n\n"
            readme_content += "**Known Issues:**\n"
            for issue in test_file['metadata']['issues']:
                readme_content += f"- {issue}\n"
            readme_content += "\n**Expected Fixes:**\n"
            for fix in test_file['metadata']['expected_fixes']:
                readme_content += f"- {fix}\n"
            readme_content += "\n---\n"
        
        readme_content += '''
## How to Use

1. Run your Refactoring Swarm on each test file:
   ```bash
   python main.py --target_dir ./sandbox/test_dataset
   ```

2. Verify that your system:
   - Detects all issues listed above
   - Successfully fixes the problems
   - Generates valid logs in `logs/experiment_data.json`
   - Passes unit tests (where applicable)

3. Use `validate_logs.py` to check log quality after each run

## Success Criteria

- ✅ All syntax errors fixed
- ✅ All logic bugs corrected
- ✅ Pylint score improved
- ✅ Comprehensive docstrings added
- ✅ Unit tests generated and passing
- ✅ All actions logged properly

---
Generated by Test Dataset Generator
Quality & Data Manager
'''
        
        readme_path = os.path.join(self.output_dir, 'README.md')
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        print(f"\n📄 Created: README.md (documentation)")


def main():
    """Main execution function"""
    print("="*60)
    print("🧪 TEST DATASET GENERATOR")
    print("="*60)
    print()
    
    generator = TestDatasetGenerator()
    generator.generate_all()
    
    print("\n" + "="*60)
    print("📋 NEXT STEPS:")
    print("="*60)
    print("1. Review the generated files in sandbox/test_dataset/")
    print("2. Test your Refactoring Swarm on these files")
    print("3. Run validate_logs.py after each test")
    print("4. Document any issues you find")
    print("\n💡 These test files will help you catch bugs before submission!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()