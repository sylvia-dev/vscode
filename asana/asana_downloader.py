import os
from datetime import datetime, timedelta
import requests
from pathlib import Path
import json
from dotenv import load_dotenv
import configparser
import sys
import uuid
import re

class AsanaDownloader:
    def __init__(self, access_token):
        print("Initializing AsanaDownloader...")
        self.access_token = access_token
        self.headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json'
        }
        self.base_url = 'https://app.asana.com/api/1.0'
        self.total_projects = 0
        self.tasks_with_attachments = 0
        self.total_files = 0
        self.total_size = 0
        self.errors = []

    def _sanitize_filename(self, filename):
        """Remove or replace invalid characters in filename"""
        if not filename:
            return f"unnamed_file_{uuid.uuid4().hex[:8]}"
            
        # Convert to string if it isn't already
        filename = str(filename)
        
        # Replace invalid characters with underscores
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        
        # Remove leading/trailing spaces and periods
        filename = filename.strip('. ')
        
        # Ensure filename isn't empty after sanitization
        if not filename or filename.isspace():
            filename = f"unnamed_file_{uuid.uuid4().hex[:8]}"
            
        # Truncate if too long (leaving room for extension)
        max_length = 255
        if len(filename) > max_length:
            base, ext = os.path.splitext(filename)
            filename = base[:max_length-len(ext)] + ext
            
        return filename

    def _get_unique_filepath(self, directory, filename):
        """Ensure filename is unique in directory"""
        base, ext = os.path.splitext(filename)
        counter = 1
        final_path = directory / filename
        
        while final_path.exists():
            new_filename = f"{base}_{counter}{ext}"
            final_path = directory / new_filename
            counter += 1
            
        return final_path

    def _guess_extension(self, content_type):
        """Guess file extension from content type"""
        content_type = content_type.lower()
        extensions = {
            'image/jpeg': '.jpg',
            'image/png': '.png',
            'image/gif': '.gif',
            'application/pdf': '.pdf',
            'text/plain': '.txt',
            'application/msword': '.doc',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
            'application/vnd.ms-excel': '.xls',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': '.xlsx',
            'application/vnd.ms-powerpoint': '.ppt',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation': '.pptx',
            'application/zip': '.zip',
            'text/csv': '.csv',
            'application/json': '.json'
        }
        return extensions.get(content_type, '.unknown')

    def get_workspace_gid(self):
        """Fetch first available workspace GID"""
        print("\nFetching workspace information...")
        url = f'{self.base_url}/workspaces'
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            workspaces = response.json()['data']
            if workspaces:
                workspace_gid = workspaces[0]['gid']
                print(f"Found workspace: {workspaces[0].get('name', 'Unnamed')} (GID: {workspace_gid})")
                return workspace_gid
            return None
        except requests.exceptions.RequestException as e:
            print(f"Error fetching workspace: {e}")
            return None

    def get_workspace_projects(self, workspace_gid):
        """Fetch all projects in a workspace"""
        print("\nFetching projects from workspace...")
        url = f'{self.base_url}/projects'
        params = {'workspace': workspace_gid, 'limit': 100}
        
        try:
            projects = []
            while True:
                print(f"Fetching batch of projects...")
                response = requests.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                data = response.json()
                
                batch = data['data']
                projects.extend(batch)
                
                if 'next_page' in data and data['next_page']:
                    params['offset'] = data['next_page']['offset']
                    print("Getting next page of projects...")
                else:
                    break
            
            self.total_projects = len(projects)
            print(f"\nFound {self.total_projects} projects in workspace")
            return projects
        except requests.exceptions.RequestException as e:
            print(f"Error fetching projects: {e}")
            return []

    def get_project_tasks(self, project_gid, modified_since):
        """Fetch tasks from a project modified after specified date"""
        print(f"\nFetching tasks modified since {modified_since.isoformat()}")
        url = f'{self.base_url}/tasks'
        params = {
            'project': project_gid,
            'modified_since': modified_since.isoformat(),
            'opt_fields': 'name,modified_at,attachments,attachments.name,attachments.download_url',
            'limit': 100
        }
        
        try:
            tasks = []
            while True:
                response = requests.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                data = response.json()
                
                batch = data['data']
                tasks.extend(batch)
                
                if 'next_page' in data and data['next_page']:
                    params['offset'] = data['next_page']['offset']
                else:
                    break
            
            tasks_with_attachments = sum(1 for task in tasks if task.get('attachments'))
            if tasks_with_attachments > 0:
                print(f"Found {tasks_with_attachments} tasks with attachments")
            self.tasks_with_attachments += tasks_with_attachments
            return tasks
        except requests.exceptions.RequestException as e:
            print(f"Error fetching tasks: {e}")
            return []

    def download_attachment(self, attachment, base_path, project_name, task_name):
        """Download an attachment and save it to the specified path"""
        try:
            print(f"\nProcessing attachment for task: {task_name}")
            
            # Get attachment details
            attachment_url = f'{self.base_url}/attachments/{attachment["gid"]}'
            print(f"Fetching attachment details from: {attachment_url}")
            response = requests.get(attachment_url, headers=self.headers)
            response.raise_for_status()
            attachment_data = response.json()['data']
            
            # Get download URL
            download_url = attachment_data.get('download_url')
            if not download_url:
                print(f"Warning: No download URL for attachment in task '{task_name}'")
                return False
            
            print(f"Got download URL: {download_url[:100]}...")
            
            # Create directory structure
            date_str = datetime.now().strftime('%Y-%m-%d')
            file_path = Path(base_path) / date_str / self._sanitize_filename(project_name) / self._sanitize_filename(task_name)
            print(f"Creating directory: {file_path}")
            file_path.mkdir(parents=True, exist_ok=True)
            
            # Download file
            print("Downloading file content...")
            file_response = requests.get(download_url)
            file_response.raise_for_status()
            
            # Update statistics
            self.total_files += 1
            self.total_size += len(file_response.content)
            
            # Get filename from attachment data or generate one
            file_name = attachment_data.get('name')
            if not file_name:
                content_disp = file_response.headers.get('content-disposition')
                if content_disp and 'filename=' in content_disp:
                    file_name = content_disp.split('filename=')[-1].strip('"\'')
                else:
                    ext = self._guess_extension(file_response.headers.get('content-type', ''))
                    file_name = f"attachment_{uuid.uuid4().hex[:8]}{ext}"
                print(f"Generated filename: {file_name}")
            
            # Sanitize filename and ensure it's unique
            file_name = self._sanitize_filename(file_name)
            full_path = self._get_unique_filepath(file_path, file_name)
            print(f"Saving to: {full_path}")
            
            # Save file
            with open(full_path, 'wb') as f:
                f.write(file_response.content)
            
            print(f"Successfully downloaded: {full_path}")
            return True
        except requests.exceptions.RequestException as e:
            error_msg = f"Error downloading attachment in task '{task_name}': {e}"
            print(error_msg)
            self.errors.append(error_msg)
            return False
        except Exception as e:
            error_msg = f"Unexpected error downloading attachment in task '{task_name}': {e}"
            print(error_msg)
            self.errors.append(error_msg)
            return False

    def print_statistics(self):
        """Print download statistics and any errors"""
        print(f"\nDownload Statistics:")
        print(f"Total projects processed: {self.total_projects}")
        print(f"Tasks with attachments: {self.tasks_with_attachments}")
        print(f"Total files downloaded: {self.total_files}")
        print(f"Total size downloaded: {self.total_size / (1024*1024):.2f} MB")
        
        if self.errors:
            print("\nErrors encountered:")
            for error in self.errors:
                print(f"- {error}")

def load_config():
    """Load configuration from .env file or config.ini"""
    print("Loading configuration...")
    load_dotenv()
    token = os.getenv('ASANA_TOKEN')
    
    if not token:
        print("No token found in .env, checking config.ini...")
        config = configparser.ConfigParser()
        if os.path.exists('config.ini'):
            config.read('config.ini')
            token = config.get('Asana', 'token', fallback=None)
    
    if token:
        print("Token loaded successfully")
    else:
        print("No token found in configuration files")
    return token

def main():
    # Load configuration
    token = load_config()
    if not token:
        print("Error: No Asana token found. Please set up your configuration.")
        sys.exit(1)
    
    # Configuration
    DOWNLOAD_PATH = 'asana_files'    # Base directory for downloads
    DAYS_AGO = 30                    # Number of days to look back
    
    print(f"\nStarting download process...")
    print(f"Download path: {DOWNLOAD_PATH}")
    print(f"Looking back {DAYS_AGO} days")
    
    # Initialize downloader
    downloader = AsanaDownloader(token)
    
    # Get workspace GID automatically
    workspace_gid = downloader.get_workspace_gid()
    if not workspace_gid:
        print("Error: Could not find any workspace.")
        sys.exit(1)
    
    # Calculate date threshold
    modified_since = datetime.now() - timedelta(days=DAYS_AGO)
    print(f"Fetching files modified since: {modified_since}")
    
    # Create base download directory
    Path(DOWNLOAD_PATH).mkdir(exist_ok=True)
    
    # Get all projects
    projects = downloader.get_workspace_projects(workspace_gid)
    
    # Process each project
    for project in projects:
        print(f"\nProcessing project: {project['name']}")
        
        # Get tasks for project
        tasks = downloader.get_project_tasks(project['gid'], modified_since)
        
        # Process each task
        for task in tasks:
            attachments = task.get('attachments', [])
            if attachments:
                print(f"Processing task: {task['name']} ({len(attachments)} attachments)")
                
                # Download each attachment
                for attachment in attachments:
                    downloader.download_attachment(
                        attachment,
                        DOWNLOAD_PATH,
                        project['name'],
                        task['name']
                    )
    
    # Print final statistics
    downloader.print_statistics()

if __name__ == "__main__":
    main()