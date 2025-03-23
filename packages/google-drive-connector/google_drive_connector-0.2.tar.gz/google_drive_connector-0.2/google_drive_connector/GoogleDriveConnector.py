from io import BytesIO
import yaml
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaFileUpload

class GoogleDriveConnector:
    def __init__(self, config_path="config.yaml"):
        self.config = self.load_config(config_path)
        self.scopes = ['https://www.googleapis.com/auth/drive']
        self.service_account_file = self.config["google_drive"]["service_account_file"]
        self.parent_folder_id = self.config["google_drive"]["parent_folder_id"]
        self.creds = self.authenticate()
        self.service = build('drive', 'v3', credentials=self.creds)

    @staticmethod
    def load_config(config_path):
        with open(config_path, "r") as f:
            return yaml.safe_load(f)

    def authenticate(self):
        return service_account.Credentials.from_service_account_file(self.service_account_file, scopes=self.scopes)

    #Get List of all files
    def list_files(self):
        results = self.service.files().list(q=f"'{self.parent_folder_id}' in parents", fields="files(id, name)").execute()
        files = results.get("files", [])
        for idx, file in enumerate(files, start=1):
            print(f"{idx}. {file['name']}")
        return files

    #Get List of all directories
    def list_directories(self):
        results = self.service.files().list(q=f"'{self.parent_folder_id}' in parents and mimeType='application/vnd.google-apps.folder'", fields="files(id, name)").execute()
        directories = results.get("files", [])
        for idx, directory in enumerate(directories, start=1):
            print(f"{idx}. {directory['name']}")
        return directories

    #Upload a file
    def upload_file(self, file_path):
        file_metadata = {'name': file_path.split('/')[-1], 'parents': [self.parent_folder_id]}
        media = MediaFileUpload(file_path, resumable=True)
        file = self.service.files().create(body=file_metadata, media_body=media, fields="id").execute()
        print(f"File uploaded successfully! File ID: {file.get('id')}")
    
    #Get a file id by name
    def get_file_id_by_name(self, file_name):
        """Finds a file by its name and returns its file ID."""
        query = f"name = '{file_name}' and '{self.parent_folder_id}' in parents"
        results = self.service.files().list(q=query, fields="files(id, name)").execute()
        files = results.get("files", [])
        
        if not files:
            print(f"No file found with name: {file_name}")
            return None
        return files[0]['id']

    #Read a file by Name
    def read_file_by_name(self, file_name):
        """Reads a file's content using its name."""
        file_id = self.get_file_id_by_name(file_name)
        if not file_id:
            return None
        return self.read_file(file_id)
    
    #Read a file by Id
    def read_file(self, file_id, binary=False):
        request = self.service.files().get_media(fileId=file_id)
        file_content = BytesIO()
        downloader = request.execute()
        file_content.write(downloader)
        file_content.seek(0)
        
        if binary:
            return file_content.read()
        else:
            return file_content.read().decode('utf-8', errors='ignore')
    
    #write to a file
    def write_to_file(self, file_path, content):
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
        print(f"Content successfully written to {file_path}")


        
connector = GoogleDriveConnector("config.yaml")

#List all files
connector.list_files()

#List all directories
connector.list_directories()

#Upload a file
connector.upload_file("output.txt")

#Read file by name
file_content = connector.read_file_by_name("Hello")
if file_content:
    print(file_content)

#Write to a file
connector.write_to_file("output.txt", "This is a test content.")

