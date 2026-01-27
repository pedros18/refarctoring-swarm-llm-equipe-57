#!/usr/bin/env python3
"""
Quality Manager Dashboard - All-in-One Tool
Provides a menu-driven interface for all Quality & Data Manager tasks
Author: Quality & Data Manager
"""

import os
import sys
import subprocess

class QualityManagerDashboard:
    """Interactive dashboard for Quality & Data Manager tools"""
    
    def __init__(self):
        self.tools = {
            '1': ('Validate Logs', 'python validate_logs.py'),
            '2': ('Generate Test Dataset', 'python generate_test_dataset.py'),
            '3': ('Monitor Telemetry (Real-time)', 'python monitor_telemetry.py'),
            '4': ('Generate Quality Report', 'python generate_quality_report.py'),
            '5': ('Quick Status Check', self.quick_status),
            '6': ('Run Full Quality Audit', self.full_audit),
        }
    
    def display_menu(self):
        """Display the main menu"""
        print("\n" + "="*70)
        print("🎯 QUALITY & DATA MANAGER DASHBOARD")
        print("="*70)
        print("\nAvailable Tools:")
        print()
        for key, (name, _) in self.tools.items():
            print(f"  [{key}] {name}")
        print("\n  [0] Exit")
        print("\n" + "="*70)
    
    def quick_status(self):
        """Quick status check of the logging system"""
        print("\n" + "="*70)
        print("🔍 QUICK STATUS CHECK")
        print("="*70)
        
        log_file = 'logs/experiment_data.json'
        
        # Check if log file exists
        if not os.path.exists(log_file):
            print("❌ Log file does not exist yet")
            print(f"   Expected location: {log_file}")
            print("   💡 Agents haven't started logging yet")
            return
        
        # Check file size
        file_size = os.path.getsize(log_file)
        if file_size == 0:
            print("⚠️  Log file exists but is empty")
            print("   💡 Agents need to call log_experiment()")
            return
        
        # Try to load and get basic stats
        try:
            import json
            with open(log_file, 'r') as f:
                data = json.load(f)
            
            print(f"✅ Log file is valid")
            print(f"   Total entries: {len(data)}")
            print(f"   File size: {file_size:,} bytes")
            
            if data:
                latest = data[-1]
                print(f"   Latest action: {latest.get('action', 'UNKNOWN')}")
                print(f"   Latest agent: {latest.get('agent_name', 'UNKNOWN')}")
                print(f"   Latest status: {latest.get('status', 'UNKNOWN')}")
            
            # Quick validation
            issues = 0
            for entry in data:
                details = entry.get('details', {})
                if 'input_prompt' not in details:
                    issues += 1
                if 'output_response' not in details:
                    issues += 1
            
            if issues > 0:
                print(f"\n⚠️  Found {issues} entries missing mandatory fields")
                print("   Run 'Validate Logs' for details")
            else:
                print("\n✅ All entries have mandatory fields")
        
        except json.JSONDecodeError:
            print("❌ Log file contains invalid JSON")
            print("   💡 Fix JSON syntax errors")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        print("="*70)
    
    def full_audit(self):
        """Run a complete quality audit"""
        print("\n" + "="*70)
        print("🔍 RUNNING FULL QUALITY AUDIT")
        print("="*70)
        print()
        
        print("Step 1/3: Validating logs...")
        os.system('python validate_logs.py')
        
        input("\nPress Enter to continue to quality report...")
        
        print("\nStep 2/3: Generating quality report...")
        os.system('python generate_quality_report.py')
        
        input("\nPress Enter to continue to recommendations...")
        
        print("\nStep 3/3: Final Recommendations")
        print("="*70)
        self._show_recommendations()
        
        print("\n✅ Full audit complete!")
        print("="*70)
    
    def _show_recommendations(self):
        """Show final recommendations"""
        recommendations = [
            "Review validation errors and fix critical issues",
            "Ensure test dataset covers all edge cases",
            "Monitor logs during next team test session",
            "Generate final report before submission",
            "Remember to force-add logs to git: git add -f logs/experiment_data.json"
        ]
        
        print("\n💡 Recommended Next Steps:")
        for i, rec in enumerate(recommendations, 1):
            print(f"   {i}. {rec}")
    
    def run_tool(self, choice):
        """Run the selected tool"""
        if choice == '0':
            print("\n👋 Goodbye!\n")
            return False
        
        if choice not in self.tools:
            print("\n❌ Invalid choice. Please try again.")
            return True
        
        name, command = self.tools[choice]
        
        if callable(command):
            # It's a Python function
            command()
        else:
            # It's a shell command
            print(f"\n🚀 Running: {name}")
            print("─" * 70)
            os.system(command)
        
        input("\nPress Enter to continue...")
        return True
    
    def run(self):
        """Main loop"""
        print("\n👋 Welcome to the Quality & Data Manager Dashboard!")
        print("This tool helps you manage all your responsibilities.")
        
        while True:
            self.display_menu()
            choice = input("\nSelect an option: ").strip()
            
            if not self.run_tool(choice):
                break


def main():
    """Main execution"""
    # Check if we're in the right directory
    if not os.path.exists('logs'):
        print("\n⚠️  WARNING: 'logs' directory not found!")
        print("Are you in the project root directory?")
        response = input("Continue anyway? (y/n): ").strip().lower()
        if response != 'y':
            print("Exiting...")
            return
    
    dashboard = QualityManagerDashboard()
    dashboard.run()


if __name__ == "__main__":
    main()