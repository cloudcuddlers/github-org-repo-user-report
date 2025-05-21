# GitHub Organization Access Report Tool

A command-line utility that generates comprehensive CSV reports detailing repositories and user permissions across GitHub organizations.

## Overview

This tool connects to the GitHub API and creates a detailed report of all repositories in specified organizations along with the users who have access, their permission levels, and email addresses (when available). The report is exported as a CSV file for easy analysis.

## Features

- List all repositories across multiple GitHub organizations
- Identify all collaborators for each repository
- Determine permission levels (Admin, Maintain, Write, Triage, Read)
- Retrieve user email addresses when publicly available
- Export data to a CSV file for easy analysis
- Built-in rate limit management for the GitHub API

## Requirements

- Python 3.6+
- GitHub Personal Access Token with appropriate permissions
- Required Python packages:
  - requests

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/github-org-access-report.git
   cd github-org-access-report
   ```

2. Install dependencies:
   ```
   pip install requests
   ```

## Usage

### Basic Usage

```bash
python github_report.py -t YOUR_GITHUB_TOKEN -o report.csv
```

This will generate a report of all organizations you have access to.

### Command Line Arguments

- `-t, --token`: GitHub Personal Access Token (can also be set as GITHUB_TOKEN environment variable)
- `-o, --output`: Output CSV file name (defaults to github_org_report.csv)
- `-org, --organizations`: Specific GitHub organizations to include (space-separated)

### Examples

Generate a report for specific organizations:
```bash
python github_report.py -t YOUR_GITHUB_TOKEN -org organization1 organization2 -o custom_report.csv
```

Using an environment variable for the token:
```bash
export GITHUB_TOKEN=your_github_token
python github_report.py -org myorganization
```

## Output Format

The generated CSV file contains the following columns:
- Organization: The GitHub organization name
- Repo Name: The repository name
- User Name: GitHub username of the collaborator
- Email: User's email address (if publicly available)
- Permission: Access level (Admin, Maintain, Write, Triage, Read)

## GitHub API Token

This tool requires a GitHub Personal Access Token with the following permissions:
- `repo` (Full control of private repositories)
- `read:org` (Read organization membership)

You can create a token at: https://github.com/settings/tokens

## Rate Limiting

The tool includes built-in handling for GitHub API rate limits and will pause execution when approaching the limit.

## License

[MIT License](LICENSE)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
