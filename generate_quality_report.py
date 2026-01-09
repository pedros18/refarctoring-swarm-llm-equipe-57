"""
Quality Report Generator for Quality & Data Manager
Generates comprehensive quality reports for the Refactoring Swarm system
Author: Quality & Data Manager
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional

class QualityReportGenerator:
    """Generate quality reports from experiment data"""
    
    def __init__(self, log_file_path: str = 'logs/experiment_data.json'):
        self.log_file_path = log_file_path
        self.report_data = None
    
    def generate_report(self, output_file: Optional[str] = None) -> str:
        """
        Generate a comprehensive quality report
        Args:
            output_file: Optional path to save the report
        Returns:
            Report as string
        """
        if not os.path.exists(self.log_file_path):
            return "❌ Error: Log file does not exist"
        
        try:
            with open(self.log_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError:
            return "❌ Error: Invalid JSON in log file"
        
        self.report_data = self._analyze_data(data)
        report = self._format_report()
        
        # Save to file if requested
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"✅ Report saved to: {output_file}")
        
        return report
    
    def _analyze_data(self, data: List[Dict]) -> Dict:
        """Analyze the log data and extract metrics"""
        analysis = {
            'total_entries': len(data),
            'by_action': {},
            'by_agent': {},
            'by_status': {},
            'by_model': {},
            'success_rate': 0,
            'error_rate': 0,
            'average_prompt_length': 0,
            'average_response_length': 0,
            'missing_prompts': 0,
            'missing_responses': 0,
            'timestamp_range': {'first': None, 'last': None},
            'issues': []
        }
        
        total_prompt_length = 0
        total_response_length = 0
        prompt_count = 0
        response_count = 0
        
        for entry in data:
            # Count by action
            action = entry.get('action', 'UNKNOWN')
            analysis['by_action'][action] = analysis['by_action'].get(action, 0) + 1
            
            # Count by agent
            agent = entry.get('agent_name', 'UNKNOWN')
            analysis['by_agent'][agent] = analysis['by_agent'].get(agent, 0) + 1
            
            # Count by status
            status = entry.get('status', 'UNKNOWN')
            analysis['by_status'][status] = analysis['by_status'].get(status, 0) + 1
            
            # Count by model
            model = entry.get('model_used', 'UNKNOWN')
            analysis['by_model'][model] = analysis['by_model'].get(model, 0) + 1
            
            # Check for missing critical fields
            details = entry.get('details', {})
            if 'input_prompt' not in details or not details.get('input_prompt'):
                analysis['missing_prompts'] += 1
                analysis['issues'].append(f"Entry missing input_prompt: {entry.get('agent_name', 'UNKNOWN')}")
            else:
                total_prompt_length += len(str(details['input_prompt']))
                prompt_count += 1
            
            if 'output_response' not in details or not details.get('output_response'):
                analysis['missing_responses'] += 1
                analysis['issues'].append(f"Entry missing output_response: {entry.get('agent_name', 'UNKNOWN')}")
            else:
                total_response_length += len(str(details['output_response']))
                response_count += 1
            
            # Track timestamps
            if 'timestamp' in entry:
                ts = entry['timestamp']
                if analysis['timestamp_range']['first'] is None:
                    analysis['timestamp_range']['first'] = ts
                analysis['timestamp_range']['last'] = ts
        
        # Calculate rates
        if analysis['total_entries'] > 0:
            success_count = analysis['by_status'].get('SUCCESS', 0)
            error_count = analysis['by_status'].get('ERROR', 0) + analysis['by_status'].get('FAILURE', 0)
            
            analysis['success_rate'] = (success_count / analysis['total_entries']) * 100
            analysis['error_rate'] = (error_count / analysis['total_entries']) * 100
        
        # Calculate averages
        if prompt_count > 0:
            analysis['average_prompt_length'] = total_prompt_length / prompt_count
        if response_count > 0:
            analysis['average_response_length'] = total_response_length / response_count
        
        return analysis
    
    def _format_report(self) -> str:
        """Format the analysis into a readable report"""
        r = self.report_data
        
        report = f"""
{'='*70}
📊 REFACTORING SWARM - QUALITY REPORT
{'='*70}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Log File: {self.log_file_path}
{'='*70}

📈 SUMMARY STATISTICS
{'─'*70}
Total Logged Entries:          {r['total_entries']}
Success Rate:                  {r['success_rate']:.1f}%
Error Rate:                    {r['error_rate']:.1f}%
Average Prompt Length:         {r['average_prompt_length']:.0f} characters
Average Response Length:       {r['average_response_length']:.0f} characters

"""
        
        # Time range
        if r['timestamp_range']['first'] and r['timestamp_range']['last']:
            report += f"""Logging Period:
  First Entry:  {r['timestamp_range']['first']}
  Last Entry:   {r['timestamp_range']['last']}

"""
        
        # Action distribution
        report += f"""
🎯 ACTION TYPE DISTRIBUTION
{'─'*70}
"""
        for action, count in sorted(r['by_action'].items(), key=lambda x: x[1], reverse=True):
            percentage = (count / r['total_entries'] * 100) if r['total_entries'] > 0 else 0
            bar = '█' * int(percentage / 2)
            report += f"{action:15} {count:4} ({percentage:5.1f}%) {bar}\n"
        
        # Agent distribution
        report += f"""
🤖 AGENT ACTIVITY
{'─'*70}
"""
        for agent, count in sorted(r['by_agent'].items(), key=lambda x: x[1], reverse=True):
            percentage = (count / r['total_entries'] * 100) if r['total_entries'] > 0 else 0
            report += f"{agent:20} {count:4} actions ({percentage:5.1f}%)\n"
        
        # Status distribution
        report += f"""
✅ STATUS DISTRIBUTION
{'─'*70}
"""
        for status, count in sorted(r['by_status'].items(), key=lambda x: x[1], reverse=True):
            percentage = (count / r['total_entries'] * 100) if r['total_entries'] > 0 else 0
            emoji = '✅' if status == 'SUCCESS' else '❌' if status in ['ERROR', 'FAILURE'] else '⚠️'
            report += f"{emoji} {status:15} {count:4} ({percentage:5.1f}%)\n"
        
        # Model usage
        report += f"""
🧠 MODEL USAGE
{'─'*70}
"""
        for model, count in sorted(r['by_model'].items(), key=lambda x: x[1], reverse=True):
            percentage = (count / r['total_entries'] * 100) if r['total_entries'] > 0 else 0
            report += f"{model:30} {count:4} calls ({percentage:5.1f}%)\n"
        
        # Data quality issues
        report += f"""
{'='*70}
🔍 DATA QUALITY ASSESSMENT
{'='*70}
"""
        
        quality_score = self._calculate_quality_score(r)
        report += f"\n📊 Estimated Data Quality Score: {quality_score:.1f}/30 points\n"
        report += f"   (This represents 30% of your final grade)\n\n"
        
        if r['missing_prompts'] > 0 or r['missing_responses'] > 0:
            report += "⚠️  CRITICAL ISSUES FOUND:\n"
            if r['missing_prompts'] > 0:
                report += f"   • {r['missing_prompts']} entries missing input_prompt (MANDATORY)\n"
            if r['missing_responses'] > 0:
                report += f"   • {r['missing_responses']} entries missing output_response (MANDATORY)\n"
            report += "\n"
        else:
            report += "✅ All entries contain mandatory fields (input_prompt, output_response)\n\n"
        
        # Action coverage
        required_actions = {'ANALYSIS', 'GENERATION', 'DEBUG', 'FIX'}
        covered_actions = set(r['by_action'].keys())
        missing_actions = required_actions - covered_actions
        
        if missing_actions:
            report += f"⚠️  Missing Action Types: {', '.join(missing_actions)}\n"
            report += "   Your system should use all action types for complete coverage.\n\n"
        else:
            report += "✅ All required action types are being logged\n\n"
        
        # Recommendations
        report += f"""
{'='*70}
💡 RECOMMENDATIONS
{'='*70}
"""
        
        recommendations = self._generate_recommendations(r)
        for i, rec in enumerate(recommendations, 1):
            report += f"{i}. {rec}\n"
        
        report += f"\n{'='*70}\n"
        report += "📝 Note: Run 'python validate_logs.py' for detailed validation\n"
        report += f"{'='*70}\n"
        
        return report
    
    def _calculate_quality_score(self, r: Dict) -> float:
        """Calculate estimated data quality score"""
        max_score = 30.0
        score = max_score
        
        # Penalties
        score -= r['missing_prompts'] * 2
        score -= r['missing_responses'] * 2
        
        # Bonus for good coverage
        required_actions = {'ANALYSIS', 'GENERATION', 'DEBUG', 'FIX'}
        covered_actions = set(r['by_action'].keys())
        coverage_bonus = len(covered_actions & required_actions) * 1
        score += coverage_bonus
        
        # Bonus for volume
        if r['total_entries'] >= 20:
            score += 2
        elif r['total_entries'] >= 10:
            score += 1
        
        # Success rate bonus
        if r['success_rate'] >= 90:
            score += 2
        elif r['success_rate'] >= 75:
            score += 1
        
        return max(0, min(max_score, score))
    
    def _generate_recommendations(self, r: Dict) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        if r['missing_prompts'] > 0:
            recommendations.append(
                "Ensure all agents include 'input_prompt' in their log_experiment calls"
            )
        
        if r['missing_responses'] > 0:
            recommendations.append(
                "Ensure all agents include 'output_response' in their log_experiment calls"
            )
        
        required_actions = {'ANALYSIS', 'GENERATION', 'DEBUG', 'FIX'}
        covered_actions = set(r['by_action'].keys())
        missing_actions = required_actions - covered_actions
        
        if missing_actions:
            recommendations.append(
                f"Implement logging for: {', '.join(missing_actions)} actions"
            )
        
        if r['total_entries'] < 10:
            recommendations.append(
                "Run more test cases to generate comprehensive logs"
            )
        
        if r['error_rate'] > 25:
            recommendations.append(
                "High error rate detected. Review and fix agent implementations"
            )
        
        if not recommendations:
            recommendations.append("Excellent! Your logging system is working well.")
            recommendations.append("Continue testing with more diverse code samples.")
        
        return recommendations


def main():
    """Main execution function"""
    import sys
    
    output_file = None
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    
    print("="*70)
    print("📊 GENERATING QUALITY REPORT")
    print("="*70)
    print()
    
    generator = QualityReportGenerator()
    report = generator.generate_report(output_file)
    
    print(report)
    
    if output_file:
        print(f"\n✅ Report also saved to: {output_file}")


if __name__ == "__main__":
    main()