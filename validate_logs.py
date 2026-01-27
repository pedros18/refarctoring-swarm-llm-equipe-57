"""
Log Validator for Quality & Data Manager
Validates that logs/experiment_data.json meets all project requirements
Author: Quality & Data Manager
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Tuple

class LogValidator:
    """Validates the experiment_data.json file against project requirements"""
    
    REQUIRED_FIELDS = ['agent_name', 'model_used', 'action', 'details', 'status', 'timestamp']
    REQUIRED_DETAIL_FIELDS = ['input_prompt', 'output_response']
    VALID_ACTION_TYPES = ['ANALYSIS', 'GENERATION', 'DEBUG', 'FIX']
    VALID_STATUSES = ['SUCCESS', 'FAILURE', 'ERROR']
    
    def __init__(self, log_file_path: str = 'logs/experiment_data.json'):
        self.log_file_path = log_file_path
        self.errors = []
        self.warnings = []
        self.stats = {
            'total_entries': 0,
            'by_action': {},
            'by_agent': {},
            'by_status': {},
            'missing_prompts': 0,
            'missing_responses': 0
        }
    
    def validate(self) -> Tuple[bool, Dict]:
        """
        Main validation function
        Returns: (is_valid, report_dict)
        """
        print("🔍 Starting Log Validation...")
        print(f"📂 Checking file: {self.log_file_path}\n")
        
        # Check if file exists
        if not os.path.exists(self.log_file_path):
            self.errors.append(f"❌ CRITICAL: Log file does not exist at {self.log_file_path}")
            return False, self._generate_report()
        
        # Check if file is empty
        if os.path.getsize(self.log_file_path) == 0:
            self.errors.append("❌ CRITICAL: Log file is empty")
            return False, self._generate_report()
        
        # Try to load JSON
        try:
            with open(self.log_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            self.errors.append(f"❌ CRITICAL: Invalid JSON format - {str(e)}")
            return False, self._generate_report()
        
        # Validate it's a list
        if not isinstance(data, list):
            self.errors.append("❌ CRITICAL: Log file must contain a JSON array")
            return False, self._generate_report()
        
        # Validate each entry
        self.stats['total_entries'] = len(data)
        
        if len(data) == 0:
            self.warnings.append("⚠️  WARNING: No log entries found. System hasn't logged any actions yet.")
        
        for idx, entry in enumerate(data):
            self._validate_entry(entry, idx)
        
        # Generate report
        is_valid = len(self.errors) == 0
        report = self._generate_report()
        
        return is_valid, report
    
    def _validate_entry(self, entry: Dict, index: int):
        """Validate a single log entry"""
        
        # Check required top-level fields
        for field in self.REQUIRED_FIELDS:
            if field not in entry:
                self.errors.append(f"❌ Entry {index}: Missing required field '{field}'")
        
        # Validate action type
        if 'action' in entry:
            if entry['action'] not in self.VALID_ACTION_TYPES:
                self.errors.append(
                    f"❌ Entry {index}: Invalid action type '{entry['action']}'. "
                    f"Must be one of {self.VALID_ACTION_TYPES}"
                )
            else:
                # Update stats
                action = entry['action']
                self.stats['by_action'][action] = self.stats['by_action'].get(action, 0) + 1
        
        # Validate status
        if 'status' in entry:
            if entry['status'] not in self.VALID_STATUSES:
                self.warnings.append(
                    f"⚠️  Entry {index}: Unusual status '{entry['status']}'. "
                    f"Expected one of {self.VALID_STATUSES}"
                )
            # Update stats
            status = entry['status']
            self.stats['by_status'][status] = self.stats['by_status'].get(status, 0) + 1
        
        # Validate agent_name
        if 'agent_name' in entry:
            agent = entry['agent_name']
            self.stats['by_agent'][agent] = self.stats['by_agent'].get(agent, 0) + 1
        
        # Validate details field
        if 'details' not in entry:
            self.errors.append(f"❌ Entry {index}: Missing 'details' field")
        elif not isinstance(entry['details'], dict):
            self.errors.append(f"❌ Entry {index}: 'details' must be a dictionary")
        else:
            details = entry['details']
            
            # Check MANDATORY fields: input_prompt and output_response
            if 'input_prompt' not in details:
                self.errors.append(f"❌ Entry {index}: Missing MANDATORY field 'input_prompt' in details")
                self.stats['missing_prompts'] += 1
            elif not details['input_prompt'] or details['input_prompt'].strip() == '':
                self.warnings.append(f"⚠️  Entry {index}: 'input_prompt' is empty")
            
            if 'output_response' not in details:
                self.errors.append(f"❌ Entry {index}: Missing MANDATORY field 'output_response' in details")
                self.stats['missing_responses'] += 1
            elif not details['output_response'] or details['output_response'].strip() == '':
                self.warnings.append(f"⚠️  Entry {index}: 'output_response' is empty")
        
        # Validate timestamp format
        if 'timestamp' in entry:
            try:
                datetime.fromisoformat(entry['timestamp'].replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                self.warnings.append(f"⚠️  Entry {index}: Invalid timestamp format")
    
    def _generate_report(self) -> Dict:
        """Generate validation report"""
        return {
            'is_valid': len(self.errors) == 0,
            'errors': self.errors,
            'warnings': self.warnings,
            'statistics': self.stats
        }
    
    def print_report(self, report: Dict):
        """Print a formatted validation report"""
        print("\n" + "="*60)
        print("📊 VALIDATION REPORT")
        print("="*60)
        
        if report['is_valid']:
            print("✅ STATUS: VALID - All requirements met!")
        else:
            print("❌ STATUS: INVALID - Critical errors found!")
        
        print(f"\n📈 STATISTICS:")
        print(f"   Total Entries: {report['statistics']['total_entries']}")
        
        if report['statistics']['by_action']:
            print(f"\n   Actions Logged:")
            for action, count in report['statistics']['by_action'].items():
                print(f"      • {action}: {count}")
        
        if report['statistics']['by_agent']:
            print(f"\n   Agents Active:")
            for agent, count in report['statistics']['by_agent'].items():
                print(f"      • {agent}: {count} actions")
        
        if report['statistics']['by_status']:
            print(f"\n   Status Distribution:")
            for status, count in report['statistics']['by_status'].items():
                print(f"      • {status}: {count}")
        
        if report['errors']:
            print(f"\n❌ ERRORS ({len(report['errors'])}):")
            for error in report['errors']:
                print(f"   {error}")
        
        if report['warnings']:
            print(f"\n⚠️  WARNINGS ({len(report['warnings'])}):")
            for warning in report['warnings']:
                print(f"   {warning}")
        
        if not report['errors'] and not report['warnings']:
            print("\n✨ Perfect! No errors or warnings found.")
        
        print("\n" + "="*60)
        
        # Data Quality Score Estimation
        if report['statistics']['total_entries'] > 0:
            quality_score = self._calculate_quality_score(report)
            print(f"\n📊 Estimated Data Quality Score: {quality_score}/30 points")
            print("   (This is 30% of your final grade!)")
        
        print("="*60 + "\n")
    
    def _calculate_quality_score(self, report: Dict) -> float:
        """Estimate the data quality score based on validation results"""
        max_score = 30.0
        score = max_score
        
        # Critical errors (each -5 points)
        critical_errors = len([e for e in report['errors'] if 'CRITICAL' in e])
        score -= critical_errors * 5
        
        # Missing mandatory fields (each -2 points)
        mandatory_errors = len([e for e in report['errors'] if 'MANDATORY' in e])
        score -= mandatory_errors * 2
        
        # Other errors (each -1 point)
        other_errors = len(report['errors']) - critical_errors - mandatory_errors
        score -= other_errors * 1
        
        # Warnings (each -0.5 points)
        score -= len(report['warnings']) * 0.5
        
        # Bonus for good coverage (if multiple action types logged)
        if len(report['statistics']['by_action']) >= 3:
            score += 2
        
        return max(0, min(max_score, score))


def main():
    """Main execution function"""
    validator = LogValidator()
    is_valid, report = validator.validate()
    validator.print_report(report)
    
    if not is_valid:
        print("⚠️  Action Required: Fix the errors above before submission!")
        print("💡 Tip: Check that all agent calls include 'input_prompt' and 'output_response'\n")
        return 1
    else:
        print("✅ Your logs are ready for submission!")
        print("💡 Remember to force-add this file to git:")
        print("   git add -f logs/experiment_data.json\n")
        return 0


if __name__ == "__main__":
    exit(main())