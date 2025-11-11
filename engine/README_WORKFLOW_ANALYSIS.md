# Workflow Analysis Tools

This directory contains tools for analyzing GitHub Actions workflow runs.

## Files

### analyze_workflow_runs.py
A Python script that analyzes GitHub Actions workflow run data and generates comprehensive markdown reports.

**Usage:**
```bash
python analyze_workflow_runs.py [data_file.json]
```

The script reads workflow data from a JSON file and generates a detailed analysis report including:
- Workflow run metadata
- Job execution details
- Step-by-step breakdowns
- Log analysis with key findings
- Performance metrics

**Output:** `WORKFLOW_ANALYSIS_REPORT.md`

### fetch_workflow_data.py
A template script for collecting workflow data. This creates a JSON structure template that can be populated with actual workflow run data.

**Usage:**
```bash
python fetch_workflow_data.py
```

**Output:** `workflow_data.json` (template)

## Generated Reports

### WORKFLOW_ANALYSIS_REPORT.md
The main analysis report containing:
- Executive summary
- Detailed analysis of each workflow run
- Job and step breakdowns
- Log analysis with timing information
- Comparative analysis
- Recommendations for optimization
- Security review

## Requirements

- Python 3.x
- No additional dependencies required for the analysis script
- JSON data can be fetched using GitHub API or GitHub CLI tools

## Example Workflow Data Structure

```json
{
  "workflows": [
    {
      "name": "Workflow Name",
      "id": 12345,
      "runs": [
        {
          "run": { /* Run metadata */ },
          "jobs": [
            {
              "job": { /* Job metadata */ },
              "logs": "Job logs content..."
            }
          ],
          "artifacts": [ /* Artifact list */ ]
        }
      ]
    }
  ]
}
```

## Features

- **Line-by-line log analysis**: Detects errors, warnings, and key actions
- **Performance metrics**: Calculates duration and identifies bottlenecks
- **Success tracking**: Provides visual indicators for step outcomes
- **Recommendations**: Suggests optimizations based on analysis
- **Security review**: Highlights security-related configurations

## Notes

The analysis tools are designed to work with data from GitHub Actions workflows and provide actionable insights for workflow optimization and debugging.
