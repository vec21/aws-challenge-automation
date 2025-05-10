import json
import os
from cli import review_code

def handler(event, context):
    """
    Lambda function handler to process code review requests.
    
    Expected parameters in the event:
    - repo: GitHub repository name (user/repo) or comma-separated list
    - days: Number of days to look back (default: 7)
    - analyze: Whether to perform code analysis (true/false)
    - notify: Whether to send email notification (true/false)
    - email: Email for notification (required if notify=true)
    - state: State of PRs to be analyzed (open, closed, all)
    """
    # Get parameters from the event
    repo = event.get('repo', 'vec21/aws-challenge-automation')
    days = event.get('days', 7)
    analyze = event.get('analyze', False)
    notify = event.get('notify', False)
    email = event.get('email')
    state = event.get('state', 'open')
    
    # Get GitHub token from environment variables
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        raise ValueError("GITHUB_TOKEN environment variable is required")
    
    # Get bucket name from environment variables
    bucket = os.getenv('BUCKET_NAME')
    
    # Generate output filename
    timestamp = context.aws_request_id if context else 'local'
    output = f"/tmp/report-{timestamp}.pdf"
    
    # Prepare arguments for the CLI
    args = ['--repo', repo, '--token', token, '--days', str(days), '--output', output, '--state', state]
    
    if bucket:
        args.extend(['--bucket', bucket])
    
    if analyze:
        args.append('--analyze')
    
    if notify and email:
        args.extend(['--notify', '--email', email])
    
    # Execute code review
    review_code(args)
    
    # Build response
    response = {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Review completed successfully',
            'report': f"s3://{bucket}/reports/{output.split('/')[-1]}" if bucket else output,
            'website': f"https://{bucket}.s3-website-{os.environ.get('AWS_REGION', 'us-east-1')}.amazonaws.com" if bucket else None
        })
    }
    
    return response