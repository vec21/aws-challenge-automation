# AWS Challenge Automation - Project Documentation

## Project Overview
This project is a CLI tool for automating code reviews with Amazon Q Developer. It integrates with GitHub repositories to fetch pull requests, analyze them, and generate PDF reports. The reports can be stored in an S3 bucket and accessed through a web interface.

## Architecture

### Infrastructure (Pulumi)
The infrastructure is defined using Pulumi with the following AWS resources:

- **S3 Bucket**: Stores generated PDF reports and hosts the web interface
  - Configured with website hosting capabilities
  - Public read access policy for viewing reports

- **Lambda Function**: Processes code review requests
  - Runtime: Python 3.9
  - Memory: 512MB
  - Timeout: 5 minutes
  - Environment variables:
    - BUCKET_NAME: S3 bucket name
    - GITHUB_TOKEN: GitHub API token
    - SNS_TOPIC_ARN: SNS topic ARN for notifications

- **IAM Role**: Provides Lambda with necessary permissions
  - S3 full access
  - SNS full access

- **SNS Topic**: Sends notifications when reports are generated

- **CloudWatch Event Rule**: Triggers Lambda function daily
  - Schedule: 8:00 AM UTC daily
  - Target: Lambda function with predefined parameters

### Components

#### CLI Tool (`cli.py`)
A command-line interface built with Click that provides the following functionality:

- **review_code**: Main command to review GitHub pull requests
  - Options:
    - `--repo`: GitHub repository (user/repo) or comma-separated list
    - `--token`: GitHub token (or set as GITHUB_TOKEN environment variable)
    - `--bucket`: S3 bucket name for report storage
    - `--days`: Number of days to look back for PRs (default: 32)
    - `--output`: Output PDF filename
    - `--state`: State of PRs to analyze (open, closed, all)
    - `--analyze`: Flag to perform code analysis on PRs
    - `--notify`: Flag to send email notification
    - `--email`: Email for notifications
    - `--limit`: Limit of PRs to process per repository

- **Features**:
  - Connects to GitHub API to fetch pull requests
  - Filters PRs by date and state
  - Performs basic code analysis (complexity, issues, languages)
  - Generates PDF reports with PR details
  - Uploads reports to S3
  - Sends email notifications via SNS

#### Lambda Handler (`handler.py`)
Processes events from CloudWatch or API Gateway:

- Extracts parameters from the event
- Uses the CLI tool to generate reports
- Returns a response with the report location

#### Web Interface (`web_interface.py`)
Generates a responsive HTML interface to browse and search reports:

- Lists reports from the last 30 days
- Provides filtering and search capabilities
- Shows report metadata (repository, state, size)
- Updates automatically when new reports are uploaded

## Usage

### Local Usage
```bash
# Set GitHub token
export GITHUB_TOKEN=your_github_token

# Review a repository
python -m src.cli review-code --repo user/repo --analyze

# Review multiple repositories
python -m src.cli review-code --repo "user/repo1,user/repo2" --days 7 --state all

# Upload to S3 and send notification
python -m src.cli review-code --repo user/repo --bucket your-bucket --notify --email user@example.com
```

### AWS Deployment
1. Configure Pulumi with AWS credentials
2. Set GitHub token in Pulumi config:
   ```bash
   pulumi config set --secret github_token your_github_token
   ```
3. Deploy the infrastructure:
   ```bash
   pulumi up
   ```

## Security Considerations
- GitHub token is stored as a secret in environment variables
- S3 bucket is configured with public read access for reports
- Lambda has least privilege permissions through IAM role

## Future Enhancements
- Integrate Amazon Q Developer programmatically for code reviews
- Add SNS notifications for report generation
- Generate automated tests using Amazon Q Developer
- Implement authentication for the web interface
- Add support for more code analysis metrics

## Dependencies
- Python 3.9+
- AWS SDK (boto3)
- PyGithub
- Click
- ReportLab
- Pulumi AWS

## License
This project is licensed under the terms of the included LICENSE file.
