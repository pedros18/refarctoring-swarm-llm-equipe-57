"""
Telemetry Monitor for Quality & Data Manager
Real-time monitoring of logging activity during development
Author: Quality & Data Manager
"""

import json
import os
import time
from datetime import datetime
from typing import Dict, List

class TelemetryMonitor:
    """Monitor and analyze logging activity in real-time"""
    
    def __init__(self, log_file_path: str = 'logs/experiment_data.json'):
        self.log_file_path = log_file_path
        self.last_check_size = 0
        self.last_entry_count = 0
    
    def watch(self, interval: int = 5):
        """
        Watch the log file for changes and report statistics
        Args:
            interval: Check interval in seconds
        """
        print("="*60)
        print("📡 TELEMETRY MONITOR - Real-time Logging Watch")
        print("="*60)
        print(f"Monitoring: {self.log_file_path}")
        print(f"Check interval: {interval} seconds")
        print("Press Ctrl+C to stop\n")
        
        try:
            while True:
                self._check_and_report()
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n\n⏹️  Monitoring stopped.")
            self._final_report()
    
    def _check_and_report(self):
        """Check log file and report if changes detected"""
        if not os.path.exists(self.log_file_path):
            print(f"⏳ [{self._timestamp()}] Waiting for log file to be created...")
            return
        
        # Check file size
        current_size = os.path.getsize(self.log_file_path)
        
        if current_size == 0:
            print(f"⏳ [{self._timestamp()}] Log file exists but is empty...")
            return
        
        # Try to load and count entries
        try:
            with open(self.log_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            current_entry_count = len(data)
            
            # Detect changes
            if current_entry_count != self.last_entry_count:
                new_entries = current_entry_count - self.last_entry_count
                print(f"\n📊 [{self._timestamp()}] NEW ACTIVITY DETECTED")
                print(f"   New entries: +{new_entries}")
                print(f"   Total entries: {current_entry_count}")
                
                # Show latest entry details
                if data and new_entries > 0:
                    latest = data[-1]
                    print(f"   Latest action: {latest.get('action', 'UNKNOWN')}")
                    print(f"   Agent: {latest.get('agent_name', 'UNKNOWN')}")
                    print(f"   Status: {latest.get('status', 'UNKNOWN')}")
                
                self.last_entry_count = current_entry_count
                self.last_check_size = current_size
        
        except json.JSONDecodeError:
            print(f"⚠️  [{self._timestamp()}] Warning: Invalid JSON in log file")
        except Exception as e:
            print(f"❌ [{self._timestamp()}] Error reading log: {str(e)}")
    
    def _timestamp(self) -> str:
        """Get current timestamp"""
        return datetime.now().strftime("%H:%M:%S")
    
    def _final_report(self):
        """Generate final report when monitoring stops"""
        print("\n" + "="*60)
        print("📈 FINAL TELEMETRY REPORT")
        print("="*60)
        
        if not os.path.exists(self.log_file_path):
            print("❌ No log file found")
            return
        
        try:
            with open(self.log_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print(f"Total Entries Logged: {len(data)}")
            
            # Count by action type
            action_counts = {}
            agent_counts = {}
            status_counts = {}
            
            for entry in data:
                action = entry.get('action', 'UNKNOWN')
                agent = entry.get('agent_name', 'UNKNOWN')
                status = entry.get('status', 'UNKNOWN')
                
                action_counts[action] = action_counts.get(action, 0) + 1
                agent_counts[agent] = agent_counts.get(agent, 0) + 1
                status_counts[status] = status_counts.get(status, 0) + 1
            
            print("\nBy Action Type:")
            for action, count in sorted(action_counts.items()):
                print(f"  {action}: {count}")
            
            print("\nBy Agent:")
            for agent, count in sorted(agent_counts.items()):
                print(f"  {agent}: {count}")
            
            print("\nBy Status:")
            for status, count in sorted(status_counts.items()):
                print(f"  {status}: {count}")
        
        except Exception as e:
            print(f"❌ Error generating report: {str(e)}")
        
        print("="*60)
    
    def get_statistics(self) -> Dict:
        """Get current statistics from the log file"""
        if not os.path.exists(self.log_file_path):
            return {'error': 'Log file does not exist'}
        
        try:
            with open(self.log_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            stats = {
                'total_entries': len(data),
                'by_action': {},
                'by_agent': {},
                'by_status': {},
                'latest_timestamp': None
            }
            
            for entry in data:
                action = entry.get('action', 'UNKNOWN')
                agent = entry.get('agent_name', 'UNKNOWN')
                status = entry.get('status', 'UNKNOWN')
                
                stats['by_action'][action] = stats['by_action'].get(action, 0) + 1
                stats['by_agent'][agent] = stats['by_agent'].get(agent, 0) + 1
                stats['by_status'][status] = stats['by_status'].get(status, 0) + 1
                
                if 'timestamp' in entry:
                    stats['latest_timestamp'] = entry['timestamp']
            
            return stats
        
        except Exception as e:
            return {'error': str(e)}
    
    def check_coverage(self) -> Dict:
        """Check if all required action types are being logged"""
        required_actions = ['ANALYSIS', 'GENERATION', 'DEBUG', 'FIX']
        
        stats = self.get_statistics()
        
        if 'error' in stats:
            return stats
        
        coverage = {
            'total_actions': len(required_actions),
            'actions_covered': 0,
            'missing_actions': [],
            'coverage_percentage': 0
        }
        
        for action in required_actions:
            if action in stats['by_action']:
                coverage['actions_covered'] += 1
            else:
                coverage['missing_actions'].append(action)
        
        coverage['coverage_percentage'] = (coverage['actions_covered'] / coverage['total_actions']) * 100
        
        return coverage


def main():
    """Main execution function"""
    import sys
    
    monitor = TelemetryMonitor()
    
    # If an argument is provided, it's the monitoring interval
    interval = 5
    if len(sys.argv) > 1:
        try:
            interval = int(sys.argv[1])
        except ValueError:
            print("Invalid interval. Using default: 5 seconds")
    
    # Run the monitor
    monitor.watch(interval)


if __name__ == "__main__":
    main()