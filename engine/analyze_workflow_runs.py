#!/usr/bin/env python3
"""
Workflow Run Artifact Analyzer
Analyzes GitHub Actions workflow run data from JSON input files.
This script processes pre-fetched workflow data to generate detailed analysis reports.
"""

import sys
import json
from datetime import datetime
from typing import Dict, List, Any


class WorkflowAnalyzer:
    """Analyzes GitHub Actions workflow runs and generates detailed reports."""
    
    def __init__(self, owner: str, repo: str):
        self.owner = owner
        self.repo = repo
    
    def load_json_data(self, filepath: str) -> Any:
        """Load JSON data from a file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: File not found: {filepath}")
            return None
        except json.JSONDecodeError as e:
            print(f"Warning: Invalid JSON in {filepath}: {e}")
            return None
    
    def analyze_log_lines(self, logs: str, job_name: str) -> List[str]:
        """Analyze logs line by line and extract meaningful information."""
        lines = logs.split('\n')
        analysis = []
        
        analysis.append(f"\n#### Log Analysis for: {job_name}")
        analysis.append(f"Total lines: {len(lines)}\n")
        
        # Track important patterns
        errors = []
        warnings = []
        important_actions = []
        
        for i, line in enumerate(lines, 1):
            line_lower = line.lower()
            
            # Detect errors
            if 'error' in line_lower or 'failed' in line_lower:
                errors.append(f"Line {i}: {line.strip()}")
            
            # Detect warnings
            elif 'warning' in line_lower or 'warn' in line_lower:
                warnings.append(f"Line {i}: {line.strip()}")
            
            # Detect important actions (setup, install, build, test, deploy)
            elif any(keyword in line_lower for keyword in ['setup', 'install', 'build', 'test', 'deploy', 'push', 'commit']):
                if line.strip() and not line.strip().startswith('#'):
                    important_actions.append(f"Line {i}: {line.strip()}")
        
        if errors:
            analysis.append("**Errors Found:**")
            analysis.extend(errors[:10])  # Limit to first 10
            if len(errors) > 10:
                analysis.append(f"... and {len(errors) - 10} more errors")
            analysis.append("")
        
        if warnings:
            analysis.append("**Warnings Found:**")
            analysis.extend(warnings[:10])  # Limit to first 10
            if len(warnings) > 10:
                analysis.append(f"... and {len(warnings) - 10} more warnings")
            analysis.append("")
        
        if important_actions:
            analysis.append("**Key Actions Detected:**")
            analysis.extend(important_actions[:20])  # Limit to first 20
            if len(important_actions) > 20:
                analysis.append(f"... and {len(important_actions) - 20} more actions")
            analysis.append("")
        
        return analysis
    
    def generate_workflow_report_from_data(self, workflow_data: Dict, workflow_name: str) -> str:
        """Generate a comprehensive report for a workflow from pre-fetched data."""
        report = []
        
        report.append(f"## Workflow Analysis: {workflow_name}")
        report.append(f"**Repository:** {self.owner}/{self.repo}")
        report.append(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        report.append("")
        
        runs = workflow_data.get('runs', [])
        
        if not runs:
            report.append("*No workflow run data available.*")
            return '\n'.join(report)
        
        for run_idx, run_data in enumerate(runs, 1):
            run = run_data.get('run', {})
            jobs = run_data.get('jobs', [])
            artifacts = run_data.get('artifacts', [])
            
            report.append(f"\n### Run #{run_idx}: {run.get('display_title', 'N/A')}")
            report.append(f"- **Run ID:** {run.get('id', 'N/A')}")
            report.append(f"- **Status:** {run.get('status', 'N/A')}")
            report.append(f"- **Conclusion:** {run.get('conclusion', 'N/A')}")
            report.append(f"- **Created:** {run.get('created_at', 'N/A')}")
            report.append(f"- **Updated:** {run.get('updated_at', 'N/A')}")
            report.append(f"- **Event:** {run.get('event', 'N/A')}")
            report.append(f"- **Branch:** {run.get('head_branch', 'N/A')}")
            commit_sha = run.get('head_sha', '')
            report.append(f"- **Commit SHA:** {commit_sha[:7] if commit_sha else 'N/A'}")
            report.append("")
            
            # Artifacts
            if artifacts:
                report.append("#### Artifacts:")
                for artifact in artifacts:
                    report.append(f"- **{artifact.get('name', 'Unnamed')}**")
                    report.append(f"  - Size: {artifact.get('size_in_bytes', 0)} bytes")
                    report.append(f"  - Expired: {artifact.get('expired', 'N/A')}")
                    report.append(f"  - Created: {artifact.get('created_at', 'N/A')}")
                report.append("")
            else:
                report.append("*No artifacts found for this run.*\n")
            
            # Jobs
            if jobs:
                report.append(f"#### Jobs ({len(jobs)} total):")
                
                for job_idx, job_data in enumerate(jobs, 1):
                    job = job_data.get('job', {})
                    logs = job_data.get('logs', '')
                    
                    report.append(f"\n##### Job {job_idx}: {job.get('name', 'Unnamed Job')}")
                    report.append(f"- **Job ID:** {job.get('id', 'N/A')}")
                    report.append(f"- **Status:** {job.get('status', 'N/A')}")
                    report.append(f"- **Conclusion:** {job.get('conclusion', 'N/A')}")
                    report.append(f"- **Started:** {job.get('started_at', 'N/A')}")
                    report.append(f"- **Completed:** {job.get('completed_at', 'N/A')}")
                    
                    # List steps
                    steps = job.get('steps', [])
                    if steps:
                        report.append(f"- **Steps ({len(steps)} total):**")
                        for step in steps:
                            status_icon = "✅" if step.get('conclusion') == 'success' else "❌" if step.get('conclusion') == 'failure' else "⏭️"
                            report.append(f"  {status_icon} {step.get('name', 'Unnamed')} ({step.get('conclusion', 'N/A')})")
                    
                    report.append("")
                    
                    # Analyze logs if available
                    if logs:
                        log_analysis = self.analyze_log_lines(logs, job.get('name', 'Unnamed Job'))
                        report.extend(log_analysis)
                    else:
                        report.append("*No logs available for this job.*\n")
            else:
                report.append("*No jobs found for this run.*\n")
            
            report.append("\n---\n")
        
        return '\n'.join(report)
    
    def generate_full_report_from_file(self, data_file: str) -> str:
        """Generate a full report for multiple workflows from a JSON data file."""
        report = []
        
        report.append("# GitHub Actions Workflow Run Analysis Report")
        report.append("")
        report.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        report.append(f"**Repository:** {self.owner}/{self.repo}")
        report.append("")
        report.append("---")
        report.append("")
        
        data = self.load_json_data(data_file)
        
        if not data:
            report.append("*Error: Could not load workflow data.*")
            return '\n'.join(report)
        
        workflows = data.get('workflows', [])
        
        for workflow_data in workflows:
            workflow_name = workflow_data.get('name', 'Unknown Workflow')
            print(f"Processing workflow: {workflow_name}")
            workflow_report = self.generate_workflow_report_from_data(workflow_data, workflow_name)
            report.append(workflow_report)
            report.append("")
        
        return '\n'.join(report)


def main():
    """Main entry point for the workflow analyzer."""
    # Configuration
    OWNER = 'Eckohaus-Ltd'
    REPO = 'Formula-to-3D-Prototype-Engine-V1'
    
    print("=" * 80)
    print("GitHub Actions Workflow Run Analyzer")
    print("=" * 80)
    print()
    
    # Initialize analyzer
    analyzer = WorkflowAnalyzer(OWNER, REPO)
    
    # Determine data file path
    if len(sys.argv) > 1:
        data_file = sys.argv[1]
    else:
        data_file = 'workflow_data.json'
    
    print(f"Reading workflow data from: {data_file}\n")
    
    # Generate report
    print("Generating comprehensive workflow analysis report...\n")
    report = analyzer.generate_full_report_from_file(data_file)
    
    # Save report
    output_file = 'WORKFLOW_ANALYSIS_REPORT.md'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n{'=' * 80}")
    print(f"Report generated successfully: {output_file}")
    print(f"{'=' * 80}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
