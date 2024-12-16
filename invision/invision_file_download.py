import requests
import json
import os
from datetime import datetime

class InVisionAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.invisionapp.com/v2"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        # Store user and team info after initialization
        self.user_info = self._get_user_info()
        self.team_info = self._get_team_info()

    def _get_user_info(self):
        """Fetch current user information"""
        endpoint = f"{self.base_url}/user"
        response = requests.get(endpoint, headers=self.headers)
        return response.json()

    def _get_team_info(self):
        """Fetch user's team information"""
        endpoint = f"{self.base_url}/teams"
        response = requests.get(endpoint, headers=self.headers)
        return response.json()

    def get_projects(self, filter_type='all'):
        """
        Fetch projects with filtering options
        filter_type: 'all', 'my', 'team'
        """
        endpoint = f"{self.base_url}/projects"
        response = requests.get(endpoint, headers=self.headers)
        projects = response.json().get('projects', [])

        if filter_type == 'all':
            return projects
        elif filter_type == 'my':
            return [p for p in projects if p.get('owner', {}).get('id') == self.user_info.get('id')]
        elif filter_type == 'team':
            team_ids = [team.get('id') for team in self.team_info.get('teams', [])]
            return [p for p in projects if p.get('team', {}).get('id') in team_ids]
        
        return []

    def get_documents(self, project_id, filter_type='all'):
        """
        Fetch documents with filtering options
        filter_type: 'all', 'my', 'team'
        """
        endpoint = f"{self.base_url}/projects/{project_id}/documents"
        response = requests.get(endpoint, headers=self.headers)
        documents = response.json().get('documents', [])

        if filter_type == 'all':
            return documents
        elif filter_type == 'my':
            return [d for d in documents if d.get('owner', {}).get('id') == self.user_info.get('id')]
        elif filter_type == 'team':
            team_ids = [team.get('id') for team in self.team_info.get('teams', [])]
            return [d for d in documents if d.get('team', {}).get('id') in team_ids]
        
        return []

    def export_document(self, document_id, export_path):
        """Export a specific document"""
        endpoint = f"{self.base_url}/documents/{document_id}/exports"
        
        # Request export
        export_response = requests.post(endpoint, headers=self.headers)
        export_data = export_response.json()
        
        # Wait for export to be ready and download
        if export_data.get('url'):
            download_response = requests.get(export_data['url'])
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"invision_export_{document_id}_{timestamp}.zip"
            full_path = os.path.join(export_path, filename)
            
            with open(full_path, 'wb') as f:
                f.write(download_response.content)
            
            return full_path
        return None

def main():
    # Configuration
    api_key = "YOUR_API_KEY"
    export_path = "invision_exports"
    # Set filter_type to 'my', 'team', or 'all'
    filter_type = 'my'  # Change this to 'team' to download team files
    
    # Create export directory
    os.makedirs(export_path, exist_ok=True)
    
    # Initialize API client
    invision = InVisionAPI(api_key)
    
    try:
        # Get filtered projects
        projects = invision.get_projects(filter_type)
        
        if not projects:
            print(f"No projects found with filter: {filter_type}")
            return

        print(f"Found {len(projects)} {filter_type} projects")
        
        for project in projects:
            print(f"\nProject: {project['name']} (ID: {project['id']})")
            
            # Get filtered documents for each project
            documents = invision.get_documents(project['id'], filter_type)
            
            if not documents:
                print(f"No documents found in project with filter: {filter_type}")
                continue

            print(f"Found {len(documents)} documents")
            
            for doc in documents:
                print(f"Exporting document: {doc['name']} (ID: {doc['id']})")
                
                exported_file = invision.export_document(doc['id'], export_path)
                
                if exported_file:
                    print(f"Successfully exported to: {exported_file}")
                else:
                    print(f"Failed to export document: {doc['name']}")
                
    except requests.exceptions.RequestException as e:
        print(f"Error occurred: {str(e)}")

if __name__ == "__main__":
    main()