import click
import os
import boto3
import time
from datetime import datetime, timedelta, timezone
from github import Github
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

@click.group()
def cli():
    """CLI for automating code review in GitHub repositories."""
    pass

@cli.command()
@click.option('--repo', required=True, help='GitHub repository (user/repo) or comma-separated list')
@click.option('--token', default=lambda: os.environ.get("GITHUB_TOKEN"), help='GitHub token (or set GITHUB_TOKEN as environment variable)')
@click.option('--bucket', default='', help='S3 bucket name for report storage')
@click.option('--days', default=32, type=int, help='Number of days to look back for PRs')
@click.option('--output', default='report.pdf', help='Output PDF filename')
@click.option('--state', default='open', type=click.Choice(['open', 'closed', 'all']), help='State of PRs to be analyzed (open, closed, all)')
@click.option('--analyze', is_flag=True, help='Perform code analysis on PRs')
@click.option('--notify', is_flag=True, help='Send email notification when the report is ready')
@click.option('--email', help='Email for notifications')
@click.option('--limit', default=100, type=int, help='Limit of PRs to be processed per repository')
def review_code(repo, token, bucket, days, output, state='open', analyze=False, notify=False, email=None, limit=100):
    """Reviews pull requests from a GitHub repository and generates a PDF report."""
    
    # Check if it's a list of repositories
    repositories = [r.strip() for r in repo.split(',')]
    all_pr_data = []
    
    # Connect to GitHub
    try:
        g = Github(token, per_page=30)  # Reduce the number of items per page
        
        # Cutoff date for filtering PRs
        since_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        for repo_name in repositories:
            click.echo(f"Reviewing repository {repo_name}")
            
            try:
                repository = g.get_repo(repo_name)
                click.echo(f"Connected to repository: {repository.full_name}")
                
                # Get pull requests with the specified state
                pulls = repository.get_pulls(state=state)
                total_pulls = pulls.totalCount
                click.echo(f"Found {total_pulls} pull requests with state '{state}'")
                
                # Limit the number of PRs processed
                pr_count = 0
                click.echo(f"Processing up to {limit} pull requests...")
                
                # Prepare data for the report
                repo_pr_data = []
                for pr in pulls:
                    # Limit the number of PRs processed
                    if pr_count >= limit:
                        click.echo(f"Limit of {limit} PRs reached. Use --limit to increase.")
                        break
                    
                    # Filter by date if necessary
                    if pr.created_at < since_date:
                        continue
                    
                    pr_count += 1
                    click.echo(f"Processing PR #{pr.number} ({pr_count}/{min(total_pulls, limit)})")
                    
                    pr_info = {
                        'repo': repo_name,
                        'number': pr.number,
                        'title': pr.title,
                        'user': pr.user.login,
                        'created_at': pr.created_at,
                        'updated_at': pr.updated_at,
                        'comments': pr.comments,
                        'additions': pr.additions,
                        'deletions': pr.deletions,
                        'changed_files': pr.changed_files,
                        'url': pr.html_url,
                        'state': pr.state,
                        'merged': pr.merged if hasattr(pr, 'merged') else False,
                        'analysis': {}
                    }
                    
                    # Perform code analysis if requested
                    if analyze:
                        pr_info['analysis'] = analyze_pull_request(repository, pr)
                        # Small pause to avoid rate limit
                        time.sleep(0.5)
                    
                    repo_pr_data.append(pr_info)
                
                all_pr_data.extend(repo_pr_data)
                
            except Exception as e:
                click.echo(f"Error processing repository {repo_name}: {str(e)}", err=True)
                
        if not all_pr_data:
            click.echo(f"No pull requests with state '{state}' found in the last {days} days.")
            return
        
        # Generate filename with repository and state information
        if len(repositories) == 1:
            repo_short = repositories[0].split('/')[1] if '/' in repositories[0] else repositories[0]
        else:
            repo_short = "multi-repos"

        if output == 'report.pdf':  # If the user didn't specify a custom name
            output = f"{repo_short}_{state}.pdf"

        # Generate PDF report
        pdf_path = generate_pdf_report(repositories, all_pr_data, output, days, state)
        click.echo(f"PDF report generated: {pdf_path}")
        
        # Upload to S3 if bucket is provided
        s3_url = None
        if bucket:
            s3_url = upload_to_s3(pdf_path, bucket)
            click.echo(f"Report uploaded to S3: {s3_url}")
            
        # Send email notification if requested
        if notify and email:
            send_notification(email, repositories, pdf_path, s3_url)
            click.echo(f"Notification sent to: {email}")
            
    except Exception as e:
        click.echo(f"Error processing pull requests: {str(e)}", err=True)

def analyze_pull_request(repository, pr):
    """Performs basic code analysis on the pull request."""
    analysis = {
        'complexity': 0,
        'issues': [],
        'languages': {},
        'risk_score': 0
    }
    
    try:
        # Get changed files
        files = pr.get_files()
        
        # Analyze each file
        for file in files:
            # Identify language by file name
            extension = os.path.splitext(file.filename)[1].lower()
            language = get_language_from_extension(extension)
            
            # Count lines by language
            if language in analysis['languages']:
                analysis['languages'][language] += file.changes
            else:
                analysis['languages'][language] = file.changes
                
            # Check size of changes
            if file.changes > 500:
                analysis['issues'].append(f"File {file.filename} has too many changes ({file.changes})")
                analysis['risk_score'] += 1
                
            # Check code patterns (simplified)
            if file.patch:
                if "TODO" in file.patch:
                    analysis['issues'].append(f"TODOs found in {file.filename}")
                if "FIXME" in file.patch:
                    analysis['issues'].append(f"FIXMEs found in {file.filename}")
                    analysis['risk_score'] += 1
                    
        # Calculate complexity based on number of files and changes
        analysis['complexity'] = min(10, len(list(files)) // 2)
        
    except Exception as e:
        analysis['issues'].append(f"Analysis error: {str(e)}")
        
    return analysis

def get_language_from_extension(extension):
    """Returns the language based on the file extension."""
    language_map = {
        '.py': 'Python',
        '.js': 'JavaScript',
        '.ts': 'TypeScript',
        '.java': 'Java',
        '.cs': 'C#',
        '.go': 'Go',
        '.rb': 'Ruby',
        '.php': 'PHP',
        '.html': 'HTML',
        '.css': 'CSS',
        '.md': 'Markdown',
        '.json': 'JSON',
        '.yml': 'YAML',
        '.yaml': 'YAML',
        '.xml': 'XML',
        '.sh': 'Shell',
        '.bat': 'Batch',
        '.ps1': 'PowerShell'
    }
    return language_map.get(extension, 'Other')

def generate_pdf_report(repositories, pr_data, output_filename, days_filter, state):
    """Generates a PDF report with pull request data."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Create PDF document
    doc = SimpleDocTemplate(output_filename, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []
    
    # Title
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=16,
        alignment=1,
        spaceAfter=12
    )
    
    repo_names = ", ".join(repositories) if len(repositories) <= 3 else f"{len(repositories)} repositories"
    elements.append(Paragraph(f"Pull Request Report - {repo_names}", title_style))
    elements.append(Paragraph(f"Generated on: {now}", styles["Normal"]))
    elements.append(Paragraph(f"Period: last {days_filter} days", styles["Normal"]))
    elements.append(Paragraph(f"State: {state}", styles["Normal"]))
    elements.append(Spacer(1, 0.25*inch))
    
    # Summary
    elements.append(Paragraph(f"Total Pull Requests: {len(pr_data)}", styles["Heading2"]))
    
    # Summary by repository
    repo_counts = {}
    for pr in pr_data:
        repo_name = pr['repo']
        if repo_name in repo_counts:
            repo_counts[repo_name] += 1
        else:
            repo_counts[repo_name] = 1
    
    if len(repo_counts) > 1:
        elements.append(Spacer(1, 0.1*inch))
        elements.append(Paragraph("PRs by Repository:", styles["Heading3"]))
        for repo_name, count in repo_counts.items():
            elements.append(Paragraph(f"• {repo_name}: {count} PRs", styles["Normal"]))
    
    elements.append(Spacer(1, 0.2*inch))
    
    # PR table
    if pr_data:
        # Table header
        table_data = [["Repo", "#", "Title", "Author", "State", "Created on", "Files", "+/-"]]
        
        # Table data
        for pr in pr_data:
            created_date = pr['created_at'].strftime("%Y-%m-%d")
            changes = f"{pr['additions']}/{pr['deletions']}"
            repo_short = pr['repo'].split('/')[1] if '/' in pr['repo'] else pr['repo']
            
            # Determine state for display
            pr_state = pr['state']
            if pr.get('merged', False):
                pr_state = "merged"
                
            table_data.append([
                repo_short,
                str(pr['number']),
                pr['title'][:40] + ('...' if len(pr['title']) > 40 else ''),
                pr['user'],
                pr_state,
                created_date,
                str(pr['changed_files']),
                changes
            ])
        
        # Create table
        table = Table(table_data, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(table)
        
        # Details of each PR
        elements.append(Spacer(1, 0.2*inch))
        elements.append(Paragraph("Pull Request Details", styles["Heading2"]))
        
        for pr in pr_data:
            elements.append(Spacer(1, 0.1*inch))
            elements.append(Paragraph(f"[{pr['repo']}] PR #{pr['number']}: {pr['title']}", styles["Heading3"]))
            elements.append(Paragraph(f"Author: {pr['user']}", styles["Normal"]))
            elements.append(Paragraph(f"State: {pr['state']}{' (merged)' if pr.get('merged', False) else ''}", styles["Normal"]))
            elements.append(Paragraph(f"Created on: {pr['created_at'].strftime('%Y-%m-%d %H:%M:%S')}", styles["Normal"]))
            elements.append(Paragraph(f"Last updated: {pr['updated_at'].strftime('%Y-%m-%d %H:%M:%S')}", styles["Normal"]))
            elements.append(Paragraph(f"Comments: {pr['comments']}", styles["Normal"]))
            elements.append(Paragraph(f"Changed files: {pr['changed_files']}", styles["Normal"]))
            elements.append(Paragraph(f"Additions/Deletions: +{pr['additions']}/-{pr['deletions']}", styles["Normal"]))
            elements.append(Paragraph(f"URL: {pr['url']}", styles["Normal"]))
            
            # Add analysis results if available
            if pr.get('analysis') and (pr['analysis'].get('issues') or pr['analysis'].get('languages')):
                elements.append(Paragraph("Code Analysis:", styles["Heading4"]))
                
                if 'languages' in pr['analysis'] and pr['analysis']['languages']:
                    lang_text = ", ".join([f"{lang}: {lines}" for lang, lines in pr['analysis']['languages'].items()])
                    elements.append(Paragraph(f"Languages: {lang_text}", styles["Normal"]))
                
                if 'complexity' in pr['analysis']:
                    elements.append(Paragraph(f"Estimated complexity: {pr['analysis']['complexity']}/10", styles["Normal"]))
                
                if 'risk_score' in pr['analysis']:
                    elements.append(Paragraph(f"Risk score: {pr['analysis']['risk_score']}", styles["Normal"]))
                
                if pr['analysis'].get('issues'):
                    elements.append(Paragraph("Identified issues:", styles["Normal"]))
                    for issue in pr['analysis']['issues']:
                        elements.append(Paragraph(f"• {issue}", styles["Normal"]))
            
            elements.append(Spacer(1, 0.1*inch))
    
    # Build the PDF
    doc.build(elements)
    return output_filename

def upload_to_s3(file_path, bucket_name):
    """Uploads the PDF file to an S3 bucket."""
    try:
        s3_client = boto3.client('s3')
        
        # Get the base filename without extension
        file_name_base = os.path.splitext(os.path.basename(file_path))[0]
        file_ext = os.path.splitext(os.path.basename(file_path))[1]
        
        # Add timestamp to the filename to make it unique
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_file_name = f"{file_name_base}_{timestamp}{file_ext}"
        
        # Define the S3 path
        date_str = datetime.now().strftime('%Y-%m-%d')
        object_key = f"reports/{date_str}/{unique_file_name}"
        
        s3_client.upload_file(file_path, bucket_name, object_key)
        
        # Generate public URL if the bucket has public access
        url = f"https://{bucket_name}.s3.amazonaws.com/{object_key}"
        
        # Update the web interface
        try:
            from web_interface import generate_index_html
            generate_index_html(bucket_name)
        except Exception as e:
            print(f"Error updating web interface: {str(e)}")
        
        return url
    except Exception as e:
        click.echo(f"Error uploading to S3: {str(e)}", err=True)
        return None

def send_notification(email, repositories, report_path, s3_url=None):
    """Sends an email notification when the report is ready."""
    try:
        # Use SNS to send email
        sns_client = boto3.client('sns')
        
        # Create SNS topic if it doesn't exist
        topic_name = "github-report-notifications"
        topic_response = sns_client.create_topic(Name=topic_name)
        topic_arn = topic_response['TopicArn']
        
        # Subscribe email to the topic if not already subscribed
        sns_client.subscribe(
            TopicArn=topic_arn,
            Protocol='email',
            Endpoint=email
        )
        
        # Prepare message
        repo_names = ", ".join(repositories) if len(repositories) <= 3 else f"{len(repositories)} repositories"
        subject = f"Pull Request Report - {repo_names}"
        
        message = f"The Pull Request report for {repo_names} is ready.\n\n"
        if s3_url:
            message += f"You can access it at: {s3_url}\n\n"
        else:
            message += f"The report was generated as {os.path.basename(report_path)}.\n\n"
            
        message += "This is an automated email, please do not reply."
        
        # Send notification
        sns_client.publish(
            TopicArn=topic_arn,
            Subject=subject,
            Message=message
        )
        
        return True
    except Exception as e:
        click.echo(f"Error sending notification: {str(e)}", err=True)
        return False

if __name__ == '__main__':
    cli()