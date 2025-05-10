import os
import json
import boto3
from datetime import datetime, timedelta

def generate_index_html(bucket_name):
    """
    Generates the HTML page for the web interface listing available reports.
    """
    # Connect to S3
    s3_client = boto3.client('s3')
    
    # Get metadata of reports from the last 30 days
    reports = []
    
    # Calculate dates for the last 30 days
    today = datetime.now()
    for i in range(30):
        date = today - timedelta(days=i)
        date_str = date.strftime('%Y-%m-%d')
        
        try:
            # List objects in the reports directory for this date
            response = s3_client.list_objects_v2(
                Bucket=bucket_name,
                Prefix=f"reports/{date_str}/"
            )
            
            if 'Contents' in response:
                for obj in response['Contents']:
                    if obj['Key'].endswith('.pdf'):
                        # Add report to the list
                        report_name = os.path.basename(obj['Key'])
                        report_url = f"https://{bucket_name}.s3.amazonaws.com/{obj['Key']}"
                        
                        # Extract information from the filename (if available)
                        repo_info = "N/A"
                        state_info = "N/A"
                        if "_" in report_name:
                            parts = report_name.split("_")
                            if len(parts) >= 2:
                                repo_info = parts[0]
                                state_info = parts[1].split(".")[0] if "." in parts[1] else parts[1]
                        
                        report_info = {
                            'date': date_str,
                            'report_name': report_name,
                            'url': report_url,
                            'size': obj['Size'],
                            'last_modified': obj['LastModified'].strftime('%Y-%m-%d %H:%M:%S'),
                            'repo': repo_info,
                            'state': state_info
                        }
                        reports.append(report_info)
        except Exception as e:
            print(f"Error listing reports for {date_str}: {str(e)}")
    
    # Sort reports by date (most recent first)
    reports.sort(key=lambda x: x.get('last_modified', ''), reverse=True)
    
    # Generate HTML
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>GitHub Pull Request Reports</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body { padding-top: 20px; }
            .report-card { margin-bottom: 20px; transition: transform 0.2s; }
            .report-card:hover { transform: translateY(-5px); box-shadow: 0 10px 20px rgba(0,0,0,0.1); }
            .empty-state { text-align: center; padding: 50px; color: #6c757d; }
            .search-container { margin-bottom: 20px; }
            .badge-state-open { background-color: #28a745; }
            .badge-state-closed { background-color: #dc3545; }
            .badge-state-all { background-color: #17a2b8; }
            .last-updated { font-size: 0.8rem; color: #6c757d; margin-top: 20px; }
        </style>
    </head>
    <body>
        <div class="container">
            <header class="mb-4">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <h1 class="display-4">GitHub Pull Request Reports</h1>
                        <p class="lead">View the generated reports for your GitHub repositories</p>
                    </div>
                    <div>
                        <button class="btn btn-outline-primary" onclick="window.location.reload()">
                            <i class="bi bi-arrow-clockwise"></i> Refresh
                        </button>
                    </div>
                </div>
            </header>
            
            <div class="search-container">
                <input type="text" class="form-control" id="searchInput" placeholder="Search reports...">
            </div>
            
            <div class="row" id="reportsContainer">
    """
    
    if reports:
        for report in reports:
            report_date = report.get('date', 'Unknown date')
            report_name = report.get('report_name', 'Report')
            report_url = report.get('url', '#')
            report_size = report.get('size', 0)
            report_size_mb = round(report_size / 1024 / 1024, 2) if report_size > 0 else 0
            report_repo = report.get('repo', 'N/A')
            report_state = report.get('state', 'N/A')
            
            # Determine the badge class based on the state
            badge_class = "badge-state-all"
            if report_state.lower() == "open":
                badge_class = "badge-state-open"
            elif report_state.lower() == "closed":
                badge_class = "badge-state-closed"
            
            html += f"""
                <div class="col-md-4 report-item" data-name="{report_name}" data-repo="{report_repo}" data-state="{report_state}">
                    <div class="card report-card">
                        <div class="card-body">
                            <h5 class="card-title">{report_name}</h5>
                            <h6 class="card-subtitle mb-2 text-muted">{report_date}</h6>
                            <p class="card-text">
                                <span class="badge {badge_class}">{report_state}</span>
                                <span class="badge bg-secondary">{report_repo}</span>
                            </p>
                            <p class="card-text">Size: {report_size_mb} MB</p>
                            <a href="{report_url}" class="btn btn-primary" target="_blank">View Report</a>
                        </div>
                    </div>
                </div>
            """
    else:
        html += """
                <div class="col-12">
                    <div class="empty-state">
                        <h3>No reports found</h3>
                        <p>No reports are available for viewing.</p>
                    </div>
                </div>
        """
    
    html += """
            </div>
            
            <footer class="mt-5 text-center text-muted">
                <p>Automatically generated by AWS Challenge Automation</p>
                <p class="last-updated">Last updated: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</p>
            </footer>
        </div>
        
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            // Search function
            document.getElementById('searchInput').addEventListener('keyup', function() {
                const searchTerm = this.value.toLowerCase();
                const items = document.getElementsByClassName('report-item');
                
                for (let i = 0; i < items.length; i++) {
                    const item = items[i];
                    const name = item.getAttribute('data-name').toLowerCase();
                    const repo = item.getAttribute('data-repo').toLowerCase();
                    const state = item.getAttribute('data-state').toLowerCase();
                    
                    if (name.includes(searchTerm) || repo.includes(searchTerm) || state.includes(searchTerm)) {
                        item.style.display = '';
                    } else {
                        item.style.display = 'none';
                    }
                }
            });
        </script>
    </body>
    </html>
    """
    
    # Save HTML to S3
    try:
        s3_client.put_object(
            Body=html,
            Bucket=bucket_name,
            Key="index.html",
            ContentType="text/html"
        )
        
        # Create error page
        error_html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Error - GitHub Reports</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        </head>
        <body>
            <div class="container text-center mt-5">
                <h1>Oops! Something went wrong.</h1>
                <p class="lead">The requested page could not be found.</p>
                <a href="/" class="btn btn-primary">Return to the homepage</a>
            </div>
        </body>
        </html>
        """
        
        s3_client.put_object(
            Body=error_html,
            Bucket=bucket_name,
            Key="error.html",
            ContentType="text/html"
        )
        
        return f"https://{bucket_name}.s3-website-{os.environ.get('AWS_REGION', 'us-east-1')}.amazonaws.com"
    except Exception as e:
        print(f"Error saving HTML to S3: {str(e)}")
        return None

if __name__ == "__main__":
    # For local testing
    bucket_name = os.environ.get('BUCKET_NAME')
    if bucket_name:
        website_url = generate_index_html(bucket_name)
        print(f"Web interface generated: {website_url}")
    else:
        print("BUCKET_NAME environment variable is required")